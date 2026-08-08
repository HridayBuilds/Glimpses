# Glimpses — Locked Technology Decisions

**What this file is:** the finalized answer to every ruled `T-nn`, kept **tight and reference-grade** — what to build, named precisely, nothing more. The technology-phase counterpart of `LOCKED_PRODUCT.md`, but deliberately without its reasoning bullets.

**What this file is not:** the explanation. It does not teach the concept, walk through alternatives, or justify the choice — that lives in **`TECH_EXPLANATIONS.md`**, linked by the same `T-nn`. This file is what you read to know what Glimpses runs on; that file is what you read to understand why and how it works.

**Source of truth for:** stack, runtime, service shapes, data model, naming. **Source of truth for product behaviour remains `LOCKED_PRODUCT.md`** — if a technology entry here ever implies different product behaviour than a `P-nn`, the `P-nn` wins and this entry is wrong.

**Covers:** 6 of 8 agenda areas ruled so far. **Opened:** 2026-08-06.

---

## Decision log

| Date | `T-nn` | Ruling |
|---|---|---|
| 2026-08-08 | `T-01` | All Python |
| 2026-08-08 | `T-02` | Step Functions Distributed Map (not SQS + DLQ) |
| 2026-08-08 | `T-03` | Domain-grouped API Lambdas (5) + 1 consolidated pipeline Lambda + `db-api` and HEIC→JPEG converter (2 shared) — 8 Lambdas total *(pipeline consolidated from 4 to 1 same day)* |
| 2026-08-08 | `T-04` | Multi-table (not single-table) — 6 tables: `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees` |
| 2026-08-08 | `T-05` | One Rekognition collection per event (not one shared account-wide collection) |
| 2026-08-08 | `T-06` | S3 state backend + native locking, no DynamoDB; per-Lambda Terraform modules; dedicated CI job for untargeted applies; 9 CI/CD jobs total; fixed `glimpses-` naming prefix, no transformation |
| 2026-08-09 | `T-07` *(partial — observability only)* | Powertools structured `Logger`, full-request auto-logging, 3-day log retention, no X-Ray, no custom metrics, every alarm wired to SNS + email, `Errors > 0`/5min alarm on all 8 Lambdas |

---

## 1. Runtime and language

**`T-01` — All Python.** Every Lambda — API handlers and the HEIC→JPEG conversion alike — runs on Python/boto3. Consolidated routing (multiple endpoints per Lambda) via AWS Lambda Powertools' `APIGatewayRestResolver`, which also handles API Gateway response conversion natively. No middleware engine (middy has no Python equivalent and Powertools already covers routing/response/CORS). No DynamoDB Toolbox (TS-only; not needed under a multi-table, GSI-per-access-pattern data model) — plain typed wrapper functions over `boto3`/`DocumentClient` cover data access instead. Layering follows `handler → manager → procedure/converter → DAO`, a folder convention independent of language.

## 2. Ingestion orchestration

**`T-02` — Step Functions Distributed Map**, not SQS + DLQ, for the face-indexing fan-out step of ingestion. The Map state iterates the batch's photo list — supplied via an **S3 `ItemReader`** pointed at the extraction step's output folder, never as a JSON array passed between states — invoking the indexing Lambda per photo up to a configured concurrency ceiling. Retry-with-backoff and a tolerated-failure-percentage are declared on the state itself; the state's completion is the batch's completion, with no separate polling loop or DynamoDB "is it done" counter required.

**`MaxConcurrency` is a Terraform variable** (e.g. `rekognition_index_max_concurrency`), not a hardcoded value — it must be set to the deploying account's actual Rekognition `IndexFaces` TPS Service Quota (check via the Service Quotas console; new/lightly-used accounts commonly start below the published default of 50 TPS). Document this requirement plainly in the Terraform variable description and in Sam-facing deploy docs, since a mismatch here produces silent throttling, not a build failure.

## 3. API shape

**`T-03` — 8 Lambdas total: 5 API-facing (domain-grouped, not one-per-endpoint), 1 consolidated pipeline Lambda, 2 shared utility Lambdas.**

**API-facing (behind API Gateway), each scoped to one DynamoDB table:**

| Lambda | Paths | Table |
|---|---|---|
| Profile | `POST /profile`, `PUT`/`DELETE /profile/selfie` | `Users` |
| Events | `POST`/`GET /events`, `GET /events/{eventId}`, `POST /events/{eventId}/archive`, `GET /events/{eventId}/stats` | `Events` |
| Membership | `POST /events/{eventId}/join`, admit/eject, pending/approved lists | `EventAttendees` |
| Upload/status | `POST /events/{eventId}/upload-url`, `GET /events/{eventId}/jobs/{jobId}/status` | `Jobs` (read), S3 pre-signed URLs |
| Gallery/photos | `GET /events/{eventId}/photos`, `?mine=true`, photo/ZIP download | `Photos` |

**Pipeline (Step Functions-triggered, `T-02`) — one consolidated Lambda, `PipelineHandler`:** the same four steps — `InitializeJob` (creates the `Jobs` row) → `Extract` (unzip, dedup, format-sniff, HEIC convert, thumbnail, write to S3/`Photos`) → `IndexOnePhoto` (one per photo, invoked by the Distributed Map; Rekognition `IndexFaces`) → `Finalize` (tallies the batch, computes terminal outcome and storage total) — but each Step Functions state invokes the same physical Lambda, passing a `step` field in its input; the handler branches internally. No external caller can reach this function; only Step Functions ever invokes it.

**Shared utility, each called from multiple places:** HEIC→JPEG converter (called from `Extract` and `Profile`, per `P-35`). `db-api` — a generic status-writer Lambda scoped to the `Jobs` table only, called as its own state from four points in the ingestion state machine (marking `EXTRACTING`, `INDEXING`, the terminal outcome, and `FAILED`); deliberately a separate Lambda rather than a shared code library, so the write is reusable and visible in the state machine's execution history — accepted tradeoff: a `db-api` failure after a real step has already succeeded can abort a batch whose work is done, which a same-process library call would not risk.

**Left open:** API Gateway flavour (HTTP API vs REST API) — not decided in this ruling.

## 4. Data model

**`T-04` — Multi-table, not single-table design.** Six DynamoDB tables, each scoped to one entity type, each keyed by that entity's own natural id: `Users` (`userID`), `Events` (`eventID`), `Jobs` (`jobId`), `Photos` (`photoID`), `Faces` (`rekognitionFaceID`), `EventAttendees` (`userID`+`eventID`). Cross-entity reads are ordinary `get`/`batchGet`/GSI-`query` calls across separate tables — no shared key space, no item collections. **Drops v1's 7th table, `SearchRateLimit`, entirely** — `P-16` removed search as a user action, so there is nothing left for it to rate-limit. GSI-per-named-access-pattern discipline carries over from v1 unchanged. Exact per-table field lists, PK/SK choices beyond the primary id, and GSI definitions (including how `P-57`+`P-16`'s forced cursor pagination and `P-85`'s storage-byte counter are actually implemented) are a following sub-decision, not yet ruled.

## 5. Rekognition collection lifecycle

**`T-05` — One Rekognition collection per event.** Created by application code at event creation (`create_event`), never in Terraform, since a collection is a data-dependent runtime resource tied to a specific `eventID` — Terraform has no visibility into it. `IndexOnePhoto` indexes each photo's faces into that event's own collection; `SearchFaces` for an attendee only ever queries that one collection, so `P-07`'s no-cross-event-visibility rule is enforced by AWS itself, not application-code filtering. `P-32` archiving is a single `DeleteCollection` call. The collection's id is stored on the `Events` table (`rekognitionCollectionID`) so a teardown script can enumerate and delete orphaned collections without depending on Terraform state. `P-52`'s per-photo deletion still requires retaining each photo's face-vector IDs so `DeleteFaces` can target them specifically, independent of this ruling.

## 6. Terraform state and naming

**`T-06` — State backend: S3 bucket, native S3 locking (`use_lockfile = true`, Terraform ≥1.10), no DynamoDB, versioning on.** No local state, ever, past the very first bootstrap. `terraform.tfstate*` stays gitignored — state files hold real values in plaintext regardless of `sensitive` markings.

**Module layout:** each of the 8 Lambdas (`T-03`) is `Backend/<name>/` (code) + `Backend/<name>/infra/` (a self-contained child module): `lambda.tf`, `iam_role.tf`, `iam_policies.tf`, `cloudwatch.tf`, `input.tf`, `output.tf`. Root `/infrastructure` is the composition root — `imports.tf` (one `module` block per Lambda + shared modules `api_gateway`, `dynamodb`, `state_machines`), `providers.tf`, `variables.tf`, `outputs.tf`.

**Deploy discipline:** every Lambda's own Jenkinsfile runs `terraform apply -target=module.<lambda>` then its code push (GitHub → zip → deployment-artifacts S3 bucket → `aws lambda update-function-code`). Every `lambda.tf` carries `lifecycle { ignore_changes = [s3_key, source_code_hash] }`. A **separate, dedicated CI job**, belonging to no single Lambda, runs the plain untargeted `apply` that builds/updates cross-module resources (the state machine, DynamoDB tables) — run by hand whenever module wiring changes, never automatic.

**CI/CD granularity: 9 jobs total** — 8 per-Lambda Jenkinsfiles + 1 dedicated untargeted-apply job. Only resources with actual code to push get a Jenkinsfile. The Terraform state bucket itself is created once, outside all 9 jobs, via a manual step or one-off script (bootstrapping problem — it can't be created by an apply that depends on it already existing).

**Naming: fixed `glimpses-` prefix, applied identically everywhere, never conditionally.** Folder name is the single source of truth; AWS-visible name = `"glimpses-" + folder_name`, underscores swapped to hyphens. No environment branching, no per-resource mapping file.

| Folder | AWS Lambda name |
|---|---|
| `profile` | `glimpses-profile` |
| `events` | `glimpses-events` |
| `membership` | `glimpses-membership` |
| `upload_status` | `glimpses-upload-status` |
| `gallery` | `glimpses-gallery` |
| `pipeline` | `glimpses-pipeline` |
| `db_api` | `glimpses-db-api` |
| `heic_converter` | `glimpses-heic-converter` |

Same rule for non-Lambda resources: `Users`/`Events`/`Jobs`/`Photos`/`Faces`/`EventAttendees` tables → `glimpses-users`, `glimpses-events`, etc.; state machine → `glimpses-ingestion`; Terraform state bucket → `glimpses-terraform-state`; deployment/artifacts bucket → `glimpses-deploy-artifacts`.

## 7. Observability, IAM, CORS, secrets

**`T-07` — observability sub-decision ruled 2026-08-09; IAM granularity, CORS, and secrets remain open.**

**Logging:** Powertools `Logger`, structured JSON, on all 8 Lambdas — no new dependency, since `T-01` already ships Powertools. `log_event=True`: the full incoming request is auto-logged on every invocation (chosen deliberately over selective-field-only logging). CloudWatch log retention set to **3 days** on every Lambda's log group, a direct consequence of `log_event=True` capturing sensitive request data (e.g. the `P-19` profile selfie).

**Tracing:** no X-Ray / Powertools `Tracer`. Cross-Lambda correlation relies on structured log fields (e.g. `jobID`) instead.

**Metrics:** no custom Powertools `Metrics`. AWS's default Lambda metrics (`Errors`, `Duration`, `Invocations`, `Throttles`) only — `P-100`'s tolerated-failure-percentage stays a manual read of Step Functions execution history, not an alarmable number.

**Alarms:** every alarm wired to an **SNS topic with an email subscription** — closes v1's silent-alarm bug (`HANDOFF.md` §7: alarms existed, nothing was ever subscribed). Alarm content: `Errors > 0` over a 5-minute window, identical shape on all 8 Lambdas, living in each Lambda's own `cloudwatch.tf` per `T-06`'s per-Lambda module layout — which also structurally closes v1's hardcoded-alarm-list bug (a new Lambda's alarm ships with its module, not a separately-remembered central list). `P-81` bounds all of this to operator-only notification; nothing here is ever user-facing.

## 8. Testing approach and CI/CD

---

## Coverage checklist

*(Populated once the first `T-nn` is ruled — mirrors `PRODUCT_WALKTHROUGH.md` §10's role of confirming nothing is missing.)*
