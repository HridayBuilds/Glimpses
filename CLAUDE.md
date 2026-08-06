# CLAUDE.md

## Project: Glimpses — start here

**Read `Miscellaneous/SESSION_HANDOFF.md` before doing anything.** It carries the current state, what's next, and how this project is run.

Glimpses is a from-scratch rebuild of a torn-down v1 — an event photo-sharing app with face-recognition search on AWS. The product was locked feature-by-feature *before* any technology was chosen.

**As of 2026-08-06 the product is locked and closed at 100 rulings (`P-01`–`P-100`), and the technology phase is open.** The revision phase resolved 11 change requests plus the AWS region and account deletion. **Read "The technology phase" at the top of `Miscellaneous/SESSION_HANDOFF.md` before anything else** — it carries the agenda, the ordering, and the rules below in full.

**The one-directional rule — this phase's version of the non-negotiable.** Product constrains technology; **technology never re-rules product.** If a stack choice makes a `P-nn` awkward or expensive, surface it as a revision request for the user to rule on. Never resolve it in the implementation. v1 failed exactly here: React 18 planned and 19 shipped, FastAPI taught and never used, Powertools shipped in the Lambda layer and never wired, CORS restriction implied by a Terraform variable and never enforced — **every one of those was decided by drift, which is what this rebuild exists to prevent.**

**`HANDOFF.md` is no longer historical-only — it is now a working input.** §7 is v1's mistake ledger (dead dependencies, silent alarms, two unresolved bugs, IAM friction found at runtime) and §9 lists eight fork points v1 actually hit. Check every technology decision against both. Do not re-derive them and do not repeat them by omission.

**The user wants to understand before anything is implemented.** Stated 2026-08-06: *"i need to understand it all before implementing anything."* No code until the decisions behind it are ruled.

**The user commits; you never do.** Stated directly on 2026-08-06: *"all commits will be made by me only not u so pls do not push or commit anything."* Leave work as uncommitted working-tree changes and say what changed.

| File | Purpose |
|---|---|
| `Miscellaneous/SESSION_HANDOFF.md` | Current state, what's next, how to work with revisions |
| `Miscellaneous/PRODUCT_WALKTHROUGH.md` | The product described end-to-end, readable in one sitting — start here for review |
| `Miscellaneous/LOCKED_PRODUCT.md` | The spec — every ruled decision with full reasoning (`P-nn`) — source of truth |
| `Miscellaneous/PRD.md` | The decision register (`D-nn`) — use for revisions |
| `Miscellaneous/HANDOFF.md` | v1 retrospective — **a working input for the technology phase.** §7 mistakes, §9 fork points |

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