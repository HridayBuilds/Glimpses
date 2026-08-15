# Session Handoff — Glimpses product lock-in

**Written:** 2026-08-05, evening · **Updated:** 2026-08-15 *(all three gaps surfaced building `heic_converter` are now closed — endpoint paths, S3 layout, and the ingestion trigger, ruled as a new `T-09` — see below)*
**Current phase:** **Implementation, mid-`heic_converter`.** Product locked at 100 rulings, technology phase fully closed. First Lambda folder built end-to-end (code + tests + Terraform + Jenkinsfile). **All three gaps surfaced discussing it are now ruled** — gap 1 (endpoint paths) on 2026-08-15, gaps 2/3 (S3 layout, ingestion trigger) together, same day, as `T-09`. Next real work: fix `heic_converter/infra/lambda.tf`'s deploy-discipline mismatch, then build `db_api` and `download`.

**`heic_converter/infra/lambda.tf`'s deploy-discipline mismatch fixed, 2026-08-15.** Removed the `null_resource`/`local-exec` pip-install-and-zip and `data.archive_file` — Terraform no longer packages or ships code. `aws_lambda_function.this` now points its `s3_bucket`/`s3_key` at the shared `glimpses-deploy-artifacts` bucket, with `lifecycle { ignore_changes = [s3_key, source_code_hash] }` so Terraform never fights Jenkins's out-of-band code push, matching `T-06`'s already-locked discipline exactly. `input.tf` gained a `deploy_artifacts_bucket` variable, same "required, no real value yet" shape as `photos_bucket_arn`/`alarm_sns_topic_arn` — that bucket doesn't exist in Terraform yet either. `cicd/Jenkinsfile` gained the actual build/zip/push/`update-function-code` stages that used to live wrongly inside Terraform, run **before** `terraform apply` (a deliberate small deviation from the doc's literal "apply then code push" sentence order — needed so the S3 object exists before the Lambda's first-ever creation, avoiding a separate manual bootstrap step). Scratch `terraform validate` against the module passes with dummy values for all three still-unbuilt shared variables.

**Two `db_api`-scoping gaps closed while starting that Lambda, 2026-08-15.** (1) **Folder shape: `db_api` is a 4-layer chain, not `heic_converter`'s 5** — `routeHandler` → `Handler` → `Manager` (branches `action`: `create`/`update_status`, shapes the item) → `DAO` (the actual `put_item`/`update_item` calls). The `Converter`-equivalent layer collapses away entirely rather than sitting near-empty, since `db_api` has no pure-computation step the way HEIC→JPEG conversion is one — confirmed by the user as the intended reading of `CLAUDE.md`'s "or `procedure`/`dao`-named equivalent" wording. (2) **`Jobs`' undefined retry/backoff field is gone, not just renamed — `P-100`/`P-56` were rewritten, `D-127`, 2026-08-15, in `LOCKED_PRODUCT.md`.** The field was only ever sketched as "a retry/backoff signal," never given a real name/shape; naming it surfaced that its only purpose was backing `P-100`'s "says when photos are being retried and that this is why it is slower" clause (added by `D-126`). The user judged that clause not worth the implementation cost and had it dropped **at the product level**, not just skipped in the schema — `P-100` no longer promises retry visibility, `P-56` reverts to "invisible in both directions" with no exception. This is technology surfacing a real cost and the user ruling on product in response, per `CLAUDE.md`'s one-directional rule — not technology deciding to omit a field quietly. `Jobs`' final field list: `jobId`, `eventID`, `uploaderID`, `status`, `succeededCount`, `failedCount`, `startedAt`, plus the `eventUploaderKey` GSI attribute — nothing else.

**Gaps 2 and 3 — S3 bucket/key layout and the ingestion trigger — CLOSED 2026-08-15, ruled together as `T-09` (they turned out to be genuinely coupled).** Full detail in `LOCKED_TECH_DECISIONS.md` §9 and `TECH_EXPLANATIONS.md` §10. Tight summary:

- **One S3 bucket, `glimpses-photos`, six prefixes** — `uploads/`, `photos/`, `thumbnails/`, `selfies/`, `qrcodes/`, `downloads/` — not one bucket per category. Considered and rejected: six buckets (no capability gain over prefix-scoped IAM/lifecycle/events) and an event-vs-user bucket split (`uploads/` is scoped to event **and** user **and** job at once, so it doesn't sit cleanly on either side of that split anyway).
- **Key shapes**, now defining `Photos.s3Key` and the `download` Lambda's zip key (both previously undefined): `uploads/event/{eventID}/user/{userId}/job/{jobId}/original.zip`, `photos/event/{eventID}/{photoID}.jpg`, `thumbnails/event/{eventID}/{photoID}.jpg`, `selfies/user/{userId}/selfie.jpg`, `qrcodes/event/{eventID}/qrcode.png`, `downloads/event/{eventID}/{downloadId}.zip`. Every key is fully server-determined via the pre-signed URL that's issued for it — no client-supplied filename ever reaches S3.
- **CloudFront + Origin Access Control (OAC) serve only `photos/`, `thumbnails/`, `qrcodes/`** — the bucket policy grants the OAC identity `s3:GetObject` on exactly those three prefixes; `uploads/`, `selfies/`, `downloads/` are never granted, so they're unreachable through CloudFront even if a path is guessed, not merely unlinked. `selfies/`'s exclusion is a product requirement, not just a technical one — `P-15`/`P-82` make selfies invisible to *everyone*, including the organizer.
- **Selfies still need a read path for their own owner** (the profile page shows Meera her own selfie back) — done via a pre-signed `GET` `Profile` mints on `GET /profile`, scoped to the caller's own key only. Made cacheable via `Cache-Control: private, max-age=86400` on the object plus a matching pre-signed expiry, since a fresh signature on every call would otherwise defeat browser caching.
- **Ingestion trigger: S3 Event Notification → EventBridge → `StartExecution` directly on the `ingestion` state machine — no glue Lambda, no client callback.** An explicit "upload complete" client callback was ruled out — it fails `P-100`'s own scenario (Arjun closes his laptop mid-upload; the batch must still complete) since a callback depends on the browser surviving long enough to make a second call, which an S3-native event doesn't. The EventBridge rule filters on `source: aws.s3`, key `{prefix: "uploads/"}` and `{suffix: "/original.zip"}`.
- **A real behavior change fell out of this:** since one S3 object must produce exactly one `StartExecution` (matching `P-37`'s "one batch"), **multi-file selections are now zipped client-side before upload**, same as a ZIP upload — one object, one key, one trigger, either way. `Extract`'s unzip step becomes unconditional rather than ZIP-only.
- **Left open, not blocking:** whether to add `retry_policy`/`dead_letter_config` on the EventBridge target for a rare transient `StartExecution` failure (dropped silently by default, unlike `T-02`'s built-in per-item retry) — flagged as the same failure shape as `HANDOFF.md` §7's silent-alarm history, worth a future pass.

**Gap 1 — full REST endpoint paths — CLOSED 2026-08-15.** Full path list for all 5 original API-facing Lambdas now in `LOCKED_TECH_DECISIONS.md` §3; reasoning in `TECH_EXPLANATIONS.md` §9. Three real decisions inside it: (1) QR code gets its own downloadable endpoint, `GET /events/{eventId}/qrcode` (`Content-Disposition: attachment`), not a field on the event-detail response — `P-90`; (2) membership actions settled at 3, not 4 — `admit`/`deny`/`eject`, each a direct status transition (`deny`/`eject` both land on `BLOCKED` directly, since `P-29`'s "one blocklist serves both" means there's no separate `block` step), plus the already-ruled self-service `leave`; (3) bulk photo delete is `POST /events/{eventId}/photos/bulk-delete` with a body-carried `photoIds` array, over a `DELETE`+query-string shape, for `P-93`'s scale headroom.

**Closing gap 1 surfaced a real architectural addition — a 10th Lambda, `download`, and a 7th DynamoDB table, `Downloads`.** Photo download split into two mechanisms: selecting a few photos needs no server work at all (`Gallery/photos` gains `POST /events/{eventId}/photos/download-urls`, just hands back pre-signed S3 URLs); downloading a whole event/selection as one ZIP is real server-side work (S3 has no native "combine objects into a zip" operation) that `Gallery/photos` can't own without breaking `T-04`'s one-table-per-Lambda IAM isolation — the same shape of gap that originally produced `CascadeDelete`. Ruled: a dedicated `download` Lambda (`Downloads` table read/write + `Photos` read-only + S3), built as a **plain asynchronous Lambda invocation, not a Step Functions state machine** (no per-item throttle to coordinate, unlike `T-02`'s fan-out — this is one sequential streaming job), with a `Content-Disposition`-forcing status-poll pattern (`POST /events/{eventId}/photos/download` → `GET .../downloads/{downloadId}/status`). Estimated build time at `P-93`'s 1,000-photo ceiling: a few minutes, comfortably inside Lambda's 15-minute cap (and the reason a synchronous endpoint was never viable against API Gateway's 29s limit). `Downloads` deliberately has **no GSI** (unlike `Jobs`) — no product ruling requires a zip download to survive a closed tab the way `P-100` requires for uploads. S3 lifecycle-expires the finished zip objects (default 48h), matching `P-90`'s own note that these are "stored artifacts that need a lifecycle." **Lambda count 9→10, DynamoDB tables 6→7, CI/CD jobs 11→12** — all three counts updated throughout `LOCKED_TECH_DECISIONS.md`.

**`heic_converter` built 2026-08-15 — the first Lambda folder, and the template for the other 8.** Confirmed shape: `src/` is a 5-layer chain — `routeHandler.py` (thin, the actual Lambda entry point AWS invokes, Powertools `Logger` with `log_event=True` per `T-07`) → `Handler/handler.py` → `Manager/manager.py` (orchestration: S3 get → convert → S3 put) → `Converter/converter.py` (pure function, `pillow-heif`/`Pillow`, no AWS calls) → `DAO/dao.py` (the two S3 calls) — each layer in its own same-named folder (e.g. `Handler/handler.py`, not a flat `handler.py`), a deliberate user call over a flatter layout, for consistency across all 9 Lambdas even where a Lambda (like this one) has only one job. `test/unit/` (pure-function, no mocking) + `test/integration/` (full chain, `moto`-backed S3) — **both actually installed real dependencies in a scratch venv and ran; both passed.** `infra/` — `lambda.tf`/`iam_role.tf`/`iam_policies.tf`/`cloudwatch.tf`/`input.tf`/`output.tf` per `T-06`'s module layout; `terraform validate` passes (checked via a scratch harness using a relative module source path, matching how root `imports.tf` will reference it). `iam_policies.tf` grants only `s3:GetObject`/`s3:PutObject` on the photos bucket, derived from this Lambda's actual AWS calls per `T-07`. **`cicd/Jenkinsfile`** — a per-Lambda `cicd/` folder holding the Jenkinsfile, the user's explicit call, **diverging from the `dynamodb`/`state_machines` precedent** (those put `Jenkinsfile` inside `infra/`, specifically to keep each module self-contained) — flagged and confirmed as intentional, not an oversight.

**Not yet fixed — a real mismatch found late in the session.** `heic_converter/infra/lambda.tf` currently packages code by running `pip install` via Terraform's `local-exec` and deploying via `archive_file`/`filename` — but `T-06`'s already-locked deploy discipline is different: Jenkins pushes code separately (zip → `deployment-artifacts` S3 bucket → `aws lambda update-function-code`), with `lifecycle { ignore_changes = [s3_key, source_code_hash] }` on the `aws_lambda_function` resource so Terraform never fights the out-of-band code push. `lambda.tf` needs rewriting to match before this module is trustworthy — not done yet, next session's first code fix.

**Also not yet done:** `heic_converter` is not wired into root `infrastructure/imports.tf`. Its `infra/input.tf` requires `photos_bucket_arn` and `alarm_sns_topic_arn` as variables with no real value yet — neither a photos S3 bucket nor the shared alerting SNS topic (`T-07`'s "every alarm wired to an SNS topic + email subscription") exists anywhere in Terraform yet. Both are shared infra nothing has built.

**`Backend/BACKEND.md` is still 0 bytes.** `CLAUDE.md` describes it as already carrying the ruled per-Lambda folder shape — it doesn't; the shape above was decided conversationally this session, not written into the file. Worth reconciling: either fill in `BACKEND.md` with what's above, or correct `CLAUDE.md`'s description. Not done yet.

**Three real gaps surfaced discussing `heic_converter`'s invocation — all three now CLOSED, superseded by the top entry above:**

1. ~~**Full REST endpoint paths, to the exact parameter-path level.**~~ **RULED 2026-08-15** — full path list in `LOCKED_TECH_DECISIONS.md` §3, reasoning in `TECH_EXPLANATIONS.md` §9. Closing this surfaced a 10th Lambda (`download`) and 7th table (`Downloads`) — see top entry.
2. ~~**S3 bucket/key layout.**~~ **RULED 2026-08-15 as `T-09`** — see top entry, `LOCKED_TECH_DECISIONS.md` §9, `TECH_EXPLANATIONS.md` §10.
3. ~~**What actually triggers the `ingestion` state machine after an upload.**~~ **RULED 2026-08-15 as `T-09`, same as above** — S3 Event Notification → EventBridge → `StartExecution`, option A of the two originally raised.

**Next step:** fix `heic_converter/infra/lambda.tf`'s deploy-discipline mismatch (packages/deploys code inside Terraform, contradicting `T-06`), then build the new `download` Lambda folder alongside `db_api`, then continue to the rest.

---

**Prior entry, superseded above but kept for history:**
**Written:** 2026-08-05, evening · **Updated:** 2026-08-13 *(DynamoDB tables live in AWS; `InitializeJob` moved to `db-api`, pipeline Lambda renamed `ingestion` — see below)*
**Current phase:** **Implementation.** Product locked at 100 rulings (`P-01`–`P-100`), technology phase fully closed (`T-01`–`T-08`, both follow-up threads closed). **Nothing remains open before/during implementation except ordinary translation of already-ruled decisions into code/Terraform** — any point where a stack choice would make a `P-nn`/`T-nn` awkward is still a revision request, never resolved silently, per `CLAUDE.md`'s one-directional rule.

**Doc pruning (2026-08-12):** `PRD.md` and `TECH_DECISIONS.md` deleted by the user — both were working registers at **0 open** items, fully superseded by `LOCKED_PRODUCT.md`/`LOCKED_TECH_DECISIONS.md`+`TECH_EXPLANATIONS.md` respectively (verified before deletion: `LOCKED_PRODUCT.md`'s `P-31` entry already carries the full `D-99`→`D-117` rewrite history inline). `HANDOFF.md` kept — its §7/§9 hold implementation-level gotchas (reserved words, flat-zip absolute imports, naming-convention traps) not yet consumed since no code existed yet. New file **`Miscellaneous/SETUP_STEPS.md`** added: a running, reproducible log of every one-time human-run environment setup step (IAM, CLI, Terraform, state bucket), written for `Sam`-style reproducibility and to double as troubleshooting notes for errors already hit once.

**New working folders, each with its own `<NAME>.md` the user is filling in incrementally:** `Backend/BACKEND.md` (per-Lambda folder shape — `infra/` matching `T-06`'s module layout, `test/` matching `T-08`, `src/` compartmentalized per `T-01`'s `handler → manager → procedure/converter → DAO` layering), `Frontend/FRONTEND.md` (not yet discussed), `infrastructure/INFRASTRUCTURE.md` (not yet filled — user said they'll specify later).

**Build approach ruled implicitly, not formally voted A/B/C/D:** the user's own proposed Backend folder shape matched the sequencing recommendation (bootstrap shared infra minimally → prove the pattern on one vertical slice → replicate). Working incrementally, by priority, confirming each step's real output before the next — not a big-bang build.

**Infra bootstrap progress so far (all logged in detail, including exact commands/errors/fixes, in `Miscellaneous/SETUP_STEPS.md`):**
1. IAM user `glimpses-terraform` created (root did this once; broad AWS-managed policies attached — `DynamoDBFullAccess`, `Lambda_FullAccess`, `IAMFullAccess`, `S3FullAccess`, `APIGatewayAdministrator`, `StepFunctionsFullAccess`, `RekognitionFullAccess`, `CloudWatchFullAccess` — scoped-down later is a known future task, not urgent for a solo-controlled account).
2. Local AWS CLI configured under a **named profile**, `glimpses` (not `default`) — `aws configure --profile glimpses`, verified via `aws sts get-caller-identity --profile glimpses`.
3. Terraform upgraded via Homebrew to 1.15.8 (already satisfied `T-06`'s ≥1.10 requirement at 1.15.6, updated anyway).
4. State bucket `glimpses-terraform-state` created by hand in `ap-south-1` (console, not CLI, at the user's preference for this action) — versioning enabled, all public access blocked, default SSE-S3 encryption.
5. Rekognition confirmed available in `ap-south-1`; **actual account `IndexFaces` TPS quota is 5, not the published default of 50** — `T-02`'s `rekognition_index_max_concurrency` Terraform variable will be set to 5 when the Step Functions module is built. Requestable increase later if needed; not blocking now.
6. `infrastructure/providers.tf` (S3 backend + `use_lockfile`, `aws` provider) and `infrastructure/variables.tf` (`aws_region`, parameterised per `P-95`/`D-124`'s obligation) written.
7. `terraform init` — hit and fixed an `InvalidClientTokenId` credential error (root cause: SDK credential chain defaults to profile `"default"` unless `AWS_PROFILE` is exported, and only `[glimpses]` exists in `~/.aws/credentials`). Fix: `export AWS_PROFILE=glimpses` before any local Terraform command, every new terminal session — **this is a permanent recurring requirement, not a one-time fix**, since `T-06`'s cross-module apply is always manual, never Jenkins-automated. Full troubleshooting callout in `SETUP_STEPS.md` §7. Init succeeded: S3 backend configured, `hashicorp/aws` v5.100.0 installed, `.terraform.lock.hcl` created.

**`infrastructure/modules/dynamodb/` built (2026-08-13).** One `.tf` file per table (style question answered: one-file-per-table, matching `T-06`'s per-Lambda module precedent) — `users.tf`, `events.tf`, `jobs.tf`, `photos.tf`, `faces.tf`, `event_attendees.tf`, plus the module's own `variables.tf`/`outputs.tf`. Three small non-`T-04` technical decisions made while building it, all confirmed by the user: **`PAY_PER_REQUEST` billing** (spiky event-driven traffic, no capacity planning), **`ALL`-projection GSIs everywhere** (tables are small, avoids a second read on every query), and **`Events`' Stream set to `OLD_IMAGE`** (a TTL expiry is always a delete, nothing to compare against). `EventAttendees`'s AWS name resolved to `glimpses-event-attendees` (hyphenated at the word boundary — the doc's naming rule only had single-word examples). Root `infrastructure/imports.tf` now has `module "dynamodb"`. `terraform validate` passed (`AWS_PROFILE=glimpses`).

**`T-06` CI/CD job split, ruled 2026-08-13 — see the `T-06` follow-up rows in `LOCKED_TECH_DECISIONS.md`/`TECH_EXPLANATIONS.md` for full detail.** Building the DynamoDB module surfaced a real bug in the original `T-06` ruling: one combined untargeted-apply job for both DynamoDB tables and the state machine would fail on a cold deploy, since the state machine's Terraform needs each Lambda's ARN, which doesn't exist until all 9 Lambda jobs have already run. **Split into two dedicated jobs, `dynamodb` and `state_machines`, fixed run order `dynamodb` → all 9 Lambda jobs → `state_machines`.** CI/CD job count: **11** (was 10). Neither job is automatic — both still run by hand, same discipline as the original single job.

**Blocking question answered, 2026-08-13 — Jenkins already existed locally.** It's a Homebrew install (`jenkins-lts`), home at `~/.jenkins`, not currently running. It had one leftover job, `glimpse`, from v1 — pointed at the old repo name (`HridayBuilds/glimpse.git`, since renamed to `Glimpses`), single combined `DEPLOY_TARGET` pipeline, script at `cicd/Jenkinsfile`. Doesn't match `T-06`'s ruled 11-job shape, so it wasn't reused. **Second question (does Terraform provision it) turned out to be moot**: Jenkins here is a local program on the user's own machine, same category as Terraform itself or `git` — not an AWS resource, so it was never in Terraform's scope to create.

**`dynamodb` Jenkins job set up, 2026-08-13, replacing the stale `glimpse` job.** Two small decisions made along the way, both the user's call: (1) **each job's `Jenkinsfile` lives inside its own Terraform module folder** (`infrastructure/modules/dynamodb/Jenkinsfile`), not a shared top-level `cicd/` folder like v1 had — keeps `T-06`'s "per-module is self-contained" rule consistent for the two non-Lambda jobs, same as `BACKEND.md`'s per-Lambda `infra/` convention; (2) **AWS auth: the job's shell just sets `AWS_PROFILE=glimpses`**, reusing the same local credential file every other Terraform command on this machine already uses, over a Jenkins Credentials-store entry — simplest for a solo/local setup, revisit if this Jenkins ever needs to run on a shared machine (`Sam`-style). `~/.jenkins/jobs/glimpse/` deleted; `~/.jenkins/jobs/dynamodb/config.xml` created (SSH remote `git@github.com:HridayBuilds/Glimpses.git`, branch `main`, `scriptPath` pointing at the new Jenkinsfile — SSH kept, not switched to HTTPS, since the old job's SSH key was already a working credential and switching to HTTPS would've needed a fresh one for no reason).

**Blocked mid-session, 2026-08-13 — the `dynamodb` Jenkins job failed on its first run**, not from anything wrong in the job itself: `git fetch` over the SSH remote timed out (`kex_exchange_identification`, banner exchange failure to `20.207.73.83:443`). Diagnosed as a real network condition on this machine, not a config mistake — `nc` confirmed raw TCP to `ssh.github.com:443`/`github.com:443` both connect, but the actual SSH handshake over 443 times out and port 22 is fully blocked outright, a pattern consistent with something on this network inspecting/breaking non-TLS traffic on 443. Confirmed plain HTTPS to `github.com` works fine. **Fix in progress, not yet applied:** switch the `dynamodb` job's git remote from SSH to HTTPS + a GitHub PAT stored in Jenkins' Credentials store (`HridayBuilds/Glimpses` is private, so anonymous HTTPS won't work) — user is generating the PAT and adding the Jenkins credential now; once done, `~/.jenkins/jobs/dynamodb/config.xml`'s `userRemoteConfig` needs updating to the HTTPS URL + `credentialsId`. Making the repo public instead was considered and explicitly not done — it would remove the need for a credential entirely, but was rejected for now in favor of keeping the smaller, reversible fix (PAT + private repo) over a permanent visibility change, absent a stronger reason.

**Provider bumped to v6 while blocked on the above, 2026-08-13.** User asked whether the `hash_key`/`range_key`-in-`global_secondary_index` syntax across the DynamoDB module was deprecated. Checked against live docs via context7: **not deprecated at the pinned v5.100.0** (confirmed from that version's own docs) — the deprecation (steering toward a new `key_schema` block, added for multi-attribute composite keys none of these 6 tables need) only exists from provider v6.x onward. Since only the `dynamodb` module has real code yet (`api_gateway`/`state_machines` are still empty placeholder folders), the blast radius for a major-version bump was judged small enough to do now rather than deferring. **Done:** `providers.tf`'s `aws` provider constraint moved `~> 5.0` → `~> 6.0`; `terraform init -upgrade` installed `hashicorp/aws v6.59.0` (hit one transient registry-connectivity timeout on the first attempt, succeeded on retry — unrelated to the SSH/GitHub network issue above, which is specific to port 443's non-TLS traffic, not to registry.terraform.io's normal HTTPS); every `global_secondary_index` block across all 6 tables (`event_attendees.tf`, `events.tf` ×3, `faces.tf`, `jobs.tf`, `photos.tf` ×2) converted from `hash_key`/`range_key` to `key_schema { attribute_name = ...; key_type = "HASH"/"RANGE" }` pairs — pure syntax swap, no schema/key/GSI behavior changed. `terraform validate` and `terraform fmt -check -recursive` both pass.

**Housekeeping, 2026-08-13 — a push was rejected for a 648MB provider binary.** `infrastructure/.terraform/` (Terraform's downloaded-provider working directory) had been accidentally committed. Fixed since it hadn't reached the remote yet (amending the not-yet-pushed commit was safe, not a history rewrite of anything published): added `**/.terraform/` to `.gitignore`, `git rm -r --cached` on the directory, amended, pushed clean. `.terraform.lock.hcl` stays tracked as normal — only the working directory itself was the problem.

**HTTPS+PAT switch completed and the `dynamodb` Jenkins job run for real, 2026-08-13 — the 6 tables now exist in AWS.** The job's `config.xml` was updated to the HTTPS remote (`https://github.com/HridayBuilds/Glimpses.git`) with `credentialsId=github-glimpses-pat`, backed by a fine-grained GitHub PAT stored in Jenkins' Credentials store (username `HridayBuilds`). Jenkins was started and the `dynamodb` job triggered from the UI — confirmed via `aws dynamodb list-tables --profile glimpses`: `glimpses-users`, `glimpses-events`, `glimpses-jobs`, `glimpses-photos`, `glimpses-faces`, `glimpses-event-attendees` all present. This closes the DynamoDB-provisioning thread entirely — the `dynamodb` Jenkins job is proven working end-to-end, not just `terraform validate`-clean.

**`InitializeJob` moved from the pipeline Lambda into `db-api`; pipeline Lambda renamed `pipeline` → `ingestion`, ruled 2026-08-13 — see the new `T-03`/`T-06` follow-up row in `LOCKED_TECH_DECISIONS.md` and the matching revision in `TECH_EXPLANATIONS.md` for full detail.** Surfaced while discussing the two non-user-facing Lambdas (`pipeline`, `db-api`) in more depth: `InitializeJob`'s entire body is a single `PutItem` on `Jobs`, meaning it was the one thing forcing `Jobs`-table IAM access onto the pipeline Lambda, whose other three steps (`Extract`/`IndexOnePhoto`/`Finalize`) never touch that table — while every other `Jobs` write already lived in `db-api`. Moved `InitializeJob` into `db-api` (now 5 `Jobs` touch points, branching on a new `action` field: `create` vs `update_status`), which removes `Jobs` from the pipeline Lambda's IAM manifest entirely. Renamed the pipeline Lambda's folder `pipeline` → `ingestion` at the same time, matching the term the docs already used elsewhere for this state machine; `db_api`'s folder name was kept as-is (never named for the status-only shape, so a `create` action doesn't make it inaccurate). Lambda count unchanged at 9, CI/CD jobs unchanged at 11 — this only moves which Lambda owns one step and renames a folder, no new Lambda/job.

**Next step:** build the first Lambda folder (`Backend/<name>/`). Per the discussion this session, recommended order: `heic_converter` and `db_api` first (small, standalone shared utilities that `ingestion` depends on), then `ingestion` itself, then the 5 API-facing Lambdas (`profile`, `events`, `membership`, `upload_status`, `gallery`) in any order, then `cascade_delete` last (depends on `events`'/`gallery`'s delete endpoints already existing to call it) — not a formal ruling, just a recommended build sequence, open to reordering. `state_machines` can't be built until `ingestion`, `db_api`, and `heic_converter` all exist, since its Terraform embeds their ARNs; per the fixed CI order it also can't be applied before all 9 per-Lambda jobs have run. Also raised this session, not yet acted on: whether to build backend and frontend fully sequentially or interleaved — leaning toward per-Lambda interleaving (build a Lambda, deploy it, then build the frontend page against its real endpoint) to avoid v1's exact frontend/backend contract-drift failure mode, but not yet formally decided since `Frontend/FRONTEND.md` hasn't been started.

**Feedback logged in memory this session:** the user runs all AWS/infra-provisioning commands themselves in their own terminal — hand over exact copy-paste commands, don't execute AWS-resource-creating commands via the Bash tool on their behalf, even when low-risk/reversible and credentials are locally available. (Read-only/local Terraform commands — `fmt`, `init`, `validate` — were run directly this session; those don't touch real AWS resources, unlike `plan`/`apply`. `aws dynamodb list-tables` was also run directly to verify the Jenkins job's result — a read-only AWS call, not a provisioning one.)

---

**Prior entry, superseded above but kept for history:**
**Written:** 2026-08-05, evening · **Updated:** 2026-08-12 *(technology phase fully closed — the `T-04` per-table follow-up is done, all 6 tables ruled including `EventAttendees`'s last 3 sub-questions; the technology phase has nothing left open)*
**Current phase:** **The technology phase — opened 2026-08-06, agenda (`T-01`–`T-08`) closed 2026-08-09.** The product is locked at 100 rulings and closed. Two follow-up sub-decisions were left open *inside* already-ruled items rather than as their own agenda lines, both now closed: `T-03`'s API Gateway flavour (ruled 2026-08-09) and `T-04`'s per-table schema (ruled 2026-08-09 → 2026-08-12, see below). **The technology phase is now fully closed — nothing remains open before implementation.**
**Next steps:** `T-01`–`T-08` all ruled (all Python; Step Functions Distributed Map; 9 Lambdas — see below; multi-table 6-table data model, all 6 tables' fields/keys/GSIs ruled; one Rekognition collection per event; S3 Terraform state + per-Lambda modules + 10 CI/CD jobs; observability/IAM/CORS/secrets; 3-tier testing pyramid + Jenkins-free local testing — see prior entries in the three tech files for full detail). `T-03` follow-up (API Gateway flavour → REST API) ruled 2026-08-09; `T-04` follow-up (all 6 tables' schema) ruled 2026-08-09 → 2026-08-12 — both fully written up in all three tech files. **Per `CLAUDE.md`'s standing rule, implementation is next** — no code gets written until the decisions behind it are ruled, and they now are.

**`T-04` follow-up — per-table fields, PK/SK choices beyond the primary id, and GSI definitions, all 6 tables (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`) — CLOSED 2026-08-12.** `P-57`+`P-16`'s forced cursor pagination and `P-85`'s storage-byte counter (surviving `P-44`/`P-52`/`P-38`/`P-55`) landed in `Photos`. `P-16`/`P-93`'s per-attendee `SearchFaces` fan-out landed as `MatchAttendees`, a new Distributed Map step on `PipelineHandler`, writing `matchedPhotoIDs` onto `EventAttendees`. Two amendments surfaced along the way and are recorded against `T-03`/`T-06`, not `T-04`: a 9th Lambda, `CascadeDelete` (originally `EventTeardown`), for cross-table delete cascades no single-table-scoped Lambda could reach — Lambda count 9, CI/CD jobs 10, both final.

**`EventAttendees` — ruled 2026-08-12, closing the `T-04` follow-up.** PK = `userID`, SK = `eventID` (fixed by `T-04`'s original ruling). Fields: `userID`, `eventID`, `status`, `matchedPhotoIDs`. **Status: 4 values — `PENDING`, `ATTENDEE`, `LEFT`, `BLOCKED`.** The row is never deleted once created — leave (`P-46`) and eject/deny (`P-29`) are both `UpdateItem` status flips on the same row, not delete/recreate, chosen so `matchedPhotoIDs` survives a leave/rejoin cycle (matches reappear instantly on rejoin instead of waiting on the next batch) and because `P-29`'s blocklist already forces "never delete" for `BLOCKED` regardless — one mechanism for every membership transition. **One GSI:** `eventID` (PK) + `status` (SK) — serves the organizer's lobby (`status=PENDING`) and roster (`status=ATTENDEE`) screens (`P-82`/`P-83`) and doubles as `MatchAttendees`' own "who's currently admitted" lookup; no `joinedAt`/ordering field, since nothing ruled requires one. **`CascadeDelete` does not scrub `matchedPhotoIDs` on photo delete** — a deleted photo's id is left stale in the set and silently excluded at read time, since `BatchGetItem` against `Photos` simply returns nothing for a missing id; no extra write-time cleanup needed. Full write-up (options, named scenarios, scorecards) in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; tight answer in `LOCKED_TECH_DECISIONS.md`; register entry in `TECH_DECISIONS.md`.

**`Faces` — ruled 2026-08-12.** PK = `rekognitionFaceID` (fixed by `T-04`'s original ruling), no SK. Fields: `rekognitionFaceID`, `eventID`, `photoID`. **Correction to how this was first written up:** `Faces` itself stores no match results, but matches are *not* computed live at read time either — they're computed once per batch and persisted separately, on `EventAttendees` (see `MatchAttendees` below). One GSI: `eventID` (PK) + `photoID` (SK), confirmed over a two-GSI split because `Gallery/photos` already holds `eventID` for free (from its own `Photos` row read) before calling `CascadeDelete`, so a single combined GSI serves both the single-photo lookup and `CascadeDelete`'s whole-event cleanup query at no extra cost. Separately, ruling `Faces` surfaced the same shape of gap `Events` did: `P-44`/`P-52` photo deletion needs `DeleteFaces` + `Faces` row deletion + an `Events` counter decrement, reach `Gallery/photos` doesn't have under one-table-per-Lambda IAM. **Ruled: reuse `EventTeardown` for this too, renamed `CascadeDelete`** — `Gallery/photos` gains a `DELETE` endpoint that invokes `CascadeDelete` (an `lambda:InvokeFunction` grant only, no direct table/Rekognition access), rather than widening `Gallery/photos`'s own role or building a near-duplicate second cascade Lambda. Lambda count stays 9, CI/CD jobs stay 10. Full write-up (including the rejected alternatives and the scorecard) in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; tight answer in `LOCKED_TECH_DECISIONS.md`.

**`EventAttendees` — ruled 2026-08-12, closing `T-04`'s follow-up.** Base key already fixed by `T-04`'s original ruling: PK = `userID`, SK = `eventID`.

**A gap surfaced scoping it, a different shape from `CascadeDelete`'s — ruled 2026-08-12.** `P-16`/`P-93` require a per-attendee `SearchFaces` fan-out (one call per attendee with a face reference, re-run whenever a batch lands — distinct from `IndexOnePhoto`'s per-*photo* fan-out), and `P-73`/`P-69` require its answer to persist (computed once, not live; must survive the user later deleting their face reference). Nothing in the pipeline ran this, and nothing was scoped to store the answer. **Ruled: a new Distributed Map step, `MatchAttendees`, added to the existing `PipelineHandler` state machine** — same mechanism `T-02` already uses for `IndexOnePhoto` (a `SearchFaces` call has the same Rekognition account-wide throttle as `IndexFaces`, needing the same per-item retry/tolerated-failure-%), rejecting a hand-rolled loop in `Finalize` and a new Stream-triggered Lambda, both of which would silently reopen the exact problem `T-02` was ruled to avoid. No new Lambda, no new CI job — `PipelineHandler` already isn't one-table-scoped (that isolation only applies to the 5 API-facing domain Lambdas), so gaining `EventAttendees` on its manifest is a normal `T-07` permission addition. The result — each attendee's matched `photoID`s, resolved from `SearchFaces`' `rekognitionFaceID` hits via the `Faces` table's GSI — is stored as a **String Set** (`matchedPhotoIDs`) directly on that attendee's own `EventAttendees` row, chosen over a List since ordering is unused (the gallery re-sorts by upload time regardless) and a Set gives free dedup plus an idempotent `ADD`.

**All three sub-questions on `EventAttendees` ruled 2026-08-12, closing `T-04`'s follow-up:**
1. **Status field: 4 values — `PENDING`, `ATTENDEE`, `LEFT`, `BLOCKED`.** Row never deleted; leave (`P-46`) and eject/deny (`P-29`) are `UpdateItem` status flips on the same row, not delete/recreate — `matchedPhotoIDs` survives a leave/rejoin cycle, and `P-29`'s blocklist already forced "never delete" for `BLOCKED` regardless, so one mechanism now covers every membership transition.
2. **GSI: `eventID` PK + `status` SK, as proposed.** Serves the organizer's roster (`P-82`)/lobby (`P-28`) screens and doubles as `MatchAttendees`' own "who's currently admitted" lookup. No `joinedAt`/ordering field added — nothing ruled requires one.
3. **`CascadeDelete` does not scrub `matchedPhotoIDs` on photo delete.** A deleted photo's id is left stale in the set and silently excluded at read time, since `BatchGetItem` against `Photos` simply returns nothing for a missing id — cheaper than an eager scrub that would cost up to 100 extra writes per deleted photo at `P-93`'s scale, for a cleanup no user can perceive.

Full write-up (options, named scenarios, scorecards) in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; tight answers in `LOCKED_TECH_DECISIONS.md`; register entry in `TECH_DECISIONS.md`. **`T-04`'s follow-up is now fully closed — all 6 tables ruled, technology phase has nothing left open, implementation is next.**

**`Photos` — ruled 2026-08-12.** PK = `photoID`, no SK. Fields: `photoID`, `eventID`, `uploaderID`, `uploaderDisplayName`, `uploaderEmail`, `uploadedAt`, `filename`, `contentHash`, `sizeBytes`, `s3Key`, a thumbnail key. No `status` field — a failed (`P-56`) or deduped (`P-38`) photo is never written here, so every row succeeded by definition. GSI 1 — gallery: `eventID` (PK), `"{uploadedAt}#{filename}"` (SK); `Query(ScanIndexForward=false)` with DynamoDB's own `LastEvaluatedKey` as the cursor implements `P-57`+`P-16`'s forced pagination directly, filename tiebreak included. GSI 2 — dedup: `eventID` (PK), `contentHash` (SK), implementing `P-38`'s per-event duplicate check. Uploader attribution (`P-86`/`P-99`) is **snapshotted onto the row at upload time** rather than live-joined to `Users` — `P-84` made display names editable, and `P-99`'s "always showed the same" name/email reads as a frozen snapshot, not a live one; a live join would also cost a `BatchGetItem` per gallery page for no ruled benefit. `sizeBytes` is stored per row so `P-85`'s storage total on `Events` can be maintained as an atomic `UpdateItem` counter (increment on write, decrement on delete) — already the mechanism named for this in the DynamoDB primer, not a fresh choice. Full write-up in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; tight answer in `LOCKED_TECH_DECISIONS.md`.

**`Jobs` — ruled 2026-08-12.** One row per upload batch (`P-36`/`P-37`: a batch is either a ZIP or a multi-file selection, from either an organizer or an attendee). Base table PK = `jobId`, no SK. Fields on the row: `jobId`, `eventID`, `uploaderID`, `status` (in-progress → terminal per `P-53`/`P-55`), `succeededCount`/`failedCount` (`P-55`), `startedAt` (for `P-53`'s hard lifetime ceiling). The status-polling endpoint (`GET /events/{eventId}/jobs/{jobId}/status`) reads this by `jobId` directly — no index needed there. **No retry/backoff field** — dropped 2026-08-15 while scoping `db_api`, see the top entry's `D-127` note.

**The GSI question — ruled.** `P-100` requires the batch's result to be visible to **the uploader specifically** whenever they next open the event — including from a fresh tab/session where no `jobId` survives client-side (the UI plan is a "come back later" button, not a link carrying the job's id forward). A naive GSI keyed on `eventID` alone (sorted by time, "give me the newest job for this event") was surfaced as wrong: with two people uploading around the same time (e.g. Meera and Sam both contributing to Priya's trip), it would return whichever job finished last, potentially showing Meera the wrong person's result. **Ruled: a GSI keyed on a composite partition key, `eventUploaderKey = "{eventID}#{uploaderID}"`, with `startedAt` as the sort key.** `Query(eventUploaderKey = "evt_123#user_456", ScanIndexForward=false, Limit=1)` returns exactly that uploader's own most recent job in that event, with no cross-contamination between concurrent uploaders. Confirmed as a GSI, not an LSI — an LSI must share the base table's partition key (`jobId`), which cannot express "group by event+uploader" at all; this isn't a close call. Two lesser costs were named and accepted as non-issues at Glimpses' scale: (1) write amplification — every `Jobs` write that touches the GSI's key attributes also writes to the GSI's copy, negligible at a few batches per event; (2) GSI reads are only ever eventually consistent, irrelevant here since the check-back-later flow is minutes-to-days later, not milliseconds after the write. A second option — a pointer written onto the uploader's `EventAttendees` row instead of a GSI — was weighed and rejected: it would give the ingestion Lambda IAM write access to a second table it doesn't otherwise touch, the same one-table-per-Lambda isolation `CascadeDelete` (then `EventTeardown`) exists to protect. Full write-up in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; tight answer in `LOCKED_TECH_DECISIONS.md`.

**A real complication surfaced mid-session, not a loose end to lose:** ruling `Events`' automatic-deletion mechanism (TTL, see below) exposed a gap that actually traces back to `P-34` — no existing Lambda had IAM reach across the tables + S3 + Rekognition a full event teardown needs. Resolved by adding a 9th Lambda, `EventTeardown` (renamed `CascadeDelete` 2026-08-12, see the `Faces` entry above), which **amends `T-03`'s Lambda count (8→9) and `T-06`'s CI/CD job count (9→10)** — both updated in `LOCKED_TECH_DECISIONS.md`, with the reasoning in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section. This same shape recurred on `Faces` 2026-08-12 (see above) — a per-table schema decision can reveal that an access pattern has no Lambda able to serve it, and that's a `T-03`/`T-06` amendment, not something to resolve quietly inside the table's own write-up.

---

## The technology phase — read this before the first decision

**Opened 2026-08-06,** on the user's instruction: they want to *"dive deep… replace mistakes of Glimpses v1… understand it all before implementing anything… and make sure they all work and align with the `LOCKED_PRODUCT.md` decisions."* Those are three standing requirements, not preferences:

1. **Depth over speed.** The user is not looking for a stack list — they are looking to understand each choice well enough to defend it. Explain what the thing physically is before naming it, use the named cast, and finish with a scorecard. Same method that worked for all 100 product rulings.
2. **Every choice is checked against `HANDOFF.md` §7 and §9.** v1's mistakes are *written down* — the drift, the dead dependencies, the silent alarms, the two unresolved bugs. §9 lists eight fork points v1 actually hit. Do not re-derive them from scratch and do not repeat them by omission.
3. **Technology may never re-open product.** This is the load-bearing rule of the phase.

### The one-directional rule

**Product constrains technology. Technology never quietly re-rules product.** If a stack choice would make a `P-nn` awkward, expensive or impossible, that is **a revision request the user rules on** — surfaced explicitly, never resolved by implementation. v1 failed exactly here: React 18 planned and 19 shipped, FastAPI taught and never used, Powertools shipped in the layer and never wired, CORS restriction implied by a variable and never enforced. **Each of those was a decision made by drift.**

### What the product rulings already deleted from v1's technology burden

Worth knowing before designing anything, because it is a real reduction in surface area and the payoff for locking product first:

| v1 carried this | Removed by |
|---|---|
| Google OAuth federation — **one of v1's two unresolved bugs**, never fixed | `P-03` — no social sign-in |
| `SearchRateLimit` table, 10 searches/hour/user/event, and the `search` endpoint itself | `P-16`, `P-73`, `P-79` — no user action triggers a search |
| `galleryMode` `PUBLIC`/`PRIVATE`, the `403 SEARCH_REQUIRED` gate, the `hasSearched` flag | `P-07` — admission is the only access control |
| Configurable `similarityThreshold` (default 80, min 70) | `P-80` — fixed at 80, exposed to nobody |
| A user-set event `date` field | `P-89` — system "Created" timestamp only |

**Do not inherit v1's data model or Lambda shape by default.** `HANDOFF.md` §9 says the gallery, search and download Lambdas were never built past stubs — there is no working shape to inherit there, and the rebuild should design them from the rulings up.

### Agenda, ordered by what unblocks what

**One at a time, options first, user rules.** The order matters — each gates the ones under it.

| # | Decision | Why here | Product inputs |
|---|---|---|---|
| 1 | **Runtime and language** — Node/TypeScript vs Python — **RULED 2026-08-08: all Python (`T-01`)** | Resolved: middy and DynamoDB Toolbox, the main draw of a Node backbone, were separately ruled unnecessary (Powertools' router already covers routing/response/CORS; the multi-table data model doesn't have the single-table key-collision problem Toolbox solves) — once neutralized, Python's more mature router and single toolchain won out over Node's small cold-start edge. `handler → manager → procedure/converter → DAO` carries over as a Python file-layout convention. See `TECH_DECISIONS.md`/`LOCKED_TECH_DECISIONS.md`/`TECH_EXPLANATIONS.md` `T-01` | `P-35` HEIC→JPEG |
| 2 | **Ingestion orchestration** — SQS + DLQ vs Step Functions Distributed Map — **RULED 2026-08-08: Step Functions Distributed Map (`T-02`)** | Chosen over v1's SQS for removing the hand-rolled polling loop and getting per-item visual execution history. Item list via S3 `ItemReader`, never passed between states. `MaxConcurrency` is a Terraform variable bound to the account's real Rekognition `IndexFaces` quota (this account measured 5 TPS, below the ~50 TPS default; increase requested). See `T-02` in the three tech files | `P-100`, `P-56`, `P-53`, `P-55`, `P-94` |
| 3 | **API shape** — one Lambda per endpoint (v1) vs consolidated router — **RULED 2026-08-08: domain-grouped, 8 Lambdas total (`T-03`, pipeline shape revised same day); amended 2026-08-09 to 9 Lambdas — see `CascadeDelete` below** | Chosen over v1's one-per-endpoint (tightest IAM, most boilerplate) and full consolidation (least boilerplate, widest blast radius). 5 API Lambdas scoped by table, 1 consolidated pipeline Lambda (`PipelineHandler`, revised from 4 named functions same day — no external invocation path, so the API-consolidation blast-radius argument doesn't transfer), plus `db-api` (generic `Jobs`-status writer, deliberately a separate Lambda over a shared code library), a shared HEIC→JPEG converter, and — added during the `T-04` follow-up as `EventTeardown`, renamed `CascadeDelete` 2026-08-12 when its scope widened to single-photo deletion — `CascadeDelete` (cross-table + S3 + Rekognition delete cascades, event- and photo-level). API Gateway flavour (HTTP vs REST API) ruled 2026-08-09: **REST API**, for WAF. See `T-03` in the three tech files | — |
| 4 | **Data model** — 7 single-purpose tables (v1) vs single-table — **RULED 2026-08-08: multi-table, 6 tables (`T-04`)** | Decided on IAM grounds: `T-03` already scoped each Lambda's role to one table, structural under multi-table, hand-built under single-table. `SearchRateLimit` dropped (v1's 7th table) since `P-16` killed search. Per-table fields/GSIs ruled 2026-08-09 → 2026-08-12, all 6 tables closed. See `T-04` in the three tech files | `P-57`+`P-16` force cursor pagination; `P-85` needs a byte counter that survives `P-44`/`P-52`/`P-38`/`P-55` — both implemented, landing in `Photos` |
| 5 | **Rekognition collection layout and lifecycle** — **RULED 2026-08-08: one collection per event (`T-05`)** | Decided on security-boundary grounds: `P-07`'s no-cross-event-visibility is AWS-enforced under per-event collections, versus dependent on application-code filtering under a shared collection. Collection id tracked on `Events` (`rekognitionCollectionID`) so a teardown script can clean up orphans without Terraform visibility — closes the exact `HANDOFF.md` §9 fork point. See `T-05` in the three tech files | `P-98`, `P-32`, `P-52` |
| 6 | **Terraform state and naming** — **RULED 2026-08-08: S3 + native locking (`T-06`)** | v1 used local state and hit a naming mismatch between Terraform resources and module filenames | `P-95` — parameterise or the region is expensive to reverse |
| 7 | **Observability, IAM granularity, CORS, secrets — RULED 2026-08-09 (`T-07`)** | All four are §7 drift items — decide deliberately or repeat them | `P-81` means nothing alerts users; alarms are for the operator only |
| 8 | **Testing approach and CI/CD** — **RULED 2026-08-09: 3-tier pyramid, `moto`-backed unit/integration, manual-only E2E, tests not wired into Jenkins (`T-08`)** | v1's pyramid and its explicit failure-path tests are worth reusing; Jenkins is already named | — |

### Loose threads — sub-decisions left open inside already-ruled items

Not their own agenda lines, but flagged explicitly rather than silently assumed:

- **`T-03` — API Gateway flavour (HTTP API vs REST API).** RULED 2026-08-09: **REST API**, for AWS WAF against Rohan's threat model, accepting the 3.5x cost over HTTP API. Confirms `T-01`'s `APIGatewayRestResolver` needed no correction. Full writeup in all three tech files.
- **`T-04` — per-table fields, PK/SK choices beyond the primary id, and GSI definitions**, all 6 tables. **CLOSED 2026-08-12** (started 2026-08-09/10). All 6 tables ruled — `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`. This is where `P-57`+`P-16`'s forced cursor pagination and `P-85`'s storage-byte counter actually get implemented — that lands specifically in `Photos`, ruled 2026-08-12.
  - **`Users` — ruled.** PK = `userID` (Cognito `sub`), no SK, no GSI. Fields: `userID`, `displayName`, `email` (full-mirrored from Cognito rather than pointer-only, since Glimpses never allows email changes post-signup, so the drift risk a mirror would otherwise carry is moot). No GSI needed — every access path already arrives holding a `userID`.
  - **`Events` — ruled.** PK = `eventID`, no SK. Fields: `eventID`, `organizerID`, `name`, `accessCode`, `joinPolicy`, `contributionPolicy`, `status`, `lastUploadAt`, `archivedAt`, `photoCount`, `attendeeCount`, `storageBytes`, `qrCodeURL` (`similarityThreshold` deliberately excluded — it's a hardcoded constant per `P-26`/`P-80`, not per-event data). GSI 1: `organizerID` (PK) + `status` (SK) — organizer's dashboard. GSI 2: `accessCode` (PK) — the join flow. GSI 3: `status` (PK) + `lastUploadAt` (SK) — the scheduled archive-scan for `P-77`/`P-78`. **Deletion mechanism (the `P-77` second 30 days) ruled: DynamoDB TTL**, not a second scheduled scan — a `deleteAt` attribute written at archive time lets DynamoDB expire the item for free, with a DynamoDB Stream on `Events` firing a cleanup Lambda on removal. TTL's known imprecision (AWS: typically within 48h) is compatible with `P-77`'s own "roughly 60 days" wording.
  - **Surfaced along the way, not a `T-04` detail — a `T-03`/`T-06` amendment:** ruling `Events`' deletion mechanism exposed that `P-34`'s manual event delete (and the new automatic TTL delete) needs IAM reach across `Events`/`Photos`/`Faces`/`EventAttendees`/S3/Rekognition that no existing Lambda has — every API Lambda is deliberately one-table-scoped. **Ruled: a dedicated 9th Lambda, `EventTeardown`**, over widening `Events`' own role, specifically to avoid giving back the IAM-isolation argument that won `T-04` its multi-table ruling in the first place. See `T-03`/`T-06` rows in the decision log above.
  - **`Jobs` — ruled.** PK = `jobId`, no SK. GSI: `eventUploaderKey` (`"{eventID}#{uploaderID}"`) PK + `startedAt` SK, so an uploader can `Query` their own most recent job in an event without holding a `jobId` — needed for `P-100`'s "result survives leaving" without cross-contaminating concurrent uploaders' results.
  - **`Photos` — ruled.** PK = `photoID`, no SK. GSI 1 (gallery): `eventID` PK + `"{uploadedAt}#{filename}"` SK, implementing `P-57`+`P-16`'s forced cursor pagination via DynamoDB's own `LastEvaluatedKey`. GSI 2 (dedup): `eventID` PK + `contentHash` SK, implementing `P-38`. Uploader attribution snapshotted at upload time (not live-joined), matching `P-99`. `sizeBytes` per row backs `P-85`'s atomic storage-byte counter on `Events`.
  - **`Faces` — ruled 2026-08-12.** PK = `rekognitionFaceID` (fixed by `T-04`'s original ruling), no SK. Fields: `rekognitionFaceID`, `eventID`, `photoID` only. **Correction:** `Faces` itself stores no match results, but matches are *not* computed live at read time either — they're computed once per batch and persisted on `EventAttendees` instead (see `MatchAttendees` below). One GSI: `eventID` PK + `photoID` SK, confirmed over a two-GSI split since `Gallery/photos` already holds `eventID` for free before calling `CascadeDelete`, so one combined GSI serves both the single-photo lookup and the whole-event cleanup query at no extra cost.
  - **Same shape of gap recurred on `Faces`, ruled 2026-08-12 — a `T-03`/`T-06` amendment, not a `Faces`-internal detail:** `P-44`/`P-52` photo deletion needs `DeleteFaces` + `Faces` row deletion + an `Events` counter decrement, reach `Gallery/photos` doesn't have under one-table-per-Lambda IAM. **Ruled: reuse `EventTeardown`, renamed `CascadeDelete`** — `Gallery/photos` gains a `DELETE` endpoint invoking it, rather than widening `Gallery/photos`'s own role or building a near-duplicate second cascade Lambda. Lambda count stays 9, CI/CD jobs stay 10.
  - **`EventAttendees` — fully ruled 2026-08-12, closing `T-04`'s follow-up.** Base key fixed: PK = `userID`, SK = `eventID`. **A third gap shape surfaced, ruled 2026-08-12:** `P-16`/`P-93`'s per-attendee `SearchFaces` fan-out had no Lambda step running it and no table storing its answer. **Ruled: a new Distributed Map step, `MatchAttendees`, added to `PipelineHandler`'s existing state machine** (reusing `T-02`'s exact mechanism — same Rekognition throttle as `IndexOnePhoto`, same need for per-item retry/tolerated-failure-%), over a hand-rolled `Finalize` loop or a new Stream-triggered Lambda (both reopen the throttling problem `T-02` solved). No new Lambda/CI job — `PipelineHandler` was never one-table-scoped. Result stored as a String Set (`matchedPhotoIDs`, not a List — dedup/idempotent `ADD` over unused ordering) on the attendee's own row. **Three sub-questions ruled:** (1) **status field: 4 values — `PENDING`, `ATTENDEE`, `LEFT`, `BLOCKED`; row never deleted, leave/eject/deny are status flips on the same row** (not delete-recreate), so `matchedPhotoIDs` survives a leave/rejoin cycle and `P-29`'s blocklist works the same way `BLOCKED` already required. (2) **GSI: `eventID` PK + `status` SK, as proposed** — serves the roster/lobby and `MatchAttendees`' own lookup; no `joinedAt`/ordering field added, since nothing ruled requires one. (3) **`CascadeDelete` does not scrub `matchedPhotoIDs` on photo delete** — stale ids are filtered out for free at read time via `BatchGetItem` against `Photos`, cheaper than an eager scrub that would cost up to 100 extra writes per deleted photo at `P-93`'s scale with no user-visible benefit.
  - Full write-up (including the DynamoDB primer — PK/SK/GSI/LSI, `Query`/`Scan`/`GetItem`/`BatchGetItem`/`UpdateItem`/`TransactWriteItems`) lives in `TECH_EXPLANATIONS.md`'s `T-04` follow-up section; the tight schema answers are in `LOCKED_TECH_DECISIONS.md`; the register entry is in `TECH_DECISIONS.md`. **`T-04`'s follow-up is now fully closed — all 6 tables ruled, the technology phase has nothing left open.**

### `T-06` — Terraform state and naming (ruled 2026-08-08)

**Fully written up in `TECH_DECISIONS.md`, `LOCKED_TECH_DECISIONS.md`, and `TECH_EXPLANATIONS.md`** — five sub-decisions: (1) state backend — S3 + native S3 locking (`use_lockfile = true`, no DynamoDB), versioning on; (2) per-Lambda Terraform module layout, replacing v1's centralized `functions` module; (3) deploy discipline — a separate dedicated CI job runs the untargeted `apply` that builds/updates the state machine, never piggybacked on a single Lambda's own pipeline; (4) CI/CD granularity — originally 8 per-Lambda Jenkinsfiles + 1 dedicated untargeted-apply job = 9 total, **amended 2026-08-09 to 10 total (9 per-Lambda + 1) following `EventTeardown`'s addition**; (5) naming — a fixed `glimpses-` prefix applied identically everywhere, no environment branching, no mapping file. See `T-06` in the three tech files for full reasoning, options considered, and the worked naming table.

### `T-07` — Observability, IAM granularity, CORS, secrets (ruled 2026-08-09)

**Fully written up in `TECH_DECISIONS.md`, `LOCKED_TECH_DECISIONS.md`, and `TECH_EXPLANATIONS.md`** — four sub-decisions, all ruled the same day.

**1. Observability.** (i) logging library — Powertools `Logger` (structured JSON), no new dependency since `T-01` already ships Powertools; (ii) `log_event=True` — the full incoming request is auto-logged on every invocation, **ruled against the recommendation** (which favored logging only explicit fields, given the `P-19` selfie/`P-68` deletion right sitting in request bodies); (iii) log retention set to **3 days**, a direct consequence of (ii); (iv) tracing — **no X-Ray**, ruled against the recommendation, on cost/effort grounds; (v) custom metrics — **none**, AWS-default Lambda metrics only, `P-100`'s failure-percentage stays a manual read; (vi) alarms wired to an **SNS topic + email subscription**, fixing `HANDOFF.md` §7's silent-alarm bug directly; (vii) the hardcoded-alarm-list bug confirmed **already closed** by `T-06`'s per-Lambda `cloudwatch.tf`, not a fresh decision — flagged out loud rather than assumed. Alarm content ruled narrow: `Errors > 0` over 5 minutes, identical on all Lambdas (8 at time of ruling, now 9 following `EventTeardown`'s addition during the `T-04` follow-up).

**2. IAM granularity.** Strict one-role-per-Lambda kept (unchanged shape from `T-03`/`T-04`), but each Lambda's permission list is **derived from a per-Lambda manifest of its actual AWS calls**, not hand-guessed upfront — directly answering `HANDOFF.md` §7's "permission missing, discovered only at runtime," rather than repeating it (hand-guessed, v1's approach) or trading it for the "tighten later, never actually tightened" risk `HANDOFF.md` documents elsewhere in the same section.

**3. CORS.** Restricted to the real frontend origin(s), via the `app_urls`-style Terraform variable v1 already had but never wired through — now actually connected, not `*`. Local dev origins need adding to the allowed list.

**4. Secrets hygiene.** A pre-commit **`gitleaks`** scanner added from the repository's first commit — the direct fix for `HANDOFF.md` §6's two real incidents (a committed CloudFront private key, a plaintext AWS-key CSV).

See `T-07` in the three tech files for full reasoning and the options considered at each step.

### `T-08` — Testing approach and CI/CD (ruled 2026-08-09) — agenda closed

**Fully written up in `TECH_DECISIONS.md`, `LOCKED_TECH_DECISIONS.md`, and `TECH_EXPLANATIONS.md`** — seven sub-decisions. Pyramid kept 3-tier (unit → integration → E2E), matching v1. Unit tests use `moto` (matches v1; LocalStack's free tier doesn't cover Rekognition, the app's most-used service). v1's explicit failure-path list carried over mostly as-is, with one adaptation (the DLQ/`COMPLETE_WITH_ERRORS` test becomes a Distributed Map per-item-failure test, since `T-02` removed the DLQ), one drop (the rate-limiter test, since `P-16` killed search), and one addition (an IAM-manifest-drift test, closing `T-07`'s manifest approach against silent drift — directly answers `HANDOFF.md` §7). Integration tests stay scoped to one Lambda's own internal chain, not cross-Lambda (Step Functions already guarantees handoff shape). E2E runs against a dedicated test event created/destroyed per run, and is manual-only — never wired into Jenkins — to control real Rekognition cost. **CI/CD wiring ruled against the recommendation:** tests are not part of any of `T-06`'s 9 Jenkins jobs at all; the user tests locally and only pushes to trigger a Jenkins deploy once local tests pass, making Jenkins a pure deploy mechanism rather than a CI gate. No formal coverage threshold. **This closes the technology agenda — all 8 items ruled.**

### How this phase is recorded — settled 2026-08-06

**Three files, not two** — a deliberate departure from the product convention, because this is explicitly a build-and-learn project and the user wants to understand and justify each decision, not just reference it:

| File | Role | Analogous to |
|---|---|---|
| `TECH_DECISIONS.md` | The raw register — every open technology question, one row each | `PRD.md` |
| `LOCKED_TECH_DECISIONS.md` | The finalized answer only, kept tight — what to build | `LOCKED_PRODUCT.md`'s ruling line, without its reasoning |
| `TECH_EXPLANATIONS.md` | The teaching material — what the thing physically is, how it works, the alternatives and why one won | New. Product never needed this; behaviour didn't require a concept explainer |

Same `T-nn` id runs through all three, permanent, never renumbered. A decision moves left to right: raised in `TECH_DECISIONS.md` → ruled and copied tight into `LOCKED_TECH_DECISIONS.md` → written up conceptually in `TECH_EXPLANATIONS.md`. All three files exist, scaffolded by agenda area, with 0 decisions ruled so far.

## The rate-limit question — closed 2026-08-06

The user's *"no rate limits as i said"* was ambiguous and was put back to them. **They confirmed it meant the caps, not `P-97`:** *"by no rate limits i meant that no 1000 photos or 5 max active events etc... and that rate limit is something we have ruled on already so no issues."*

**`P-97` stands exactly as ruled** — access-code attempts are limited per account and per IP, in application code. Only its *thresholds* remain unset, which is what `P-97`'s own last bullet already says and belongs with the join flow. The caps reading was `P-40`, already reversed by `D-115`. **No ruling changed; no new `D-nn` row, because nothing was decided that was not already decided.**

**Build cost is a legitimate reason to rule, and the user uses it.** `D-119` was decided purely on "not worth it for a portfolio project", with no options requested. When a ruling's cost is mostly *implementation* rather than *product*, say so plainly and early — it may be the deciding factor.

**The user commits; the AI never does.** All revision work stays as uncommitted working-tree changes. Stated explicitly 2026-08-06: *"all commits will be made by me only not u so pls do not push or commit anything."*

---

## Read these first, in this order

| File | What it holds |
|---|---|
| `Miscellaneous/PRODUCT_WALKTHROUGH.md` | **Start here.** The product described as the user experiences it, end-to-end, with ruling ids linked. One sentence per ruling, no "why" reasoning. ~541 lines, readable in one sitting. |
| `Miscellaneous/LOCKED_PRODUCT.md` | **The source of truth.** Every ruling as `P-nn` with full reasoning, accepted costs, and design obligations. Authoritative if it ever disagrees with the walkthrough. ~900 lines. |
| `Miscellaneous/PRD.md` | **The decision register.** Every question as `D-nn`. Rows marked RULED point at their `P-nn`; some rows carry design obligations and assumptions flagged for verification. **Revisions go here first.** |
| `Miscellaneous/CLAUDE.md` | This project's governance instructions in the repo. Read it before starting. |
| `Miscellaneous/HANDOFF.md` | v1 retrospective. Historical only. |

Do **not** re-derive decisions already in `LOCKED_PRODUCT.md`. Do **not** duplicate its content elsewhere. **All changes must go through `PRD.md` and `LOCKED_PRODUCT.md`, with the spec as the authoritative source.**

---

## How this project works — read before doing anything

**The user makes every decision. The AI presents options with honest tradeoffs and a recommendation, then waits.**

This is the core principle of the rebuild. In v1 the user let an AI dictate architecture and inherited choices they later regretted. Violating this is the single worst thing you can do.

Concretely:
- Present 2–3 genuine options per question, each with honest cost — not a token alternative next to an obvious winner.
- Mark the recommendation, but **never assume it**.
- Go **one decision at a time.** The user has repeated this across sessions.
- When a ruling contradicts an earlier one, say so plainly and rewrite the affected `P-nn` rather than layering an exception.
- **Speed does not come out of the user's decision rights.** Tighter explanations are good; bundling decisions or ruling by implication is not.

**Revisions are treated as fresh decisions.** If the user says "I want to change P-20", that is not an override of a prior ruling — it is a new ruling that overwrites it. The entire cluster it affects should be audited, because one reversal cascades (`P-20`/`P-68`/`P-73`/`P-75`/`P-76` all share "forward-only"; reverting one may require reconsidering others).

### How to explain things

This has worked across three sessions and should stay the default:

- **Drop the jargon.** Ingest, gate, trigger, scope, policy branch — these obscure rather than clarify.
- **Use named, concrete scenarios** and run every option through all of them. Recurring cast: **Meera** (attendee wanting her own photos), **Arjun** (wedding photographer, bulk ZIP), **Priya** (collaborative trip organizer), **Rohan** (attendee with no selfie / adversarial case).
- **Build up from what the thing physically is** before naming it. Explain that EXIF is "a small block of text inside the photo file", that a ZIP is "many files in one box", that a QR is "a picture encoding a link".
- **Then a scorecard** — options as rows, scenarios as columns, ✅/⚠️/❌ in cells. The user rules quickly and confidently every time this is used.

### Process rules learned the hard way

1. **Do not bundle two decisions into one set of options.** If an option contains an "and", check whether it is two rulings. On 2026-08-05, five questions were split before being presented.
2. **Say out loud when you write in an assumption.** Minor recommendations may be written into the spec marked clearly — but only for genuinely minor points, always announced. When a consequence is *forced* by existing rulings rather than chosen, label it "forced, not ruled" and invite override.
3. **Audit the spec's existing wording after every ruling.** Eight entries needed rewriting on 2026-08-05 alone because new rulings made their wording false. If a new ruling makes an old bullet untrue, rewrite it rather than layering an exception.
4. **Every changed line should trace to the user's request.** Don't "improve" adjacent code or reasoning unasked. Match existing style. If you notice unrelated dead code or weak arguments, mention it — don't delete it.
5. **Do not moralise about privacy. Added 2026-08-06 at the user's explicit request:** *"i think we might be emphasizing way too much on this permissions etc... which is causing a lot of changes, maybe relax it a bit the privacy etc.. part as it is a product such as is."* The first `P-86` write-up called the ruling "the largest privacy exposure in the spec", added a paragraph dramatising an attacker harvesting emails, and inflated `§7` — which manufactured cascade work the ruling never required. **State the consequence in one line and move on.** This is a photo-sharing app where people see who contributed what; that is ordinary. Keep *design obligations* (they protect earlier rulings from drift), cut the alarm.
6. **Check the spec before describing it.** On 2026-08-06 a cascade list naming five rulings was given to the user from memory and was partly wrong, and the user's item 10 turned out to be **already built** (`P-64`/`P-65`) — the "conflict" was a stale sentence in `P-07`. Read the rulings first; several of the user's requests may already be satisfied.

Document conventions: `P-nn` and `D-nn` ids are **permanent and never reused or renumbered**. Questions killed by a ruling are marked `DISSOLVED`, not deleted. **Recount statuses from table rows; never decrement a figure.**

**How revisions are recorded** — the convention the file already set with `D-99`/`P-31`, followed again on 2026-08-06: a revised ruling **keeps its `P-nn` and is rewritten in place**, marked *(Rewritten YYYY-MM-DD by `D-nn`)*. Only a genuinely new question gets a new `P-nn`. The old decision-log row is marked *(Superseded — see the row above)* rather than deleted, and a new dated row goes at the **top** of the §11 table.

---

## The revision queue — the live worklist

The user reviewed `PRODUCT_WALKTHROUGH.md` on 2026-08-06 and raised 11 changes. **The queue is now empty** — all eleven are resolved, and three further items were settled in the same session.

### Also settled 2026-08-06, outside the eleven

| Ruling | Change | Register row |
|---|---|---|
| `P-95` **rewritten** | Region named: **`ap-south-1` (Mumbai)**. Obligation: verify Rekognition is available there before building | `D-124` |
| `P-74` **rewritten** | **Account deletion does not exist and will not be added.** `P-75` and `P-76` **DISSOLVED**, reasoning retained in place. `P-68`'s selfie deletion survives and is now the only withdrawal action | `D-125` |
| `P-100` **new** (item 4) | Progress shown on the open upload screen, retries explained as the reason for a delay, and — the load-bearing half — **ingestion never depends on the uploader staying**; the `P-55` result is stored on the event | `D-126` |
| **Collection architecture** | Not ruled — the user deferred it explicitly to the technology phase: *"for collections architecture we will see during the technology phase"* | `P-98` |

### Ruled on 2026-08-06 — nine rulings changed plus one wording fix, all cascades already applied

| Ruling | Change | Register row |
|---|---|---|
| `P-89` **rewritten** (item 11) | Name **editable**; optional **description added**, shown in the lobby too; **no user-set date** — a system "Created" timestamp, labelled as such. `P-28` amended | `D-121`, `D-122`, `D-123` |
| `P-29` **reaffirmed** (item 8) | **No change** — blocklist stays. Don't reopen without solving code rotation | `D-120` |
| `P-54` **rewritten** (item 3) | **ZIP top level only** — subfolders not opened; stated up front, and a no-photos-found ZIP says why | `D-119` |
| `P-07` **reworded** | Wording defect only — permission vs. presentation; no ruling changed | `D-118` |
| `P-31` **rewritten** (item 2) | **All share blocking removed** — an `ACTIVE` event is shareable at all times, ingestion irrelevant | `D-117` |
| `P-53` **re-founded** | Batch timeout kept, but justified by `P-55`'s final count instead of `P-31`'s deadlock | `D-117` |
| `P-82` **reversed** | Organizer's attendee/pending lists now show **display name + email** | `D-112` |
| `P-86` **reversed** | Every photo shows uploader **name + email**, visible to **everyone** | `D-113` |
| `P-83` **rewritten** | No member-list screen; uploaders identifiable from the gallery, non-uploaders not named | `D-113` |
| `P-99` **new** | Attribution persists unchanged after ejection *(originally "after account deletion or ejection" — narrowed the same day by `D-125`, which removed account deletion)* | `D-114` |
| `P-40` **reversed** | **No product limits at all** — no photo cap, no event cap, no attendee cap | `D-115` |
| `P-85` **revised** | Three informational numbers: photo count, attendee count, **storage used** | `D-116` |

**`P-29` was reopened and reaffirmed unchanged** (item 8, `D-120`) — the blocklist stays. Declined once it was clear that `P-90`'s permanent join code means ejection without a blocklist is undone by retyping the code. **Do not reopen without also solving code rotation.**

**Two items needed no ruling:**
- **Item 5** (ingestion speed) — parked as *technical, not product*. `P-94` already states its ~30 min is a design target never shown to users. Belongs in the SQS vs Step Functions Distributed Map comparison.
- **Item 10** (dual gallery) — **the product already did this.** The user thought `P-07` forbade a "my photos" view; `P-64` (filter toggle), `P-65` (opens on matches, toggle starts *on*), `P-21` and `P-69` already deliver it.

### The wording fix — done 2026-08-06 (`D-118`)

`P-07`'s second sentence (*"no mode in which an attendee sees only their own matches"*) contradicted `P-64` and has been corrected. The user confirmed the intent: **two views — your own photos, or the entire collection** — which is exactly what `P-64`/`P-65` already build. `P-07` now speaks only to permission. No ruling changed, no cascade.

**Where the bad phrasing came from, because the pattern will recur:** the 2026-08-03 decision-log row recording the removal of a matches-only *screen with its own permission* was phrased loosely, and that phrasing migrated into the ruling itself, where it later read as banning `P-64`'s *filter*. The log row is now annotated in place. **When a log row and a ruling disagree, the ruling's intent wins — but check whether the row seeded the error.**

---

## Where things stand

**Product: 100 rulings · 0 open · 0 questions waiting.** Four items are carried forward, none of them a product decision: `P-97`'s rate-limit thresholds, `P-98`'s collection architecture, `P-100`'s progress/retry mechanism and `P-88`'s bulk approval. The user deferred the middle two to the technology phase explicitly. `P-75` and `P-76` are **dissolved** — they still exist as ids and text, but describe nothing the product does. **Recount from table rows; never decrement** — `PRD.md` gained `D-117` through `D-126` on 2026-08-06.

Note that the count rose by only **one** (`P-100`) across ten register rows: `D-117`, `D-119`, `D-121`–`D-125` all rewrote existing `P-nn` in place, `D-118` was a wording fix and `D-120` a reaffirmation. Per convention, revisions keep their `P-nn`.

**Technology: nothing decided.** Deliberately deferred.

**Repo state:** `main` has three commits — b60e14a locking the product, 94217a0 adding the walkthrough, and da41e0e committing the 2026-08-06 revisions. Later edits sit uncommitted in the working tree; **the user commits when they choose.** Backend and Frontend are empty directories. No secret-scanner (gitleaks) installed yet.

### The product in one paragraph

Sign up with email, password and a display name, verifying by numeric code. Join an event with a 6-character code or by scanning its QR, either walking straight in or waiting in a lobby for approval. See every photo in the event immediately. If you've added a selfie to your profile, the event opens directly on the photos you're in, and they keep updating as more arrive — you're never asked to search, and there is no way to re-run matching. Anyone admitted can add photos unless the organizer turns that off, and can share the code onward — **the code works from the moment the event exists, even mid-upload.** Nobody is notified of anything, ever. **An event is a name plus an optional description, both editable; you never type a date, only a "Created" timestamp the system sets.** **Every photo shows who uploaded it — name and email — to everyone, and keeps showing it after they leave.** Photos download at full resolution, individually or as an archive. **Nothing is capped: no photo limit, no event limit, no attendee limit.** **Uploading is fire-and-forget: hand over the ZIP, close the tab, come back to photos.** **You cannot delete your account — only your selfie, which stops future matching.** Events go read-only after 30 days without an upload and are deleted 30 days after that.

*(Updated 2026-08-06. The bolded clauses are what the revisions changed — previously photos carried no attribution, events were capped at 1,000 photos / 5 per organizer, an upload's fate if you left was unstated, and account deletion existed.)*

### What changed on 2026-08-06

- **Thirteen rulings changed and two added** — `P-82`, `P-86`, `P-83`, `P-40`, `P-85`, `P-31` (with `P-53` re-founded), `P-07`, `P-54`, `P-89` (with `P-28`), `P-95`, `P-74` (dissolving `P-75` and `P-76`), plus new `P-99` and `P-100`. See "The revision queue" above and the decision log at the top of `LOCKED_PRODUCT.md` §11.
- **Every cascade was chased and applied.** §7 gained point 6, `P-41`'s citation was corrected, `P-52` gained a guard against filter-by-uploader, `P-74`'s deletion-screen disclosure moved to `P-72`'s privacy page when deletion itself was removed, `P-87`/`P-97`/`P-93`/`P-25` lost the cap they cited as their bound, and the §8 permission tables were updated. Superseded decision-log rows are marked in place rather than deleted.
- **Both recommendations were overridden on the privacy cluster and on the caps.** Recorded as overrides in the log, per convention.
- **The user asked for less privacy emphasis** — see the process rules below. The first draft of the `P-86` write-up was rewritten to cut it.

### What changed in the session before that

- **`PRODUCT_WALKTHROUGH.md` was written** — the readable, end-to-end walkthrough, grouped by user journey rather than decision order. Designed to be read in one sitting and checked against.
- **`SESSION_HANDOFF.md` and `CLAUDE.md` were updated** to reflect the product lock being complete.
- **First commit pushed to `main`** (b60e14a) — 6 files, 1,569 lines, including `.gitignore` with credential patterns v1 leaked.

### What still needs doing before the technology discussion

1. ~~**v1's leaked credentials need rotating**~~ — **the user deleted them on 2026-08-06** and no AWS resources from v1 remain. *Confirm once that the AWS key was deleted in IAM rather than only removed from the folder, and that the Google OAuth secret and CloudFront signing PEM were revoked at their sources too — a live key is usable even against an empty account.*
2. **Check AWS account creation date** — the 6-month free-tier credit clock is the project's real deadline.
3. **`gitleaks` installation and pre-commit hook** — before any real code is committed.
4. ~~**Any product revisions**~~ — **the revision phase is complete.** The technology phase is next.

---

## The remaining unruled/assumed items

These were flagged in the spec as open or explicitly assumed. They are *not* open questions in `PRD.md` — they are embedded in the rulings and marked as such.

| Item | Where marked | What it is |
|---|---|---|
| **Rate-limit thresholds** | `P-97` | The mechanism is locked; the numbers are not. Set them when the join flow is built |
| **Collection architecture** | `P-98` | Assumed one collection per event. **Deferred to the technology phase by the user on 2026-08-06**, in those words |
| **Progress and retry state** | `P-100` | How it is actually produced — SQS bookkeeping vs Step Functions execution state. **Deferred to the technology phase by the user on 2026-08-06.** `P-100` is an *input* to that choice, not a constraint on it |
| **Bulk approval of a waiting queue** | `P-88` | `P-88` removed *pre*-approval, not approving several waiting people at once. Left as an ordinary interface question |

*(Closed 2026-08-06: the AWS region, now `ap-south-1` by `D-124`; and whether account deletion exists, now ruled out by `D-125`.)*

**How progress and retry state are produced** is not on this list, because it is a technology question rather than an unruled product one — but `P-100` is a deliberate input to it, and its bullet says plainly: *do not let the stack choice quietly narrow what this ruling promises.*

---

## How to work with revisions

**The user will indicate a change by describing it in conversation.** You should:

1. **Understand what's changing** — ask clarifying questions if the scope is ambiguous. Is it just one ruling, or a cluster?
2. **Surface the cascade** — if `P-20` is revisited, note that `P-68`, `P-73`, `P-98` and `P-99` share "forward-only" and may need reconsideration too.
3. **Update `PRD.md` first** — mark the affected `D-nn` row as reopened or add a new one if needed, describing the proposed change.
4. **Update `LOCKED_PRODUCT.md`** with the new ruling, rewriting affected related entries, and adding a dated row to the decision log.
5. **Check the walkthrough** — does it still describe the product truthfully? Update it if the change affects user-facing behavior.
6. **Verify coverage** — grep the changed `P-nn` ids across all three files, and grep the *old* wording to catch stale claims elsewhere. On 2026-08-06 this caught false statements in `P-41`, `P-93`, `P-87`, `P-97`, `§7` and two §8 tables that no amount of reading the changed ruling would have surfaced.

If a change cascades into five rulings, present all five at once as a cluster, not serially — the user should see the full consequence.

**What worked well on 2026-08-06, worth repeating:** options presented as a short table of 2–3 genuine choices, each with a complexity note, run through the named cast (Meera, Arjun, Priya, Rohan — plus **Sam**, who self-deploys the repo from Terraform, introduced for the caps decision), then a scorecard with ✅/⚠️/❌. The user ruled in one line every time.

---

## Verified facts — researched, not recalled

### AWS cost model

- **Free Tier restructured 15 July 2025:** $200 credits, valid 6 months from account creation; no ongoing per-service allowance.
- **Binding constraint is time, not money:** a 1,000-photo wedding costs ~$1.26 for 60 days; $200 covers ~180 events; the 6-month expiry arrives first.
- **Indexing dominates, ~6× the cost of storing a photo** — one-time charge on arrival; retention cannot recover it.
- **Rekognition free tier:** 1,000 Group 1 images/month (both `SearchFaces` and `SearchFacesByImage`), 1,000 face vectors.
- **`SearchFaces` evaluates the whole collection in one call** — no pagination; one call per event regardless of photo count.
- **Searching by stored face ID bills identically to searching by image** — same Group 1 rate, same free-tier pool.
- **Rekognition's 15 MB S3-object limit is documented as unraisable.**
- **Bandwidth is the only unbounded cost** — scales with downloads; roughly $0.085/GB at CloudFront; 100 guests × 200 photos ≈ $1.70.

### Image handling

- **PNG is ~12× larger than JPEG q90 at 12 MP, and HEIC is already lossy** — PNG preserves degraded pixels, not quality.
- **PNG can exceed Rekognition's 15 MB limit** on detailed photos; JPEG q90–95 at ~1 MB is standard.
- **iOS auto-transcodes HEIC→JPEG on browser file inputs** unless `accept` lists `image/heic` (which inverts it to hand back HEIC). Use `accept="image/jpeg,image/png"`.
- **`pillow-heif` has prebuilt manylinux wheels** (Python path); `sharp` deliberately excludes HEIC (HEVC patents) (Node path).
- **SHA-256 hashing is ~1% of per-photo work** (~1.2 ms local, ~2–3 ms Lambda, vs ~127 ms transcode).

### AWS service notes

- **EventBridge Bus vs Pipes:** Bus is pub/sub; Pipes is point-to-point and requires poll-based sources (SQS, Kinesis, DynamoDB Streams, MSK). S3 cannot be a Pipes source.
- **SQS's role is a shock absorber** — buffering, per-message retry, DLQ isolation, concurrency control. Step Functions Distributed Map provides all four natively with visual history.
- **API Gateway flavour:** HTTP API is cheaper with native JWT; REST API has usage plans and API keys. `P-97` (rate limiting in application code) leaves both viable.
- **Cognito email sender:** ~50/day default; swappable to SES (which starts in sandbox mode). Not a constraint at this scale.

---

## Technical carry-forward, still undecided

**Backend runtime and vocabulary — resolved by `T-01` (2026-08-08):** all Python. `handler → manager → procedure/converter → DAO` carries over as a Python file-layout convention (it was never Node-specific). No middy (Powertools' `APIGatewayRestResolver` already covers routing, response conversion, CORS). No DynamoDB Toolbox (multi-table data model doesn't need single-table key protection; plain typed `boto3` wrapper functions cover data access instead — a working assumption, not a formal `T-nn`, revisit only if `T-04` changes the data model shape).

**Locked stack elements the user has named:** Jenkins CI/CD, React frontend, Terraform IaC, Cognito, DynamoDB, S3, CloudFront, CloudWatch. Lambda consolidation via Powertools' `APIGatewayRestResolver` (handlers doing routing, not one-per-endpoint).

**Design obligations from product rulings** — load-bearing, not cosmetic:

- Cursor-based pagination — position-based paging breaks under `P-57` + `P-16`.
- Streaming ZIP builder with temporary storage, expiring links, cleanup (`P-60`).
- Per-photo face IDs retained for deletion from the Rekognition collection (`P-52`).
- Batch state needs a terminal deadline (`P-53`) and a retry budget inside it (`P-56`), plus a durable place to hold progress and the `P-55` result (`P-100`).
- File type sniffed from content, not extension (`P-54`).
- Stored QR images per event, generated at creation, deleted on event deletion (`P-90`).
- Access-code attempt counter per account and per IP, in application code (`P-97`).
- ~30-minute end-to-end target for 1,000-photo batch (`P-94`).
- Scroll-position restoration in the gallery (`P-63`).
- Empty "my photos" state designed deliberately (`P-65`).
- Frozen-filter state visibly marked (`P-69`).
- Privacy page stating **that accounts cannot be deleted** and that the name and email on contributed photos stay visible (`P-72`, `P-74`, `P-86`). *(Moved 2026-08-06 from the account-deletion screen, which no longer exists.)*
- "Deletion is not retroactive" wording on photos and ejection (`P-44`, `P-29`).
- Event lifetime stated at creation and warned before transition (`P-33`).
- Terraform resource names parameterised from the start, or `P-95` becomes expensive to reverse.
- **The Distributed Map's `MaxConcurrency` must be a Terraform variable, never hardcoded** (`T-02`) — it has to match the deploying account's actual Rekognition `IndexFaces` TPS quota, which varies per account (new/lightly-used accounts commonly sit below the ~50 TPS published default) and is checked via the Service Quotas console, not assumed. A hardcoded value throttles silently rather than failing the build. *Added 2026-08-08.*
- **The Map state's photo list is read from S3 via `ItemReader`, never passed as workflow JSON** (`T-02`) — keeps state-machine payloads at the `jobId`/S3-path scale v1 already established, inside the 256KB ASL data-transfer limit. *Added 2026-08-08.*
- **Verify Rekognition is available in `ap-south-1` before building** — it is not offered in every region (`P-95`).
- Upload progress must survive the uploader leaving, and must degrade honestly rather than freeze during a slow retry (`P-100`).
- **The gallery must offer no filtering or selection by uploader** (`P-86` + `P-52`). Attribution is now visible, which puts the "delete everything this person added" control `P-52` deliberately rejected one filter away from existing. *Added 2026-08-06 — this one is a guard against drift, not a nicety.*
- **Uploader attribution belongs on the opened photo, not on every thumbnail** (`P-86`), or `P-57`'s single grid becomes a credits list.
- **The per-event storage byte total must stay correct across `P-44` deletion, `P-52` bulk deletion, `P-38` dedup skips and `P-55` partial batch failures** (`P-85`). A drifting counter is worse than none, because `P-81` surfaces no discrepancy. *Added 2026-08-06.*
- **Two `P-54` messages are the entire mitigation for not recursing, and both must survive into the build.** (a) The "photos must be at the ZIP's top level" line wherever a ZIP can be chosen — organizer upload and `P-36` attendee contribution. (b) The explanatory message when a ZIP yields no top-level photos, instead of a bare zero. Without them, a photographer's nested export ingests nothing with no way to work out why. *Added 2026-08-06.*
- **No share block may be reintroduced** (`P-31`). Ingestion state now affects no permission anywhere, and `P-53`'s batch timeout no longer rests on it — a future change to batch handling must not quietly re-derive one. *Added 2026-08-06.*
- **Nothing bounds spend any more** (`P-40`, `P-25`). No photo cap, no event cap, no upload quota, no alerting. Rekognition bills on arrival at ~6× whole-life storage cost, so `terraform destroy` recovers nothing already spent. Ruled deliberately as an accepted portfolio risk; `P-87`'s per-membership counter is the only place a volume guard could later go. *Added 2026-08-06.*
- **`db-api`'s IAM role must stay scoped to the `Jobs` table only** (`T-03`). It is a generic, reusable Lambda called from four separate pipeline states — the whole reason it's safe as a separate function rather than a shared code library is that its blast radius stays narrow. Widening its use to other tables later would need this re-examined, not assumed away. *Added 2026-08-08.*

---

## Suggested next steps

1. **The 8-item agenda is closed.** `T-01`–`T-08` are all ruled — see the decision log at the top of `LOCKED_TECH_DECISIONS.md`.
2. **The `T-04` follow-up is closed — all 6 tables ruled.** `Users`, `Events`, `Jobs`, `Photos`, `Faces`, and `EventAttendees` (see "Loose threads" above). `EventAttendees`'s 3 sub-questions (status values/leave-rejoin semantics, the roster/lobby GSI, stale-match cleanup on photo delete) were ruled 2026-08-12, closing the table and the follow-up. `TECH_DECISIONS.md` has been written up with the one follow-up entry covering all 6 tables, matching how the `T-03` API Gateway follow-up was recorded only once closed.
3. **The user already knows DynamoDB's core vocabulary** (PK, SK, GSI, LSI, `GetItem`/`Query`/`Scan`/`BatchGetItem`/`UpdateItem`/`TransactWriteItems`) — taught in full during the `Events` discussion, in case it needs to come up again during implementation.
4. **The `CascadeDelete` (formerly `EventTeardown`) pattern is closed too** — 9 Lambdas, 10 CI/CD jobs, both final, no further amendments expected from schema work since none remains.
5. **The technology phase has nothing left open.** Per `CLAUDE.md`'s standing rule, no code gets written until the decisions behind it are ruled — they now are. **Implementation is next.**

---

## Housekeeping reminders

- v1 leaked AWS key, OAuth secret, CloudFront PEM — **rotate these regardless**.
- Check AWS account creation date — the 6-month clock is the deadline.
- `gitleaks` should be installed and hooked before real code is committed.
