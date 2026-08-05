# Session Handoff — Glimpses product lock-in

**Written:** 2026-08-05, evening · **Updated:** 2026-08-06 *(revision phase complete)*
**Current phase:** **Revisions done — the product is locked again at 100 rulings.** The user reviewed the walkthrough and raised **11 change requests**; all eleven are resolved, and the same session also closed the AWS region and account-deletion questions that had been carried as unruled. See "The revision queue" below for what changed.
**Next steps:** **The technology discussion.** One question outstanding first — see "One question waiting on the user" below. Then stack, data model and service shapes, starting with **SQS vs Step Functions Distributed Map**, which `P-100` has now made a concrete product question rather than a taste one.

## One question waiting on the user

On 2026-08-06 the user said *"no rate limits as i said"* while settling several items at once. **It has two readings and must not be resolved silently:**

1. **Only the numbers stay open** — `P-97`'s access-code attempt limiting stays as a mechanism, and only its thresholds are unruled. This is what was already on the unruled list, so the phrase may just have been confirming it.
2. **`P-97` goes entirely** — no limiting on access-code attempts at all.

Reading 2 is security-relevant and worth one plain sentence to the user before acting: `P-27`'s ~1 billion code combinations only protect anything if guessing is bounded, and with `P-26`'s `OPEN` default plus `P-07`, a guessed code is immediate full access to the gallery. Ask; do not assume.

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
| `P-99` **new** | Attribution persists unchanged after account deletion or ejection | `D-114` |
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

**Product: 100 rulings · 0 open · 2 unruled/assumed, plus 1 question waiting** (see the top of this file). The 2 are `P-97`'s rate-limit thresholds and `P-98`'s collection architecture, the second explicitly deferred by the user to the technology phase. `P-75` and `P-76` are **dissolved** — they still exist as ids and text, but describe nothing the product does. **Recount from table rows; never decrement** — `PRD.md` gained `D-117` through `D-126` on 2026-08-06.

Note that the count rose by only **one** (`P-100`) across ten register rows: `D-117`, `D-119`, `D-121`–`D-125` all rewrote existing `P-nn` in place, `D-118` was a wording fix and `D-120` a reaffirmation. Per convention, revisions keep their `P-nn`.

**Technology: nothing decided.** Deliberately deferred.

**Repo state:** `main` has two commits (b60e14a locking the product, 94217a0 adding the walkthrough). **The 2026-08-06 revisions are uncommitted working-tree changes** to `LOCKED_PRODUCT.md`, `PRD.md`, `PRODUCT_WALKTHROUGH.md`, `SESSION_HANDOFF.md` and `CLAUDE.md` — the user commits when they choose. Backend and Frontend are empty directories. No secret-scanner (gitleaks) installed yet.

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

1. **v1's leaked credentials need rotating** — AWS access key, Google OAuth secret, CloudFront signing PEM. These were in a deleted source folder but deletion is not revocation.
2. **Check AWS account creation date** — the 6-month free-tier credit clock is the project's real deadline.
3. **`gitleaks` installation and pre-commit hook** — before any real code is committed.
4. **Any product revisions the user wants to make** — which is the current phase.

---

## The remaining unruled/assumed items

These were flagged in the spec as open or explicitly assumed. They are *not* open questions in `PRD.md` — they are embedded in the rulings and marked as such.

| Item | Where marked | What it is |
|---|---|---|
| **Rate-limit thresholds** | `P-97` | The mechanism is locked; the numbers are not. **See the question at the top of this file before touching this** |
| **Collection architecture** | `P-98` | Assumed one collection per event. **Deferred to the technology phase by the user on 2026-08-06**, in those words |

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

**Backend vocabulary:** the user's desired Node/TypeScript with `handler → manager → procedure/converter → DAO`, middy, and DynamoDB Toolbox.

**HEIC tension:** decoding is materially easier in Python. The user said they want Python "for this conversion" — clarify whether that means a separate function or a whole-stack choice.

**Locked stack elements the user has named:** Jenkins CI/CD, React frontend, Terraform IaC, Cognito, DynamoDB, S3, CloudFront, CloudWatch. Lambda consolidation (handlers doing routing, not one-per-endpoint).

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
- **Verify Rekognition is available in `ap-south-1` before building** — it is not offered in every region (`P-95`).
- Upload progress must survive the uploader leaving, and must degrade honestly rather than freeze during a slow retry (`P-100`).
- **The gallery must offer no filtering or selection by uploader** (`P-86` + `P-52`). Attribution is now visible, which puts the "delete everything this person added" control `P-52` deliberately rejected one filter away from existing. *Added 2026-08-06 — this one is a guard against drift, not a nicety.*
- **Uploader attribution belongs on the opened photo, not on every thumbnail** (`P-86`), or `P-57`'s single grid becomes a credits list.
- **The per-event storage byte total must stay correct across `P-44` deletion, `P-52` bulk deletion, `P-38` dedup skips and `P-55` partial batch failures** (`P-85`). A drifting counter is worse than none, because `P-81` surfaces no discrepancy. *Added 2026-08-06.*
- **Two `P-54` messages are the entire mitigation for not recursing, and both must survive into the build.** (a) The "photos must be at the ZIP's top level" line wherever a ZIP can be chosen — organizer upload and `P-36` attendee contribution. (b) The explanatory message when a ZIP yields no top-level photos, instead of a bare zero. Without them, a photographer's nested export ingests nothing with no way to work out why. *Added 2026-08-06.*
- **No share block may be reintroduced** (`P-31`). Ingestion state now affects no permission anywhere, and `P-53`'s batch timeout no longer rests on it — a future change to batch handling must not quietly re-derive one. *Added 2026-08-06.*
- **Nothing bounds spend any more** (`P-40`, `P-25`). No photo cap, no event cap, no upload quota, no alerting. Rekognition bills on arrival at ~6× whole-life storage cost, so `terraform destroy` recovers nothing already spent. Ruled deliberately as an accepted portfolio risk; `P-87`'s per-membership counter is the only place a volume guard could later go. *Added 2026-08-06.*

---

## Suggested next steps

1. **Work the revision queue** — four items left (8, 11, 3, 4) plus the `P-07` wording fix. They are listed near the top of this file with the user's exact words and the rulings each one touches. **One at a time, options first.**
2. **Suggested order:** item 3, then 8, then 11 (which is 2–3 rulings, not one), then 4 (which collides with `P-81` and needs the most care).
3. **Once satisfied** — begin the technology discussion. Stack, data model, service shapes.

---

## Housekeeping reminders

- v1 leaked AWS key, OAuth secret, CloudFront PEM — **rotate these regardless**.
- Check AWS account creation date — the 6-month clock is the deadline.
- `gitleaks` should be installed and hooked before real code is committed.
