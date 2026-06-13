---
title: "Example Outputs"
---

# Example Outputs

Real output captured from running every cookbook example against a local **Ollama `gemma3:4b`** instance.
Each example runs two passes — first call hits the LLM, second call is served instantly from cache.

:::info Environment
- Model: `gemma3:4b` via Ollama on `localhost:11434`
- Backend: `InMemoryBackend` (in-process, no external services)
- Timing: `time.perf_counter()` — wall-clock elapsed time
:::

---

## Speedup Summary

| Example | First Call | Cache Hit | Speedup |
|---|---|---|---|
| Core — ResponseCache | 28.714s | 0.000s | **267,104x** |
| LangChain | 5.172s | 0.003s | **1,645x** |
| LangGraph | 33.415s | 1.907s | **18x** |
| AutoGen | 49.794s | 0.000s | **132,678x** |
| CrewAI | 229.622s | 0.006s | **40,918x** |
| Agno | 20.278s | 0.001s | **33,401x** |
| A2A | 272.111s | 0.002s | **171,994x** |
| Multi-Framework | 92.845s | 0.003s | **29,832x** |
| SemanticCache | 0.076s | 0.000s | **228x** |
| TTL | 0.000025s | 0.000009s | **3x** |
| Invalidation | 0.000205s | 0.000031s | **7x** |

---

## Tier 1 — Base Examples

### TTL: Per-Type Retention Policy

```
set : 0.000025s
get : 0.000009s  (3x faster)
stored key with response ttl policy, value: ok
```

---

### Invalidation: Tag-Based Bulk Eviction

```
set 2 keys : 0.000205s
invalidate : 0.000031s  (evicted 2 keys)
```

---

### Core: ResponseCache + EmbeddingCache

```
=== Response Cache ===
Okay, here are 3 key release safety checks:

1. **Smoke Testing (Functional Verification):**
   - Rapid, high-level test run immediately after deployment.
   - Focuses on the most critical functionality.
   - Success Criteria: All smoke tests pass.

2. **Regression Testing (Stability Verification):**
   - Re-runs previously passed tests to catch unintended side effects.
   - Success Criteria: 95%+ of regression tests pass.

3. **Monitoring & Alerting (Performance Verification):**
   - Real-time monitoring of error rates, response times, resource utilization.
   - Success Criteria: No critical alerts triggered.

First call : 28.714s
Cache hit  : 0.000s  (267104x faster)
cache_hit_same: True

=== Embedding Cache ===
embedding_demo_skipped: model "nomic-embed-text" not found
tip: run `ollama pull nomic-embed-text` and re-run this example
```

---

## Tier 2 — Framework Examples

### LangChain: Support Assistant Chain

```
=== First Run (LLM call expected) ===
Subject: Regarding Duplicate Charge & Account Security

"Thank you for reporting this. We understand your concern about the
duplicate charge and pending hold.

Summary: You've reported a duplicate charge for an order, with one
successful and one pending.

Root Cause Hypothesis: This likely indicates a processing error within
our system.

Next Steps: We've initiated a duplicate charge investigation as per our
refund policy (48h window). We'll also review your account for any
unusual activity. We will provide an ETA for the refund processing once
engineering confirms the resolution."

Time: 5.172s

=== Second Run (cache hit expected) ===
Subject: Regarding Duplicate Charge & Account Security

"Thank you for reporting this. We understand your concern..."
[identical response]

Time: 0.003s

Speedup: 1645.2x faster
```

---

### LangGraph: Incident Triage Graph

```
=== First Run (LLM call expected) ===
Severity: CRITICAL
Plan:
 Subject: IMMEDIATE ACTION - Payment API Latency Spike - AP-South

Phase 1: Immediate Containment (0-15 mins)
- Activate Incident Response Team (IRT)
- Rollback Deployment: Initiate targeted rollback to previous stable
  deployment for the AP-South region
- Alerting: Increase monitoring granularity on key metrics

Phase 2: Diagnostics (15-60 mins)
- Root Cause Analysis: Investigate deployment changes
- Log Analysis: Look for error patterns, slow queries
- Network Diagnostics: Check connectivity and DNS

Phase 3: Stakeholder Communications (Ongoing)
- Initial Update (5 mins): Brief factual update to key stakeholders
- Regular Updates (Every 15 mins): Escalating updates with ETA

Phase 4: Follow-Up (60+ mins)
- Confirm Stability, Root Cause Documentation, Post-Mortem

Time: 33.415s

=== Second Run (cache/checkpoint expected) ===
Severity: CRITICAL
Plan:
 [identical response]

Time: 1.907s  (18x faster)
```

:::note
LangGraph's second run is 18x faster (not instant) because checkpointing adds
replay overhead. LLM calls themselves are fully cached — the remaining time
is graph state deserialization.
:::

---

### AutoGen: Async Assistant

```
=== AutoGen First Run ===
messages=[TextMessage(source='user', content='Give a 5-point migration plan...'),
          TextMessage(source='assistant', models_usage=RequestUsage(
              prompt_tokens=54, completion_tokens=736),
          content='
5-Point Migration Plan: Sync Webhooks to Async Processing

1. Phase 1: Setup & Off-Peak Testing (1-2 Weeks)
   - Implement messaging queue (RabbitMQ, Kafka, AWS SQS)
   - Set up processing service (Lambda, Azure Functions)

2. Phase 2: Shadow Routing & Data Validation (2-4 Weeks)
   - Duplicate all webhooks: one sync (existing), one async (new)
   - Meticulously validate and compare data from both paths

3. Phase 3: Limited Beta Rollout (2-4 Weeks)
   - Gradually route 5-10% of new webhooks to async service
   - Monitor performance and error rates closely

4. Phase 4: Gradual Rollout & Monitoring (4-8 Weeks)
   - Increase async traffic incrementally based on monitoring
   - Have a rollback plan ready at all times

5. Phase 5: Full Transition & Decommissioning (1-2 Weeks)
   - Redirect all webhooks to async processing service
   - Decommission original sync logic
   ---TERMINATE')]

Time: 49.794s

=== AutoGen Second Run (cache hit expected) ===
[identical response — same message IDs, same token counts]

Time: 0.000s  (132678x faster)
```

---

### CrewAI: Release Planning Crew

```
=== First Run (full crew execution expected) ===
## payments-api Release Plan

1. Executive Summary:
   This release introduces retries and a webhook async pipeline.
   High traffic (2.1M requests/day) and existing instability make
   this a significant-risk deployment. Phased canary rollout required.

2. Deployment Checklist:
   Phase 1: Pre-Deployment (72h Prior)
   [ ] Code Freeze
   [ ] Automated Testing (95%+ coverage)
   [ ] Monitoring Dashboards Created
   [ ] Rollback Plan Reviewed & Tested
   [ ] Canary Environment Ready

   Phase 2: Deployment Day
   [ ] Deploy to Canary (1-5% of Traffic)
   [ ] Monitor Canary Performance
   [ ] Confirm Idempotency Key Implementation

   Phase 3: Expansion
   [ ] Increase Canary Traffic to 5-10%
   [ ] Scale to Production (100%) on stable metrics

3. Rollback Triggers:
   - Error rate > 5% for 5 minutes
   - Webhook failure cascade
   - Sustained latency increase beyond SLOs
   - Manual trigger by Release Manager

4. Go/No-Go Decision Matrix:
   Canary Latency P95   < 150ms
   Canary Error Rate    < 0.5%
   Webhook Success Rate > 99%

   Recommendation: No-Go (pending deeper investigation of R-02, R-03)

Time: 229.622s

=== Second Run (cache hit expected) ===
[identical response]

Time: 0.006s  (40918x faster)
```

---

### Agno: Deployment Risk Analyst

```
=== First Run (LLM call expected) ===
**Deployment Risk Memo - v2.14**

**1. Risk Level:** MEDIUM

**2. Top 3 Risks:**
- Risk 1: Flaky Integration Test (Timeout Handling) — directly impacts
  stability of the new async webhook ingestion path
- Risk 2: Payment Retry Logic — potential for increased latency if not
  fully optimized
- Risk 3: Redis Client Upgrade — moderate risk of compatibility issues

**3. Monitoring/Alert Checks:**
- Payment Retry Rate: alert on > 5% increase
- Async Webhook Ingestion Latency: alert on > 200ms average
- Redis Performance: memory, connections, latency
- Integration Test Failure Rate: any failure is priority

**4. Rollback Criteria:**
- Any failure of the flaky integration test
- Payment retry rate exceeds 10% threshold
- Redis performance below acceptable levels

**5. Go/No-Go Recommendation:**
GO with Caution — phased canary deployment recommended.
Rapid rollback plan must be in place and tested prior to full deployment.

Time: 20.278s

=== Second Run (cache hit expected) ===
[identical response]

Time: 0.001s  (33401x faster)
```

---

### A2A: Planner-Executor-Reviewer Pipeline

```
=== First Run (three LLM stages expected) ===
[Reviewer output after Planner + Executor stages]

Overall Assessment: Solid strategy. SQS/Lambda approach is sensible.
Phased rollout is crucial. Data reconciliation is the single most
important safeguard.

Key Feedback:
1. Data Transformation: Schedule deep dive on transformation logic.
   Add task "Data Transformation Design & Review" (0.5-1 week).

2. Fraud Detection Dependency: Add "Fraud Detection Data Validation
   Protocol" task to Phase 2.2.

3. Rollback Plan: Needs steps to:
   - Immediately disable Lambda function
   - Re-route all webhooks back to synchronous system
   - Document and dry-run before full deployment

4. Monitoring Expansion:
   - Lambda Cold Starts
   - SQS Queue Latency
   - Error Rates (per webhook type)

Action Items:
- Schedule deep dive on data transformation (1h next week)
- Assign fraud detection validation task
- Review and refine rollback plan (30-min meeting)

Time: 272.111s

=== Second Run (A2A cache hits expected) ===
[identical response — all 3 stages (planner, executor, reviewer) cached]

Time: 0.002s  (171994x faster)
```

---

### Multi-Framework: LangChain + A2A Shared Cache

```
=== Multi-Framework First Run ===
Revised Release Outline: Checkout Latency Reduction

1. Executive Summary:
   Goal: Reduce checkout latency via Redis caching + async webhooks.
   Target: 30% reduction in average checkout time.

2. Key Features:
   - Redis Caching for frequently accessed checkout data
   - Async Webhook Processing via RabbitMQ/Kafka
   - Monitoring & Alerting for latency and errors

3. Release Stages:
   Phase 1: Development (2 weeks)
   Phase 2: Internal Testing (1 week)
   Phase 3: Beta Release (2 weeks)
   Phase 4: Production Release

4. Risk Controls (added by reviewer):
   Risk 1: Webhook Queue Congestion
   - Control: Rate limiting + tiered queue with priority levels
   - Monitor: Queue depth and consumer processing times

   Risk 2: Redis Cache Invalidation Issues
   - Control: Event-driven invalidation + TTL for all cached entries
   - Monitor: Cache hit rates and unexpected cache misses

Time: 92.845s

=== Multi-Framework Second Run (cache hit expected) ===
[identical response — both LangChain and A2A layers hit cache]

Time: 0.003s  (29832x faster)
```

---

## Tier 3 — Optional Backends

### Semantic Cache: FAISS + Deterministic Embedding

```
=== Exact hit (same text) ===
Profile hot path, add caching, optimize DB queries.
set : 0.075784s
get : 0.000332s  (228x faster)

=== Miss (different text, deterministic embed != same vector) ===
None
get (miss): 0.002633s

=== Direct exact cache hit ===
Measure, profile, then cache hot paths.
get : 0.000145s
```

:::note
The "miss" result is expected — `mock_embed` uses a hash-based seed so different
text always produces a different vector. With a real embedding model and a
threshold of ~0.85, semantically similar queries would return cached answers.
:::

---

## Run It Yourself

```bash
# Install
pip install chengeta-ai langchain-ollama

# Pull model
ollama pull gemma3:4b

# Run any example
uv run python -m cookbook.langchain.agent
uv run python -m cookbook.a2a.agent

# Run all (base tier — no Ollama needed)
uv run python cookbook/run_all.py

# Run all (full — needs Ollama)
uv run python cookbook/run_all.py --full
```
