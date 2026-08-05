# Glimpse — Project Handoff (v1 retrospective, pre-rebuild)

**Purpose of this document:** This is the full technical and architectural memory of "Glimpse v1" — an event photo-sharing app with face-recognition search, built solo on AWS. The source code/infra folder (`Miscellaneous/Deletion_On_Context_Consume/`) is being deleted after this document is written, and all live AWS resources have already been torn down (Terraform destroy + manual Rekognition/SSM cleanup completed). This document exists so a rebuild can reuse what worked, consciously revisit what didn't, and — per the project owner's explicit wish — put **the human in the decision seat this time**, with AI presenting options/tradeoffs rather than dictating architecture. Everywhere a past decision is recorded, it's presented as "what we did and why" — not as a recommendation to repeat it.

Status at freeze: infra + CI/CD + auth + event management + upload/ingestion/face-indexing pipeline were fully built and working. The attendee-facing consumption features — **gallery browsing, face search, and download** — were the next unbuilt phase (stub Lambdas only). Two known bugs were open and unresolved (see §7).

---

## 1. Product concept

**One-line pitch:** *"Here is my face — show me every photo I appear in."* An event photographer/organizer uploads one ZIP of hundreds/thousands of event photos. Attendees don't scroll everything — they upload a selfie and the app finds only their photos via Rekognition face matching.

**Organizer journey:**
1. Sign up (email/password or Google), create an event: name, date, description, `galleryMode` (`PUBLIC` or `PRIVATE`), `similarityThreshold` (default 80, min 70). Gets a unique 6-char access code and a dedicated Rekognition face collection (`glimpse-evt-{eventID}`), created at event-creation time.
2. Requests a pre-signed S3 URL and uploads one ZIP of all photos directly to S3 (bytes never touch the API/Lambda — no size limit).
3. The ZIP landing in S3 triggers an EventBridge → Step Functions pipeline: extract photos + generate ~400px thumbnails → fan out to SQS → per-photo Rekognition `IndexFaces` → poll until done.
4. Organizer polls a status endpoint every 10-15s and sees two-stage progress ("Extracting 143/800" → "Indexing 512/800"), until a terminal state (`COMPLETE` / `COMPLETE_WITH_ERRORS` / `FAILED`).
5. Shares the access code out-of-band (WhatsApp/email/QR).
6. Uploading a second ZIP later always creates a new Job record (never appends to the old one — deliberate).
7. Can archive the event: blocks new uploads/searches, keeps existing photos viewable, and **deletes the Rekognition collection** to stop ongoing cost.

**Attendee journey:**
1. Sign up/login (same Cognito pool).
2. Joins via access code only — no event ID needed in the URL, resolved server-side.
3. Behavior is fully driven by `galleryMode`:
   - **PUBLIC:** full gallery shown immediately; a "Find My Photos" button lets them filter to just their matches via selfie upload, with a toggle back to the full gallery.
   - **PRIVATE:** search-first screen, zero photos shown until a selfie is uploaded and matched — no route/API ever exposes other attendees' photos.
4. Face search: selfie → Rekognition `SearchFacesByImage` against the event's collection → keep matches above threshold → map to photos. Rate-limited to **10 searches/hour/user/event** (protects against Rekognition cost spikes from abuse).
5. Download as ZIP: server-side zip build in S3, returns a time-limited pre-signed URL (avoids streaming through Lambda memory/timeout).
6. All photo viewing goes through **CloudFront signed URLs**; direct S3 access is blocked entirely.

**Explicitly out of scope for v1:** mobile apps, admin dashboard, payments, photo editing, video, multi-event batch search, individual (non-ZIP) image upload, public sharing outside the access code, auto-deploy on git push.

---

## 2. Tech stack (as actually built, not just as originally planned)

| Layer | Choice | Note |
|---|---|---|
| Region | `ap-south-1` (Mumbai) | Cost/latency/regional availability for Rekognition, Cognito, Step Functions |
| Backend runtime | Python 3.12 on Lambda, boto3 | boto3 ships with the runtime; chosen over Node/TS despite early planning docs leaning Node/TS, because AWS's Rekognition/S3/DynamoDB examples/tooling are Python-heavy |
| API pattern | **One Lambda per endpoint** (no FastAPI/Mangum, no web framework) | API Gateway does routing, Cognito Authorizer does auth — a framework was judged to add cold-start weight for no benefit at this scale |
| Frontend | React **19** (planning docs said 18 — actual build drifted upward), Vite **8**, plain JSX (deliberately no TypeScript), Tailwind CSS | JSX-no-TS tradeoff explicitly accepted: faster to start, cost = no compile-time contract between frontend/backend shapes |
| Frontend libs | `aws-amplify` v6 (Cognito auth), `@tanstack/react-query` (fetching + status polling), `axios`, `react-router-dom` v6, `react-dropzone`, `yet-another-react-lightbox` (present, not yet wired in), `framer-motion`, `lucide-react`, `react-hot-toast` |
| Auth | Cognito User Pool (sole identity source) + Amplify Auth (frontend) + Cognito Authorizer (API Gateway) + Google as a federated IdP | JWT validated by API Gateway itself — no hand-rolled JWT parsing anywhere |
| Ingestion trigger | S3 upload → EventBridge → Step Functions (Standard workflow) | S3-as-trigger chosen over an API call because S3 is a more reliable "the file actually arrived" signal — works even if the browser tab closes |
| Face indexing fan-out | SQS + DLQ → `index_worker` Lambda → Rekognition `IndexFaces` | Chosen over a plain loop (hits Lambda's 15-min limit, no backpressure) and over Step Functions Distributed Map ("valid, but more advanced to configure and debug for a first build") |
| Data store | DynamoDB, 7 single-purpose tables (not single-table design) | "Easier to read and fits a first build"; every GSI justified against a named access pattern (see §3) |
| Thumbnails | Pillow (~400px), packaged in a Lambda layer built inside Docker (`python:3.12-slim --platform linux/amd64`) | The originally-planned `public.ecr.aws/lambda/python:3.12` base image did **not** work for this — its custom entrypoint is incompatible with plain `pip install`. Concrete correction if repeating this pattern. |
| CDN/delivery | CloudFront with Origin Access Control (OAC) + signed URLs for the private photos bucket | S3 buckets are 100% private; CloudFront (or pre-signed S3 URLs for upload/download) is the only read/write path |
| IaC | Terraform, modular (9 modules), **local state only** (no S3 backend/DynamoDB lock) | Explicitly an MVP/solo-work simplification, flagged in the docs as a "harden later" item |
| CI/CD | Jenkins, installed locally via Homebrew (`brew install jenkins-lts`), **not Dockerized**, manual "Build Now" only, no webhooks | Deliberate Continuous *Delivery* (not Deployment) — "deployments are always intentional, never accidental." Terraform apply/destroy was deliberately kept **out of** the Jenkins pipeline and always run by hand. |
| Observability | AWS Lambda Powertools declared as a layer dependency, but **actual handler code uses plain `print()` logging** — Powertools/pydantic were never actually wired into the handlers despite being shipped in the layer (dead weight) | Worth deciding deliberately next time rather than by drift |
| Monitoring | CloudWatch alarms (DLQ depth, per-Lambda errors/throttles) | **No SNS topic was ever attached** — alarms were console-visible only, not actually alerting anyone |

---

## 3. Data model (DynamoDB, 7 tables)

Design philosophy stated in the original docs: single-purpose tables, not single-table design, because it's easier to reason about for a first build. All tables on-demand billing, all GSIs `projection_type = ALL`. IDs are UUIDv4 unless noted; atomic counters always use `ADD`/`SET x = x + :n`, **never** read-modify-write, because indexing workers write concurrently.

- **`Users`** — PK `userID` (= Cognito `sub`). GSI `email-index`. Exists for app-profile data/joins beyond what the JWT already carries; row is created lazily on first authenticated call (no Cognito trigger).
- **`Events`** — PK `eventID`. Fields include `accessCode` (unique), `status`, `galleryMode`, `similarityThreshold`, running counters (`totalPhotos`/`extractedPhotos`/`indexedPhotos`/`failedPhotos`), `rekognitionCollectionID`. GSI `organizer-index` (organizer's event list, newest first), GSI `accessCode-index` (resolve joins). Access-code uniqueness enforced by conditional put + regenerate-on-collision.
- **`Jobs`** — PK `jobId`. This is the **source of truth** for a single ingestion run (the "job with steps" model); `Events`' counters are just convenience mirrors. Fields: `jobType`, `status` (`PENDING`→`EXTRACTING`→`INDEXING`→terminal), progress counters, `currentStep`, `errorMessage`, `stepFunctionArn`. GSI `event-index` (PK `eventID`, SK `createdAt`) — the status endpoint reads the latest job for an event via this. A single event can have multiple Jobs over its life (each ZIP upload = new Job, never an append).
- **`Photos`** — PK `photoID`. GSI `event-index` (PK `eventID`, SK `uploadedAt`) for the paginated gallery.
- **`Faces`** — PK `rekognitionFaceID` (the Rekognition-assigned ID). GSI `photo-index`. Search flow: selfie → Rekognition returns matched face IDs above threshold → look up each in `Faces` by PK → collect unique `photoID`s → fetch those `Photos`.
- **`EventAttendees`** — PK `userID`, SK `eventID`. `hasSearched` (bool) gates PRIVATE-mode access. GSI `event-index` for organizer/debug attendee listing.
- **`SearchRateLimit`** — PK `userID`, SK `eventID`. `searchCount`, `windowStart`, DynamoDB TTL for auto-cleanup. Logic: if `now - windowStart >= 1h`, reset; else if `searchCount >= 10`, reject; else atomic `ADD`. **Note:** this table was fully provisioned but never actually used — the `search` Lambda was still a stub at freeze time.

Every GSI in the original design doc is tied to a named, concrete access pattern rather than added speculatively — worth keeping that discipline in the rebuild.

---

## 4. Backend architecture

**Pattern:** one Lambda per REST endpoint, three files each — `handler.py` (HTTP/event glue), `schema.py` (input validation via a dataclass `from_body`/`from_params` factory, raising a shared `AppError` on failure), `service.py` (pure business logic). Pipeline workers (Step Functions Tasks / SQS consumers) are single-file since they aren't HTTP endpoints.

**Business Lambdas actually built:** `create_event`, `list_events`, `get_event`, `archive_event`, `join_event`, `get_upload_url`, `event_status`, `event_stats`, `health` — all fully implemented. **`gallery`, `search`, `download` were still stub placeholders at freeze** despite having full IAM roles, DynamoDB tables, and API Gateway routes already provisioned.

**Pipeline Lambdas (Step Functions/SQS-triggered, not API Gateway):** `init_job` → `extract_thumbnail` → `enqueue_indexing` → (loop: `check_progress`) → `mark_complete`/`mark_failed`, plus `index_worker` as the SQS consumer.

**Shared library (`glimpse_shared`, packaged in a Lambda layer):** `config.py` (env var constants), `db.py` (one DynamoDB table getter per table), `auth.py` (`get_caller()` — the single choke point for reading Cognito claims out of the API Gateway authorizer context), `responses.py` (`json_response`/`error_response`), `errors.py` (one `AppError(code, message, http)` class — the uniform error vocabulary), `validators.py`, `access_codes.py` (6-char code generator, ambiguous chars excluded, collision retry), `rekognition.py` (the *only* module allowed to call Rekognition, per its own docstring convention).

**Ingestion pipeline (Step Functions, Standard workflow):**
```
Format Input → Extract Params From Path
→ Initialize Job (EXTRACTING)
→ Extract & Thumbnail (unzip, Pillow thumbs, write Photos rows)
→ Enqueue Indexing (SQS SendMessageBatch, → INDEXING)
→ [Wait 15s → Check Progress → Choice: done? no→loop / yes→Mark Complete] 
→ Succeed
Every Task: Retry (backoff) + Catch(States.ALL) → Handle Exception → Mark Job Failed → Fail
```
Only `jobId` is carried through state-machine JSON (256KB hard ASL limit) — Lambdas read/write S3 and DynamoDB directly, never pass image bytes through the state machine. Standard (not Express) workflow was chosen deliberately for full visual execution history during debugging, since runs can last minutes.

**Why SQS+DLQ for face indexing** (the most deeply reasoned architectural choice in the whole project): Rekognition has rate limits — firing thousands of calls at once gets throttled; some photos will always fail transiently and need retry; some will fail for real and need to be set aside without stopping the batch; and a single Lambda looping over thousands of calls risks the 15-minute execution limit. `maxReceiveCount=3` on the DLQ redrive bounds retries; visibility timeout is set to ≥6× the worker's max duration to avoid premature redelivery of in-flight messages.

**IAM:** every Lambda gets its own role with a hand-written least-privilege policy (e.g. `get_upload_url` can `PutObject` only under `events/*/upload/*`; `index_worker` gets `rekognition:IndexFaces` only, never delete/create). No Lambda has blanket `s3:*`/`dynamodb:*` access. This produced real friction during the build — several roles were found missing a specific permission only at runtime, not design time (see §7).

**Why Rekognition collections are created at runtime by Lambda, not in Terraform:** they're a data-dependent, ephemeral resource tied to a dynamic `eventID` (created in `create_event`, deleted in `archive_event`) — not static infrastructure. Consequence: Terraform has zero visibility into them, so a full teardown requires archiving events first (or a manual `rekognition delete-collection` pass, which is what we ended up doing) or they become an orphaned cost leak. **This is worth a deliberate decision in the rebuild** — e.g., tagging/tracking these collections in DynamoDB (already done, via `Events.rekognitionCollectionID`) so a teardown script can enumerate and clean them without depending on Terraform state at all.

---

## 5. Frontend architecture

**Structure** (`frontend/src/`): `lib/` (Amplify config, an axios instance with a request interceptor that attaches the Cognito ID token as `Authorization: Bearer`, shared React Query client), `auth/` (`AuthContext`/`AuthProvider` wrapping Amplify + a Hub listener for OAuth callback events, `RequireAuth` role-aware route guard), `hooks/` (`useEvents`, `useEvent`, `useJobStatus` polling hook, `useUpload`), `pages/` (Login, Signup, VerifyEmail, OrganizerDashboard, CreateEvent, EventDetail, UploadPage, JoinEvent, GalleryPage), plain Tailwind components (no component library — hand-rolled `.btn`/`.input`/`.badge` classes via `@apply`).

**Key polling pattern** — stops on terminal state, directly mirroring the pipeline's own terminal-state design:
```js
refetchInterval: (data) =>
  ['COMPLETE','COMPLETE_WITH_ERRORS','FAILED'].includes(data?.status) ? false : 12000
```

**Direct-to-S3 uploads** for both the ZIP and the (future) selfie: get a pre-signed URL, PUT with `onUploadProgress` for a progress bar, bytes never pass through the API.

**`GalleryPage` was still a placeholder ("coming in Phase 7")** at freeze — the actual face-search/gallery-browsing UI was never built, matching the backend stub status.

---

## 6. Security design

- Cognito is the sole identity source; API Gateway's Cognito Authorizer validates every JWT (no hand-rolled parsing). Google sign-in via Cognito federation, kept in Cognito's free "Testing" mode (whitelisted test users only, no production app review).
- Role comes from a `custom:role` JWT claim; every Lambda does its own ownership check inline (e.g. `organizerID == claims.sub`). **PRIVATE mode is explicitly hardened**: the gallery endpoint (once built) was designed to return 403 `SEARCH_REQUIRED` until the user has a successful search, and never return other attendees' photos through any parameter or route.
- S3 buckets fully private (Block Public Access on); CloudFront + Origin Access Control is the only read path; CloudFront signed URLs for viewing (15-60 min), S3 pre-signed URLs for upload (15 min) and download (10 min).
- Per-event Rekognition collections isolate face data and are deleted on archive.
- `glimpse-admin` (the IAM user used by Terraform/Jenkins) had **`AdministratorAccess`** — explicitly flagged in the original docs as "pragmatic for a solo build, not used at runtime by the app, tighten later." Worth actually tightening this time rather than re-deferring.
- **Concrete issue found during this handoff's exploration, not in the original docs:** `infra/modules/cdn/` had **both the CloudFront signing public key AND the private key committed as real PEM files on disk** — contradicting the project's own documentation, which claimed the private key only ever lived in SSM SecureString. If this repo/folder was ever pushed to a remote or shared, **that private key must be treated as compromised** (rotate if the app is ever rebuilt with signed URLs again). This is exactly the kind of drift-from-documented-intent worth catching early in a rebuild via a pre-commit secret scanner.
- Also flagged previously: a live AWS access-key CSV and Google OAuth client secret sit in plaintext across several scratch files (`Glimpses_docs/`, `.env.local`, `terraform.tfvars`) — rotate these before/alongside the rebuild since they were used to run the just-completed teardown.

---

## 7. Known issues, mistakes, and things to do differently (the important part)

**Open, unresolved bugs at freeze:**
1. Upload page flashed "ZIP not uploaded yet" on revisit after a completed upload, before the status poll resolved — root cause was React Query serving a stale/undefined cached value before the fresh fetch completed. Two fix attempts failed to close a ~200-400ms window. A cleaner fix (not applied): use React Query's `initialData`/`placeholderData` as a real loading sentinel, or a route-level loader/Suspense boundary that pre-fetches job status before the page renders.
2. **Google OAuth sign-in never fully completed** — user landed back on login unauthenticated even though the Cognito user was created. Suspected root cause: Amplify v6 + React Router + CloudFront SPA rewrite interaction — possibly the PKCE code verifier not surviving the redirect hop, or a Hub-event/route-render timing race. Multiple fix attempts (Hub listener reordering, loading flags) didn't resolve it. If Google sign-in is wanted in the rebuild, this deserves isolated investigation up front rather than debugging it embedded in a full app.

**Resolved bugs worth knowing about (so they aren't repeated):**
- The Pillow Lambda layer produced full-size, not thumbnail, images for a while — caused by using the wrong Docker base image for the layer build (see §2 tech stack note).
- EventBridge originally fired on every `.jpg`/thumbnail write, not just ZIP uploads, because the S3 event filter used OR-semantics (separate prefix+suffix) instead of a single wildcard pattern (`events/*/upload/*.zip`).
- Several IAM roles were missing a specific permission discovered only at runtime (not design time) — the strict one-role-per-Lambda approach is good for security but created real iteration friction; consider writing IAM policies test-first against actual code paths, or generating them from a manifest of each Lambda's actual AWS calls, rather than hand-guessing upfront.
- A counter bug: `totalPhotos` was set from the raw ZIP entry count (including macOS metadata files like `__MACOSX/._*.jpg`) instead of the actual count of images extracted, breaking the "done when indexed+failed==total" convergence check. Fixed by setting the total *after* the extraction loop using the real extracted count.
- `"indexed"` is a DynamoDB reserved word — required `ExpressionAttributeNames` workarounds. Worth a naming convention (e.g. prefixing/avoiding reserved words) decided upfront next time.
- Lambda zips are flat directories — imports must be absolute, never relative, or deploys break. An easy, recurring gotcha worth documenting in a rebuild's contributing guide from day one.
- Deploy script had to strip the `glimpse-dev-` prefix and hyphen→underscore convert to match zip filenames — a naming-convention mismatch between Terraform resource names and Python module names that could be avoided by choosing one consistent naming scheme across both from the start.

**Deferred-on-purpose (documented as backlog, not oversights):** SES/custom domain for Cognito email, Terraform S3 remote-state backend + DynamoDB lock, WAF, KMS customer-managed keys, IAM Identity Center / short-lived creds, periodic key rotation, Cognito advanced-security tier, API Gateway throttling/usage plans, SNS alerting on CloudWatch alarms.

**Drift/technical-debt discovered while re-reading the actual code (not previously documented as issues):**
- CORS was hardcoded to `*` in both the shared response helper and API Gateway's mock CORS integrations, despite an `app_urls` Terraform variable that implied origin-restriction was intended but never wired through.
- Several dependencies were shipped in the Lambda layer but never actually used in code: `aws-lambda-powertools` and `pydantic` (all logging is plain `print()`, all schemas are stdlib `dataclasses`), and `stream-unzip` (extraction uses stdlib `zipfile` instead) — pure unused weight in every cold start.
- Two Cognito groups (`organizers`/`attendees`) were provisioned but never actually used for authorization — role gating is done entirely via a JWT custom claim, making the groups vestigial. Worth picking one mechanism deliberately next time.
- Some shared validator helpers (`require_owner`, `require_event_active`) were written but never called — ownership checks ended up hand-duplicated inline in every service file instead, an incomplete refactor.
- The Step Functions polling loop (`Wait 15s → Check Progress → loop`) has no maximum iteration count or overall workflow timeout — a stuck job could poll indefinitely on a Standard workflow.
- A DLQ URL was derived by string-replacing `"glimpse-dev-indexing"` in code rather than reading a dedicated env var — breaks for any environment/name other than exactly `glimpse-dev`.
- The monitoring module's per-Lambda alarm list was hardcoded in root `main.tf` rather than derived from the functions module's outputs — new Lambdas silently get no alarm unless someone remembers to add them to a separate list.
- No SNS topic was attached to any CloudWatch alarm — alarms existed but nothing was subscribed to them, so they were effectively silent.

**Build progress at freeze:** infra, Jenkins CI/CD, auth, event management, and the full upload→extract→index pipeline were complete and working. Gallery, search, and download (the actual attendee-facing "see and get your photos" features) were the next phase, not yet started beyond stub Lambdas/placeholder pages. Frontend polish, broader testing/hardening, and a proper README were also not yet started.

---

## 8. Testing approach that was used

Test pyramid: many fast unit tests (pytest + moto-mocked AWS) → some integration tests per Lambda → a handful of high-value E2E journeys run against the actually-deployed stack. Notable explicit calls: verify the rate limiter really blocks the 11th search; verify direct S3 GET on a private object fails; verify an expired signed URL fails; verify unauthenticated calls get 401 and cross-role calls get 403; and — importantly — prove the *failure* branch and DLQ path work, not just the happy path (a deliberately-corrupted ZIP should drive the pipeline to `FAILED`, and a forced-failing message should land in the DLQ and produce `COMPLETE_WITH_ERRORS`). One documented, accepted testing compromise: `COMPLETE_WITH_ERRORS` via DLQ was verified by code review only, not a live test, because artificially failing Rekognition mid-flow was judged impractical for a dev environment.

---

## 9. Questions worth deciding deliberately in the rebuild (not prescriptions — just the fork points this project actually hit)

- **API style:** one-Lambda-per-endpoint again, or a grouped/router pattern (e.g. Powertools' API Gateway resolver) to reduce IAM/deploy-script boilerplate at the cost of a slightly heavier single function?
- **Observability:** actually wire up Powertools structured logging/tracing this time, or consciously stick with print-based logging and drop the unused dependency instead of carrying dead weight?
- **IAM granularity:** keep strict one-role-per-Lambda (real security benefit, but caused iteration friction from under-scoped permissions discovered at runtime), or start slightly broader within a service boundary and tighten before launch?
- **Terraform state:** local (simple, single point of failure, what v1 did) vs. S3+DynamoDB remote backend from day one (more setup, safer, avoids a second copy of live secrets sitting in a folder like the `terraform.tfvars` here)?
- **Rekognition collection lifecycle tracking:** rely on Terraform (doesn't see them at all, as we learned) or keep the DynamoDB-tracked approach v1 used (`Events.rekognitionCollectionID`) and build a teardown script around that from the start, rather than discovering it as a manual step during a real teardown?
- **CORS/origin restriction:** actually enforce the `app_urls` allowlist this time, or accept `*` for a private-beta-only app and restrict at launch?
- **Gallery/search/download:** these were never built in v1 — worth scoping and designing fresh rather than inheriting the stub shape, since the rebuild is an opportunity to redesign these from the data model up if desired.
- **Secrets hygiene:** the v1 CloudFront private key being committed as a real PEM file despite documentation claiming SSM-only storage is exactly the kind of gap a pre-commit secret scanner (e.g. gitleaks) would have caught — worth deciding whether to add one from commit #1 this time.

---

## 10. Reference: original planning-doc lineage (for context on how decisions evolved)

The project went through three visible stages of planning documents, useful context if any of the deleted source docs are ever needed again (they won't be, since this handoff was written before deletion, but the reasoning trail matters):
1. **`Glimpses_docs/SUMMARY.md`** — the earliest "what and why" pitch document, written before some decisions were locked (e.g. it still shows an open FastAPI-vs-Pattern-A decision).
2. **`Glimpses_docs/Project_Pre_Req.md`** — a beginner-oriented AWS/stack teaching primer, written around the same early stage — notably it still teaches FastAPI+Mangum as the assumed backend pattern, which was later overturned in favor of one-Lambda-per-endpoint.
3. **`Image_Retrieval_System/MISC/*.md`** (inside the actual repo — `PLAN.md`, `SUMMARY.md`, `CLOUD.md`, `DATA_MODEL.md`, `BACKEND.md`, `FRONTEND.md`, `DEVOPS.md`, `SECURITY.md`, `TESTING.md`, plus per-phase progress logs) — the finalized, locked, authoritative build documentation the actual codebase was built against. This is where essentially everything in this handoff was sourced from.

This lineage itself is a small lesson: the original teaching/pitch documents drifted from what was actually built (FastAPI was taught but never used; React 18 was planned but React 19 shipped). Worth deciding upfront in the rebuild whether planning docs will be treated as living/updated documents or historical snapshots, so a future handoff doesn't have to reverse-engineer which decisions actually stuck.
