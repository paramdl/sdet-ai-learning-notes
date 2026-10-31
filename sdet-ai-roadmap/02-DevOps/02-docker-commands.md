# Docker — Complete Command Reference for SDETs

> Why an SDET needs Docker: consistent browser versions between local and CI, disposable test databases, running the app under test, and reproducible visual-regression baselines. "Works on my machine" dies here.

---

## 1. Core concepts in one table

| Term | Meaning |
|---|---|
| **Image** | Read-only template. A recipe. |
| **Container** | A running instance of an image. |
| **Dockerfile** | Instructions to build an image. |
| **Registry** | Where images are stored (Docker Hub, ECR, GHCR). |
| **Volume** | Persistent storage that survives container deletion. |
| **Network** | How containers talk to each other. |
| **Compose** | Defining and running multi-container setups. |

---

## 2. Images

```bash
docker pull mcr.microsoft.com/playwright:v1.50.0-noble
docker pull node:20-alpine
docker pull postgres:16

docker images
docker image ls
docker image ls -a
docker image inspect node:20-alpine
docker history node:20-alpine        # layer by layer

docker rmi node:20-alpine
docker image prune                   # remove dangling images
docker image prune -a                # remove all unused images

docker build -t my-tests .
docker build -t my-tests:v1 -f Dockerfile.ci .
docker build --no-cache -t my-tests .
docker build --build-arg NODE_VERSION=20 -t my-tests .
docker build --target=builder -t my-tests .       # stop at a stage

docker tag my-tests:latest myuser/my-tests:v1
docker push myuser/my-tests:v1
docker login
docker logout

docker save -o my-tests.tar my-tests:latest
docker load -i my-tests.tar
```

---

## 3. Containers

```bash
docker run node:20-alpine node -e "console.log('hi')"

docker run -it node:20-alpine sh          # interactive shell
docker run -d nginx                       # detached (background)
docker run --rm node:20-alpine node -v    # auto-remove when it exits
docker run --name my-app nginx
docker run -p 8080:80 nginx               # host:container port
docker run -e NODE_ENV=production node:20-alpine
docker run --env-file .env node:20-alpine
docker run -v "$(pwd)":/app node:20-alpine       # bind mount
docker run -v mydata:/data node:20-alpine        # named volume
docker run -w /app node:20-alpine                # working directory
docker run --network my-net node:20-alpine
docker run --memory=2g --cpus=2 node:20-alpine
docker run --ipc=host mcr.microsoft.com/playwright:v1.50.0-noble  # needed for Chromium

# listing
docker ps                            # running
docker ps -a                         # all including stopped
docker ps -q                         # ids only
docker ps --filter "status=exited"

# lifecycle
docker start my-app
docker stop my-app
docker restart my-app
docker pause my-app
docker unpause my-app
docker kill my-app
docker rm my-app
docker rm -f my-app                  # force remove running
docker rm $(docker ps -aq)           # remove all containers

# inspecting
docker logs my-app
docker logs -f my-app                # follow
docker logs --tail 100 my-app
docker logs --since 10m my-app
docker inspect my-app
docker stats
docker top my-app
docker port my-app
docker diff my-app

# executing in a running container
docker exec -it my-app sh
docker exec -it my-app bash
docker exec my-app ls /app
docker exec -u root -it my-app sh

# copying files
docker cp my-app:/app/results.json ./results.json
docker cp ./config.json my-app:/app/
```

---

## 4. Dockerfile for a Playwright suite

```dockerfile
# Use the official Playwright image — browsers and OS deps pre-installed.
# ALWAYS pin the version to match your @playwright/test version exactly.
FROM mcr.microsoft.com/playwright:v1.50.0-noble

WORKDIR /app

# Copy manifests first — this layer caches unless deps change
COPY package*.json ./
RUN npm ci

# Then copy source (changes often, so it goes last)
COPY . .

ENV CI=true

CMD ["npx", "playwright", "test"]
```

```bash
docker build -t playwright-tests .
docker run --rm playwright-tests
docker run --rm -v "$(pwd)/playwright-report":/app/playwright-report playwright-tests
docker run --rm -e BASE_URL=https://staging.example.com playwright-tests
docker run --rm playwright-tests npx playwright test --project=chromium --grep @smoke
```

### Multi-stage build — smaller final image

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM mcr.microsoft.com/playwright:v1.50.0-noble AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY playwright.config.ts ./
CMD ["npx", "playwright", "test"]
```

### `.dockerignore` — do not skip this

```
node_modules
npm-debug.log
.git
.gitignore
test-results
playwright-report
blob-report
.env
.env.*
auth/*.json
dist
*.md
.vscode
```

> Without `.dockerignore`, `COPY . .` sends your entire `node_modules` and `.git` to the daemon. Builds go from seconds to minutes.

---

## 5. Dockerfile instructions reference

```dockerfile
FROM node:20-alpine AS base       # base image, optionally named stage
WORKDIR /app                      # cd, creates if missing
COPY src/ ./src/                  # copy from build context
ADD file.tar.gz /app/             # like COPY but auto-extracts archives and takes URLs
RUN npm ci                        # execute at BUILD time, creates a layer
CMD ["npm", "test"]               # default command at RUN time, overridable
ENTRYPOINT ["npx", "playwright"]  # fixed command; CMD becomes its arguments
ENV NODE_ENV=production           # env var available at build and run
ARG NODE_VERSION=20               # build-time only variable
EXPOSE 3000                       # documentation only — does not publish
VOLUME /data                      # declare a mount point
USER node                         # drop from root
HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000/health || exit 1
LABEL maintainer="alex"
```

### `CMD` vs `ENTRYPOINT` — an interview favourite

```dockerfile
CMD ["npm", "test"]
# docker run my-image               → npm test
# docker run my-image npm run lint  → npm run lint   (CMD replaced)

ENTRYPOINT ["npx", "playwright", "test"]
# docker run my-image               → npx playwright test
# docker run my-image --grep @smoke → npx playwright test --grep @smoke  (appended)
```

**Answer:** "`CMD` sets a default that's fully replaced by run arguments. `ENTRYPOINT` fixes the executable and treats run arguments as its parameters. For a test image I use `ENTRYPOINT` with the runner and `CMD` with default flags, so callers can pass `--grep` without repeating the whole command."

### Layer caching — why order matters

```dockerfile
# ❌ Any source change busts the npm ci cache — slow rebuilds every time
COPY . .
RUN npm ci

# ✅ Source changes only bust the last layer
COPY package*.json ./
RUN npm ci
COPY . .
```

---

## 6. Volumes and networks

```bash
# volumes
docker volume create test-data
docker volume ls
docker volume inspect test-data
docker volume rm test-data
docker volume prune

docker run -v test-data:/data alpine              # named volume
docker run -v "$(pwd)/reports":/app/reports alpine   # bind mount
docker run -v "$(pwd)":/app:ro alpine             # read-only
docker run --tmpfs /tmp alpine                    # in-memory

# networks
docker network create my-net
docker network create --driver bridge my-net
docker network ls
docker network inspect my-net
docker network connect my-net my-container
docker network disconnect my-net my-container
docker network rm my-net
docker network prune
```

> Containers on the same user-defined network resolve each other **by container name**. That's how your test container reaches `http://app:3000` without knowing an IP.

---

## 7. Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://test:test@db:5432/testdb
      NODE_ENV: test
    depends_on:
      db:
        condition: service_healthy
    networks:
      - test-net

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./seed.sql:/docker-entrypoint-initdb.d/seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks:
      - test-net

  tests:
    build:
      context: .
      dockerfile: Dockerfile.playwright
    ipc: host                          # Chromium needs this
    environment:
      BASE_URL: http://app:3000        # service name, not localhost
      CI: "true"
    volumes:
      - ./playwright-report:/app/playwright-report
      - ./test-results:/app/test-results
    depends_on:
      - app
    networks:
      - test-net

volumes:
  pgdata:

networks:
  test-net:
    driver: bridge
```

```bash
docker compose up
docker compose up -d                 # detached
docker compose up --build            # rebuild first
docker compose up app db             # specific services

docker compose down
docker compose down -v               # also remove volumes
docker compose down --rmi all

docker compose ps
docker compose logs
docker compose logs -f tests
docker compose logs --tail=50 app

docker compose exec app sh
docker compose run --rm tests npx playwright test --grep @smoke
docker compose restart app
docker compose build --no-cache
docker compose config                # validate and print resolved config

# the CI one-liner: run tests, exit with the test suite's exit code
docker compose up --build --abort-on-container-exit --exit-code-from tests
```

---

## 8. Cleanup — you will need these

```bash
docker system df                     # what's using disk
docker system prune                  # stopped containers, unused networks, dangling images
docker system prune -a               # + all unused images
docker system prune -a --volumes     # + volumes. destructive.

docker container prune
docker image prune -a
docker volume prune
docker network prune

docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
```

---

## 9. Practical SDET recipes

**Disposable test database**
```bash
docker run -d --name testdb \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:16-alpine

# run tests, then
docker rm -f testdb
```

**Consistent visual-regression baselines**
```bash
# generate baselines in the SAME image CI uses — otherwise font rendering differs
docker run --rm -v "$(pwd)":/app -w /app \
  mcr.microsoft.com/playwright:v1.50.0-noble \
  npx playwright test --update-snapshots
```

**Sharded run across containers**
```bash
docker run --rm -e SHARD=1 playwright-tests npx playwright test --shard=1/4 &
docker run --rm -e SHARD=2 playwright-tests npx playwright test --shard=2/4 &
docker run --rm -e SHARD=3 playwright-tests npx playwright test --shard=3/4 &
docker run --rm -e SHARD=4 playwright-tests npx playwright test --shard=4/4 &
wait
```

**Mock API server (WireMock)**
```bash
docker run -d --name mock -p 8080:8080 \
  -v "$(pwd)/mappings":/home/wiremock/mappings \
  wiremock/wiremock:latest
```

**Selenium Grid, if you ever need it**
```bash
docker run -d -p 4444:4444 -p 7900:7900 --shm-size=2g selenium/standalone-chrome:latest
# noVNC to watch the browser: http://localhost:7900  (password: secret)
```

---

## 10. Interview questions

**Q. Image vs container?**
An image is an immutable template; a container is a running instance of it. Many containers from one image. Analogy: class and object.

**Q. `CMD` vs `ENTRYPOINT`?**
`CMD` is a default command, fully replaced by arguments to `docker run`. `ENTRYPOINT` fixes the executable and appends run arguments to it. Combine them so the image has a fixed runner plus overridable flags.

**Q. `COPY` vs `ADD`?**
`COPY` copies local files. `ADD` also auto-extracts tar archives and can fetch URLs. Prefer `COPY` — `ADD`'s extra behaviour is implicit and surprising.

**Q. What is layer caching and how do you exploit it?**
Each instruction creates a cached layer. A change invalidates that layer and everything after it. So copy `package.json` and run `npm ci` *before* copying source — dependency installs then stay cached across source changes.

**Q. Bind mount vs volume?**
A bind mount maps a host path into the container — good for source code and pulling out reports. A named volume is Docker-managed storage — better for databases, portable, and not dependent on host paths.

**Q. How do containers communicate?**
On a user-defined network they resolve each other by service or container name via Docker's embedded DNS. That's why a test container uses `http://app:3000` rather than `localhost` — `localhost` inside a container is that container.

**Q. Why is `.dockerignore` important?**
Without it the whole build context — `node_modules`, `.git`, reports — is sent to the daemon, making builds slow and images fat. It also prevents secrets like `.env` being baked into an image.

**Q. How do you keep image size down?**
Alpine or slim base images, multi-stage builds so build tools don't ship, `npm ci --omit=dev` for production, combining `RUN` commands to reduce layers, and a strict `.dockerignore`.

**Q. Why does Playwright need `--ipc=host`?**
Chromium uses shared memory heavily. Docker's default `/dev/shm` is 64 MB, which causes crashes on complex pages. `--ipc=host` (or `--shm-size=2g`) fixes it. This is one of the most common "works locally, crashes in Docker" causes.

**Q. How do you run tests in Docker in CI?**
Build an image pinned to the Playwright version, run it against the app via Compose on a shared network, mount a volume for reports, and use `--exit-code-from tests` so the pipeline inherits the suite's exit code. Artifacts — HTML report and traces — get published from the mounted folder.

**Q. How do you debug a failing container?**
`docker logs` first. Then `docker exec -it <name> sh` to look around inside a running one. If it exits immediately, override the entrypoint: `docker run -it --entrypoint sh my-image`. `docker inspect` shows the resolved config, mounts, and env.

**Q. Container vs virtual machine?**
A VM virtualises hardware and runs a full guest OS — heavy, slow to start, strongly isolated. A container shares the host kernel and isolates at the process level — megabytes, starts in milliseconds, weaker isolation boundary.

---

## Practice checklist

- [ ] Written a Dockerfile for your Playwright suite and run it
- [ ] Correctly ordered layers so `npm ci` stays cached
- [ ] Written a `.dockerignore` and measured the build-time difference
- [ ] Mounted a volume to get `playwright-report` out of the container
- [ ] Written a `docker-compose.yml` with app + db + tests on one network
- [ ] Used `--exit-code-from` so a test failure fails the compose run
- [ ] Generated visual baselines inside the container and confirmed they match CI
- [ ] Debugged a container with `exec` and an overridden entrypoint
- [ ] Hit and fixed the `/dev/shm` Chromium crash

---

**Next:** `03-jenkins.md`
