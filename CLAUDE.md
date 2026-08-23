# CLAUDE.md

## Project: Glimpses — start here

**Read `Miscellaneous/SESSION_HANDOFF.md` before doing anything.** It carries the current state, what's next, and how this project is run.

Glimpses is a from-scratch rebuild of a torn-down v1 — an event photo-sharing app with face-recognition search on AWS. The product was locked feature-by-feature *before* any technology was chosen.

**As of 2026-08-12 the technology phase is fully closed and implementation has begun.** The product is locked at 100 rulings (`P-01`–`P-100`); the technology phase's agenda is fully ruled `T-01`–`T-09`. Architecture as it stands: 10 Lambdas, 7 DynamoDB tables (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`, `Downloads`), one S3 bucket (`glimpses-photos`, six prefixes), CloudFront in front of `photos/`/`thumbnails/`/`qrcodes/` only. Full reasoning for every ruling lives in `LOCKED_TECH_DECISIONS.md` (tight answers) and `TECH_EXPLANATIONS.md` (the why); don't re-derive it here — read those files. Two Lambdas were added beyond the original plan because a table needed IAM reach no existing Lambda had: `EventTeardown` (event deletion) and `CascadeDelete` (photo deletion, originally event-only, renamed when reused), plus `download` (server-side ZIP building, since `Gallery/photos` can't take on a second table without breaking `T-04`'s one-table-per-Lambda isolation). `EventAttendees` carries a 4-value `status` (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`, rows never deleted) and a `matchedPhotoIDs` String Set kept current by two `ingestion` entry points: `MatchAttendees` (Step Functions Distributed Map, batch-arrival fan-out) and `MatchOneAttendee` (DynamoDB Stream on `EventAttendees`, filtered to `status` transitioning onto `ATTENDEE`, so late admits/joins/rejoins still get matched against the whole collection). Full detail on `MatchOneAttendee`'s reasoning in `LOCKED_TECH_DECISIONS.md`'s decision log (2026-08-16) and `TECH_EXPLANATIONS.md` §2.

**Implementation status, updated 2026-08-18 — full chronological build log lives in `Miscellaneous/SESSION_HANDOFF.md`, read its top entry before doing anything.** AWS/Terraform bootstrap is done (`Miscellaneous/SETUP_STEPS.md`): IAM user `glimpses-terraform`, CLI profile `glimpses`, Terraform 1.15.8, versioned+locked-down state bucket. All 7 Terraform modules exist and validate (`dynamodb`, `buckets`, `alarms`, `cloudfront`, `state_machine`, and one module per Lambda) — deliberately kept as **separate modules with separate Jenkins jobs**, not bundled, per the user's explicit call ("keep things separate as it helps understanding"). CI/CD job count: 15, fixed run order `dynamodb`/`buckets`/`alarms` → `cloudfront` → all 10 per-Lambda jobs → `state_machine`. Local Jenkins (Homebrew, not AWS-provisioned) — per-module `cicd/Jenkinsfile`; job setup itself (Multibranch Pipeline, script paths) is the user's own responsibility, not something this repo automates.

**4 of 10 Lambdas built: `heic_converter`, `db_api`, `download`, `ingestion`.** Confirmed folder shape for all: `src/` is `routeHandler.py` → `Handler/handler.py` → `Manager/manager.py` → (optional) `Converter/converter.py` (collapses away when there's no pure-computation step, e.g. `db_api`) → `DAO/dao.py`; `test/unit/`+`test/integration/` (`moto`-backed, all passing); `infra/` per `T-06`'s module layout; `cicd/Jenkinsfile`. Lesson learned building `db_api` and carried into every Lambda since: DynamoDB clients/resources in `DAO` must be built **lazily, per call, not cached at module level** — a module-level client can be created before a test's `@mock_aws` context is active and silently bypass the mock. `ingestion` is the deepest of the four: 5 steps (`Extract`/`IndexOnePhoto`/`Finalize`/`ListAttendees`/`MatchAttendees`) as per-step modules under one shared `Manager`/`Converter`/`DAO`, plus the `MatchOneAttendee` stream entry point reusing `MatchAttendees`' own match-resolution logic directly. **Remaining, not yet built:** `profile`, `events`, `membership`, `upload_status`, `gallery`, `EventTeardown`, `CascadeDelete`.

**`state_machine` module built 2026-08-17, `Jobs.status` enum finalized 2026-08-18.** ASL at `infrastructure/modules/state_machine/templates/ingestion_pipeline.asl.json.tftpl`, written in JSONata (`QueryLanguage: JSONata`, the user's explicit call). Final `Jobs.status` enum: `CREATED → EXTRACTING → INDEXING → MATCHING → SUCCESS`/`FAILED` — two-way terminal, `PARTIAL` dropped. **Enum enforcement lives in `db_api`, not the ASL** — the state machine only ever sends a named action (`mark_extracting`/`mark_indexing`/`mark_matching`/`mark_success`/`mark_failed`/`create`); `db_api`'s `Manager` maps each action to its status string internally, and an unrecognized action raises. `Finalize` computes only `succeededCount`/`failedCount`, no status field; a `Choice` state right after it (`CheckIndexingOutcome`) routes `succeededCount = 0` straight to `JobFailed`, skipping `ListAttendees`/`MatchAttendees` entirely since there's nothing new to match. The real terminal write (`mark_success`) happens after `MatchAttendees`' Map, immediately before the `Succeed` state `IngestionSucceeded`. Full ruling in `LOCKED_TECH_DECISIONS.md`'s decision log (2026-08-18 row). **Next: build the 5 remaining API Lambdas + `CascadeDelete`, then a real Jenkins/`apply` pass to actually deploy everything.**

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

*(The generic "reduce common LLM coding mistakes" guidelines — think before coding, simplicity first, surgical changes, goal-driven execution — are not repeated here; they already apply globally from `~/.claude/CLAUDE.md`.)*

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
