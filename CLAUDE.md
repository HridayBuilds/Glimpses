# CLAUDE.md

## Project: Glimpses — start here

**Read `Miscellaneous/SESSION_HANDOFF.md` before doing anything.** It carries the current state, what's next, and how this project is run.

Glimpses is a from-scratch rebuild of a torn-down v1 — an event photo-sharing app with face-recognition search on AWS. The product was locked feature-by-feature *before* any technology was chosen.

**As of 2026-08-12 the technology phase is fully closed and implementation has begun.** The product is locked at 100 rulings (`P-01`–`P-100`), the technology phase's 8-item agenda is fully ruled (`T-01`–`T-08`), and both loose threads left inside already-ruled items are closed too: `T-03`'s API Gateway flavour (REST API, for WAF) and `T-04`'s per-table fields/PK-SK/GSI definitions for all 6 tables — `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`. Ruling `Events` surfaced a real gap (no Lambda had IAM reach for full event teardown), closed by adding a 9th Lambda, `EventTeardown` — which amends `T-03`'s Lambda count and `T-06`'s CI/CD job count. The same gap shape recurred on `Faces`: photo deletion needed reach no existing Lambda had, closed by reusing that same Lambda rather than adding a 10th — renamed `CascadeDelete` since it's no longer event-only. A third, different-shaped gap surfaced scoping `EventAttendees`: nothing in the pipeline actually ran the per-attendee `SearchFaces` fan-out `P-16`/`P-93` require, and nothing stored its result — closed by adding `MatchAttendees`, a new Distributed Map step on the existing `PipelineHandler` state machine (no new Lambda), writing each attendee's matched `photoID`s as a String Set (`matchedPhotoIDs`) onto their `EventAttendees` row. `EventAttendees`'s three remaining sub-questions are also ruled: (1) status is a 4-value field (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`), the row is never deleted, leave/eject/deny are status flips in place; (2) one GSI, `eventID` PK + `status` SK, serves the organizer's roster/lobby and `MatchAttendees`' own "who's admitted" lookup; (3) `CascadeDelete` does not scrub `matchedPhotoIDs` on photo delete — a stale id is filtered out for free at read time.

**Implementation is now in progress.** AWS/Terraform environment bootstrap is done and logged step-by-step in `Miscellaneous/SETUP_STEPS.md`: IAM user `glimpses-terraform`, local CLI profile `glimpses`, Terraform 1.15.8, the `glimpses-terraform-state` S3 bucket (versioned, public access blocked), `infrastructure/providers.tf`/`variables.tf` written, `terraform init` succeeded. Real per-service quota found and recorded: this AWS account's actual Rekognition `IndexFaces` TPS is **5**, not the published default of 50 — `T-02`'s `rekognition_index_max_concurrency` variable will be set accordingly. **`infrastructure/modules/dynamodb/` is built** — all 6 tables, one `.tf` file per table, `PAY_PER_REQUEST`/`ALL`-projection GSIs/`Events`' `OLD_IMAGE` stream all confirmed, wired into root `imports.tf`, `terraform validate` passing. **`T-06`'s CI/CD job split is ruled** (2026-08-13): the untargeted-apply job is now two, `dynamodb` and `state_machines`, fixed run order `dynamodb` → all 9 Lambda jobs → `state_machines` (job count 10 → 11) — because the tables must be created **by the `dynamodb` Jenkins job, not a manual local `apply`**, per the user's explicit instruction. **Blocked on:** whether a Jenkins instance already exists or needs to be stood up first, and if so whether Terraform provisions it — open questions for next session. Full detail and exact next action in `Miscellaneous/SESSION_HANDOFF.md`'s top entry — read it before doing anything.

**Three new working files exist, each a `<NAME>.md` in its own top-level folder, being filled in incrementally by the user, piece by piece — do not write to them speculatively, only what's been explicitly given so far:** `Backend/BACKEND.md` (per-Lambda folder shape: `infra/` = `T-06`'s per-Lambda Terraform module, `test/` = `T-08`'s unit+integration tests, `src/` compartmentalized per `T-01`'s `handler → manager → procedure/converter → DAO` layering — this shape is already fully determined by prior rulings, not a new decision), `Frontend/FRONTEND.md` (not yet discussed), `infrastructure/INFRASTRUCTURE.md` (not yet filled — user will specify later).

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