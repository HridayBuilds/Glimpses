# CLAUDE.md

## Project: Glimpses — start here

**Read `Miscellaneous/SESSION_HANDOFF.md` before doing anything.** It carries the current state, what's next, and how this project is run.

Glimpses is a from-scratch rebuild of a torn-down v1 — an event photo-sharing app with face-recognition search on AWS. The product was locked feature-by-feature *before* any technology was chosen.

**As of 2026-08-12 the technology phase is fully closed and implementation has begun.** The product is locked at 100 rulings (`P-01`–`P-100`), the technology phase's 8-item agenda is fully ruled (`T-01`–`T-08`), and both loose threads left inside already-ruled items are closed too: `T-03`'s API Gateway flavour (REST API, for WAF) and `T-04`'s per-table fields/PK-SK/GSI definitions for all 6 tables — `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`. Ruling `Events` surfaced a real gap (no Lambda had IAM reach for full event teardown), closed by adding a 9th Lambda, `EventTeardown` — which amends `T-03`'s Lambda count and `T-06`'s CI/CD job count. The same gap shape recurred on `Faces`: photo deletion needed reach no existing Lambda had, closed by reusing that same Lambda rather than adding a 10th — renamed `CascadeDelete` since it's no longer event-only. A third, different-shaped gap surfaced scoping `EventAttendees`: nothing in the pipeline actually ran the per-attendee `SearchFaces` fan-out `P-16`/`P-93` require, and nothing stored its result — closed by adding `MatchAttendees`, a new Distributed Map step on the existing `PipelineHandler` state machine (no new Lambda), writing each attendee's matched `photoID`s as a String Set (`matchedPhotoIDs`) onto their `EventAttendees` row. `EventAttendees`'s three remaining sub-questions are also ruled: (1) status is a 4-value field (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`), the row is never deleted, leave/eject/deny are status flips in place; (2) one GSI, `eventID` PK + `status` SK, serves the organizer's roster/lobby and `MatchAttendees`' own "who's admitted" lookup; (3) `CascadeDelete` does not scrub `matchedPhotoIDs` on photo delete — a stale id is filtered out for free at read time.

**Implementation is now in progress.** AWS/Terraform environment bootstrap is done and logged step-by-step in `Miscellaneous/SETUP_STEPS.md`: IAM user `glimpses-terraform`, local CLI profile `glimpses`, Terraform 1.15.8, the `glimpses-terraform-state` S3 bucket (versioned, public access blocked), `infrastructure/providers.tf`/`variables.tf` written, `terraform init` succeeded. Real per-service quota found and recorded: this AWS account's actual Rekognition `IndexFaces` TPS is **5**, not the published default of 50 — `T-02`'s `rekognition_index_max_concurrency` variable will be set accordingly. **`infrastructure/modules/dynamodb/` is built** — all 6 tables, one `.tf` file per table, `PAY_PER_REQUEST`/`ALL`-projection GSIs/`Events`' `OLD_IMAGE` stream all confirmed, wired into root `imports.tf`, `terraform validate` passing (provider bumped `~> 5.0` → `~> 6.0` on 2026-08-13, GSI syntax updated `hash_key`/`range_key` → `key_schema` blocks accordingly, no schema change). **`T-06`'s CI/CD job split is ruled** (2026-08-13): the untargeted-apply job is now two, `dynamodb` and `state_machines`, fixed run order `dynamodb` → all 9 Lambda jobs → `state_machines` (job count 10 → 11) — because the tables must be created **by the `dynamodb` Jenkins job, not a manual local `apply`**, per the user's explicit instruction. **Jenkins found already installed locally** (Homebrew `jenkins-lts`, not running) with one stale v1-era job, removed; the `dynamodb` job is set up (`infrastructure/modules/dynamodb/Jenkinsfile`, one `Jenkinsfile` per module — not a shared `cicd/` folder) but its first run failed on an SSH-over-443 network issue reaching GitHub. **Blocked on:** finishing the SSH→HTTPS+PAT remote switch for that job, then starting Jenkins and running the `dynamodb` job for real. Full detail and exact next action in `Miscellaneous/SESSION_HANDOFF.md`'s top entry — read it before doing anything.

**Three new working files exist, each a `<NAME>.md` in its own top-level folder, being filled in incrementally by the user, piece by piece — do not write to them speculatively, only what's been explicitly given so far:** `Backend/BACKEND.md` (still 0 bytes as of 2026-08-15 — the per-Lambda folder shape has been decided conversationally, not yet written into the file itself; see the `heic_converter` entry below and `SESSION_HANDOFF.md`'s top entry for the real shape in use), `Frontend/FRONTEND.md` (not yet discussed), `infrastructure/INFRASTRUCTURE.md` (not yet filled — user will specify later).

**First Lambda, `heic_converter`, built 2026-08-15 — full detail in `SESSION_HANDOFF.md`'s top entry.** Confirmed folder shape for all 10 Lambdas going forward: `src/` is a 5-layer chain, `routeHandler.py` (thin, actual Lambda entry, Powertools-logged) → `Handler/handler.py` → `Manager/manager.py` → `Converter/converter.py` (or `procedure`/`dao`-named equivalent per Lambda) → `DAO/dao.py`, each layer in its own same-named folder — **the `Converter`-equivalent layer is optional and collapses away when a Lambda has no pure-computation step, giving a 4-layer chain instead (confirmed building `db_api` below)**; `test/unit/` + `test/integration/` (`moto`-backed); `infra/` per `T-06`'s module layout; **`cicd/Jenkinsfile`** — a per-Lambda `cicd/` folder, the user's deliberate call, diverging from the `dynamodb`/`state_machines` precedent of putting `Jenkinsfile` inside `infra/`. Both `heic_converter` unit and integration tests actually ran (real `pillow-heif`/`moto` install in a scratch venv) and passed. **`heic_converter/infra/lambda.tf`'s deploy-discipline bug is now fixed, 2026-08-15** — the `local-exec` pip install and `archive_file` were removed; `aws_lambda_function.this` now points at the shared `glimpses-deploy-artifacts` bucket with `lifecycle { ignore_changes = [s3_key, source_code_hash] }`, matching `T-06` exactly, and `cicd/Jenkinsfile` gained the real build/zip/push/update-function-code stages. Not yet wired into root `infrastructure/imports.tf`: `infra/input.tf` takes `photos_bucket_arn`, `alarm_sns_topic_arn`, and `deploy_artifacts_bucket` as required variables with no real value yet, since none of the photos S3 bucket, the shared alerting SNS topic (`T-07`), or the deploy-artifacts bucket exist in Terraform yet.

**Second Lambda, `db_api`, built 2026-08-15 — full detail in `SESSION_HANDOFF.md`'s top entry.** A genuine 4-layer chain (no `Converter`-equivalent — `db_api` has no pure-computation step), built deploy-discipline-correct from the start (no `local-exec`/`archive_file` ever written). Owns `Jobs`: `create` and `update_status` actions, IAM-scoped to `PutItem`/`UpdateItem` only (never reads). Building it surfaced and closed two real gaps: (1) confirmed the 4-layer-chain reading above; (2) `Jobs`' undefined retry/backoff field was dropped **at the product level**, not just the schema — `P-100`/`P-56` were formally rewritten as `D-127` in `LOCKED_PRODUCT.md`, removing the retry-visibility promise `D-126` had added, per this file's own one-directional rule (technology surfaced the cost, the user ruled on product). All 5 tests (4 unit, 1 integration) pass; a real `moto` test-isolation bug was found and fixed along the way — a module-level DynamoDB client/table object can be created before a test's `@mock_aws` context is active and silently bypass the mock, so every Lambda's `DAO` layer should build its AWS client/resource **lazily, per call, not cached at module level**. Same wiring gap as `heic_converter`, plus one more: not yet in root `infrastructure/imports.tf`, and additionally needs `Jobs`' real table ARN from the `dynamodb` module's outputs, not yet passed through.

**Third Lambda, `download`, built 2026-08-15 — full detail in `SESSION_HANDOFF.md`'s top entry.** 4-layer chain, same reasoning as `db_api`: the zip-build step is inherently S3 reads/writes, not a pure computation separable into its own layer, so it lives in `Manager` (orchestration) with every boto3 call in `DAO` (built lazily, per the `db_api` `moto` lesson). Three actions on one Lambda, since the ruled design (`LOCKED_TECH_DECISIONS.md` §3/§9) requires a synchronous kickoff, a backgrounded build, and a synchronous status poll to all be the same function: `kickoff` (from `POST /events/{eventId}/photos/download`, writes a `PENDING` `Downloads` row, then asynchronously self-invokes with `InvocationType=Event` — needed a new IAM grant, `lambda:InvokeFunction` on its own ARN, the first Lambda to need one) → `build` (self-invoked only, never called from API Gateway; streams each photo from S3 into a zip via the `stream-zip` library using `NO_COMPRESSION_64`/`STORED`, multipart-uploading part-sized chunks to S3 as it goes so the full archive is never buffered, then flips the row to `READY`/`FAILED`) → `status` (from `GET .../downloads/{downloadId}/status`, reads the row and mints a pre-signed `GET` once `READY`). **The `Downloads` DynamoDB table did not exist anywhere in Terraform yet, so it was added to `infrastructure/modules/dynamodb/` (`downloads.tf`, PK-only `downloadId`, no GSI, matching the ruling) as part of this build** — `terraform validate` passes on both the `dynamodb` module and root `infrastructure/`. All 7 tests (6 unit, 1 integration — the integration test builds a real zip via `moto`-mocked S3 multipart upload and unzips it to verify contents) actually ran in a scratch venv and passed. `infra/` built deploy-discipline-correct from the start; IAM is scoped to `Downloads` (read/write) + `Photos` (read-only, `GetItem`/`BatchGetItem`/`Query`) + the shared `glimpses-photos` bucket, prefix-scoped per `T-09` (`photos/*` read-only, `downloads/*` read+write — never `uploads/`/`selfies/`/`thumbnails/`/`qrcodes/`) + self-invoke. Same wiring gap as the other two: not yet in root `infrastructure/imports.tf`, still needs `deploy_artifacts_bucket`/`alarm_sns_topic_arn`/the photos bucket's real ARN, none of which exist in Terraform yet.

**All three Lambdas wired into root `infrastructure/imports.tf`, 2026-08-15 — full detail in `SESSION_HANDOFF.md`'s top entry.** Wiring surfaced that the shared resources all three Lambdas depended on didn't exist in Terraform yet, so three new modules were built first: `infrastructure/modules/buckets/` (`glimpses-deploy-artifacts` + `glimpses-photos`, the latter with a lifecycle rule expiring `downloads/` after 48h), `infrastructure/modules/alarms/` (the `T-07` SNS topic + email subscription, taking `alarm_email` as a required variable — **still not supplied**), `infrastructure/modules/cloudfront/` (OAC + distribution + the bucket-policy scoping `s3:GetObject` to `photos/`/`thumbnails/`/`qrcodes/` only, per `T-09`). Built as **three separate modules and three separate Jenkins jobs, not one bundled "shared" module** — the user explicitly rejected that bundling ("keep things separate as it helps understanding") even though `dynamodb`/`buckets`/`alarms` could technically share one untargeted apply. Every module/Lambda's Jenkinsfile now lives inside a `cicd/` subfolder, including `dynamodb`'s, which was retroactively moved there from its module root. **CI/CD job count 12 → 15**; fixed run order `dynamodb`/`buckets`/`alarms` (mutually independent) → `cloudfront` (needs `buckets`' outputs) → all 10 per-Lambda jobs → `state_machines`. Root `terraform fmt -check -recursive` clean, `terraform init` succeeded, `AWS_PROFILE=glimpses terraform validate` passes across all 7 modules. **Two loose ends flagged, not yet resolved:** the local Jenkins `dynamodb` job's `config.xml` (outside git) still points at the old pre-move Jenkinsfile path and needs manual updating; `alarm_email` has been asked for twice and still has no real value.

**All three gaps surfaced building `heic_converter` are now CLOSED, 2026-08-15.** Gap 1 (full REST endpoint paths) is fully ruled (`LOCKED_TECH_DECISIONS.md` §3, reasoning in `TECH_EXPLANATIONS.md` §9). Closing it surfaced a real architectural addition: a **10th Lambda, `download`**, and a **7th DynamoDB table, `Downloads`** — photo download split into a no-server-work pre-signed-URL path (stays on `Gallery/photos`) and a real server-side ZIP-build path, which needed its own Lambda to avoid breaking `T-04`'s one-table-per-Lambda IAM isolation (same shape of gap that originally produced `CascadeDelete`). `download` runs as a plain async Lambda invocation (not Step Functions — no per-item throttle to coordinate), streams objects into a zip without buffering the whole batch, and is IAM-scoped to `Downloads` (read/write) + `Photos` (read-only) + S3. Lambda count 9→10, tables 6→7, CI/CD jobs 11→12.

Gaps 2 and 3 (S3 bucket/key layout, ingestion trigger) turned out to be coupled and were ruled together the same day as a new agenda item, **`T-09`** (`LOCKED_TECH_DECISIONS.md` §9, reasoning in `TECH_EXPLANATIONS.md` §10): **one S3 bucket, `glimpses-photos`, six prefixes** — `uploads/`, `photos/`, `thumbnails/`, `selfies/`, `qrcodes/`, `downloads/` — with a fully server-determined key under each (this now defines `Photos.s3Key`, previously an undefined-shape field, and the `download` Lambda's zip key). **CloudFront, via Origin Access Control, reads only `photos/`/`thumbnails/`/`qrcodes/`** — the bucket policy's `Resource` scoping is the actual enforcement boundary, not folder naming, so `uploads/`, `selfies/`, and `downloads/` stay unreachable through CloudFront even if a path is guessed; `selfies/`'s exclusion is a product requirement too, since `P-15`/`P-82` make selfies invisible to everyone including the organizer. Everything outside those three prefixes moves only through Lambda-issued pre-signed URLs — including a pre-signed `GET` for the *owner's own* selfie on `GET /profile`, since `P-82` only hides selfies from other people, not from their own owner. **`ingestion` is started by an S3 Event Notification routed through EventBridge straight to `StartExecution`** — no glue Lambda, no client "upload complete" callback (rejected: it fails `P-100`'s own scenario, since a browser tab closing between the `PUT` finishing and a second callback call would silently strand the batch, which an S3-native event can't do). One real behavior change fell out of this: because the trigger needs one S3 object per batch, **multi-file selections are now zipped client-side before upload**, same as a ZIP upload.

**The one-directional rule — this phase's version of the non-negotiable.** Product constrains technology; **technology never re-rules product.** If a stack choice makes a `P-nn` awkward or expensive, surface it as a revision request for the user to rule on. Never resolve it in the implementation. v1 failed exactly here: React 18 planned and 19 shipped, FastAPI taught and never used, Powertools shipped in the Lambda layer and never wired, CORS restriction implied by a Terraform variable and never enforced — **every one of those was decided by drift, which is what this rebuild exists to prevent.**

**`HANDOFF.md` is no longer historical-only — it is now a working input.** §7 is v1's mistake ledger (dead dependencies, silent alarms, two unresolved bugs, IAM friction found at runtime) and §9 lists eight fork points v1 actually hit. Check every technology decision against both. Do not re-derive them and do not repeat them by omission.

**The user wants to understand before anything is implemented.** Stated 2026-08-06: *"i need to understand it all before implementing anything."* No code until the decisions behind it are ruled.

**The user commits; you never do.** Stated directly on 2026-08-06: *"all commits will be made by me only not u so pls do not push or commit anything."* Leave work as uncommitted working-tree changes and say what changed.

| File | Purpose |
|---|---|
| `Miscellaneous/SESSION_HANDOFF.md` | Current state, what's next, how to work with revisions |
| `Miscellaneous/PRODUCT_WALKTHROUGH.md` | The product described end-to-end, readable in one sitting — start here for review |
| `Miscellaneous/LOCKED_PRODUCT.md` | The spec — every ruled decision with full reasoning (`P-nn`) — source of truth |
| `Miscellaneous/HANDOFF.md` | v1 retrospective — **still a working input during implementation.** §7 mistakes, §9 fork points; keep checking new code against both |
| `Miscellaneous/LOCKED_TECH_DECISIONS.md` | The finalized technology answers, kept tight — what to build |
| `Miscellaneous/TECH_EXPLANATIONS.md` | The concepts behind each `T-nn` — what it is, how it works, why it won — this is the learning material |
| `Miscellaneous/SETUP_STEPS.md` | Reproducible log of every one-time human-run environment setup step (IAM, CLI, Terraform, state bucket) — includes exact commands, errors hit, and fixes, doubles as troubleshooting notes |
| `Backend/BACKEND.md`, `Frontend/FRONTEND.md`, `infrastructure/INFRASTRUCTURE.md` | Working, incrementally-filled specs for each part of the actual build — only as complete as what the user has explicitly given so far |

**`PRD.md` and `TECH_DECISIONS.md` were deleted 2026-08-12** — both were working registers at 0 open items, fully superseded by `LOCKED_PRODUCT.md` and `LOCKED_TECH_DECISIONS.md`/`TECH_EXPLANATIONS.md` respectively (verified before deletion that rewrite history like `P-31`'s `D-99`→`D-117` chain is preserved inline in the locked files). Don't reference them as if they still exist.

**The non-negotiable rule: the user makes every decision.** Present options with honest tradeoffs and a recommendation, then wait. Never decide architecture silently or by implementation drift. In v1 the user let an AI dictate everything and ended up not understanding their own system — this rebuild exists to fix that. Explain concepts and syntax as you go; the user wants to understand, not just receive.

**How to explain:** plain language, no jargon, and run every option through **named concrete scenarios** before naming it abstractly — then summarise as a scorecard (options as rows, scenarios as columns). The user has asked twice for simpler explanations; this is the default, not a fallback. Recurring cast: **Meera** (attendee), **Arjun** (wedding photographer), **Priya** (collaborative trip organizer), **Rohan** (adversarial), **Sam** (self-deploys the repo from Terraform).

**Read the spec before describing it.** Never list a cascade from memory — grep the rulings. On 2026-08-06 a cascade given from recall was partly wrong, and one of the user's requests turned out to be **already built**, with the apparent conflict being nothing but a stale sentence. Some requests may need no change at all.

**Don't moralise about privacy.** The user asked directly for less of this on 2026-08-06: it inflates the write-up and manufactures cascade work the ruling never required. State a consequence in one line and move on. Keep *design obligations* — they stop earlier rulings being undone by drift — and cut the alarm.

**Revision convention:** a revised ruling **keeps its `P-nn` and is rewritten in place**, marked *(Rewritten YYYY-MM-DD by `D-nn`)*. Only a genuinely new question gets a new `P-nn`. Superseded decision-log rows are marked, never deleted. Ids are permanent; **recount statuses from table rows, never decrement.**

---

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.