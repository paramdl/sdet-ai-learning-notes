# PART 21 — Docker & Kubernetes for AI QA Engineers

> **Goal of this part:** exactly as much container and orchestration knowledge as this job requires, and no more. You are not becoming a platform engineer. You are becoming someone who can run their own test environment, reproduce a CI failure locally, and read logs from a production pod without asking for help.

---

# PART A — DOCKER 🔴 MUST LEARN

## 21.1 Why a tester needs it

| Need | Docker's answer |
|---|---|
| Run a vector DB locally without installing it | `docker run qdrant/qdrant` |
| Reproduce "works on my machine" | The image is the machine |
| Run your eval suite the same way CI does | Same image, same result |
| Spin up a whole test stack | Compose |
| Test against a local model server | Container with a mounted model |
| Isolate conflicting Python dependencies | One image per project |

## 21.2 The concepts

| Term | Meaning | Analogy |
|---|---|---|
| **Image** | Immutable filesystem + config | A class |
| **Container** | A running instance of an image | An object |
| **Dockerfile** | The recipe for building an image | The class definition |
| **Volume** | Persistent storage outside the container | A mounted external drive |
| **Network** | How containers reach each other | A private LAN |
| **Compose** | Multi-container definitions in one YAML | docker-compose.yml |
| **Registry** | Where images are stored | Docker Hub, GHCR, ECR |

**The one thing that trips people up:** containers are ephemeral. Anything written inside a container is gone when it stops, unless it is on a volume. Test data, model caches, and vector DB contents all need volumes.

## 21.3 The commands you will actually use

```bash
# Run a vector DB for your RAG lab. -d = background, -p = port mapping,
# -v = persist data so it survives a restart.
docker run -d --name qdrant -p 6333:6333 \
  -v "$PWD/qdrant_data:/qdrant/storage" qdrant/qdrant

# What is running?
docker ps                      # running
docker ps -a                   # including stopped

# Logs — the command you will use most in a debugging session.
docker logs qdrant             # all
docker logs -f qdrant          # follow (like tail -f)
docker logs --tail 100 qdrant  # last 100 lines
docker logs qdrant 2>&1 | grep -i error

# Get a shell inside a running container to inspect its state.
docker exec -it qdrant sh

# Environment variables — how you inject API keys and config.
docker run --env-file .env myimage
docker run -e LLM_MODEL=llama3.1:8b myimage

# Clean up (disk fills fast with AI images — they are large).
docker system df               # what is using space
docker system prune -a         # remove unused images/containers
docker stop qdrant && docker rm qdrant
```

## 21.4 A Dockerfile for your eval suite

```dockerfile
# Pin the version. "python:3" changes under you and breaks reproducibility.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies BEFORE copying code, so a code change does not
# invalidate the dependency layer. This one ordering choice is the
# difference between a 10-second and a 3-minute rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Never bake secrets into an image — they persist in the layer history
# even if a later layer deletes them. Inject at runtime.
ENV PYTHONUNBUFFERED=1

CMD ["pytest", "tests/", "-v", "--junitxml=/results/results.xml"]
```

```bash
docker build -t genai-eval:latest .

# Run with secrets injected and results written to the host.
docker run --rm \
  --env-file .env \
  -v "$PWD/results:/results" \
  genai-eval:latest
```

## 21.5 Compose — the whole test stack

```yaml
# docker-compose.test.yml — one command to stand up a full RAG test env.
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 5s
      retries: 10

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_PASSWORD: test
      POSTGRES_DB: ragtest
    ports: ["5432:5432"]
    volumes: ["pg_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_models:/root/.ollama"]

  app:
    build: .
    depends_on:
      qdrant:   {condition: service_healthy}
      postgres: {condition: service_healthy}
    environment:
      VECTOR_URL: http://qdrant:6333        # service name = hostname
      DATABASE_URL: postgresql://postgres:test@postgres:5432/ragtest
      LLM_BASE_URL: http://ollama:11434/v1
    ports: ["8000:8000"]

volumes:
  qdrant_data:
  pg_data:
  ollama_models:
```

```bash
docker compose -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml logs -f app
docker compose -f docker-compose.test.yml down -v    # -v also drops volumes
```

**`healthcheck` plus `depends_on: condition: service_healthy` is the detail worth learning.** Without it, your app container starts before the database is ready and your test run fails for reasons that have nothing to do with your code — the classic source of "flaky" CI.

---

# PART B — KUBERNETES 🟠 SHOULD LEARN (a narrow slice)

## 21.6 What a tester actually needs

You will not write manifests or design deployments. You will:
- Read logs from a pod in a test or staging cluster
- Check whether a service is healthy and why it is not
- Understand why a pod restarted
- Verify config and secrets are what you expect
- Understand scaling behaviour when you load-test
- Port-forward a service to test it locally

That is roughly 15 commands and 6 concepts.

## 21.7 The concepts

| Concept | Meaning |
|---|---|
| **Pod** | One or more containers running together; the smallest unit |
| **Deployment** | Manages a set of identical pods; handles rollout and restart |
| **Service** | A stable network address in front of changing pods |
| **ConfigMap** | Non-secret configuration injected as env vars or files |
| **Secret** | Same, for sensitive values (base64-encoded, **not encrypted by default**) |
| **Namespace** | A logical partition of the cluster (e.g. `staging`, `prod`) |
| **HPA** | Horizontal Pod Autoscaler — adds pods under load |
| **Liveness / readiness probe** | Health checks; readiness controls whether traffic is routed |

**The tester-relevant insight:** a **liveness probe that is too aggressive** will restart a pod mid-request. For LLM workloads with 30-second responses, a 10-second liveness timeout causes restarts under normal load — which looks like random 502s to your test suite. Checking probe timeouts against realistic response times is a genuine, findable defect.

## 21.8 The commands

```bash
# Where am I?
kubectl config get-contexts
kubectl config use-context staging
kubectl get ns

# What is running?
kubectl get pods -n staging
kubectl get pods -n staging -w             # watch live
kubectl get deploy,svc -n staging

# Why is it unhealthy? `describe` shows EVENTS — the actual reason.
kubectl describe pod my-app-7d9f-x2k4 -n staging

# Logs
kubectl logs my-app-7d9f-x2k4 -n staging
kubectl logs -f deploy/my-app -n staging          # follow the deployment
kubectl logs my-app-7d9f-x2k4 -n staging --previous   # the CRASHED instance
kubectl logs -l app=my-app -n staging --tail=200      # all pods by label

# Shell in
kubectl exec -it my-app-7d9f-x2k4 -n staging -- sh

# Test a service locally without exposing it publicly.
kubectl port-forward svc/my-app 8080:80 -n staging
# then: curl http://localhost:8080/health

# Config and secrets
kubectl get configmap my-config -n staging -o yaml
kubectl get secret my-secret -n staging -o jsonpath='{.data.API_KEY}' | base64 -d

# Resource usage during a load test
kubectl top pods -n staging
kubectl get hpa -n staging
```

**`--previous` is the one to remember.** When a pod crash-loops, the current instance's logs are empty; the useful logs belong to the instance that died.

## 21.9 What to check in a K8s environment

| Check | Command / method | Why |
|---|---|---|
| Pod restart count | `kubectl get pods` → RESTARTS column | Non-zero means something is failing |
| **OOMKilled** | `describe pod` → Last State | Memory limit too low; common with model servers |
| **Probe timeouts vs LLM latency** | Read the deployment spec | Aggressive probes restart pods mid-request |
| Resource limits | `describe pod` → Limits | Too low throttles; too high wastes |
| **HPA behaviour under load** | `kubectl get hpa -w` during a load test | Does it scale in time, or after the spike passes? |
| Secrets not in ConfigMaps | Inspect both | API keys in a ConfigMap is a finding |
| Image tag is pinned | `describe deploy` | `:latest` in production is non-reproducible |
| Env parity | Compare staging vs prod configs | The source of "works in staging" |

```
TC-K8S-001  Liveness probe vs LLM response time
Method:     Read the deployment's livenessProbe timeoutSeconds and
            periodSeconds. Compare with p99 request duration.
Expected:   Probe timeout comfortably exceeds worst-case request handling,
            or the probe hits a lightweight endpoint that does not block
            behind LLM work.
Failure:    Pods restart during long requests → intermittent 502s that
            look like random flakiness
Priority:   High
```

## 21.10 What you can skip ⚪

Helm chart authoring, operators and CRDs, service mesh internals, cluster networking (CNI), RBAC design, storage classes, cluster upgrades, node management. Learn these only if you move into platform work.

---

## 21.11 Self-check

1. Why does dependency installation come before `COPY . .` in a Dockerfile?
2. Why must secrets never be baked into an image?
3. What does `depends_on: condition: service_healthy` prevent?
4. Which `kubectl logs` flag do you need for a crash-looping pod?
5. How can a liveness probe cause intermittent failures in an LLM service?
6. Why is a Kubernetes Secret not the same as an encrypted secret?

---

**Next:** [PART-22-CLOUD-AI.md](PART-22-CLOUD-AI.md) — Azure, AWS, and Google from a tester's seat.
