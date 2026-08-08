# Session Handoff — Glimpses product lock-in

**Written:** 2026-08-05, evening · **Updated:** 2026-08-09 *(technology phase in progress — `T-01` through `T-06` ruled, `T-07` observability sub-decision ruled)*
**Current phase:** **The technology phase — opened 2026-08-06.** The product is locked at 100 rulings and closed; see "The technology phase" below for how it runs and what the agenda is. The product sections of this file are now history, kept for the conventions they establish.
**Next steps:** `T-01` (runtime and language) is ruled — **all Python**. `T-02` (ingestion orchestration) is ruled — **Step Functions Distributed Map**. `T-03` (API shape) is ruled — **8 Lambdas: 5 domain-grouped API Lambdas, 1 consolidated pipeline Lambda, 2 shared utility Lambdas (`db-api`, HEIC→JPEG converter)** *(pipeline consolidated from 4 to 1 on 2026-08-08, same day, while working through `T-06`)*. `T-04` (data model) is ruled — **multi-table, 6 tables** (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`; v1's `SearchRateLimit` dropped since `P-16` killed search). `T-05` (Rekognition collection layout) is ruled — **one collection per event**, created/destroyed at runtime by app code, tracked on the `Events` table for teardown. `T-06` (Terraform state and naming) is ruled — **S3 state backend + native locking, per-Lambda modules, dedicated CI job for untargeted applies, 9 CI/CD jobs total, fixed `glimpses-` naming prefix**. `T-07`'s **observability** sub-question is ruled 2026-08-09 — **Powertools structured `Logger`, `log_event=True` (full request auto-logged), 3-day log retention, no X-Ray, no custom metrics, every alarm on SNS + email, `Errors > 0`/5min alarm on all 8 Lambdas**; the hardcoded-alarm-list bug was confirmed already closed by `T-06`'s per-Lambda `cloudwatch.tf`. Fully written up in all three tech files. **Next up: the rest of `T-07` — IAM granularity, CORS, secrets — then agenda item 8, testing approach and CI/CD.**

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
| 3 | **API shape** — one Lambda per endpoint (v1) vs consolidated router — **RULED 2026-08-08: domain-grouped, 8 Lambdas total (`T-03`, pipeline shape revised same day)** | Chosen over v1's one-per-endpoint (tightest IAM, most boilerplate) and full consolidation (least boilerplate, widest blast radius). 5 API Lambdas scoped by table, 1 consolidated pipeline Lambda (`PipelineHandler`, revised from 4 named functions same day — no external invocation path, so the API-consolidation blast-radius argument doesn't transfer), plus `db-api` (generic `Jobs`-status writer, deliberately a separate Lambda over a shared code library) and a shared HEIC→JPEG converter. See `T-03` in the three tech files | `P-97` leaves the API Gateway flavour (HTTP vs REST API) still open |
| 4 | **Data model** — 7 single-purpose tables (v1) vs single-table — **RULED 2026-08-08: multi-table, 6 tables (`T-04`)** | Decided on IAM grounds: `T-03` already scoped each Lambda's role to one table, structural under multi-table, hand-built under single-table. `SearchRateLimit` dropped (v1's 7th table) since `P-16` killed search. Per-table fields/GSIs left as a following sub-decision. See `T-04` in the three tech files | `P-57`+`P-16` force cursor pagination; `P-85` needs a byte counter that survives `P-44`/`P-52`/`P-38`/`P-55` |
| 5 | **Rekognition collection layout and lifecycle** — **RULED 2026-08-08: one collection per event (`T-05`)** | Decided on security-boundary grounds: `P-07`'s no-cross-event-visibility is AWS-enforced under per-event collections, versus dependent on application-code filtering under a shared collection. Collection id tracked on `Events` (`rekognitionCollectionID`) so a teardown script can clean up orphans without Terraform visibility — closes the exact `HANDOFF.md` §9 fork point. See `T-05` in the three tech files | `P-98`, `P-32`, `P-52` |
| 6 | **Terraform state and naming** — **RULED 2026-08-08: S3 + native locking (`T-06`)** | v1 used local state and hit a naming mismatch between Terraform resources and module filenames | `P-95` — parameterise or the region is expensive to reverse |
| 7 | **Observability, IAM granularity, CORS, secrets** — **observability sub-question RULED 2026-08-09 (`T-07`, partial); IAM/CORS/secrets still open** | All four are §7 drift items — decide deliberately or repeat them | `P-81` means nothing alerts users; alarms are for the operator only |
| 8 | **Testing approach and CI/CD** | v1's pyramid and its explicit failure-path tests are worth reusing; Jenkins is already named | — |

### `T-06` — Terraform state and naming (ruled 2026-08-08)

**Fully written up in `TECH_DECISIONS.md`, `LOCKED_TECH_DECISIONS.md`, and `TECH_EXPLANATIONS.md`** — five sub-decisions: (1) state backend — S3 + native S3 locking (`use_lockfile = true`, no DynamoDB), versioning on; (2) per-Lambda Terraform module layout, replacing v1's centralized `functions` module; (3) deploy discipline — a separate dedicated CI job runs the untargeted `apply` that builds/updates the state machine, never piggybacked on a single Lambda's own pipeline; (4) CI/CD granularity — 8 per-Lambda Jenkinsfiles + 1 dedicated untargeted-apply job = 9 total; (5) naming — a fixed `glimpses-` prefix applied identically everywhere, no environment branching, no mapping file. See `T-06` in the three tech files for full reasoning, options considered, and the worked naming table.

### `T-07` — Observability (ruled 2026-08-09; IAM granularity, CORS, secrets still open)

**Fully written up in `TECH_DECISIONS.md`, `LOCKED_TECH_DECISIONS.md`, and `TECH_EXPLANATIONS.md`** — seven sub-decisions under the observability slice of `T-07`: (1) logging library — Powertools `Logger` (structured JSON), no new dependency since `T-01` already ships Powertools; (2) `log_event=True` — the full incoming request is auto-logged on every invocation, **ruled against the recommendation** (which favored logging only explicit fields, given the `P-19` selfie/`P-68` deletion right sitting in request bodies); (3) log retention set to **3 days**, a direct consequence of (2); (4) tracing — **no X-Ray**, ruled against the recommendation, on cost/effort grounds; (5) custom metrics — **none**, AWS-default Lambda metrics only, `P-100`'s failure-percentage stays a manual read; (6) alarms wired to an **SNS topic + email subscription**, fixing `HANDOFF.md` §7's silent-alarm bug directly; (7) the hardcoded-alarm-list bug confirmed **already closed** by `T-06`'s per-Lambda `cloudwatch.tf`, not a fresh decision — flagged out loud rather than assumed. Alarm content ruled narrow: `Errors > 0` over 5 minutes, identical on all 8 Lambdas. See `T-07` in the three tech files for full reasoning and the options considered at each step.

**IAM granularity, CORS, and secrets hygiene — the other three §7 drift items — are not yet discussed.**

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

1. **Work the agenda in order.** `T-01` (runtime and language → all Python), `T-02` (ingestion orchestration → Step Functions Distributed Map), `T-03` (API shape → 8 domain-grouped/pipeline/utility Lambdas), `T-04` (data model → multi-table, 6 tables), and `T-05` (Rekognition collection layout → one per event) are ruled. **Next: agenda item 6, Terraform state and naming**, in `TECH_DECISIONS.md`. **One at a time, options first, run through the named cast.**
2. **The full agenda is the table** in "The technology phase" above — eight decisions, ordered by what unblocks what.
3. **After each ruling:** copy the tight answer into `LOCKED_TECH_DECISIONS.md`, write the concepts up in `TECH_EXPLANATIONS.md`, and add a dated row to both decision logs.
4. **The user is learning these concepts from scratch.** Once agreed on a decision at a high level, expect several follow-up rounds going deeper into the mechanics before it's ready to rule (`T-02` took this shape: SQS vs Distributed Map → simpler retrace → isolate the confusing part → trace with small numbers → connect to a real numeric example, i.e. Rekognition's actual TPS quota). Don't rush past this to get to a ruling.

---

## Housekeeping reminders

- v1 leaked AWS key, OAuth secret, CloudFront PEM — **rotate these regardless**.
- Check AWS account creation date — the 6-month clock is the deadline.
- `gitleaks` should be installed and hooked before real code is committed.
