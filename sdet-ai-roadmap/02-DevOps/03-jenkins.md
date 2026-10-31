# Jenkins — Setup, Pipelines, Commands

> Jenkins is still what most Indian enterprises and GCCs run. GitHub Actions is nicer, but Jenkins is what gets asked about in interviews here. Learn both — Actions for your own repos, Jenkins because the job requires it.

---

## 1. Run Jenkins in Docker (fastest path)

```bash
# create a network so Jenkins can talk to other containers
docker network create jenkins

# run Jenkins LTS
docker run -d \
  --name jenkins \
  --network jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts-jdk17

# get the initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# open http://localhost:8080
```

**Setup wizard:** paste the password → Install suggested plugins → create admin user → done.

### Plugins to install

Manage Jenkins → Plugins → Available:

- **NodeJS** — provides Node in the build environment
- **Docker Pipeline** — `docker { }` agent blocks
- **HTML Publisher** — publish the Playwright HTML report
- **JUnit** — parse test results, show trends
- **Pipeline: Stage View** — visualise stages
- **Blue Ocean** — nicer pipeline UI
- **Git / GitHub** — SCM integration
- **Credentials Binding** — inject secrets
- **Timestamper**, **AnsiColor** — readable logs

### Configure NodeJS

Manage Jenkins → Tools → NodeJS installations → Add:
- Name: `node20`
- Install automatically → NodeJS 20.x

---

## 2. Jenkins CLI

```bash
# download the CLI jar
curl -O http://localhost:8080/jnlpJars/jenkins-cli.jar

# authenticate with an API token (User → Configure → API Token)
export JENKINS_URL=http://localhost:8080
export JENKINS_USER=admin
export JENKINS_TOKEN=<your-token>

alias jcli="java -jar jenkins-cli.jar -s $JENKINS_URL -auth $JENKINS_USER:$JENKINS_TOKEN"

jcli help
jcli list-jobs
jcli build my-job
jcli build my-job -p BRANCH=main -p SUITE=smoke
jcli build my-job -s                       # wait for completion
jcli build my-job -s -v                    # and stream console output
jcli console my-job
jcli console my-job 42                     # specific build number
jcli get-job my-job > job.xml
jcli create-job new-job < job.xml
jcli update-job my-job < job.xml
jcli delete-job my-job
jcli disable-job my-job
jcli enable-job my-job
jcli stop-builds my-job
jcli who-am-i
jcli restart
jcli safe-restart                          # wait for running builds first
jcli reload-configuration
jcli groovy = < script.groovy
```

### REST API

```bash
# trigger a build
curl -X POST "$JENKINS_URL/job/my-job/build" --user "$JENKINS_USER:$JENKINS_TOKEN"

# with parameters
curl -X POST "$JENKINS_URL/job/my-job/buildWithParameters?BRANCH=main&SUITE=smoke" \
  --user "$JENKINS_USER:$JENKINS_TOKEN"

# job status
curl -s "$JENKINS_URL/job/my-job/lastBuild/api/json" --user "$JENKINS_USER:$JENKINS_TOKEN" | jq .result

# console output
curl -s "$JENKINS_URL/job/my-job/lastBuild/consoleText" --user "$JENKINS_USER:$JENKINS_TOKEN"

# with CSRF crumb (if enabled)
CRUMB=$(curl -s --user "$JENKINS_USER:$JENKINS_TOKEN" \
  "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)")
curl -X POST -H "$CRUMB" "$JENKINS_URL/job/my-job/build" --user "$JENKINS_USER:$JENKINS_TOKEN"
```

---

## 3. Declarative Jenkinsfile — Playwright suite

```groovy
pipeline {
    agent any

    tools {
        nodejs 'node20'
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Target env')
        choice(name: 'SUITE', choices: ['smoke', 'regression', 'all'], description: 'Which suite')
        string(name: 'BRANCH', defaultValue: 'main', description: 'Branch to test')
        booleanParam(name: 'HEADED', defaultValue: false, description: 'Run headed')
    }

    environment {
        CI = 'true'
        BASE_URL = "https://${params.ENVIRONMENT}.example.com"
        // secret text credential stored in Jenkins
        API_TOKEN = credentials('api-token')
        // username/password credential — creates USER_CREDS_USR and USER_CREDS_PSW
        USER_CREDS = credentials('test-user-creds')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
        retry(1)
    }

    triggers {
        cron('H 2 * * *')                    // nightly ~2am
        pollSCM('H/15 * * * *')              // poll every 15 min
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.BRANCH}",
                    url: 'https://github.com/user/repo.git',
                    credentialsId: 'github-creds'
                sh 'git log -1 --oneline'
            }
        }

        stage('Install') {
            steps {
                sh 'node --version && npm --version'
                sh 'npm ci'
                sh 'npx playwright install --with-deps'
            }
        }

        stage('Lint & Typecheck') {
            parallel {
                stage('Lint')      { steps { sh 'npm run lint' } }
                stage('Typecheck') { steps { sh 'npx tsc --noEmit' } }
            }
        }

        stage('Test') {
            steps {
                script {
                    def grepArg = params.SUITE == 'all' ? '' : "--grep @${params.SUITE}"
                    sh "npx playwright test ${grepArg} --reporter=list,html,junit"
                }
            }
        }

        stage('Sharded Test') {
            when { expression { params.SUITE == 'regression' } }
            parallel {
                stage('Shard 1') { steps { sh 'npx playwright test --shard=1/4' } }
                stage('Shard 2') { steps { sh 'npx playwright test --shard=2/4' } }
                stage('Shard 3') { steps { sh 'npx playwright test --shard=3/4' } }
                stage('Shard 4') { steps { sh 'npx playwright test --shard=4/4' } }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'results.xml'

            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'playwright-report',
                reportFiles: 'index.html',
                reportName: 'Playwright Report'
            ])

            archiveArtifacts artifacts: 'test-results/**/*.zip, test-results/**/*.png',
                             allowEmptyArchive: true

            cleanWs()
        }
        success {
            echo "✅ Build ${env.BUILD_NUMBER} passed"
        }
        failure {
            echo "❌ Build ${env.BUILD_NUMBER} failed"
            // emailext / slackSend go here
        }
        unstable {
            echo "⚠️ Tests failed but build completed"
        }
    }
}
```

---

## 4. Jenkinsfile with a Docker agent

```groovy
pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.50.0-noble'
            args '--ipc=host -u root'
            reuseNode true
        }
    }

    environment {
        BASE_URL = 'https://staging.example.com'
    }

    stages {
        stage('Install') { steps { sh 'npm ci' } }
        stage('Test')    { steps { sh 'npx playwright test --reporter=junit,html' } }
    }

    post {
        always {
            junit 'results.xml'
            publishHTML([reportDir: 'playwright-report', reportFiles: 'index.html',
                         reportName: 'Playwright Report', keepAll: true, allowMissing: true])
        }
    }
}
```

### Per-stage agents

```groovy
pipeline {
    agent none
    stages {
        stage('Build') {
            agent { docker { image 'node:20-alpine' } }
            steps { sh 'npm ci && npm run build' }
        }
        stage('Test') {
            agent { docker { image 'mcr.microsoft.com/playwright:v1.50.0-noble'; args '--ipc=host' } }
            steps { sh 'npx playwright test' }
        }
    }
}
```

---

## 5. Groovy essentials for Jenkinsfiles

```groovy
// variables
def name = 'test'
String s = 'typed'
int n = 5
def list = ['a', 'b', 'c']
def map = [env: 'dev', region: 'in']

// string interpolation — double quotes only
echo "Running on ${env.BRANCH_NAME} build ${env.BUILD_NUMBER}"
echo 'No ${interpolation} in single quotes'

// conditionals
script {
    if (env.BRANCH_NAME == 'main') {
        sh 'npm run deploy'
    } else if (env.BRANCH_NAME.startsWith('release/')) {
        sh 'npm run deploy:staging'
    } else {
        echo 'Feature branch — tests only'
    }
}

// loops
script {
    ['chromium', 'firefox', 'webkit'].each { browser ->
        sh "npx playwright test --project=${browser}"
    }
}

// dynamic parallel stages
script {
    def shards = [:]
    for (int i = 1; i <= 4; i++) {
        def n = i
        shards["shard-${n}"] = {
            sh "npx playwright test --shard=${n}/4"
        }
    }
    parallel shards
}

// capture shell output
script {
    def commit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    def status = sh(script: 'npm test', returnStatus: true)   // exit code, doesn't fail build
    echo "Commit ${commit}, tests exited ${status}"
}

// try/catch
script {
    try {
        sh 'npx playwright test'
    } catch (Exception e) {
        currentBuild.result = 'UNSTABLE'
        echo "Tests failed: ${e.message}"
    } finally {
        sh 'npm run cleanup'
    }
}

// read files
script {
    def pkg = readJSON file: 'package.json'
    echo "Version: ${pkg.version}"
    def props = readProperties file: 'test.properties'
    writeFile file: 'summary.txt', text: "Build ${env.BUILD_NUMBER}"
}

// when conditions
stage('Deploy') {
    when {
        allOf {
            branch 'main'
            environment name: 'DEPLOY', value: 'true'
            expression { currentBuild.result == null }
        }
    }
    steps { sh 'npm run deploy' }
}

stage('Nightly only') {
    when { triggeredBy 'TimerTrigger' }
    steps { sh 'npx playwright test --grep @nightly' }
}

// manual approval gate
stage('Approve') {
    steps {
        timeout(time: 15, unit: 'MINUTES') {
            input message: 'Deploy to production?', ok: 'Deploy',
                  submitter: 'admin,release-managers'
        }
    }
}

// credentials in a block
withCredentials([
    string(credentialsId: 'api-token', variable: 'TOKEN'),
    usernamePassword(credentialsId: 'db', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASS')
]) {
    sh 'npx playwright test'
}
```

### Useful environment variables

```groovy
env.BUILD_NUMBER
env.BUILD_ID
env.BUILD_URL
env.JOB_NAME
env.WORKSPACE
env.BRANCH_NAME          // multibranch pipelines
env.CHANGE_ID            // PR number
env.GIT_COMMIT
env.GIT_BRANCH
env.NODE_NAME
currentBuild.result
currentBuild.duration
currentBuild.currentResult
```

---

## 6. Scripted pipeline (older style — recognise it)

```groovy
node('linux') {
    try {
        stage('Checkout') {
            checkout scm
        }
        stage('Install') {
            sh 'npm ci'
        }
        stage('Test') {
            sh 'npx playwright test'
        }
        currentBuild.result = 'SUCCESS'
    } catch (e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        junit 'results.xml'
        cleanWs()
    }
}
```

**Declarative vs scripted:** declarative has a fixed structure, built-in `post` blocks, and validates before running — use it. Scripted is raw Groovy, more flexible, harder to maintain. You'll meet scripted in legacy pipelines.

---

## 7. Shared libraries

```
jenkins-shared-lib/
├── vars/
│   ├── runPlaywrightTests.groovy
│   └── notifySlack.groovy
└── src/
    └── com/company/TestUtils.groovy
```

```groovy
// vars/runPlaywrightTests.groovy
def call(Map config = [:]) {
    def suite   = config.suite ?: 'smoke'
    def browser = config.browser ?: 'chromium'
    def shards  = config.shards ?: 1

    sh 'npm ci'
    sh 'npx playwright install --with-deps'

    if (shards > 1) {
        def jobs = [:]
        for (int i = 1; i <= shards; i++) {
            def n = i
            jobs["shard-${n}"] = {
                sh "npx playwright test --project=${browser} --grep @${suite} --shard=${n}/${shards}"
            }
        }
        parallel jobs
    } else {
        sh "npx playwright test --project=${browser} --grep @${suite}"
    }
}
```

```groovy
// in a Jenkinsfile
@Library('my-shared-lib') _

pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                runPlaywrightTests(suite: 'regression', browser: 'chromium', shards: 4)
            }
        }
    }
}
```

---

## 8. GitHub Actions equivalent — for your own repos

```yaml
# .github/workflows/tests.yml
name: Playwright Tests

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      suite:
        type: choice
        options: [smoke, regression, all]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.50.0-noble
      options: --ipc=host
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      - run: npx playwright test --shard=${{ matrix.shard }}/4 --reporter=blob
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
          API_TOKEN: ${{ secrets.API_TOKEN }}

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 7

  merge-reports:
    if: always()
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with:
          name: html-report
          path: playwright-report
```

---

## 9. Interview questions

**Q. What is Jenkins and why use it?**
An open-source automation server for CI/CD. It's valued for its plugin ecosystem, self-hosting (important where data can't leave the network), and maturity. The trade-off against GitHub Actions or GitLab CI is that you maintain the infrastructure yourself.

**Q. Declarative vs scripted pipeline?**
Declarative has a defined structure with `pipeline`, `stages`, `post`, validates syntax before running, and is far more readable. Scripted is raw Groovy inside a `node` block — more flexible but harder to maintain. New pipelines should be declarative.

**Q. What is a Jenkinsfile and why keep it in the repo?**
The pipeline definition as code, versioned alongside the application. Pipeline changes get reviewed like code, history is visible, and branches can have different pipelines. The alternative — configuring jobs in the UI — is unreviewable and undocumented.

**Q. How do you handle secrets?**
Jenkins Credentials store, injected via `credentials()` in the environment block or `withCredentials`. They're masked in console output. Never in the Jenkinsfile, never in environment variables committed to the repo. For real production I'd prefer Vault or a cloud secret manager with Jenkins pulling at runtime.

**Q. How do you run stages in parallel?**
A `parallel` block with nested stages, or build the map dynamically in a `script` block for things like test shards. Watch out for shared workspace conflicts — parallel stages on the same agent share a directory.

**Q. What's in the `post` block?**
`always`, `success`, `failure`, `unstable`, `changed`, `aborted`. `always` is where test-result publishing, artifact archiving, and workspace cleanup go — those must run whether tests passed or not.

**Q. How do you publish Playwright results in Jenkins?**
JUnit reporter output via the `junit` step for trend graphs and per-test history, plus the HTML Publisher plugin for the Playwright HTML report, plus `archiveArtifacts` for traces and screenshots so failures can be debugged after the fact.

**Q. Build failed vs unstable — what's the difference?**
Failed means the pipeline itself broke — a compile error, a missing dependency. Unstable usually means the build completed but tests failed. Keeping them distinct lets you treat "the pipeline is broken" differently from "the product has a bug."

**Q. How do you trigger a Jenkins job from outside?**
The REST API with an API token, the CLI jar, a webhook from GitHub, or `build job:` from another pipeline. For GitHub, a webhook to `/github-webhook/` is better than polling — polling wastes resources and adds latency.

**Q. What is a Jenkins agent?**
A machine that executes builds; the controller schedules and coordinates. Agents let you scale out and run jobs on specific platforms via labels. Best practice is that the controller runs no builds at all.

**Q. How would you speed up a slow Jenkins pipeline?**
Parallelise independent stages, shard the test suite across agents, cache `node_modules` and Docker layers, use a pre-built image with browsers rather than installing them each run, skip stages with `when` conditions, and run only affected tests on PRs with the full suite nightly.

**Q. Jenkins vs GitHub Actions?**
Actions is managed, YAML-based, tightly integrated with GitHub, and has almost no maintenance cost — better for most new projects. Jenkins wins when you need self-hosting for compliance, have complex legacy pipelines, need plugins with no Actions equivalent, or aren't on GitHub. Many enterprises run both.

---

## Practice checklist

- [ ] Jenkins running in Docker with plugins installed
- [ ] A pipeline job pointed at a GitHub repo, building from a Jenkinsfile
- [ ] Parameterised build with environment and suite choices
- [ ] Playwright HTML report published and viewable from the build page
- [ ] JUnit results showing test trends across builds
- [ ] Parallel sharded test execution
- [ ] Secrets injected via the Credentials store, masked in logs
- [ ] A nightly cron trigger that actually fired
- [ ] The same pipeline rebuilt as a GitHub Actions workflow with sharding and merged reports

---

**Next:** `04-kubernetes-highlevel.md`
