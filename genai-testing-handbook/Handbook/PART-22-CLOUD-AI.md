# PART 22 — Cloud AI Platforms

> **Goal of this part:** know what to test on each major cloud AI platform. You are learning this as a **tester**, not a cloud architect — you need to know what the platform does, where its failure modes are, and which of its behaviours will surprise your test suite.

⏳ Cloud AI product names and features change faster than almost anything else in this book. Treat the *categories* as stable and verify every product name against the vendor's current documentation.

---

## 22.1 What is the same everywhere

Whatever the cloud, the platform gives you the same six things, and each has the same test surface:

| Capability | What to test |
|---|---|
| **Model endpoints** | Contract, streaming, errors, quotas (Part 5) |
| **Managed RAG / search** | Retrieval quality, chunking config, ACL trimming (Part 7) |
| **Content filters** | Both directions: unsafe blocked, safe not blocked (Part 13) |
| **Quotas and throttling** | Per-deployment limits, and behaviour at the limit |
| **Regional deployment** | Data residency, and **model availability differs by region** |
| **Identity and access** | Who can call the model, with what permissions |

**The single most important cloud-specific behaviour to internalise:** managed platforms apply their own content filters *in addition to* your application's guardrails, and they behave differently by region, deployment, and configuration. A refusal you see in testing may come from the platform, not the model or your prompt. Distinguishing the three is a debugging skill worth practising.

---

## 22.2 Microsoft Azure

| Service | Purpose | Tester's notes |
|---|---|---|
| **Azure OpenAI / Azure AI Foundry** | Hosted model endpoints | ⏳ Branding has consolidated under AI Foundry; the deployment model is the key concept |
| **Azure AI Content Safety** | Content filters | Configurable severity per category — **test at the configured level, not the default** |
| **Azure AI Search** | Managed retrieval, vector + keyword + hybrid | Where enterprise RAG usually lives on Azure |
| Azure AI Document Intelligence | Document/OCR extraction | Table extraction quality is a real test surface (Part 7 §7.3) |
| Azure Key Vault | Secrets | Where API keys should live |
| Azure Monitor / App Insights | Observability | Where traces land |

### The Azure-specific concepts that affect your tests

**① Deployments, not models.** You do not call a model; you call a *deployment* — a named instance of a model with its own quota and content-filter configuration. Consequences:
- The deployment name is what appears in your config, and **two deployments of the same model can behave differently** (different filter settings, different versions).
- Quota is per deployment, per region. A load test exhausts one deployment's quota, not the account's.

```
TC-AZ-001  Deployment configuration parity
Method:     Compare the content-filter configuration, model version, and
            quota of the test deployment against production
Expected:   Identical, or differences documented
Failure:    Testing against a permissive test deployment while production
            runs strict filters — every guardrail result is invalid
Priority:   High
```

**② Content filter behaviour.** Azure returns a distinct error/finish reason when its filter blocks content, on input or output. Your tests must distinguish:
- Model refused (alignment)
- Platform filter blocked (Azure)
- Your guardrail blocked (your code)

Three different causes, three different fixes. Assert on the *reason*, not just on "no answer".

**③ Regional model availability.** A model available in one region may not be in another. A test suite pinned to a region that production does not use is testing a different system.

### AI Search test surface
| Test | Note |
|---|---|
| Hybrid search configuration | Vector + keyword weighting is tunable and affects Part 7 metrics |
| Semantic ranker on/off | Compare retrieval metrics with and without |
| **Security trimming** | Document-level ACL filtering — the tenant/permission tests from Part 7 §7.9 |
| Indexer schedule | Freshness SLA: how long from document change to retrievable |
| Skillset failures | Enrichment pipeline errors can silently drop documents |

---

## 22.3 Amazon Web Services

| Service | Purpose | Tester's notes |
|---|---|---|
| **Amazon Bedrock** | Multi-vendor hosted models under one API | Model access must be explicitly enabled per model per region |
| **Bedrock Guardrails** | Managed guardrails | Configurable topic/content/PII policies — test the four corpora against them |
| **Bedrock Knowledge Bases** | Managed RAG | Chunking and embedding config are exposed and testable |
| **Bedrock Agents** | Managed agent orchestration | Action groups = tools; apply Part 9 |
| **OpenSearch Service** | Vector + keyword search | Common vector store on AWS |
| SageMaker | Custom model training and hosting | You need only the *endpoint* view |
| CloudWatch | Logs and metrics | Where traces land |
| Secrets Manager | Secrets | |

### AWS-specific concepts

**① Model access is opt-in.** Each model must be enabled in each region. A test failing with an access error is often a permissions issue, not a code bug — check this first.

**② IAM is the access boundary**, and it is fine-grained. Your tests should include a negative case: a role without `bedrock:InvokeModel` gets a clean denial, and the application handles it gracefully rather than 500-ing.

**③ Bedrock Guardrails are a separate, testable component.** They can be applied independently of the model, which means you can and should test them in isolation with the four-corpus method (Part 13 §13.7) before testing the integrated system.

**④ Cross-region inference** can route requests to other regions for capacity. **This is a data-residency question** — verify whether it is enabled and whether that is acceptable for your data classification. It is an easy compliance finding.

```
TC-AWS-001  Cross-region inference and data residency
Method:     Determine whether cross-region inference is enabled for the
            deployment, and which regions are in scope
Expected:   Consistent with the data-residency commitments in the
            product's privacy policy and any customer contracts
Priority:   High (Critical for regulated data)
```

---

## 22.4 Google Cloud

| Service | Purpose | Tester's notes |
|---|---|---|
| **Vertex AI** | The umbrella platform for models and MLOps | |
| **Gemini models via Vertex** | Hosted model endpoints | Distinct from the consumer/AI Studio surface — different auth, quotas, and terms |
| **Vertex AI Search** | Managed retrieval / enterprise search | Managed RAG |
| Vertex AI Safety filters | Configurable harm-category thresholds | Test at the configured thresholds |
| Vertex AI Model Garden | Third-party and open models | Model provenance questions apply |
| Cloud Logging / Trace | Observability | |
| Secret Manager | Secrets | |

### Google-specific concepts

**① Two distinct surfaces.** The developer-facing API and the Vertex enterprise surface differ in authentication, quota, region control, and data-handling terms. **Testing against one and shipping on the other is a real and common mistake** — the quotas and safety defaults are not the same.

**② Safety settings are explicit thresholds per harm category.** They are set per request or per deployment. Assert that the configured thresholds in test match production, exactly as in `TC-AZ-001`.

**③ Grounding features.** Vertex offers grounding against Google Search or your own data, with returned grounding metadata. That metadata is directly testable — it is a citation source, so apply the citation-validation tests from Part 7 §7.8.

---

## 22.5 The cloud-agnostic test checklist

Regardless of platform:

```
□ Model/deployment identity asserted in responses (catches substitution)
□ Test and production deployment configs compared and documented
□ Regional availability confirmed for every model used
□ Quota limits known; behaviour at the limit tested
□ Platform content filters tested separately from app guardrails
□ Filter/refusal reasons distinguishable in logs (platform vs model vs app)
□ IAM/RBAC negative case: unauthorised caller gets a clean denial
□ Secrets in the platform secret store, not in config or code
□ Data residency verified, including any cross-region routing
□ Cost attribution per feature/tenant available
□ Logs and traces retained per policy, with PII redacted
□ Model deprecation notices tracked (Part 18 §18.3)
□ Fallback across providers or regions tested (Part 14 §14.9)
```

---

## 22.6 How much cloud should you learn?

| Depth | Verdict |
|---|---|
| Console navigation, finding a deployment, reading its config | 🔴 MUST |
| Reading logs and metrics for your service | 🔴 MUST |
| Calling the model API with the cloud SDK | 🔴 MUST |
| Understanding quotas, regions, and deployment models | 🔴 MUST |
| Configuring managed guardrails to test them | 🟠 SHOULD |
| Setting up a managed RAG index end to end | 🟠 SHOULD |
| IAM policy authoring | 🟡 OPTIONAL |
| Infrastructure as code (Terraform/Bicep) | 🟡 OPTIONAL — useful for reproducible test environments |
| Networking, VPC, private endpoints | ⚪ NOT REQUIRED |
| Cost optimisation architecture | ⚪ NOT REQUIRED |

**Pick one cloud and learn it properly** — whichever your employer uses. The concepts transfer; the console navigation does not, and console navigation is not what makes you valuable.

---

## 22.7 Self-check

1. Why can two deployments of the same model behave differently?
2. Name the three possible sources of a refusal and why distinguishing them matters.
3. Why is cross-region inference a compliance question?
4. What is the risk of testing against one Google surface and shipping on the other?
5. Why is "model access not enabled" a common false bug report on AWS?
6. What is security trimming and which Part 7 test covers it?

---

**Next:** [PART-23-LLMOPS.md](PART-23-LLMOPS.md) — lifecycles, registries, drift, and where QA sits among MLOps and AI Engineering.
