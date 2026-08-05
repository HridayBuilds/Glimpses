# Session Handoff — Glimpses product lock-in

**Written:** 2026-08-05 *(supersedes the 2026-08-04 evening handoff)*
**Next session focus:** **the product is locked — the register has zero open rows.** Next is the *technology* discussion, which has been deliberately deferred since the start. Before that, two pieces of housekeeping: commit the repository (still zero commits) and rotate v1's leaked credentials.

---

## Read these first, in this order

| File | What it holds |
|---|---|
| `Miscellaneous/LOCKED_PRODUCT.md` | **The spec.** Every ruled decision as `P-nn`, with reasoning and accepted costs. Source of truth. |
| `Miscellaneous/PRD.md` | **The working register.** Every question as `D-nn`. Ruled rows point at their `P-nn`. Now fully closed. |
| `Miscellaneous/HANDOFF.md` | v1 retrospective. Historical only — v1 was torn down and its source deleted. Useful for "what went wrong last time", not for what to build. |

Do **not** re-derive decisions already in `LOCKED_PRODUCT.md`. Do **not** duplicate its content anywhere.

---

## How this project works — read this before doing anything

**The user makes every decision. The AI presents options with real tradeoffs and a recommendation, then waits.**

This is the whole point of the rebuild. In v1 the user let an AI dictate the architecture, ended up not understanding their own system, and inherited choices they later regretted. Violating this is the single worst thing you can do here.

Concretely:
- Present 2–3 genuine options per question, each with an honest cost — not a token alternative next to an obvious winner.
- Mark the recommendation, but never assume it.
- **Go one decision at a time.** The user asked for this explicitly and has repeated it across sessions.
- When a ruling contradicts an earlier one, say so plainly and rewrite the affected `P-nn` rather than layering an exception.

**The user overrode the recommendation 12 times on 2026-08-05** (`D-46`, `D-47`, `D-97`, `D-107`, `D-63`, `D-85`, `D-15`, `D-19`, `D-13`, `D-70`, `D-71`, `D-73`) after five overrides the previous session. Every override was coherent. **Do not treat a recommendation as the expected answer.**

**Speed does not come out of the user's decision rights.** Midway through 2026-08-05 the user said "there is still a lot to tackle let us start and get through this quickly". The correct response was to cut AI verbosity — shorter framing, tighter scorecards — **not** to bundle decisions or rule anything by implication. That distinction held and should keep holding.

### How to explain things

This has worked across three sessions and should stay the default:

- **Drop the jargon.** *Ingest*, *gate*, *trigger*, *scope*, *policy branch* consistently obscure rather than clarify.
- **Use named, concrete scenarios** and run every option through all of them. Recurring cast: **Meera** (attendee wanting her own photos), **Arjun** (wedding photographer, bulk ZIP), **Priya** (collaborative trip organizer), **Rohan** (attendee with no selfie / the adversarial case).
- **Build up from what the thing physically is** before naming it. Explaining that EXIF is "a small block of text inside the photo file", that a ZIP is "many files in one box", and that a QR code is "a picture that encodes a link" all landed immediately.
- **Then a scorecard** — options as rows, scenarios as columns, ✅/⚠️/❌ in the cells. The user rules quickly and confidently every time this is used.

### Three process rules learned the hard way

1. **Do not bundle two decisions into one set of options.** This has happened repeatedly. **If an option contains an "and", check whether it is two rulings.** On 2026-08-05 five questions were split before being presented (`D-46`, `D-09`, `D-98`, `D-61`, plus `D-61`'s missed `ATTENDEE` column, which became `D-110`).
2. **Say out loud when you write in an assumption.** Minor recommendations may be written into the spec marked clearly as such — but only for genuinely minor points, and always announced. Never for anything structural. When a consequence is *forced* by existing rulings rather than chosen, label it "forced, not ruled" and invite an override.
3. **Audit the spec's existing wording after every ruling.** The spec has been caught three times claiming more than the system delivers. On 2026-08-05, eight earlier entries had to be amended because new rulings made their wording false — `P-70`, `P-71`, `P-20`, `P-51`, `P-31`, `P-02`, `P-18`, and §7 points 1 and 5. **A new ruling that makes an old bullet untrue is not "consistent by default".**

Document conventions: `P-nn` and `D-nn` ids are permanent and never reused or renumbered *(a duplicate `D-103` was created and had to be renumbered to `D-105` — check before assigning)*. Questions killed by a later ruling are marked `DISSOLVED`, not deleted. **Recount statuses from the table rows; never decrement a figure.**

---

## Where things stand

**Product: 79 ruled · 4 dissolved · 1 answered · 0 open · 3 other — 87 rows total.**

The 3 "other" rows are pointers, not live questions: `D-30` (superseded by `D-80`), `D-45` (remainder was `D-91`, ruled), `D-09` (split into `D-106`/`D-107`, both ruled).

**Technology: nothing decided.** Deliberately deferred until the product was locked. It now is.

**Repo state:** `Backend/` and `Frontend/` are empty directories, and **`master` still has zero commits** — none of these documents are committed. The user has a branch they want this pushed to and will name it.

The product's shape in one paragraph:

> Sign up with email, password and a display name, verifying by typed numeric code. Join an event with a 6-character code or by scanning its QR, either walking straight in or waiting in a lobby for the organizer. See every photo in the event immediately. If you've added a selfie to your profile, the event opens directly on the photos you're in, and they keep updating as more arrive — you're never asked to search, and there is no way to re-run a match. Anyone admitted can add photos unless the organizer turns that off, and can share the code onward. Nobody is notified of anything, ever. Photos carry no uploader attribution and download at full resolution, individually or as an archive. Events go read-only after 30 days without an upload and are deleted 30 days after that.

---

## What was ruled on 2026-08-05

`P-70`–`P-98` — **29 rulings, summarised only. The reasoning lives in `LOCKED_PRODUCT.md`; don't re-derive it.**

- **Privacy of non-users** (`P-70`–`P-72`) — a person photographed at an event but not using Glimpses has **no removal path**, and the spec now says so rather than implying otherwise. No face-indexing notice appears anywhere in the product. One public plain-language privacy page exists, linked from signup and the site footer — reachable, not surfaced.
- **Forward-only matching** (`P-73`, `P-76`, `P-79`, `P-98`) — no manual re-match, no per-event opt-out, account deletion leaves computed match sets in place. **`P-98` re-founded `P-20` after `D-96` disproved its cost argument** (see below).
- **Account lifecycle** (`P-74`, `P-75`) — contributed photos survive account deletion with the link severed; events the deleted user organized are archived immediately.
- **Retention** (`P-77`, `P-78`) — 30 days active / 30 days archived, confirmed. "Activity" means uploads only; viewing and downloading do not extend the clock.
- **Tuning** (`P-80`) — `similarityThreshold` fixed at 80, exposed to nobody. Carried from v1 and **never measured against real photos.**
- **Notifications** (`P-81`) — none of any kind. No badges, no unread counts, no feed, no push. This dissolved `D-87` outright.
- **Identity and visibility** (`P-82`–`P-86`) — organizers see display names only; attendees cannot see each other; display name collected at signup; organizers get photo and attendee counts and nothing else; photos carry no uploader attribution.
- **Contribution and joining** (`P-87`–`P-91`) — no per-attendee quota, no pre-approved guest list, event name and date fixed at creation, QR generated server-side and stored as a file, email verification by typed numeric code.
- **Non-functional** (`P-92`–`P-97`) — mobile-web first; target 100 attendees per event and ~10 concurrent events (planning figures, **not enforced caps** — `P-40` remains the only real limit); ~30-minute ingestion target for a full batch; one region, one environment, no staging; current browsers with basic untested accessibility; **access-code attempts are the only rate-limited action.**

### Three things that matter more than the individual rulings

1. **`D-96` was answered from AWS primary sources and overturned a spec justification.** `SearchFaces` evaluates an entire collection in **one call regardless of photo count** — there is no pagination, and `MaxFaces` caps results returned, not collection scanned. And searching by stored face ID bills **identically** to searching by image (both Group 1, same free-tier pool) — so there is no cheaper stored-ID path. `P-20` had been ruled against a fan-out of *(events × photos in each)*, which does not exist: recompute costs about **$0.005 for a five-event attendee**. The user re-looked at `P-20` under `D-111` and **confirmed it on structural grounds instead** (`P-98`). **The lesson is general: check the arithmetic behind any ruling that cites cost.**
2. **`P-20`'s accepted cost is now a chosen one.** An attendee who fixes a bad selfie gets no improvement in any event that has stopped receiving photos — which under `P-32`/`P-33` is every event 30 days after its last upload. That was previously softened by "recompute would be expensive". It isn't. `P-98` records this as the **cheapest ruling in the spec to reverse** if real use argues against it.
3. **`P-97` keeps the API Gateway choice open.** Usage plans and API keys exist only on REST API, not HTTP API. Because rate limiting lives in application code (a DynamoDB counter), the cheaper HTTP API stays available — a real downstream consequence to carry into the technology discussion.

### Explicitly flagged as unruled or assumed — do not treat as settled

- **Which AWS region** (`P-95` locks *one* region, not *which*).
- **Whether the event date should be mutable** unlike the name — written into `P-89` as an assumption.
- **Whether account deletion should exist at all** — `P-74` labels it "forced, not ruled — open to override".
- **Rate-limit thresholds** for `P-97` — the mechanism is locked, the numbers belong in §10's tuning table.
- **One Rekognition collection per event** — assumed by `P-98`'s cost arithmetic; it is a technology decision that has not been made.

---

## Verified facts — researched, not recalled. Do not re-derive.

### AWS cost model

- **The AWS Free Tier changed on 15 July 2025.** The old per-service allowances (5 GB S3, 1,000 Rekognition images/month, 12 months) are gone for new accounts. The model is **$200 in credits, valid 6 months from account creation.** The user confirmed they are on this plan and already using it.
- **The binding constraint is time, not money.** S3 Standard $0.023/GB/mo · Rekognition Group 1 $0.001/image · face vectors $0.00001/face/mo. A 1,000-photo wedding costs **~$1.26 for its entire 60-day life**; $200 covers ~180 events. **Credits won't run out — the 6-month expiry arrives first.**
- **Rekognition indexing dominates, ~6× the cost of storing a photo for its whole life** — a one-time charge paid on arrival that retention cannot claw back. This is why `P-40` counts photos, not bytes.
- **`SearchFaces` and `SearchFacesByImage` are both Group 1 at the same rate** and draw on the same 1,000-image/month free-tier pool. **A search evaluates the whole collection in one call** — no pagination, no `NextToken`; `MaxFaces` (ceiling 4096) caps matches returned, not collection scanned. *(`D-96`, verified 2026-08-05 against the SearchFaces API reference and the Rekognition pricing page.)*
- **Rekognition's 15 MB S3-object limit is documented as unraisable.** This is what ruled out storing PNGs, and it is now also the canonical example of a *deterministic* failure under `P-56`.
- **Bandwidth is the only cost not bounded by `P-40`** (`P-59`). It scales with downloads, not photo count: 100 guests × 200 photos ≈ 20 GB ≈ $1.70 at CloudFront's ~$0.085/GB. Small, but the one line item that grows with success.

### Image handling

- **PNG was ruled out on measured evidence.** At 12 MP a photo is ~1.0 MB as JPEG q90 and **~12.1 MB as PNG** — on a smooth landscape, the friendliest case. Real detailed photos land at 20–25 MB, over the Rekognition limit. PNG is also *dominated*: far larger than the source HEIC while containing no more information, because **HEIC is already lossy**.
- **The OSS path is clean.** Everything routes through **libheif** (LGPL) + libde265. Python: `pillow-heif` ships **prebuilt manylinux wheels** — a Lambda layer is a `pip install`. Node: `sharp`'s prebuilt binaries **deliberately exclude HEIC** (HEVC patents), so it needs a custom libvips build or the much slower pure-JS `heic-convert`. **A genuine Node-vs-Python data point.**
- **iOS auto-transcodes HEIC→JPEG** on browser file inputs via `accept` content negotiation. **The trap:** listing `image/heic` in `accept` inverts it and Safari hands back HEIC. Use `accept="image/jpeg,image/png"`. **ZIPs bypass this entirely**, as do desktop drag-and-drop and iCloud-synced files — server-side conversion stays mandatory.
- **Hashing is not a cost concern.** SHA-256 over a 3.6 MB photo: ~1.2 ms locally, ~2–3 ms on a full-vCPU Lambda, versus ~127 ms for decode+re-encode. **~1% of per-photo work.** Lambda gives a full vCPU at **1,769 MB**; the conversion function must be at or above that regardless.

### Flagged as recalled, not verified — confirm before relying on

- **AWS promotional credits do not cover Route 53 domain *registration*** (AWS resells the name from a registry). The ~$0.50/month hosted zone **is** covered, and ACM certificates are free. Recorded in `P-30` with this caveat attached. Low stakes — the user declined a domain regardless.
- **Cognito's built-in email sender caps around 50 messages/day** and can be swapped to SES later without product change. **SES starts new accounts in sandbox mode**, delivering only to individually verified addresses; leaving sandbox is a written request to AWS. Underpins `P-51` and `P-91`, though `P-51` was ruled on deliverability and abuse surface rather than on these limits.

---

## Immediately next

### 1. Commit the repository — before anything else

`master` has **zero commits**. Three sessions of rulings exist only on disk. The user has a target branch in mind and will name it. **Add a secret scanner (gitleaks) in that first commit, not after it** — see housekeeping below.

### 2. The technology discussion

This is the whole remaining project, and it has been deferred on purpose so that it could be argued against a locked product rather than shaping it. Carry-forward material is in the section below. **The same rules apply — one decision at a time, options with honest costs, the user rules.** Given how much of the stack is already named by the user, much of this is sequencing and a handful of genuine forks (Node vs Python, HTTP vs REST API, SQS vs Step Functions Distributed Map, collection layout).

### 3. Loose ends worth closing early in that discussion

The unruled/assumed list above — region, event-date mutability, `P-97` thresholds, collection layout. None block the technology conversation; several are answered naturally inside it.

---

## Technology — carry forward, still undecided

**The user's desired backend architecture is a Node/TypeScript vocabulary.** They described `handler → manager → procedure/converter → DAO`, plus **middy** middleware and **DynamoDB Toolbox**. `dynamodb-toolbox` is TypeScript-only; `middy` is Node-only. Neither has a Python equivalent under those names. v1 chose Python for "AWS's Rekognition examples are Python-heavy", which is weak — the project makes only a handful of distinct SDK calls.

If Node is chosen, TypeScript is near-mandatory given that design: converters between object shapes are ceremony without types to convert between, and shared types across frontend and backend directly fix v1's accepted "no compile-time contract" cost.

**The HEIC tension stands:** decoding is materially easier in Python. The user said they want Python "for this conversion" — which may mean a separate function or container image rather than a whole-stack choice. **Clarify rather than assuming either way.**

Locked stack elements the user has already named: Jenkins CI/CD, React frontend, Terraform IaC, Cognito auth, DynamoDB, S3, CloudFront, CloudWatch. Also wants Lambda consolidation — handlers doing routing rather than v1's one-Lambda-per-endpoint.

**Technical obligations the product rulings created**, all of which the technology choices must carry:
- **Cursor-based pagination** is mandatory (`P-63`), not a preference — position-based paging breaks under `P-57` + `P-16`.
- **A streaming ZIP builder** with temporary storage, expiring links, and cleanup (`P-60`) — the largest single build item ruled so far.
- **Per-photo face IDs must be retained** so `P-52` can delete a photo's vectors from the Rekognition collection.
- **Batch state needs a terminal deadline** (`P-53`) and a silent retry budget that fits inside it (`P-56`).
- **File type must be sniffed from content, not extension** (`P-54`).
- **A stored QR image per event** (`P-90`), generated server-side and served through CloudFront.
- **An access-code attempt counter** per account and per IP (`P-97`) — in application code, which is what keeps HTTP API viable.
- **A ~30-minute end-to-end target for a 1,000-photo batch** (`P-94`) — the concurrency design has an actual number to hit.

---

## Technical findings from the v1 analysis

Not recorded in `HANDOFF.md` itself. They answer questions the user explicitly asked — don't make them re-ask.

**EventBridge — Bus vs Pipes is not a choice between alternatives.**
- An **Event Bus** is pub/sub: producers → rules with pattern matching → targets. It has an *input transformer* to reshape JSON, but **no enrichment**.
- **Pipes** is point-to-point and its source must be **poll-based** (SQS, Kinesis, DynamoDB Streams, MSK). It supports filter → **enrich** → transform → target.
- **Therefore S3 cannot be a Pipes source.** The ZIP-arrival trigger must be a Bus rule. Pipes remains useful elsewhere — e.g. DynamoDB Streams → Pipe → enrich → notify.
- v1's bug where EventBridge fired on every thumbnail write came from separate prefix and suffix filters (OR semantics). EventBridge rules support a `wildcard` matcher, so `events/*/upload/*.zip` is expressible as one correct pattern.

**SQS's role is a shock absorber, not messaging.** It buys buffering, per-message retry, poison-message isolation via DLQ, and concurrency control — to stop thousands of simultaneous Rekognition calls from being throttled. **`P-56` makes this a product requirement, not just an implementation nicety, and `P-18` now names pipeline concurrency as the binding constraint.** **Step Functions Distributed Map provides all four natively** with visual execution history and a `ToleratedFailurePercentage` setting — which also maps directly onto `P-55`'s partial-success reporting. v1 dismissed it as "too advanced" without real evaluation; it deserves a genuine head-to-head.

**Rekognition needs no ML knowledge.** Two API calls: `IndexFaces` (detect faces, store vectors in a "collection", return opaque FaceIds) and a search call (given a face, return FaceIds above a threshold). A "collection" is an AWS-managed vector store you never see inside. `similarityThreshold` is purely a precision/recall dial — now fixed at 80 by `P-80` and still never measured.

**Polling is a smaller problem than it feels.** v1 polled every 12s and stopped on terminal state — ~50 requests for a 10-minute job, against an API Gateway free tier of 1M/month. WebSockets would be strictly worse, and `P-81` removes any notification use case for them. The cheap wins are stopping when the tab is hidden (`document.visibilityState`) and backing off as jobs lengthen. Don't spend design effort here.

**API Gateway flavour is a live fork, and `P-97` deliberately left it open.** HTTP API is cheaper and faster with a native JWT authorizer; usage plans and API keys exist only on REST API. Because `P-97` puts rate limiting in application code, **neither flavour is forced** — decide it on its own merits.

**v1's rate limiting was essentially nothing** — one table (10 searches/hour/user/event) provisioned and never wired up, because the search Lambda was a stub. `P-97` replaces it wholesale; there is nothing to untangle.

---

## Housekeeping the user should be reminded of

From `HANDOFF.md` §6: v1 left a live AWS access-key CSV, a Google OAuth client secret, and a **CloudFront signing private key committed as a real PEM file** in the now-deleted source folder. **These need rotating regardless of what gets built.** Add a secret scanner (e.g. gitleaks) from the first commit — exactly the gap that would have caught it.

**Also unresolved:** the user should check their AWS account's actual creation date. The 6-month Free Tier clock is the project's real deadline and is already running.

**Still uncommitted:** `master` has zero commits. Every document in `Miscellaneous/` exists only on disk.

---

## Suggested skills

- **`/grill-me`** — installed at `~/.claude/skills/grill-me/`. A thin wrapper ("a relentless interview to sharpen a plan or design"); the substance is asking hard questions one cluster at a time. User-invocable only, so it won't appear in auto-listed skills. Used across all three product sessions and suits the technology discussion just as well.
- **`/domain-modeling`** — **now due.** The product is locked and the data model is the natural first technology artefact. §8 fixes the vocabulary for membership states; keep it consistent. The model must carry: retained per-photo face IDs, per-event match sets, frozen-filter state, batch status, display names, stored QR images, and access-code attempt counters.
- **`/research`** — for anything cost- or capability-shaped. Every "verified fact" above came from doing this properly, and **four of those findings overturned spec assumptions**, most recently `D-96` against `P-20`.
