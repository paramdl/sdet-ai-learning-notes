# Kubernetes — High Level for SDETs

> **Scope check:** you are not becoming a Kubernetes engineer. You need enough to (a) answer interview questions without freezing, (b) deploy a test app or grid, and (c) debug why the app under test is broken in a cluster.
>
> **Budget: ~8 hours total.** Do not exceed it. Depth here has poor return for your goal.

---

## 1. Why it exists

Docker runs one container on one machine. Kubernetes runs thousands across many machines and handles:

- **Scheduling** — deciding which machine runs what
- **Self-healing** — restarting crashed containers, replacing dead nodes
- **Scaling** — more replicas when load rises
- **Service discovery** — stable names and IPs for things that keep moving
- **Rolling updates** — deploy new versions without downtime, roll back on failure

**One-line interview answer:** "Docker packages an application; Kubernetes orchestrates many containers across a cluster — scheduling, healing, scaling, networking, and rollouts."

---

## 2. Core objects — the ones that matter

| Object | What it is |
|---|---|
| **Pod** | Smallest deployable unit. One or more containers sharing network and storage. Usually one container. Ephemeral — they die and get replaced. |
| **ReplicaSet** | Keeps N identical pods running. You rarely create one directly. |
| **Deployment** | Manages ReplicaSets. Handles rolling updates and rollbacks. **This is what you actually write.** |
| **Service** | Stable network endpoint in front of a changing set of pods. Load balances. |
| **Ingress** | HTTP routing from outside the cluster to services. Host and path based. |
| **ConfigMap** | Non-secret configuration as key-value pairs. |
| **Secret** | Same, but for sensitive values (base64-encoded, not encrypted by default). |
| **Namespace** | Virtual cluster for isolating environments or teams. |
| **Job** | Runs a pod to completion. **This is how you run a test suite.** |
| **CronJob** | A Job on a schedule. Nightly regression runs. |
| **PersistentVolumeClaim** | A request for durable storage. |
| **StatefulSet** | Like Deployment, but for stateful things with stable identity — databases. |
| **DaemonSet** | One pod on every node — log collectors, monitoring agents. |

### Service types

| Type | Reach |
|---|---|
| `ClusterIP` | Inside the cluster only (default) |
| `NodePort` | Exposed on a port of every node |
| `LoadBalancer` | Cloud provider load balancer with an external IP |
| `ExternalName` | DNS alias to an external host |

---

## 3. Architecture in four lines

**Control plane:** `api-server` (the front door for every command), `etcd` (the cluster's database), `scheduler` (assigns pods to nodes), `controller-manager` (makes reality match desired state).

**Worker nodes:** `kubelet` (runs the pods), `kube-proxy` (networking rules), a container runtime (containerd).

**The key idea — declarative reconciliation:** you declare desired state in YAML; controllers continuously work to make the cluster match it. You don't say "start a container," you say "three of these should exist," and Kubernetes keeps it true.

---

## 4. Local cluster setup

```bash
# Option 1: Docker Desktop — Settings → Kubernetes → Enable. Easiest on Windows.

# Option 2: kind (Kubernetes in Docker)
choco install kind                  # or: scoop install kind
kind create cluster --name test-cluster
kind delete cluster --name test-cluster
kind load docker-image my-tests:latest --name test-cluster   # load a local image

# Option 3: minikube
choco install minikube
minikube start
minikube stop
minikube delete
minikube dashboard
minikube service my-service --url

# verify
kubectl cluster-info
kubectl get nodes
```

---

## 5. kubectl — the commands you need

```bash
# context
kubectl config get-contexts
kubectl config current-context
kubectl config use-context kind-test-cluster
kubectl config set-context --current --namespace=testing

# get
kubectl get pods
kubectl get pods -A                        # all namespaces
kubectl get pods -n testing
kubectl get pods -o wide                   # with node and IP
kubectl get pods -w                        # watch
kubectl get pods -l app=my-app             # by label
kubectl get deployments,services,pods
kubectl get all
kubectl get pod my-pod -o yaml
kubectl get pods --sort-by=.status.startTime

# describe — your first debugging step
kubectl describe pod my-pod
kubectl describe deployment my-app
kubectl describe service my-service
kubectl describe node my-node

# logs
kubectl logs my-pod
kubectl logs -f my-pod                     # follow
kubectl logs my-pod -c my-container        # multi-container pod
kubectl logs my-pod --previous             # logs from the crashed instance
kubectl logs -l app=my-app --tail=100      # across pods by label
kubectl logs --since=10m my-pod

# exec and port-forward
kubectl exec -it my-pod -- sh
kubectl exec -it my-pod -- bash
kubectl exec my-pod -- ls /app
kubectl port-forward pod/my-pod 8080:80
kubectl port-forward service/my-service 8080:80
kubectl port-forward deployment/my-app 3000:3000

# apply and delete
kubectl apply -f deployment.yaml
kubectl apply -f k8s/                      # whole directory
kubectl apply -k overlays/staging          # kustomize
kubectl delete -f deployment.yaml
kubectl delete pod my-pod
kubectl delete pods --all -n testing
kubectl delete namespace testing

# scale and rollout
kubectl scale deployment my-app --replicas=5
kubectl autoscale deployment my-app --min=2 --max=10 --cpu-percent=70
kubectl rollout status deployment/my-app
kubectl rollout history deployment/my-app
kubectl rollout undo deployment/my-app
kubectl rollout undo deployment/my-app --to-revision=2
kubectl rollout restart deployment/my-app
kubectl set image deployment/my-app my-app=my-image:v2

# quick imperative creation
kubectl create namespace testing
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=NodePort
kubectl run debug --image=busybox -it --rm -- sh      # throwaway debug pod
kubectl create job manual-run --from=cronjob/nightly-tests

# configmaps and secrets
kubectl create configmap app-config --from-literal=BASE_URL=https://staging.example.com
kubectl create configmap app-config --from-file=config.json
kubectl create secret generic api-creds --from-literal=token=abc123
kubectl get secret api-creds -o jsonpath='{.data.token}' | base64 -d

# troubleshooting
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl top nodes
kubectl top pods
kubectl api-resources
kubectl explain deployment.spec.template.spec.containers
kubectl cp my-pod:/app/report.html ./report.html
```

---

## 6. YAML you should be able to read

### Deployment + Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: testing
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:                       # the pod template
    metadata:
      labels:
        app: my-app               # must match the selector above
    spec:
      containers:
        - name: my-app
          image: my-registry/my-app:v1.2.0
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: "production"
            - name: BASE_URL
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: BASE_URL
            - name: API_TOKEN
              valueFrom:
                secretKeyRef:
                  name: api-creds
                  key: token
          resources:
            requests:             # guaranteed
              memory: "256Mi"
              cpu: "250m"
            limits:               # ceiling — exceeded memory = OOMKilled
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:          # restart if this fails
            httpGet: { path: /health, port: 3000 }
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:         # remove from service if this fails
            httpGet: { path: /ready, port: 3000 }
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  namespace: testing
spec:
  type: ClusterIP
  selector:
    app: my-app                   # routes to pods with this label
  ports:
    - port: 80                    # the service port
      targetPort: 3000            # the container port
```

### Job — running your test suite

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: playwright-tests
  namespace: testing
spec:
  backoffLimit: 1                 # retries on failure
  ttlSecondsAfterFinished: 3600   # auto-cleanup
  completions: 4                  # run 4 pods to completion
  parallelism: 4                  # all at once — one per shard
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: playwright
          image: my-registry/playwright-tests:latest
          command: ["npx", "playwright", "test"]
          args: ["--shard=$(JOB_COMPLETION_INDEX)/4"]
          env:
            - name: BASE_URL
              value: "http://my-app-service.testing.svc.cluster.local"
            - name: CI
              value: "true"
          resources:
            requests: { memory: "1Gi", cpu: "1" }
            limits:   { memory: "2Gi", cpu: "2" }
          volumeMounts:
            - name: reports
              mountPath: /app/playwright-report
      volumes:
        - name: reports
          persistentVolumeClaim:
            claimName: test-reports-pvc
```

```bash
kubectl apply -f test-job.yaml
kubectl get jobs -n testing
kubectl logs -f job/playwright-tests -n testing
kubectl delete job playwright-tests -n testing
```

### CronJob — nightly regression

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-regression
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: tests
              image: my-registry/playwright-tests:latest
              command: ["npx", "playwright", "test", "--grep", "@regression"]
```

---

## 7. DNS inside the cluster

A service is reachable at:

```
<service-name>.<namespace>.svc.cluster.local
```

From the same namespace, just `<service-name>` works. So your test pod reaches the app as `http://my-app-service` or `http://my-app-service.testing.svc.cluster.local`.

**This is the single most useful thing to know as a tester** — it's how you point `BASE_URL` at the app under test.

---

## 8. Debugging checklist

```bash
kubectl get pods                             # what state?
kubectl describe pod <name>                  # events at the bottom tell you why
kubectl logs <name>
kubectl logs <name> --previous               # if it's crash-looping
kubectl get events --sort-by=.metadata.creationTimestamp
```

| Pod status | Usual cause |
|---|---|
| `Pending` | No node has enough resources, or a PVC isn't bound |
| `ImagePullBackOff` | Wrong image name/tag, or missing registry credentials |
| `CrashLoopBackOff` | Container starts then exits — check `logs --previous` |
| `OOMKilled` | Exceeded the memory limit |
| `Error` | Non-zero exit code |
| `Running` but not ready | Readiness probe failing |

---

## 9. Helm — just the concept plus five commands

Helm is the package manager. A "chart" is a templated bundle of Kubernetes YAML with a `values.yaml` for per-environment config.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo postgres
helm install my-db bitnami/postgresql
helm install my-db bitnami/postgresql -f custom-values.yaml
helm list
helm upgrade my-db bitnami/postgresql --set auth.password=newpass
helm rollback my-db 1
helm uninstall my-db
helm template my-app ./chart          # render without installing — good for review
```

**Why you'd care:** spinning up a test database or Selenium Grid is one `helm install` instead of hand-written YAML.

---

## 10. Interview questions

**Q. What is Kubernetes and why use it over plain Docker?**
Docker runs containers on one host. Kubernetes orchestrates them across a cluster — scheduling, self-healing, scaling, service discovery, and zero-downtime rollouts. You need it once you have more containers and machines than a person can manage by hand.

**Q. What is a pod?**
The smallest deployable unit — one or more containers sharing a network namespace and storage. Usually one container; a second appears as a sidecar for logging or a proxy. Pods are ephemeral and replaceable, which is why you never address them directly.

**Q. Deployment vs ReplicaSet vs Pod?**
A Deployment manages ReplicaSets, which manage Pods. You write Deployments; the layers below are managed for you. The Deployment is what gives you rolling updates and rollback.

**Q. What does a Service do?**
Provides a stable name and IP in front of a changing set of pods, and load-balances across them. Pods come and go with new IPs; the Service doesn't. It selects pods by label.

**Q. ConfigMap vs Secret?**
Both inject configuration. Secrets are intended for sensitive data and are base64-encoded — which is encoding, not encryption. Without encryption-at-rest enabled on etcd and proper RBAC, a Secret isn't genuinely secret. That nuance is worth stating.

**Q. Liveness vs readiness probe?**
Liveness failing restarts the container. Readiness failing removes it from the Service's endpoints without restarting. Readiness is what prevents traffic hitting a pod that's still warming up — and a common cause of flaky tests against a freshly deployed environment.

**Q. How would you run a test suite in Kubernetes?**
As a Job — it runs pods to completion and reports success or failure, unlike a Deployment which restarts forever. With `parallelism` and `completions` I can shard across pods. For nightly runs, a CronJob. Reports go to a PersistentVolume or get pushed to object storage.

**Q. How do containers find each other?**
Cluster DNS. A Service is resolvable at `service.namespace.svc.cluster.local`, and just `service` within the same namespace. My test pod points `BASE_URL` at the app's service name.

**Q. What is a namespace for?**
Logical isolation inside one cluster — separate dev, staging, and test environments, scope RBAC, and apply resource quotas. Names only need to be unique within a namespace.

**Q. What happens when a pod crashes?**
The kubelet restarts it per the restart policy. If it keeps crashing, backoff increases and the status becomes `CrashLoopBackOff`. If the whole node dies, the controller schedules replacements elsewhere. This self-healing is the core value proposition.

**Q. What's the difference between requests and limits?**
Requests are what the scheduler guarantees and uses to place the pod. Limits are the hard ceiling — exceeding memory gets the container OOMKilled, exceeding CPU gets it throttled. Setting these wrong is a frequent cause of tests that pass locally and die in a cluster.

**Q. How do you debug a failing pod?**
`kubectl describe pod` first — the events section usually names the cause. Then `logs`, and `logs --previous` if it's crash-looping. `kubectl get events` for cluster-level context. If it's running but wrong, `exec` in and look around.

---

## 11. Practice checklist — 8 hours, no more

- [ ] Local cluster running via kind or Docker Desktop
- [ ] Deployed nginx with `kubectl create deployment`, scaled it to 3, watched pods appear
- [ ] Written a Deployment + Service YAML by hand and applied it
- [ ] Used `port-forward` to reach the app from your browser
- [ ] Built your Playwright image, loaded it into kind, ran it as a **Job**
- [ ] Read the Job's logs and retrieved the report
- [ ] Deliberately broken a pod (wrong image tag) and diagnosed it with `describe`
- [ ] Created a ConfigMap and a Secret and consumed both as env vars
- [ ] Installed something with Helm

**Stop here.** Networking internals, operators, service meshes, and CRDs are not your job.

---

**Next:** `../03-LLM/01-python-for-llm.md`
