# Glimpses — Technology Explanations

**What this file is:** the teaching material behind every ruled `T-nn` — what the thing physically is, how it actually works, what alternatives existed and why one won. Written so the user understands and can justify each decision, not just use it. This is a **build-and-learn project** — the point of this file is that the user could explain any entry here to someone else without re-deriving it.

**What this file is not:** the reference. It does not state the final answer tersely — that lives in **`LOCKED_TECH_DECISIONS.md`**, linked by the same `T-nn`. Read that file to know what Glimpses runs on; read this one to understand why.

**How each entry is written** — same discipline that ruled the product, adapted for concepts rather than product behaviour:

1. **Build up from what the thing physically is**, the way `PRODUCT_WALKTHROUGH.md` explained EXIF as "a small block of text inside the photo file" before naming it. A Lambda cold start, a DynamoDB GSI, a Step Functions state machine — plain language first, jargon second.
2. **Run every real option through named concrete scenarios** — reuse the cast (Meera, Arjun, Priya, Rohan, Sam) wherever the technology choice has a user-visible or operator-visible consequence; introduce new technical scenarios (e.g. "a batch of 1,000 photos", "a Lambda cold start under load") where the product cast doesn't reach.
3. **A scorecard** — options as rows, scenarios or criteria as columns.
4. **What v1 did, and whether this repeats or departs from it** — every entry cross-references `HANDOFF.md` where relevant, since avoiding v1's mistakes by name is the point of this phase.
5. **The recommendation, marked, never assumed.**

**Covers:** 0 of 0 technology decisions explained so far. **Opened:** 2026-08-06.

---

## 1. Runtime and language

*(Not yet ruled — nothing to explain yet.)*

## 2. Ingestion orchestration

## 3. API shape

## 4. Data model

## 5. Rekognition collection lifecycle

## 6. Terraform state and naming

## 7. Observability, IAM, CORS, secrets

## 8. Testing approach and CI/CD
