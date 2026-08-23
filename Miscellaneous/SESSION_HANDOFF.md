# Session Handoff — Glimpses

**Written:** 2026-08-05, evening · **Updated:** 2026-08-18 *(condensed — see note at bottom. `Jobs.status` enum finalized as a two-way terminal, enum enforcement moved into `db_api`, state machine's terminal write repositioned to the true end of the pipeline. Resume prompt at the very bottom.)*

**Current phase:** Implementation. Product locked at 100 rulings (`P-01`–`P-100`), technology phase fully closed (`T-01`–`T-09`). 4 of 10 Lambdas built (`heic_converter`, `db_api`, `download`, `ingestion`), plus the `state_machine` module (non-Lambda) wiring `ingestion`'s steps together end-to-end, upload → matched photos. All 7 Terraform modules validate. Nothing has actually been `apply`'d/deployed to AWS yet outside the one-time bootstrap in `SETUP_STEPS.md`.

For full reasoning behind any ruling, read `LOCKED_TECH_DECISIONS.md` (tight answers + decision log) and `TECH_EXPLANATIONS.md` (the why, in plain language). This file tracks *build* history and *what's next* — it does not re-derive rulings.

---

## Current state, by area

**Terraform modules (all validate):** `dynamodb` (7 tables), `buckets` (`glimpses-deploy-artifacts` + `glimpses-photos`), `alarms` (`T-07` SNS topic + email sub, `alarm_email` defaults to the user's email), `cloudfront` (OAC scoped to `photos/`/`thumbnails/`/`qrcodes/`), `state_machine`, and one module per Lambda. Kept as **separate modules, separate Jenkins jobs** — the user's explicit call against bundling, "keep things separate as it helps understanding." CI/CD job count: 15. Fixed run order: `dynamodb`/`buckets`/`alarms` (independent) → `cloudfront` (needs `buckets`) → all 10 per-Lambda jobs → `state_machine`. Local Jenkins is Homebrew (`jenkins-lts`), not AWS-provisioned; per-module `cicd/Jenkinsfile`; actual job setup (Multibranch Pipeline, script paths) is the user's own responsibility, not something this repo automates.

**Lambda folder convention (all 4 built Lambdas follow this):** `src/routeHandler.py` (Powertools-logged entry) → `Handler/handler.py` → `Manager/manager.py` → optional `Converter/` (collapses away with no pure-computation step, e.g. `db_api`) → `DAO/dao.py` (every AWS client built **lazily, per call** — a `moto` test-isolation lesson from `db_api`: a module-level client can be created before `@mock_aws` is active and silently bypass the mock). Plus `test/unit/` + `test/integration/` (real `moto`, all currently passing), `infra/` (deploy-discipline-correct: Lambda code lives in the shared `glimpses-deploy-artifacts` bucket, `lifecycle { ignore_changes = [s3_key, source_code_hash] }`, Terraform never packages/ships code — Jenkins does), `cicd/Jenkinsfile`.

**`heic_converter`** (built 2026-08-15) — the only 5-layer Lambda (has a real `Converter` step). Converts HEIC→JPEG, invoked synchronously by `ingestion`'s `Extract`.

**`db_api`** (built 2026-08-15) — 4-layer, no `Converter`. Sole writer of `Jobs`. Originally `create`/`update_status`; **as of 2026-08-18, action-based**: `create`, `mark_extracting`, `mark_indexing`, `mark_matching`, `mark_success`, `mark_failed` — see "Jobs enum" section below. IAM scoped to `PutItem`/`UpdateItem` only, never reads.

**`download`** (built 2026-08-15) — 4-layer (zip-build is inherently S3 I/O, not pure computation, so it lives in `Manager`). Three actions on one Lambda: `kickoff` (sync, writes `PENDING` `Downloads` row, self-invokes async — first Lambda needing `lambda:InvokeFunction` on its own ARN) → `build` (self-invoked only, streams photos into a zip via `stream-zip`/`STORED`, multipart-uploads without buffering the full archive, flips row to `READY`/`FAILED`) → `status` (reads row, mints pre-signed `GET` once ready). Added the `Downloads` table (PK-only `downloadId`, no GSI) to the `dynamodb` module as part of this build.

**`ingestion`** (built 2026-08-17) — the deepest Lambda, Option A folder shape (per-step files inside one shared `Manager`/`Converter`/`DAO`, not sibling per-step chains) confirmed 2026-08-16 specifically because `MatchOneAttendee` reuses `MatchAttendees`' resolution logic directly. `Handler` branches on invocation shape: `{"step": ...}` (Step Functions) vs `{"Records": [...]}` (DynamoDB Stream). Six `Manager` files: `extract.py` (unzip, content-sniff format, content-hash dedup, HEIC convert via `heic_converter` invoke, PNG→JPEG via local Pillow — my own call to satisfy `T-09`'s unconditional `.jpg` key shape — thumbnail, writes `Photos` row incl. uploader snapshot per P-99), `index_one_photo.py` (`IndexFaces` on one photo, writes `Faces` rows, catches its own Rekognition errors so a bad photo is counted `FAILED` rather than aborting its Map item), `finalize.py` (pure arithmetic — **see "Jobs enum" below, this changed 2026-08-18**), `list_attendees.py` (queries `EventAttendees`' `eventID-status-index` for who's currently admitted — added building the ASL, since nothing else produced this list), `match_attendees.py` (batch-arrival fan-out: resolves each admitted attendee's selfie via `SearchFacesByImage`, resolves hits to `photoID`s via `Faces`' base-table `GetItem`, `ADD`s to `EventAttendees.matchedPhotoIDs`), `match_one_attendee.py` (thin wrapper, same resolution logic, triggered by the `EventAttendees` Stream filtered to `status` transitioning onto `ATTENDEE` — covers late admits/joins/rejoins the batch-arrival path can't reach). 26 tests passing in a real scratch venv (`Pillow`/`moto`). One unconfirmed-but-added IAM grant: read-only `Users` (needed for the P-99 uploader snapshot; not in `T-03`'s original manifest, added pragmatically, later confirmed by the user and `LOCKED_TECH_DECISIONS.md` updated to match).

**Remaining, not yet built:** `profile`, `events`, `membership`, `upload_status`, `gallery`, `EventTeardown`, `CascadeDelete`.

---

## `state_machine` module and the `Jobs.status` enum — the actual live thread

Built 2026-08-17 (`infrastructure/modules/state_machine/`, ASL in `templates/ingestion_pipeline.asl.json.tftpl`, `QueryLanguage: JSONata` per the user's explicit request — rewritten from an initial JSONPath draft; both Distributed Maps' `MaxConcurrency` come from measured Rekognition quotas, both **5** on this account). Wires `Extract → IndexPhotos (Map) → Finalize → ListAttendees → MatchAttendees (Map)` end to end, triggered by an EventBridge rule on the `uploads/.../original.zip` S3 event per `T-09`.

Building/reviewing this ASL surfaced and closed, over several rounds of the user catching real gaps (not decided silently):

- `db_api` needed calling from `Jobs`' actual touch points, not just once — closed by adding a write before/after every real phase transition.
- `ListAttendees`/`MatchAttendees` had `Retry` but no `Catch` — fixed, routed to a tracked `IngestionFailed` terminal.
- The happy path had no explicit success marker — added `IngestionSucceeded` (`Type: Succeed`), symmetric with `IngestionFailed` (`Type: Fail`).
- `Extract`'s photo list was returned as a plain JSON field, contradicting `T-02`'s "never as a JSON array passed between states" — fixed to write a `manifest.json` to S3 and return only a pointer, read via a real `ItemReader`.

**Finalized 2026-08-18, this session — the enum itself and where it's enforced:**

- **Dropped `PARTIAL` entirely.** The user's call: `succeededCount`/`failedCount` already carry that nuance; a third terminal status added nothing actionable.
- **Zero-succeeded now also terminates as `FAILED`**, not any success variant.
- **Enum enforcement moved into `db_api`, out of the state machine — the user's explicit, direct instruction** ("the state machine should not tell the string that is a wrong practice"). The ASL now sends only **named actions** (`mark_extracting`/`mark_indexing`/`mark_matching`/`mark_success`/`mark_failed`/`create`); `db_api`'s `Manager` holds the one `_STATUS_BY_ACTION` mapping from action → status string, and an unrecognized action raises. This is now the actual enum-enforcement boundary.
- **`Finalize` no longer computes or returns any `status` field** — just `succeededCount`/`failedCount`. Reversed my own earlier recommendation (keep a computed status in Python) after the user asked "why do we need this status then?" — agreed it was unnecessary indirection once only one trivial check remained.
- **New `Choice` state, `CheckIndexingOutcome`, right after `Finalize`** — `succeededCount = 0` routes straight to `JobFailed`, skipping `ListAttendees`/`MatchAttendees` entirely (nothing new to match). This placement was **the user's own insight**, not mine — I'd originally proposed checking at the end of the pipeline; the user pointed out checking right after `Finalize` avoids running two states pointlessly when there's nothing to match.
- **The real terminal write moved to after `MatchAttendees`' Map**, immediately before `IngestionSucceeded` — a new unconditional `UpdateJobStatus` state calling `mark_success`, since that Map is the pipeline's actual end, not `Finalize`.

**Final `Jobs.status` enum:** `CREATED → EXTRACTING → INDEXING → MATCHING → SUCCESS`/`FAILED` (14 states total in the ASL). Fully implemented and tested — `db_api`'s `Manager`/tests updated, `ingestion`'s `finalize.py`/tests updated, ASL template updated, `LOCKED_TECH_DECISIONS.md`'s `Jobs` entry and decision log updated to match. Verified via local template render (correct state graph) plus `terraform fmt -check -recursive`/`terraform validate`, both clean.

---

## Architecture summary (for orientation, not re-derivation — see `LOCKED_TECH_DECISIONS.md` for reasoning)

10 Lambdas (`heic_converter`, `db_api`, `download`, `ingestion`, `profile`, `events`, `membership`, `upload_status`, `gallery`, `CascadeDelete`), 7 DynamoDB tables (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`, `Downloads`), 1 S3 bucket `glimpses-photos` with 6 prefixes (`uploads/`, `photos/`, `thumbnails/`, `selfies/`, `qrcodes/`, `downloads/`), CloudFront+OAC in front of `photos/`/`thumbnails/`/`qrcodes/` only. `EventAttendees.status` is 4-valued (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`), rows never deleted; `matchedPhotoIDs` (String Set) kept current by `MatchAttendees` (batch-arrival fan-out) and `MatchOneAttendee` (stream-triggered, catches late admits/joins/rejoins). `CascadeDelete` (originally `EventTeardown`, renamed when reused for photo deletion too) exists because no single-table-scoped Lambda has IAM reach for full event/photo teardown across tables + S3 + Rekognition.

AWS/Terraform bootstrap (`Miscellaneous/SETUP_STEPS.md`): IAM user `glimpses-terraform`, CLI profile `glimpses`, Terraform 1.15.8, versioned+locked-down state bucket `glimpses-terraform-state`. Measured (not assumed) Rekognition quotas on this account: `IndexFaces` and `SearchFacesByImage` both **5 TPS** — both `state_machine` module variables.

---

## Known open items (not blocking)

- `Finalize`'s "all photos in this batch failed" `FAILED` and `JobFailed`'s "the execution itself crashed" `FAILED` still write the identical status string from different causes — not yet decided whether this needs distinguishing.
- A dropped/failed `MatchOneAttendee` stream invocation silently misses one attendee with no automatic catch-up — accepted at `P-93`'s scale, flagged for later if it ever bites.
- No `retry_policy`/`dead_letter_config` on the EventBridge target that starts `ingestion` — a rare transient `StartExecution` failure would be dropped silently, same failure shape as `HANDOFF.md` §7's silent-alarm history. Flagged, not fixed.

## Next step

Build the 5 remaining API-facing Lambdas (`profile`, `events`, `membership`, `upload_status`, `gallery`) and `CascadeDelete`. `CascadeDelete` should come after `events`/`gallery`'s delete endpoints exist to call it. After that: a real Jenkins run + `apply` pass to actually deploy something to AWS for the first time.

**Resume prompt (paste after `/clear`):**
> Read `CLAUDE.md`, then `Miscellaneous/SESSION_HANDOFF.md` in full. 4 of 10 Lambdas are built (`heic_converter`, `db_api`, `download`, `ingestion`) plus the `state_machine` module. `Jobs.status` is finalized as `CREATED → EXTRACTING → INDEXING → MATCHING → SUCCESS`/`FAILED`, enforced inside `db_api` via named actions, not by the state machine. Nothing is currently open or mid-discussion. Next real work: build the 5 remaining API-facing Lambdas (`profile`, `events`, `membership`, `upload_status`, `gallery`) plus `CascadeDelete` — pick a build order and start.

---

*This file was condensed 2026-08-18 — the full play-by-play build log (every intermediate correction, every command run, every test count per revision, the entire technology-phase ruling narrative) that used to live here was trimmed to the summary above. Nothing ruled was lost: every locked decision referenced here is also in `LOCKED_TECH_DECISIONS.md`, which remains the source of truth, and full concept-level reasoning stays in `TECH_EXPLANATIONS.md`. If you need the original blow-by-blow narrative, it's in git history for this file.*
