# Session Handoff — Glimpses product lock-in

**Written:** 2026-08-05, evening *(product lock complete; revisions pending)*
**Current phase:** Product review before technology discussion. The user is reviewing the 98 locked rulings and may request revisions that overturn some existing decisions.
**Next steps:** Accept revision requests via changes to `PRD.md` and `LOCKED_PRODUCT.md`, then proceed to the technology discussion once the user is satisfied.

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

Document conventions: `P-nn` and `D-nn` ids are **permanent and never reused or renumbered**. Questions killed by a ruling are marked `DISSOLVED`, not deleted. **Recount statuses from table rows; never decrement a figure.**

---

## Where things stand

**Product: 98 ruling locked · 0 open · 5 unruled/assumed — 87 decision rows total.** (The 5 unruled items are in the spec as explicit assumptions; they are not open questions.)

**Technology: nothing decided.** Deliberately deferred.

**Repo state:** `master` has one commit (b60e14a, locking the product). Backend and Frontend are empty directories. No secret-scanner (gitleaks) installed yet.

### The product in one paragraph

Sign up with email, password and a display name, verifying by numeric code. Join an event with a 6-character code or by scanning its QR, either walking straight in or waiting in a lobby for approval. See every photo in the event immediately. If you've added a selfie to your profile, the event opens directly on the photos you're in, and they keep updating as more arrive — you're never asked to search, and there is no way to re-run matching. Anyone admitted can add photos unless the organizer turns that off, and can share the code onward. Nobody is notified of anything, ever. Photos carry no uploader attribution and download at full resolution, individually or as an archive. Events go read-only after 30 days without an upload and are deleted 30 days after that.

### What changed since the last session

- **`PRODUCT_WALKTHROUGH.md` was written** — the readable, end-to-end walkthrough of all 98 rulings, grouped by user journey rather than decision order. ~541 lines, designed to be read in one sitting and checked against.
- **All 98 rulings are verified to appear in both the spec and the walkthrough** — no ruling is missing from either.
- **`SESSION_HANDOFF.md` and `CLAUDE.md` were updated** to reflect the product lock being complete.
- **First commit pushed to `main`** (b60e14a) — 6 files, 1,569 lines, including `.gitignore` with credential patterns v1 leaked.

### What still needs doing before the technology discussion

1. **v1's leaked credentials need rotating** — AWS access key, Google OAuth secret, CloudFront signing PEM. These were in a deleted source folder but deletion is not revocation.
2. **Check AWS account creation date** — the 6-month free-tier credit clock is the project's real deadline.
3. **`gitleaks` installation and pre-commit hook** — before any real code is committed.
4. **Any product revisions the user wants to make** — which is the current phase.

---

## The five unruled/assumed items

These were flagged in the spec as open or explicitly assumed. They are *not* open questions in `PRD.md` — they are embedded in the rulings and marked as such.

| Item | Where marked | What it is |
|---|---|---|
| **Which AWS region** | `P-95` | Locked that there is one region; not which one |
| **Event date mutability** | `P-89` | Assumed immutable like the name; flagged as an assumption |
| **Whether account deletion exists at all** | `P-74` | Labeled "forced, not ruled — open to override" |
| **Rate-limit thresholds** | `P-97` | The mechanism is locked; the numbers are not |
| **Collection architecture** | `P-98` | Assumed one collection per event; a technology decision |

---

## How to work with revisions

**The user will indicate a change by describing it in conversation.** You should:

1. **Understand what's changing** — ask clarifying questions if the scope is ambiguous. Is it just one ruling, or a cluster?
2. **Surface the cascade** — if `P-20` is revisited, note that `P-68`, `P-73`, `P-75`, `P-76` and `P-98` share "forward-only" and may need reconsideration too.
3. **Update `PRD.md` first** — mark the affected `D-nn` row as reopened or add a new one if needed, describing the proposed change.
4. **Update `LOCKED_PRODUCT.md`** with the new ruling, rewriting affected related entries, and adding a dated row to the decision log.
5. **Check the walkthrough** — does it still describe the product truthfully? Update it if the change affects user-facing behavior.
6. **Verify coverage** — run the python script to confirm all rulings appear in both the spec and the walkthrough.

If a change cascades into five rulings, present all five at once as a cluster, not serially — the user should see the full consequence.

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
- Batch state needs a terminal deadline (`P-53`) and a silent retry budget inside it (`P-56`).
- File type sniffed from content, not extension (`P-54`).
- Stored QR images per event, generated at creation, deleted on event deletion (`P-90`).
- Access-code attempt counter per account and per IP, in application code (`P-97`).
- ~30-minute end-to-end target for 1,000-photo batch (`P-94`).
- Scroll-position restoration in the gallery (`P-63`).
- Empty "my photos" state designed deliberately (`P-65`).
- Frozen-filter state visibly marked (`P-69`).
- Event deletion screen stating that contributed photos remain (`P-74`).
- "Deletion is not retroactive" wording on photos and ejection (`P-44`, `P-29`).
- Event lifetime stated at creation and warned before transition (`P-33`).
- Terraform resource names parameterised from the start, or `P-95` becomes expensive to reverse.

---

## Suggested next steps

1. **Review the product** — read `PRODUCT_WALKTHROUGH.md` and flag anything you'd like to change.
2. **Propose revisions** — one at a time. The AI will surface cascades and present options.
3. **Once satisfied** — begin the technology discussion. Stack, data model, service shapes.

---

## Housekeeping reminders

- v1 leaked AWS key, OAuth secret, CloudFront PEM — **rotate these regardless**.
- Check AWS account creation date — the 6-month clock is the deadline.
- `gitleaks` should be installed and hooked before real code is committed.
