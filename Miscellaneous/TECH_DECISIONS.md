# Glimpses — Open Technology Decisions & Working Notes

**What this file is:** the working space where technology decisions get made. Options, tradeoffs, and unresolved questions live here — the technology-phase counterpart of `PRD.md`.

**What this file is not:** the answer. Once a question is ruled, the decision moves to **`LOCKED_TECH_DECISIONS.md`** as a tight, reference-grade entry, and the concepts and reasoning behind it are written up in **`TECH_EXPLANATIONS.md`**. Read `LOCKED_TECH_DECISIONS.md` first if you want to know what Glimpses runs on; read `TECH_EXPLANATIONS.md` if you want to know why and how.

**How we work:** AI presents options with real tradeoffs — using named concrete scenarios and a scorecard, the same method that ruled all 100 product decisions — and the user rules. Nothing gets decided by default or by implementation drift. **Technology never re-rules product**: if an option here would make a `P-nn` awkward or expensive, that is surfaced as a product revision request, not resolved here.

**Status:** 7 ruled · 0 open *(register opened 2026-08-06)*

**Ids:** `T-nn`, stable and never reused or renumbered. A question closed without a technology choice attached (because product made it moot, or because it dissolved into another question) is marked **DISSOLVED**, not deleted.

---

## How to read the register

Each question has a stable `T-nn` id. Questions are grouped by the agenda area in `SESSION_HANDOFF.md`'s "The technology phase" table. The **Product inputs** column names which `P-nn` rulings constrain the answer — check these before proposing options, since they are not negotiable inputs to the decision, only the decision itself is open.

---

## Agenda area 1 — Runtime and language

### `T-01` — Backend runtime and language

**RULED 2026-08-08 → A (all Python).** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question:** one Lambda runtime/language for the whole backend, or split by function? v1 planned Node/TS and shipped Python by drift (`HANDOFF.md` §2) — this had to be decided deliberately, not inherited.

**Options considered:**
- **A — All Python.** Every Lambda, including HEIC→JPEG conversion, in Python/boto3, using Powertools' `APIGatewayRestResolver` for consolidated routing.
- **B — All Node/TypeScript.** Eliminated early — `sharp` deliberately excludes HEIC decoding (patent reasons), and `P-35` requires it everywhere an image enters the product.
- **C — Node/TS backbone + one isolated Python Lambda for HEIC→JPEG only.** Everything else in Node/TS with Powertools' `Router`, evaluated against the user's named vocabulary (middy, DynamoDB Toolbox, `handler → manager → procedure/converter → DAO`).

**Why A won over C:** the layering pattern (`handler → manager → DAO`) is a folder convention, not Node-specific — it works identically in Python. That left only two Node-specific tools in play, and both were ruled unnecessary on their own merits before the runtime question closed: **middy** — Powertools' router already provides routing, response conversion, and CORS, so a second middleware engine would duplicate it (and repeat `HANDOFF.md` §7's "shipped, never wired" mistake with Powertools/pydantic in v1); **DynamoDB Toolbox** — its value is protecting single-table designs from key collisions, and this project is keeping v1's multi-table, GSI-per-access-pattern model, where a "join" is just an ordinary `get`/`batchGet` across tables, not a shared key space. With both off the table, C's only remaining edge was Node's slightly faster cold start at 512MB — real but small for an I/O-bound JSON API — against Python's genuinely more mature Powertools router (Node's TS event-handler package was found split across two still-settling import paths) and a single build toolchain instead of two. **Product input:** `P-35` (HEIC→JPEG applies to organizer ZIPs, attendee contributions, and profile selfies alike — all served by the same one Python function under either option).

**Decided by the user, final.**

**Follow-on, not re-opened:** DynamoDB Toolbox is *not adopted* — plain typed wrapper functions over the AWS SDK v3 `DocumentClient` cover the multi-table access pattern without an extra dependency. This is a working assumption, not a formal `T-nn` ruling, and can be revisited if `T-04` (data model) turns up a reason to.

---

## Agenda area 2 — Ingestion orchestration

### `T-02` — Face-indexing fan-out: SQS + DLQ vs Step Functions Distributed Map

**RULED 2026-08-08 → Step Functions Distributed Map.** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question:** how does the ingestion pipeline fan out per-photo Rekognition indexing calls across a batch (up to ~1,000 photos), retry transient failures, isolate real failures, and detect batch completion — the mechanism `P-100` deliberately left open, flagging it as a genuine input to this decision.

**Options considered:**
- **SQS + DLQ (v1's approach).** A queue holds one message per photo; a worker Lambda consumes them; retry is implicit (an unacknowledged message becomes visible again after its timeout); a DLQ catches messages that fail `maxReceiveCount` times; a separate polling loop (Step Functions Standard `Wait → Check → loop`) is needed to detect "batch complete," reading DynamoDB counters maintained by hand.
- **Step Functions Distributed Map.** A single state in the ingestion workflow iterates over the batch's photo list, invoking the indexing Lambda per item with a configured concurrency ceiling (`MaxConcurrency`). Retry-with-backoff and a tolerated-failure-percentage are declared directly on the state, not coded. The state's own completion is the batch's completion — no polling loop required.

**Why Distributed Map won:** v1's own stated reason for SQS — *"valid, but more advanced to configure and debug for a first build"* (`HANDOFF.md` §2) — bought a hand-rolled polling loop and DynamoDB counter bookkeeping that Distributed Map removes entirely, replacing it with a single visual, per-item execution history in the Step Functions console. For a build-and-learn project, that visibility was judged worth the cost of building on a less common, less documented AWS feature. Cost at this batch size (~1,000 state transitions/batch) is trivial either way.

**Product inputs:** `P-100` (progress/retry visibility — explicitly names this exact choice as its input, and its own text warns not to let the stack choice narrow what it promises); `P-56` (transient retry); `P-53` (hard batch deadline); `P-55` (final counts, not filenames).

**Design obligation, load-bearing:** the Map state's item list must come from an **S3 `ItemReader`** pointed at the extraction step's output folder (`events/{eventId}/jobs/{jobId}/photos/`) — **not** a JSON array of photo IDs passed between states. This keeps state-machine payloads at the `jobId`/S3-path scale v1 already established (`HANDOFF.md` §4: *"only `jobId` was carried through state-machine JSON — 256KB hard ASL limit"*), rather than reintroducing bulk data into state transitions.

**Design obligation, load-bearing:** `MaxConcurrency` on the Map state must be a **Terraform variable**, not a hardcoded value — it is bound by the account's actual Rekognition `IndexFaces` TPS quota (a Service Quota, not a product constant), which differs per AWS account and is frequently below the commonly-cited default for new/lightly-used accounts. Hardcoding it risks throttling for anyone who deploys this (`Sam`) without knowing to change it.

**Decided by the user, final.**

---

## Agenda area 3 — API shape

### `T-03` — Backend Lambda-function shape: API grouping, pipeline Lambdas, and shared utility Lambdas

**RULED 2026-08-08 → Domain-grouped API Lambdas + one consolidated pipeline Lambda + two shared utility Lambdas (`db-api`, HEIC→JPEG converter).** *(Pipeline shape revised 2026-08-08, same day — see "Pipeline Lambdas" below.)* See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question:** how many physical Lambda functions does the backend consist of, and which endpoints/pipeline steps share one? v1 built one Lambda per business endpoint (9 functions) plus a separate set of pipeline Lambdas. `HANDOFF.md` §9 names this exact fork point: *"one-Lambda-per-endpoint again, or a grouped/router pattern... to reduce IAM/deploy-script boilerplate at the cost of a slightly heavier single function?"*

**Options considered, for the API-facing surface:**
- **A — One Lambda per endpoint (v1's shape).** Tightest possible IAM per action; deploy/Terraform boilerplate grows with every endpoint.
- **B — Fully consolidated, one Lambda for the entire API.** Least boilerplate; one IAM role carries the union of every permission any endpoint needs — widest possible blast radius from a single bug.
- **C — Domain-grouped: several Lambdas, each scoped to one bounded resource/table.** Chosen.

**Ruled: C.** Five API-facing Lambdas, each scoped to one DynamoDB table:

| Lambda | Paths | Table |
|---|---|---|
| Profile | `POST /profile`, `PUT`/`DELETE /profile/selfie` | `Users` |
| Events | `POST`/`GET /events`, `GET /events/{eventId}`, `POST /events/{eventId}/archive`, `GET /events/{eventId}/stats` | `Events` |
| Membership | `POST /events/{eventId}/join`, admit/eject, pending/approved lists | `EventAttendees` |
| Upload/status | `POST /events/{eventId}/upload-url`, `GET /events/{eventId}/jobs/{jobId}/status` | `Jobs` (read), issues S3 pre-signed URLs |
| Gallery/photos | `GET /events/{eventId}/photos`, `?mine=true`, photo/ZIP download | `Photos` |

**Why C over A and B:** grouping by which table/data an endpoint touches — not by URL prefix, which is a real point of confusion worth documenting since most endpoints share the `/events/...` prefix regardless of which table they touch — keeps IAM blast radius bounded per domain, while cutting Terraform/deploy boilerplate from 9 functions down to 5.

**Pipeline Lambda — revised same day, 2026-08-08, to one consolidated function (extends `T-02`'s shape, differentiated internally rather than by named functions):** the four pipeline steps — `InitializeJob` (creates the `Jobs` row, generates `jobId`), `Extract` (unzips top-level photos per `P-54`, dedup hash per `P-38`, format-sniffs, calls the HEIC converter when needed, generates thumbnails per `P-35`, writes results to S3, writes pending `Photos` rows), `IndexOnePhoto` (invoked once per photo by the Distributed Map from `T-02`; calls Rekognition `IndexFaces`, writes face ID(s) back), `Finalize` (tallies `INDEXED`/`FAILED` across the batch, computes the terminal outcome per `P-55` and the updated storage total per `P-85`) — are now one physical Lambda function, `PipelineHandler`. Each Step Functions state still invokes it separately, passing a `step` field in the state's input JSON; the Lambda's own handler branches on that field, the same role a URL path plays for the API Lambdas' router, except there is no HTTP path here at all — nothing external ever calls this function, only Step Functions.

**Why revised:** raised by the user directly while working through the Terraform module layout (agenda item 6) — reconsidered against the same "wide IAM role, single blast radius" argument that ruled out fully-consolidating the *API* Lambdas (Option B, above), and found not to transfer. The API case turns on an external caller being able to reach a Lambda directly through API Gateway; these four pipeline steps have **no external invocation path at all** — only Step Functions calls them, with input it generates itself. That removes the scenario the original argument depended on. The one real cost specific to this merge: `IndexOnePhoto` (by far the highest invocation count — once per photo, potentially hundreds of times a batch) now carries the whole pipeline's dependencies (Pillow/`pillow-heif` for HEIC, zip handling) in its package even though most invocations only need the Rekognition call. Judged acceptable — cold start is already amortized across a long-running batch. Accepted tradeoff, explicit: CloudWatch logs for all four steps now interleave in one log group instead of four separate ones, making a single step's logs slightly more work to isolate.

**Two shared utility Lambdas, each called from multiple places:**

- **HEIC→JPEG converter** — called from `Extract` (organizer/attendee batches) and `Profile` (selfie upload), per `P-35`'s "applies everywhere an image enters the product." Kept as its own function so the conversion logic exists exactly once, not duplicated at each call site.
- **`db-api`** — a generic status-writer Lambda, scoped to the `Jobs` table only. Called from four separate states in the ingestion state machine (marking `EXTRACTING`, `INDEXING`, the terminal outcome, and `FAILED`), each with a different status value as input.

**Why `db-api` is a separate Lambda state, not a shared code library:** a shared library (a `jobs_dao.py` imported into each pipeline Lambda, extending the `T-01` DAO-layer convention) would avoid a real failure mode entirely, since the write would run in the same process as the actual work it records. This was raised and considered directly. **The user's explicit preference was a genuinely separate, reusable Lambda function instead**, accepted with one tradeoff named plainly: a `db-api` call failing *after* its preceding step already succeeded can abort a batch whose real work is done — a gap a same-process library call would not have. Judged acceptable given `db-api`'s narrow scope (`Jobs` table only, nothing else) and Step Functions' own `Retry` making the failure rare in practice.

**Total Lambda count: 8** — 5 API-facing, 1 pipeline, 2 shared utility (HEIC converter, `db-api`). Compares to v1's ~16 (9 business + 7 pipeline).

**API Gateway flavour — left open at the time this section was first ruled, picked back up and ruled 2026-08-09, after the technology agenda closed.**

**Flagged before ruling:** `T-01`'s locked text names Powertools' `APIGatewayRestResolver` — a resolver class specific to the REST API event shape, not interchangeable with HTTP API's `APIGatewayHttpResolver`. Had REST API shipped by implementation default just because that resolver was named first, that would have been an undecided choice made by drift, the exact failure mode this rebuild exists to prevent. Surfaced explicitly rather than resolved silently.

**Options considered:**
- **A — HTTP API.** $1/million requests, lower latency, simpler CORS config. No AWS WAF support, no gateway-side request validation, no usage plans/API keys, no resource policies, no response caching. Cognito auth via a generic JWT authorizer.
- **B — REST API.** $3.50/million requests (3.5x HTTP API's price). Supports AWS WAF, gateway-side request-body schema validation, usage plans/API keys, resource policies, response caching. Cognito auth via a dedicated User Pool authorizer.

Verified current (2026-08-09): both authorizer types check the identical Cognito-issued JWT for an identical outcome — not a real differentiator. Of REST API's exclusive features, only **AWS WAF** maps to anything Glimpses actually needs: usage plans/API keys assume third-party API consumers (none exist), response caching and resource policies answer needs the product never raised. WAF specifically matters because **Rohan is a named adversarial persona** in this project (`P-07`'s access-control boundary exists because of him) — WAF can reject malicious-shaped or rate-abusive requests at the edge, before they cost a Lambda invocation or add noise to `T-07`'s `log_event=True` logging.

**Ruled: B — REST API**, accepting the 3.5x per-request cost specifically for WAF's edge protection against Glimpses' own named threat model. `T-01`'s `APIGatewayRestResolver` was correct as written — no correction required.

**Product inputs:** `P-35` (HEIC conversion applies everywhere an image enters), `P-54` (content-sniffed file type, ZIP top-level-only), `P-38` (dedup before conversion), `P-55`/`P-100` (terminal job status, durable progress), `P-07` (admission-only access control — the boundary WAF adds edge-level defense in front of).

**Decided by the user, final.**

---

## Agenda area 4 — Data model

### `T-04` — Data model: single-purpose multi-table vs single-table design

**RULED 2026-08-08 → A (multi-table, 6 tables).** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question:** does each entity type get its own DynamoDB table, keyed by its own natural id (v1's approach, "7 tables"), or do all entity types share one table using generic `PK`/`SK` attributes and type-prefixed key values ("single-table design")?

**Options considered:**
- **A — Multi-table.** Each entity — `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees` — gets its own table, keyed by its own id (`userID`, `eventID`, `jobId`, `photoID`, `rekognitionFaceID`, `userID`+`eventID`). Cross-entity reads are ordinary `get`/`batchGet`/GSI-`query` calls across separate tables. **6 tables, not v1's 7** — `SearchRateLimit` is dropped entirely, since `P-16` removed search as a user action and there is nothing left to rate-limit that way.
- **B — Single-table.** One table, generic `PK`/`SK`, every entity type's key values prefixed by type (`EVENT#123`, `PHOTO#456`, `USER#abc`). Related items (e.g. an event and its photos) can share a partition key so one Query returns both — an "item collection" — at the cost of designing the full key scheme up front, since it's expensive to change later.

**Why A won over B:** the join-reduction B exists to buy (fewer round trips for deep, high-traffic entity graphs) is real but small here — Glimpses' graph is shallow, nothing needs more than one or two hops, and the extra round trip multi-table costs is milliseconds. What actually decided it was IAM: `T-03` already scoped each API Lambda's role to exactly one table (Profile → `Users` only, Membership → `EventAttendees` only, etc.) — under multi-table that isolation is structural, a table boundary *is* an IAM boundary. Under single-table, everything shares one physical table, so the same isolation would have to be reconstructed by hand with item-level IAM key-prefix conditions, which nobody on this project has used before. Ruling B would also have reopened `T-01`, which already assumed multi-table when it ruled DynamoDB Toolbox unnecessary (Toolbox's value is protecting single-table designs from key collisions).

**Product inputs:** `P-57`+`P-16` (force cursor-based pagination, not yet designed — a design detail within whichever tables carry `Photos`); `P-85` (a storage-byte counter that must stay correct across `P-44`/`P-52`/`P-38`/`P-55`, not yet designed); `P-16` removing search killed `SearchRateLimit` outright, which is why the table count drops from v1's 7 to 6.

**Left open, not decided here:** the exact per-table field list, PK/SK/GSI definitions, and how the `P-85` byte counter and `P-57`/`P-16` cursor pagination are actually implemented on top of these 6 tables — a following sub-decision, not this one.

**Decided by the user, final.**

---

## Agenda area 5 — Rekognition collection lifecycle

### `T-05` — Rekognition collection layout: one per event vs one shared account-wide collection

**RULED 2026-08-08 → A (one collection per event).** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question:** a Rekognition "collection" is just a named bucket of face vectors, and nothing about the API forces one per event — `P-98` flagged "one collection per event" as an unruled assumption sitting underneath its own `SearchFaces`-cost arithmetic. Does each event get its own collection (v1's assumption, never formally ruled), or does the whole account share one collection with per-vector `ExternalImageId` tagging?

**Options considered:**
- **A — One collection per event.** `create_event` creates a collection (e.g. `glimpses-event-{eventID}`); `IndexOnePhoto` indexes into it; `SearchFaces` for an attendee only ever queries that one collection; `P-32` archiving is one `DeleteCollection` call.
- **B — One shared, account-wide collection.** Created once (in Terraform, not at runtime); every indexed vector tagged with `ExternalImageId` = `eventID`/`photoID`; a search returns matches from every event ever run, filtered down to the current event in application code.

**Why A won:** `P-07` already rules "no cross-event visibility, ever" as a hard permission boundary. Under A that boundary is enforced by AWS itself — a `SearchFaces` call physically cannot reach another event's collection. Under B it would be enforced entirely by application code correctly filtering every result, forever, with a cross-event data leak as the failure mode of a filtering bug. `P-32`'s archive-by-deleting-the-collection design is a one-call `DeleteCollection` under A; under B it becomes a targeted `DeleteFaces` hunt through a shared bucket. B's only real advantage — the collection becomes a static, Terraform-visible resource instead of a runtime-managed one — is a lifecycle-tracking convenience, not a reason to share the security boundary across every event in the account.

**Design obligation, load-bearing:** collections are created/destroyed by application code at runtime (in `create_event`/on archive), not Terraform — Terraform has zero visibility into them, the same fork point v1 hit (`HANDOFF.md` §4, §9). The collection's id must be tracked in the `Events` table (as v1's `Events.rekognitionCollectionID` already did) so a teardown script can enumerate and clean up orphans without depending on Terraform state — closing `HANDOFF.md` §9's fork point deliberately rather than rediscovering it during a real teardown.

**Product inputs:** `P-98` (flags the per-event-collection assumption directly), `P-32` (archiving permanently deletes the collection — one call under A), `P-52` (deleting a photo must remove just that photo's face vectors via `DeleteFaces`, which requires retaining per-photo face IDs regardless of A or B).

**Decided by the user, final.**

---

## Agenda area 6 — Terraform state and naming

### `T-06` — Terraform state backend, module layout, deploy discipline, CI/CD granularity, and naming convention

**RULED 2026-08-08 → S3 + native locking · per-Lambda modules · dedicated untargeted-apply job · 9 CI/CD jobs · fixed `glimpses-` prefix, no transformation.** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning. Five sub-decisions, all ruled the same day, in this order.

**1. State backend.** v1 used local state only, flagged in `HANDOFF.md` §2 as a harden-later item never actually hardened.

**Options considered:**
- **A — Local state.** No sharing, no locking — nothing exists to lock.
- **B — S3 remote state + DynamoDB locking.** The classic pattern; a separate DynamoDB table holds one lock-flag row during an `apply`.
- **C — S3 remote state + S3 native locking (`use_lockfile = true`, Terraform ≥1.10).** Same durability as B, no DynamoDB table required.

**Ruled: C**, plus S3 versioning turned on for rollback insurance. C dominates B — identical protection against overlapping applies, one fewer AWS resource to create/IAM-permission/remember exists, at the cost of requiring Terraform ≥1.10 (a non-issue on a fresh install). Local (A) was eliminated on Sam's fresh-deploy scenario — without shared state, Sam's `apply` has no memory of what's already built and would either try to recreate existing resources or require an out-of-band copy of the state file. **Explicitly corrected in-session:** committing the state file to Git is not a substitute for a shared backend — state files hold real values in plaintext even for variables marked `sensitive` (that flag only suppresses console/log output, not the stored value) and are unmergeable JSON blobs rewritten wholesale on every apply; `terraform.tfstate*` stays gitignored regardless of which backend option was chosen, matching v1's own `.gitignore`.

**2. Per-Lambda module layout — user-originated.** Each of the 8 Lambdas (`T-03`) gets its own folder under `Backend/<name>/` with its code plus a self-contained `infra/` child module: `lambda.tf` (the `aws_lambda_function` resource), `iam_role.tf` + `iam_policies.tf` (scoped IAM, structurally enforcing the per-Lambda isolation `T-03`/`T-04` already established), `cloudwatch.tf` (log group + alarm co-located with the Lambda they belong to), `input.tf` (`variable` blocks), `output.tf` (`output` blocks, at minimum the Lambda's ARN). Root `/infrastructure` is the composition root: `imports.tf` holds one `module` block per Lambda folder plus shared modules (`api_gateway`, `dynamodb`, `state_machines`), wiring one module's `output` into another's `variable`.

**Why this over v1's shape:** v1 used a single centralized `infra/modules/functions/` module looping over all Lambdas via a map — one shared piece of code computing every Lambda's AWS name, which is exactly the mechanism that produced the naming mismatch `HANDOFF.md` §7 describes (a value computed once centrally had to be recomputed separately by the deploy script, and the two could drift). Per-Lambda modules remove the class of bug outright — nothing about one Lambda's naming or shape is computed in a shared place that a second, independent piece of code has to agree with.

**3. Deploy discipline — how the state machine actually gets built, given `-target` limitations.**

**Options considered:**
- **A — A separate, dedicated CI job runs the untargeted `apply`.** Every Lambda's own Jenkinsfile stays targeted (`-target=module.<lambda>`) plus its code push; nothing cross-cutting is ever a side effect of a single Lambda's deploy. The dedicated job is triggered by hand, whenever module wiring changes (first build of the state machine, or a later addition that it needs to reference).
- **B — Piggyback the untargeted apply onto one specific Lambda's own pipeline** (e.g. `finalize`'s), the pattern from the user's prior company. Works, but requires remembering an indirect trigger — "did wiring change? then go run *that unrelated* Lambda's job, not the one I actually touched" — and runs a full apply as a side effect of routine, code-only deploys of that one Lambda.
- **C — Decouple entirely via `data "aws_lambda_function"` lookups by name**, removing the module-to-module dependency so no untargeted apply is ever strictly required. Rejected: trades a compile-time-checked reference (`module.x.arn`, which errors if `x` doesn't exist) for a runtime string-name lookup, which is a direct re-introduction of the drift risk `HANDOFF.md` §7 already describes.

**Ruled: A.** Chosen because it's the only option that handles the general case (any future cross-module wiring, not one pre-picked Lambda) correctly, keeps routine per-Lambda deploys fast and side-effect-free, and puts a human review checkpoint (the `apply` plan output) exactly at the moment multiple modules are being wired together — the moment a mistake is most expensive.

**Mechanical grounding this decision rests on, established in-session:** `-target` walks a resource's own dependencies but never anything that *depends on* the target — so a targeted apply on any single Lambda will never build or update the state machine, regardless of how many times it's run. A Lambda's ARN exists the moment Terraform's `aws_lambda_function` resource is first created (AWS's `CreateFunction` call), independent of and prior to any Jenkins code push (`UpdateFunctionCode`, a distinct AWS call that fails outright if the Lambda doesn't already exist — proof Jenkins cannot itself create the resource). Every `lambda.tf` needs `lifecycle { ignore_changes = [s3_key, source_code_hash] }`, or a later unrelated `apply` could silently overwrite code Jenkins already deployed — since v1 already used this same code-deploy split (confirmed against v1's real `DEVOPS.md`), this is a pre-existing risk being closed, not a new one introduced by this design.

**4. CI/CD granularity.**

**Ruled: 8 independent per-Lambda Jenkinsfiles + 1 dedicated job for the Option-A untargeted apply = 9 CI/CD jobs total** — not one shared v1-style Jenkinsfile with a `DEPLOY_TARGET` parameter. Resolving distinction: only resources with actual application code to push need a Jenkinsfile (the GitHub → zip → S3 → `update-function-code` sequence only makes sense for code) — the state machine and DynamoDB tables are pure Terraform config with nothing to zip, so they're built by the one dedicated untargeted-apply job instead, never getting a pipeline of their own. **Flagged as a related but separate special case, not formally part of this ruling:** the Terraform state bucket itself can't be created by a normal `apply` using that same backend (a bootstrapping problem — Terraform needs the bucket to exist before it can use it as a backend), so it's created once, outside all 9 jobs, via a manual step or small one-off script.

**5. Naming convention — the actual mechanism behind `HANDOFF.md` §7's bug.** v1's deploy script had to strip a `glimpse-dev-` prefix and convert hyphens to underscores to translate between the Terraform resource name and the zip/AWS function name — three-plus spellings of the same Lambda, generated in different places, kept in sync by hand.

**Options considered:**
- **A — One name, everywhere, no transformation.** Folder name is the source of truth; every other name is a direct copy, with one single fixed rule applied identically with no exceptions (see below), never a conditional or environment-dependent transform.
- **B — Environment-prefixed names** (`glimpses-dev-`, `glimpses-prod-`), v1's actual pattern, requiring a script to add/strip the prefix depending on context.
- **C — A centralized mapping file** listing Terraform-label → AWS-name → zip-name per Lambda explicitly, allowing names to differ but keeping the mapping in one place.

**Ruled: A, with a fixed `glimpses-` prefix always applied, never conditionally.** Folder name stays plain (`Backend/profile/`); AWS-visible name is `"glimpses-" + folder_name` with underscores swapped to hyphens (AWS Lambda naming convention) — a single fixed rule, applied identically by every one of the 9 CI/CD jobs, with zero per-Lambda exceptions and no environment branching. B was not adopted since this project has no multiple-environment requirement to justify the added indirection; C was considered and rejected as still requiring a manual step (add a mapping row) per new Lambda — the same forgettable-step shape as v1's actual bug, just centralized rather than scattered.

**Worked example (full naming table for all 8 Lambdas plus DynamoDB/state-machine/bucket resources) recorded in `LOCKED_TECH_DECISIONS.md`.**

**Product inputs:** `P-95` (region choice — parameterise or the region is expensive to reverse; the naming/module conventions here don't change this, but any hardcoded region reference would repeat the same class of drift this whole decision exists to prevent).

**Decided by the user, final.**

---

## Agenda area 7 — Observability, IAM granularity, CORS, secrets

### `T-07` — Observability, IAM granularity, CORS, secrets

**RULED 2026-08-09, four sub-decisions: observability, IAM granularity, CORS, secrets.** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning.

**Question (observability):** how much to actually wire up of the Powertools observability surface (`T-01` already brought the dependency in for routing) — v1 shipped Powertools/pydantic unused (`HANDOFF.md` §7), and separately shipped alarms with no SNS subscription and a hardcoded, drift-prone alarm list. `HANDOFF.md` §9 names "actually wire up Powertools structured logging/tracing this time, or consciously stick with print-based logging" as a fork point to decide deliberately.

**Sub-decision — logging.**

**Options considered:**
- **A — Keep plain `print()`** (v1's approach). Zero setup; CloudWatch still captures it, but only as unstructured text — cross-Lambda correlation (e.g. reconstructing one `jobID`'s path across all 8 Lambdas) means manually cross-referencing timestamps across 8 separate log groups.
- **B — Powertools `Logger` (structured JSON).** A few lines of setup, no new dependency (already shipped for `T-01`'s routing). Every log line carries request id, function name, cold-start flag, plus explicit fields (`jobID`, `eventID`, `photoID`). CloudWatch Logs Insights becomes queryable by field.

**Ruled: B.** The marginal cost is near-zero since Powertools is already a dependency — unlike v1, where it sat unused specifically because nothing forced adoption.

**Sub-decision — what gets logged.**

**Options considered:**
- **A — `log_event=True`.** Powertools convenience decorator that auto-logs the entire incoming request (full body, headers) on every invocation, zero code needed.
- **B — Log only explicitly-named fields.** More typing per call; nothing reaches the logs unless a developer deliberately adds it.

**Ruled: A**, against the recommendation (B was recommended, given the `Profile` Lambda's request body carries the `P-19` selfie and `P-68` already treats that selfie as sensitive enough to be user-deletable on demand). **Design obligation attached as a direct consequence:** CloudWatch log retention set to **3 days** per Lambda (CloudWatch's own default is indefinite retention) — decided in the same exchange, specifically because A means sensitive request data (selfie bytes, auth tokens) now lands in every Lambda's logs by default.

**Sub-decision — tracing (X-Ray).**

**Options considered:**
- **A — Skip X-Ray**, rely on structured-log `jobID` correlation only. To diagnose a slow multi-Lambda batch, reconstruct the timeline from log timestamps by hand.
- **B — Powertools `Tracer` / X-Ray.** A visual, per-hop timeline across all 8 Lambdas for a single request/job. Low marginal cost (free tier covers this project's scale; a couple of decorator lines), but is a service that has to actually be looked at, or it repeats v1's "wired but never used" pattern.

**Ruled: A**, against the recommendation (B was recommended, given the pipeline's shape — one request fanning out across 8 Lambdas — is exactly what tracing is built for). Ruled on cost/effort grounds.

**Sub-decision — custom metrics.**

**Options considered:**
- **A — AWS-default Lambda metrics only** (`Errors`, `Duration`, `Invocations`, `Throttles` — free, zero setup). `P-100`'s tolerated-failure-percentage stays a manual read of Step Functions execution history.
- **B — Add narrow custom metrics (Powertools `Metrics`)**, e.g. a per-batch `PhotosFailedPercent`, to make `P-100`'s threshold alarmable automatically. Only pays off as a prerequisite to an alarm actually watching it.

**Ruled: A.** Consistent with also ruling out X-Ray on cost/effort grounds — metrics were the smaller of the two remaining observability wins.

**Sub-decision — alarms: notification.** This is the direct fix for `HANDOFF.md` §7's "no SNS topic was attached to any CloudWatch alarm — alarms existed but nothing was subscribed."

**Options considered:**
- **A — Alarms with no SNS subscription** (repeats v1's exact setup — a flipped alarm state nobody sees).
- **B — Every alarm wired to an SNS topic, with an email subscribed.** One topic, one subscription; a broken pipeline produces an actual email instead of a console state nobody checks.

**Ruled: B.**

**Sub-decision — alarms: avoiding the hardcoded-alarm-list bug.** `HANDOFF.md` §7: *"the monitoring module's per-Lambda alarm list was hardcoded in root `main.tf` rather than derived from the functions module's outputs — new Lambdas silently get no alarm."*

**Not a fresh choice — already closed by `T-06`.** `T-06`'s per-Lambda module layout gives each Lambda its own `cloudwatch.tf`, living inside that Lambda's own folder alongside `lambda.tf`. Creating a new Lambda module means its alarm definition ships with it by construction — there is no separate centralized list that can silently fall out of sync. Flagged explicitly rather than assumed, and confirmed with the user.

**Sub-decision — alarm content.** **Ruled (recommendation accepted without change): `Errors > 0` over a 5-minute evaluation window, identical shape on all 8 Lambdas**, using the AWS-default `Errors` metric from the metrics sub-decision above. Deliberately narrow — no duration or throttle alarms — matching `P-81` (alarms are operator-only, nothing here is ever user-facing) and the same minimalism already applied to metrics.

**Product inputs:** `P-81` (alarms/observability are operator-only, never surfaced to users); `P-19`/`P-68` (profile selfie — the concrete sensitive data driving the logging-retention decision); `P-100` (the tolerated-failure-percentage that custom metrics would have made alarmable, if ruled).

**Sub-decision — IAM granularity.** `HANDOFF.md` §7: *"several IAM roles were missing a specific permission discovered only at runtime... strict one-role-per-Lambda is good for security but created real iteration friction."* `HANDOFF.md` §9 names this as a fork point to decide deliberately.

**Options considered:**
- **A — Strict one-role-per-Lambda, hand-written permissions** (v1's exact approach). Tightest security; whatever a developer forgets to anticipate surfaces as a runtime `AccessDenied`, not a build-time error.
- **B — Start broader within a service boundary, tighten before launch.** Fewer runtime surprises during development; real risk that "tighten before launch" quietly never happens, echoing `HANDOFF.md` §7's `AdministratorAccess`-on-Terraform-user item, flagged as "tighten later" and never tightened.
- **C — Strict one-role-per-Lambda, but the policy is derived from the code rather than hand-guessed.** `HANDOFF.md` §7 names this directly: *"writing IAM policies test-first against actual code paths, or generating them from a manifest of each Lambda's actual AWS calls."* Same tight end-state as A; the permission list is checked against a concrete manifest of each Lambda's actual AWS calls instead of guessed from memory.

**Ruled: C.** The only option that answers `HANDOFF.md`'s diagnosis directly rather than repeating it (A) or trading it for a different, historically-proven-to-linger risk (B).

**Sub-decision — CORS.** `HANDOFF.md` §7: *"CORS was hardcoded to `*`... despite an `app_urls` Terraform variable that implied origin-restriction was intended but never wired through."*

**Options considered:**
- **A — Keep `*`** (repeats v1's actual shipped behavior). Zero configuration; any website's JavaScript can read API responses from a logged-in user's browser (auth still gates the underlying data — CORS is a separate layer, not the only one).
- **B — Restrict to the real frontend origin(s)**, using the `app_urls`-style variable v1 already had but never connected. Small to wire up — not new infrastructure, just actually reading a variable that already half-existed. Local development origins (e.g. `localhost`) need to be added to the allowed list too.

**Ruled: B.**

**Sub-decision — secrets hygiene.** `HANDOFF.md` §6 records two concrete incidents: a real CloudFront private key committed as a PEM file despite docs claiming SSM-only storage, and a live AWS access-key CSV + OAuth secret sitting in plaintext scratch files. `HANDOFF.md` §9 names the fix directly: *"exactly the kind of gap a pre-commit secret scanner... would have caught — worth deciding whether to add one from commit #1."*

**Options considered:**
- **A — No automated scanner; rely on discipline** (`.gitignore`, remembering not to commit keys) — v1's actual approach, and v1's own repo is the counterexample: `.gitignore` existed and the private key was committed anyway.
- **B — A pre-commit secret scanner (`gitleaks`) from the first commit.** Runs automatically before any commit completes; catches AWS-key-shaped and PEM-shaped content before it reaches git history, not after. One-time setup.

**Ruled: B.** Cheapest ruling on the whole agenda, against two incidents that actually happened in this project's own history, not hypothetical ones.

**Product inputs (IAM/CORS/secrets):** none beyond `HANDOFF.md` §6/§7/§9 directly — these three are infrastructure-hygiene rulings with no `P-nn` dependency.

**Decided by the user, final.**

---

## Agenda area 8 — Testing approach and CI/CD

### `T-08` — Testing approach and CI/CD

**RULED 2026-08-09, seven sub-decisions.** See `LOCKED_TECH_DECISIONS.md` for the tight answer and `TECH_EXPLANATIONS.md` for the reasoning. Checked against `HANDOFF.md` §8 (v1's testing approach, described in full) and §7/§9 for the specific failure modes it should close rather than repeat.

**Sub-decision — testing pyramid shape.**

**Options considered:**
- **A — Keep v1's 3-tier shape**: unit → integration → E2E. Highest coverage of failure modes across the whole stack, highest build/maintain cost.
- **B — 2-tier**: unit + E2E only, no separate integration tier. Cheaper, but wiring bugs between a single Lambda's own internal layers (`handler → manager → dao`) only surface at E2E, which is slower and costs real Rekognition money to iterate against.
- **C — unit only.** Cheapest, but catches neither internal wiring bugs nor real-deployment bugs (auth wiring, Terraform-provisioned resources actually working).

**Ruled: A.** Matches v1's own shape, already flagged in the agenda as worth reusing, and the pipeline's real multi-step wiring (`T-02`'s Distributed Map) is exactly the kind of bug a missing integration tier would let through.

**Sub-decision — unit test mocking library.**

**Options considered:**
- **A — `moto`** (v1's approach). Monkey-patches `boto3` so AWS calls are redirected to an in-memory fake that simulates real AWS behavior (error shapes, not-found semantics) — no network, no Docker, free. Covers Rekognition.
- **B — Hand-written `unittest.mock`.** No behavior simulation; the test author must already know and hardcode what AWS would actually do, which risks testing an assumption rather than real behavior.
- **C — LocalStack.** A Dockerized set of real HTTP servers imitating AWS services, closer to real behavior than `moto` for DynamoDB/S3 — but Rekognition's `IndexFaces` is LocalStack-Pro-only (paid), and this project leans on Rekognition more than any other service.

**Ruled: A.** Matches v1, free, no Docker requirement, and the one AWS service this app depends on most (Rekognition) isn't covered by LocalStack's free tier anyway — C would still need `moto` or hand-mocking for that part regardless.

**Sub-decision — explicit failure-path test list.** v1 named specific failure scenarios to test deliberately, not just happy paths (`HANDOFF.md` §8). Carried forward, adapted, or dropped as follows:

| v1's test | Ruling |
|---|---|
| Corrupted ZIP drives the pipeline to `FAILED` | Kept as-is — extraction step unchanged |
| Forced-failing message → DLQ → `COMPLETE_WITH_ERRORS` | **Adapted.** `T-02` replaced SQS+DLQ with Step Functions Distributed Map — no DLQ exists anymore. Equivalent: one deliberately-bad photo in a batch fails only that item (`ToleratedFailurePercentage` not exceeded), the execution still completes, and the per-item failure appears in the Distributed Map's S3 result output — same intent as v1's `COMPLETE_WITH_ERRORS`, new mechanism |
| Rate limiter blocks the 11th search | **Dropped.** `P-16` removed search as a user action entirely |
| Direct S3 GET on a private object fails | Kept as-is |
| Expired signed URL fails | Kept as-is |
| Unauthenticated calls get 401, cross-role calls get 403 | Kept as-is (`P-07`) |
| *(new)* Each Lambda's IAM policy matches its manifest of actual AWS calls | **Added.** `T-07` ruled IAM permissions derive from a per-Lambda manifest rather than being hand-guessed — without a test enforcing the two stay in sync, the manifest can drift from the code exactly the way `HANDOFF.md` §7's "permission missing, discovered only at runtime" happened in the first place |

**Testing compromise carried forward, not silently:** v1 verified `COMPLETE_WITH_ERRORS` by code review only, not a live test, since forcing Rekognition to fail mid-flow was judged impractical in a dev environment. The adapted Distributed Map version has the same practicality problem — same compromise accepted here.

**Sub-decision — integration test scope.**

**Options considered:**
- **A — one Lambda's full internal chain (`handler → manager → service/dao`), `moto`-backed**, invoked as a single unit the way API Gateway/Step Functions would call it, only the AWS boundary faked.
- **B — cross-Lambda chaining** (invoke one Lambda's handler for real, feed its real output into the next Lambda's handler in the same test). Closer to true integration, but Step Functions already guarantees the data handoff shape between states — largely re-testing a guarantee the orchestration layer already provides, for a lot of extra test-maintenance cost.
- **C — skip a distinct integration tier**, fold into E2E. Cheaper to build, but wiring bugs then only get caught against the real deployed stack.

**Ruled: A.**

**Sub-decision — E2E test environment and frequency.**

**Options considered (environment):**
- **A — a dedicated test event, created and torn down by the test itself**, inside the project's single AWS account (no separate dev/prod split exists — `T-05`/`T-06` never introduced one). A real `Event`, a real Rekognition collection, a few real photos, deleted at the end of the run.
- **B — a long-lived shared test event**, created once, reused across runs. Less teardown code, but risks state leaking between runs (a previous run's leftover photo throwing off a count-based assertion).

**Ruled: A.**

**Options considered (frequency):**
- **A — every Jenkins run.** Maximum safety net, but multiplies real Rekognition spend by every ordinary commit, given `T-06` already committed to 9 Jenkinsfiles firing on regular work.
- **B — manual only**, kept out of the automatic Jenkins jobs, run by hand before something that matters. Matches v1's own description of E2E as "a handful of high-value journeys," not a constantly-run suite.

**Ruled: B.**

**Sub-decision — CI/CD wiring: do tests run inside the 9 Jenkins jobs `T-06` already set up?**

**Options considered:**
- **A — tests run as a required step before deploy in each of the 8 per-Lambda Jenkinsfiles; failure stops the pipeline.** Matches `HANDOFF.md`'s "deployments are always intentional" philosophy already established in `T-06`.
- **B — tests run and report, but don't block deploy.** Relies on a human reading Jenkins output.
- **C — tests are not part of any Jenkinsfile at all**, run locally by the developer before pushing; Jenkins is triggered only once local tests already pass, and functions purely as a deploy mechanism, not a test gate.

**Ruled: C**, against the recommendation (A was recommended, on the grounds that C means a broken Lambda can deploy if the developer skips or forgets local testing, with nothing in Jenkins to catch it — under A, Arjun's real upload would still hit last-known-good code even after a broken push; under C it wouldn't). User's process: test locally first, only push to trigger a Jenkins deploy once local tests pass.

**Untargeted-apply job:** stays independent of the 8 Lambda jobs' pass/fail, as `T-06` already ruled — manual "Build Now," not gated on anything (not a fresh decision, confirmed unchanged).

**Sub-decision — formal coverage requirement.**

**Options considered:**
- **A — a coverage number, checked locally with `pytest-cov`** (e.g. an 80% line-coverage target). Concrete signal, but a weak proxy — full coverage of a function that never exercises its own error branch still "passes."
- **B — no formal number.** The named failure-path list (above) is the real substance; coverage beyond that is a judgment call each time, not a tracked metric.

**Ruled: B.** Consistent with testing already being fully self-disciplined (no CI gate per the wiring ruling above) — a tracked percentage adds bookkeeping without changing what actually gets tested.

**Product inputs:** none beyond `HANDOFF.md` §7/§8/§9 directly — testing/CI-CD is process, not a `P-nn`-dependent ruling.

**Decided by the user, final.**

---

## Decision log

| Date | `T-nn` | What happened |
|---|---|---|
| 2026-08-08 | `T-01` | Ruled **A — all Python**. B (all Node) eliminated early on HEIC. C (Node/TS + isolated Python HEIC Lambda) considered and rejected once middy and DynamoDB Toolbox — the main reasons to prefer Node — were separately ruled unnecessary for this project's shape. |
| 2026-08-08 | `T-02` | Ruled **Step Functions Distributed Map** over SQS + DLQ. Departs from v1's choice deliberately — v1's own reasoning for SQS ("more advanced to configure and debug") is outweighed here by removing a hand-rolled polling loop and getting per-item visual execution history. Two load-bearing build notes attached: item list via S3 `ItemReader` (not passed state-to-state), and `MaxConcurrency` as a Terraform variable tied to the account's real Rekognition quota. |
| 2026-08-08 | `T-03` | Ruled **domain-grouped API Lambdas (C)** over one-per-endpoint (A) or fully consolidated (B) — 5 API Lambdas scoped by table, extends `T-02` with 4 named pipeline Lambdas, plus two shared utility Lambdas: HEIC→JPEG converter (called from `Extract` and `Profile`) and `db-api` (generic `Jobs`-status writer, called from 4 pipeline states, deliberately a separate Lambda rather than a shared code library — user's explicit choice, with the failure-mode tradeoff named). 11 Lambdas total. *(Superseded same day — see row below.)* |
| 2026-08-08 | `T-03` | **Revised**, same day: the 4 named pipeline Lambdas consolidated into 1 (`PipelineHandler`), differentiated internally by a `step` field rather than by separate functions. Raised while working through `T-06`'s Terraform module layout. The "wide IAM role = wide blast radius" reasoning that ruled out fully-consolidating the *API* Lambdas doesn't transfer here, since pipeline Lambdas have no external invocation path — only Step Functions ever calls them. Total Lambda count: **8** (5 API-facing, 1 pipeline, 2 shared utility). |
| 2026-08-08 | `T-04` | Ruled **A — multi-table (6 tables)** over single-table design (B). Decided on IAM grounds: `T-03` already scoped each Lambda's role to one table, which is structural under multi-table and would need hand-built key-prefix conditions under single-table. Table count drops from v1's 7 to 6 — `SearchRateLimit` dropped, since `P-16` removed search as a user action. Exact per-table fields/GSIs left as a following sub-decision. |
| 2026-08-08 | `T-05` | Ruled **A — one Rekognition collection per event** over one shared account-wide collection (B). Decided on security-boundary grounds: `P-07`'s "no cross-event visibility" is enforced by AWS itself under A (a search can't reach another event's collection) versus entirely by application-code filtering under B. Collection id tracked on the `Events` table for teardown, since Terraform can't see runtime-created collections. |
| 2026-08-08 | `T-06` | Ruled, five sub-decisions: **(1)** S3 state backend + native locking (`use_lockfile`), no DynamoDB, versioning on. **(2)** per-Lambda Terraform module layout (user-originated), replacing v1's single centralized `functions` module. **(3)** deploy discipline — a separate dedicated CI job runs the untargeted `apply` that builds/updates the state machine; every Lambda's own Jenkinsfile stays targeted, over piggybacking on one Lambda's pipeline (rejected — indirect trigger, easy to forget) or decoupling via `data` lookups (rejected — reintroduces `HANDOFF.md` §7's drift risk). **(4)** CI/CD granularity — 8 per-Lambda Jenkinsfiles + 1 dedicated untargeted-apply job = 9 total; only resources with actual code get a pipeline. **(5)** naming — fixed `glimpses-` prefix applied identically everywhere, no environment branching, no per-Lambda mapping file; folder name is the single source of truth. |
| 2026-08-09 | `T-07` | Ruled, four sub-decisions. **Observability:** Powertools structured `Logger` (B over plain `print()`); `log_event=True` — full request auto-logged (A over selective-field logging, against recommendation); 3-day log retention added as a direct consequence; no X-Ray (A, against recommendation, cost/effort); no custom metrics (A, AWS defaults only); every alarm wired to SNS + email (B, fixes v1's silent-alarm bug); hardcoded-alarm-list bug confirmed already closed by `T-06`'s per-Lambda `cloudwatch.tf`; alarm content `Errors > 0`/5min, all 8 Lambdas alike. **IAM granularity:** strict one-role-per-Lambda, policy derived from a per-Lambda manifest of actual AWS calls (C, over hand-guessed A or broaden-then-tighten B). **CORS:** restricted to real frontend origin(s) (B), `app_urls` variable actually wired through instead of v1's unused `*`. **Secrets:** pre-commit `gitleaks` scanner from commit #1 (B), directly answering `HANDOFF.md` §6's two real incidents. |
| 2026-08-09 | `T-08` | Ruled, seven sub-decisions. **Pyramid shape:** 3-tier, unit + integration + E2E (A, matches v1). **Unit mocking:** `moto` (A, matches v1; LocalStack's free tier doesn't cover Rekognition). **Explicit failure-path list:** four of v1's tests kept as-is, the DLQ/`COMPLETE_WITH_ERRORS` test adapted to `T-02`'s Distributed Map per-item-failure equivalent, the rate-limiter test dropped (`P-16` killed search), an IAM-manifest-drift test added (closes `T-07`'s manifest approach against silent drift). **Integration scope:** single Lambda's full internal chain, `moto`-backed (A), not cross-Lambda (B, redundant with Step Functions' own guarantees) or folded into E2E (C). **E2E:** dedicated test event created/torn down per run (A, not a shared long-lived one); manual-only, not run on every Jenkins job (B, cost control on real Rekognition spend). **CI/CD wiring:** tests are not part of any Jenkinsfile (C, against recommendation A — tests gate deploy); user tests locally, only pushes to trigger a Jenkins deploy once local tests pass; the untargeted-apply job stays independent, unchanged from `T-06`. **Coverage:** no formal number tracked (B) — the named failure-path list is the real substance. |
| 2026-08-09 | `T-03` (follow-up) | API Gateway flavour, left open at the original `T-03` ruling, picked back up post-agenda. Ruled **B — REST API** over HTTP API (A), specifically for AWS WAF's edge-level protection against Rohan's named adversarial threat model (`P-07`) — accepting REST API's 3.5x-higher per-request cost ($3.50/million vs $1/million). Cognito-auth outcome is identical either way (User Pool authorizer vs JWT authorizer both check the same token). Flagged and resolved a real drift risk in passing: `T-01`'s `APIGatewayRestResolver` naming turned out to already match this ruling, not an accidental default. |
