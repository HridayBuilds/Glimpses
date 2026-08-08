# Glimpses — Technology Explanations

**What this file is:** the teaching material behind every ruled `T-nn` — what the thing physically is, how it actually works, what alternatives existed and why one won. Written so the user understands and can justify each decision, not just use it. This is a **build-and-learn project** — the point of this file is that the user could explain any entry here to someone else without re-deriving it.

**What this file is not:** the reference. It does not state the final answer tersely — that lives in **`LOCKED_TECH_DECISIONS.md`**, linked by the same `T-nn`. Read that file to know what Glimpses runs on; read this one to understand why.

**How each entry is written** — same discipline that ruled the product, adapted for concepts rather than product behaviour:

1. **Build up from what the thing physically is**, the way `PRODUCT_WALKTHROUGH.md` explained EXIF as "a small block of text inside the photo file" before naming it. A Lambda cold start, a DynamoDB GSI, a Step Functions state machine — plain language first, jargon second.
2. **Run every real option through named concrete scenarios** — reuse the cast (Meera, Arjun, Priya, Rohan, Sam) wherever the technology choice has a user-visible or operator-visible consequence; introduce new technical scenarios (e.g. "a batch of 1,000 photos", "a Lambda cold start under load") where the product cast doesn't reach.
3. **A scorecard** — options as rows, scenarios or criteria as columns.
4. **What v1 did, and whether this repeats or departs from it** — every entry cross-references `HANDOFF.md` where relevant, since avoiding v1's mistakes by name is the point of this phase.
5. **The recommendation, marked, never assumed.**

**Covers:** 5 of 8 agenda areas explained so far. **Opened:** 2026-08-06.

---

## 1. Runtime and language

### `T-01` — Backend runtime and language: all Python

**What "runtime and language" actually means:** each AWS Lambda function is its own independent process — you choose its language when you create it, and different Lambdas in the same app can run different languages with zero conflict. So this was never really a single on/off switch; it was "how many languages does this backend use, and where's the line drawn."

**Why it was even a question:** the user wanted a Node/TypeScript vocabulary — `handler → manager → procedure/converter → DAO`, middy, DynamoDB Toolbox — but also confirmed early that HEIC→JPEG conversion (`P-35`) should be Python specifically, since Python's `pillow-heif` has prebuilt wheels and just works, while Node's standard image library `sharp` **deliberately excludes HEIC support** (a patent-licensing decision by its maintainer, not a gap that will close). That left it genuinely open whether "Python for this conversion" meant one function or the whole stack — and v1 had already drifted here once, planning Node/TS and shipping Python by default because AWS's own Rekognition/S3/DynamoDB examples are Python-heavy (`HANDOFF.md` §2). This ruling exists so the same thing doesn't happen by accident twice.

**Options run through the cast:**

- **A — All Python.** Every Lambda, HEIC included, Python/boto3.
- **B — All Node/TS.** Eliminated immediately — HEIC has no clean Node path.
- **C — Node/TS backbone + one isolated Python Lambda for HEIC only.** Resolves the ambiguity literally: the vocabulary lives everywhere except one narrow, S3-in/S3-out function.

| | Meera (uploads HEIC selfie) | Arjun (bulk ZIP, mixed formats) | Sam (self-deploys via Terraform) | Matches named vocabulary |
|---|---|---|---|---|
| A — All Python | ✅ native | ✅ same | ✅ one runtime, one build step | ❌ — no Python middy/Toolbox equivalents |
| B — All Node/TS | ❌ no viable HEIC path | ❌ same | — | — (eliminated) |
| C — Node/TS + isolated Python HEIC | ✅ native, isolated | ✅ same | ⚠️ two runtimes, two Lambda build steps | ✅ everywhere but one function |

**Two concepts worth knowing, since they were the actual deciding factor:**

- **middy** is a small wrapper around a Lambda handler that lets you bolt on reusable steps — parse the JSON body, catch errors, add CORS headers — instead of repeating that logic in every handler.
- **DynamoDB Toolbox** is a TypeScript library that lets you define a table's shape once and get back typed read/write calls, instead of hand-building raw AWS SDK attribute-expression strings. Its real value is in **single-table design**, where one table holds several entity types sharing a key space and it's easy to build the wrong key by accident.

Both are Node/TS-only. That's what made C attractive at first — until each was checked against what this project actually needs, independently of the runtime question:

- **middy turned out to duplicate, not add.** AWS Lambda Powertools' router (available in *both* languages) already handles routing, API Gateway response conversion, and CORS as a `.use()` middleware. Adding middy on top would be two overlapping middleware systems — and "a dependency shipped in the layer, never wired into the handlers" is literally listed as a v1 mistake in `HANDOFF.md` §7 (Powertools and pydantic shipped, never used). Skipping middy avoids repeating that in reverse.
- **DynamoDB Toolbox turned out not to fit the data model.** Glimpses is keeping v1's multi-table, GSI-per-access-pattern design (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`) rather than single-table design. DynamoDB has no server-side join in either language, so a "join" here is always an ordinary `get`/`batchGet` across separate tables — the key-collision problem Toolbox exists to prevent doesn't arise. Plain typed wrapper functions over `boto3` give the same type safety without an extra dependency.

**With both of those neutralized, the vocabulary argument for C collapsed to almost nothing** — `handler → manager → procedure/converter → DAO` is a file-layout convention, not a Node feature; it works identically as `handler.py → manager.py → dao.py`. What was left was a straight, much smaller tradeoff:

| | Cold start @ 512MB | Router maturity | Toolchain |
|---|---|---|---|
| A — All Python | ⚠️ slightly slower (heavier interpreter/import boot) | ✅ years-old, stable, OpenAPI + Pydantic validation built in | ✅ one runtime, one build step |
| C — Node/TS + isolated Python HEIC | ✅ small, consistent edge (V8 boots faster) | ⚠️ newer — found split across two still-settling import paths in current docs | ⚠️ two runtimes, two build steps |

For an I/O-bound JSON API where the DynamoDB round-trip dominates latency either way, Node's cold-start edge was judged not worth a second toolchain and a less mature router — especially once there was no vocabulary cost left to offset it.

**Ruled 2026-08-08: A — all Python.** Consolidated routing uses Powertools' `APIGatewayRestResolver`. No middy. No DynamoDB Toolbox.

**Cross-reference to `HANDOFF.md`:** this directly answers §2's drift note (Node/TS planned, Python shipped) by making the same outcome a deliberate choice instead of an accident, and directly avoids repeating §7's "unused dependency shipped in the layer" mistake with middy.

## 2. Ingestion orchestration

### `T-02` — Face-indexing fan-out: Step Functions Distributed Map

**The problem, physically stated:** indexing Arjun's 1,000-photo batch means calling Rekognition once per photo. That can't be one Lambda looping 1,000 times — Lambda has a hard 15-minute maximum runtime, and a crash partway through loses track of what's already done. It has to be many separate, independent Lambda runs, coordinated by something that hands out the work, retries failures, sets aside the ones that keep failing, and knows the moment every photo is accounted for.

**Two ways to build that coordinator, both considered:**

- **SQS + DLQ (what v1 built).** A queue holds one message per photo. A worker Lambda picks a message, works on it, and deletes it when done. If it crashes or times out without deleting the message, the message reappears after a timeout and another worker retries it — retry falls out of *not telling the queue you're finished*, not written code. Messages that fail enough times move to a second, idle queue (the dead-letter queue) instead of retrying forever. The gap: nothing here knows when the whole batch is done — v1 had to add a separate loop, polling a DynamoDB counter every 15 seconds, wrapped in its own Step Functions Standard workflow state.
- **Step Functions Distributed Map.** One state in the ingestion workflow, given a list of items, that runs the indexing Lambda once per item — many in parallel, up to a concurrency ceiling you set (`MaxConcurrency`) — with retry-with-backoff and a tolerated-failure-percentage written directly onto the state as configuration, not code. Because the fan-out is one state, the diagram simply advances to the next state the instant every item is accounted for — "is the batch done" isn't a question answered by separate code, it's what the state finishing already means.

**Where the list of items comes from matters, and it's a real constraint, not a style choice.** Step Functions caps data passed between states at 256KB. v1 already established the discipline of never carrying bulk data through the state machine — *"only `jobId` was carried through state-machine JSON... Lambdas read/write S3 and DynamoDB directly"* (`HANDOFF.md` §4). The Distributed Map's `ItemReader` setting lets it read its item list directly from an S3 location — by the time this state runs, the extraction step has already written all the batch's photos into S3, so the Map state is simply pointed at that folder. Nothing about the batch's contents ever passes through the workflow's own JSON.

**The concurrency ceiling is bound by Rekognition, not by Lambda.** Lambda can trivially run hundreds of invocations at once — it was never the constraint. Rekognition enforces its own account-wide rate limit (a Service Quota) on `IndexFaces` calls, independent of how many Lambdas fire at once; sending more than that limit just produces throttling errors that the retry logic then has to absorb, which is slower, not faster. New or lightly-used AWS accounts commonly start **below** the commonly-cited default of 50 TPS — this project's account measured **5 TPS** before requesting an increase. `MaxConcurrency` has to track whatever the account's real, approved quota actually is.

**Run through the maths, so "will this be slow" has an answer:** even at a conservative 50 TPS, indexing 1,000 photos is roughly 20 seconds of raw Rekognition throughput — comfortably inside `P-94`'s ~30-minute design target, which is an accepted worst-case ceiling (heavy retries, a very large batch), not the expected runtime.

**Why Distributed Map over SQS, given both work:** SQS's pieces (queue, DLQ, worker, polling loop) are individually simple and extremely well-documented — that's real, and it's exactly what made v1 choose it, calling the alternative *"more advanced to configure and debug for a first build"* (`HANDOFF.md` §2). What tips it the other way here: Distributed Map removes the hand-rolled polling loop and DynamoDB bookkeeping entirely, and replaces scattered CloudWatch log-diving with one visual, per-photo execution history in the Step Functions console — a genuine advantage for a project whose stated goal is understanding what was built, not just shipping it. Cost is not a real differentiator at this scale (roughly $25 per million state transitions; a 1,000-photo batch is on the order of 1,000 transitions).

**Ruled 2026-08-08: Step Functions Distributed Map.** Two build-time obligations attached, both load-bearing: the item list is read from S3 via `ItemReader`, never passed as workflow JSON; and `MaxConcurrency` is a Terraform variable set to the deploying account's actual Rekognition quota, checked and requested-to-increase before relying on it, not hardcoded to an assumed default.

**Cross-reference to `HANDOFF.md`:** departs deliberately from v1's SQS choice (§2), while keeping its "don't carry bulk data through the state machine" discipline (§4) and directly serving `P-100`'s progress/retry requirement, which named this exact decision as its input.

## 3. API shape

### `T-03` — Backend Lambda-function shape

**What "how many Lambdas" actually means:** every endpoint in the API — `POST /events`, `GET /events/{eventId}/status` — has to be wired to something that runs code when it's called. That something is always a Lambda function, but nothing forces a one-to-one mapping between endpoints and functions. **API Gateway matches on the full path *pattern*, not a literal string** — `/events/{eventId}` and `/events/xyz789` are the same route as far as routing is concerned, `eventId` is just a variable handed to whichever code answers it. And critically, **you choose which Lambda answers each route by hand, in Terraform** — two routes sharing a URL prefix (`/events/{eventId}/join` and `/events/{eventId}/archive`) do not have to share a function just because their paths look similar. This was a live point of confusion worth recording: grouping by literal URL prefix is not a real pattern, because nearly everything in this product hangs off an event, and grouping that way would silently reintroduce "one Lambda for everything" by accident.

**Why it was a question:** v1 built one Lambda per business endpoint (9 functions, `HANDOFF.md` §2), each with its own IAM role and Terraform resource. `HANDOFF.md` §9 names the fork point directly: keep that, or move to something grouped, trading tighter security for less deploy boilerplate.

**Options run through the cast:**

- **A — One Lambda per endpoint (v1's shape).**
- **B — Fully consolidated, one Lambda for the whole API.**
- **C — Domain-grouped: a handful of Lambdas, each scoped to one bounded resource.**

| | Meera (opens gallery) | Priya (creates/manages event) | Rohan (adversarial — probes for over-broad permissions) | Sam (self-deploys via Terraform) |
|---|---|---|---|---|
| A — one per endpoint | ✅ tightest IAM per action | ✅ same | ✅ smallest blast radius per compromised function | ❌ 9+ separate Terraform resources, grows with every endpoint |
| B — one Lambda, all endpoints | ⚠️ works | ⚠️ works | ❌ one role needs the *union* of every permission any endpoint uses | ✅ one resource, one deploy package |
| C — grouped by domain | ⚠️ works, shares a role only with other endpoints touching the same table | ⚠️ works, same | ⚠️ blast radius bounded to one domain, not the whole API | ⚠️ a handful of resources, moderate boilerplate |

**Ruled 2026-08-08: C.** Five Lambdas, each scoped to exactly one DynamoDB table — Profile (`Users`), Events (`Events`), Membership (`EventAttendees`), Upload/status (`Jobs`), Gallery/photos (`Photos`). The grouping line is **what table an endpoint touches, not what its URL looks like** — `join_event` and `archive_event` both live under `/events/{eventId}/...` but write different tables, so they sit in different Lambdas despite the shared prefix.

**The pipeline's four steps, extending `T-02` rather than reopening it:** `InitializeJob` (creates the `Jobs` row) → `Extract` (unzip, `P-38` dedup, format-sniff, HEIC convert, `P-35` thumbnail — one pass, not two) → `IndexOnePhoto` (the Distributed Map's per-item invocation) → `Finalize` (tallies the batch, computes `P-55`'s terminal outcome and `P-85`'s storage total).

**Revised same day, while working through `T-06`'s Terraform module layout: these four steps share one physical Lambda, not four.** Step Functions still has four separate *states* — each one invokes the same Lambda ARN, passing a `step` value in its input (`{"step": "extract", ...}`), and the Lambda's own handler branches on it internally. This is the pipeline equivalent of the API Lambdas' path-based router, except there's no HTTP path involved at all, since nothing outside Step Functions can ever call this function.

**Why this is a different call than the API consolidation question above, not a contradiction of it:** Option B there (fully consolidate the API) was rejected because *"one IAM role carries the union of every permission any endpoint needs"* — real risk, because any external caller can hit an API Lambda directly through API Gateway. The pipeline Lambdas have **no external invocation path whatsoever** — the only thing that ever calls them is Step Functions, with input Step Functions generates itself. Remove the "a stranger can reach this directly" scenario, and a wide IAM role stops being the same kind of risk. What's left is a smaller, real cost: `IndexOnePhoto` runs far more often than the other three steps (once per photo, potentially hundreds of times a batch) and now carries the whole pipeline's dependencies — Pillow/`pillow-heif` for HEIC, zip handling — in its package even on invocations that never touch that code. Accepted as minor, since cold start is already amortized across a long batch. Also accepted: CloudWatch logs for all four steps now land in one log group instead of four, so isolating one step's logs takes a little more filtering than before.

**Two shared utility Lambdas, and a real distinction worth keeping straight: a shared code *library* vs. a shared Lambda *function* are not the same reuse.**

- A **library** (e.g. a `jobs_dao.py` imported into several Lambdas, extending `T-01`'s DAO-layer convention) runs *inside* whichever Lambda imports it — same process, same invocation. If the Lambda's real work succeeds, the library call succeeds or fails as part of that same atomic step.
- A **separate Lambda function**, called as its own state, is a genuinely separate execution — over the network, with its own chance to fail *independently* of the step that called it.

Both count as "reuse" (one place the logic lives, not copy-pasted), but only the second introduces a gap where real work can succeed while the follow-up call fails on its own. This was worked through directly for **`db-api`** — a generic status-writer Lambda, scoped to the `Jobs` table only, called as its own state from four points in the ingestion pipeline (marking `EXTRACTING`, `INDEXING`, the terminal outcome, `FAILED`) rather than embedded in each pipeline Lambda's own code. **The user's explicit choice was the separate-Lambda version**, accepting the gap it introduces — a `db-api` call failing right after `Extract` finishes could abort a batch whose 1,000 photos are already safely in S3 — on the grounds that Step Functions' own `Retry` makes this rare in practice, and `db-api`'s narrow scope (one table, nothing else) keeps its IAM role tight regardless of how many places call it.

The **HEIC→JPEG converter** is the same shape of shared Lambda, called from `Extract` (batch ingestion) and `Profile` (selfie upload) — `P-35` requires the conversion everywhere an image enters the product, so one function serving both call sites avoids writing the conversion logic twice.

**Total: 8 Lambdas** — 5 API-facing, 1 consolidated pipeline, 2 shared utility. v1 had roughly 16 (9 business + 7 pipeline).

**Cross-reference to `HANDOFF.md`:** directly answers §9's named fork point ("one-Lambda-per-endpoint again, or a grouped/router pattern... at the cost of a slightly heavier single function"), choosing the middle position deliberately rather than re-inheriting v1's shape or over-correcting to full consolidation.

## 4. Data model

### `T-04` — Data model: multi-table

**What DynamoDB physically is:** not a spreadsheet — closer to a giant rented filing cabinet. Every stored item is a folder that can hold whatever fields it needs (unlike a SQL row, items in the same table don't need matching shape). To find a folder fast, DynamoDB needs a label on it: a **partition key (PK)**, which decides which physical shelf the folder lives on — give it the exact PK and DynamoDB goes straight there, instantly. An optional **sort key (SK)** lets many folders share one PK and stay ordered on that shelf, so a range of them (e.g. "all of Priya's photos, newest first") comes back in one trip. A **GSI (Global Secondary Index)** is a second, auto-maintained copy of the table with a different PK/SK, for asking a different question of the same data — `Events.organizer-index` answers "this organizer's events," while the main table only answers "this one event by id." The hard rule underneath all of it: DynamoDB can only answer questions shaped like "give me the folder(s) with this exact label" — an exact PK, or a PK plus an SK range, via the table or a GSI. There is no SQL-style arbitrary `WHERE`; anything else means scanning the whole table.

**The actual question:** one filing cabinet per entity type, or one cabinet for everything?

- **A — Multi-table.** Each entity — `Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees` — gets its own table, keyed by its own natural id. Answering "show Meera this event's photos" takes two trivial calls: one to `Events` for the name, one to `Photos` via its `event-index` GSI for the photos. Simple code, one table maps to one concept.
- **B — Single-table.** Every entity shares one table, using generic `PK`/`SK` attributes with the entity type baked into the key value as a prefix (`EVENT#123`/`METADATA`, `EVENT#123`/`PHOTO#456`, `USER#abc`/`EVENT#123` for a membership row). The payoff: if an event's own item and its photo items share the same `PK`, one Query returns both together — an "item collection," fewer round trips. The cost: the full key scheme has to be designed before writing any code, since every access pattern it doesn't anticipate is expensive to retrofit — this is exactly the problem DynamoDB Toolbox exists to manage, already ruled unnecessary in `T-01` on the assumption multi-table would be chosen here.

**Run through the cast:**

| | Meera opens gallery (event + its photos) | Arjun checks batch status (one `Jobs` row) | Priya views event stats (one `Events` row) | Rohan, adversarial (can a compromised Lambda reach outside its domain?) | Sam self-deploys via Terraform |
|---|---|---|---|---|---|
| A — Multi-table | ⚠️ two trivial calls | ✅ one direct get | ✅ one direct get | ✅ IAM role says "this table only" | ⚠️ 6 DynamoDB resources, not 1 |
| B — Single-table | ✅ one call, if the key scheme was designed for it up front | ✅ same, if designed for it | ✅ same | ⚠️ one shared physical table — item-level IAM isolation needs key-prefix conditions, not just a table-scoped role | ✅ one table |

**Why A won, and why it wasn't really close:** B's whole reason to exist — fewer round trips across a deep, high-traffic entity graph — doesn't pay off here. Glimpses' graph is shallow (nothing needs more than one or two hops), so multi-table's extra round trip costs milliseconds, not a real performance problem. What decided it was the Rohan column, and it ties directly back to `T-03`: that ruling already scoped each API Lambda's IAM role to exactly one table (Profile → `Users` only, Membership → `EventAttendees` only, and so on). Under multi-table that isolation is structural — a table boundary *is* an IAM boundary, free. Under single-table, the same guarantee would have to be rebuilt by hand with item-level key-prefix IAM conditions, a technique nobody on this project has used before, just to get back to where `T-03` already stood. Choosing B here would have effectively reopened `T-01` too, which assumed multi-table when it ruled DynamoDB Toolbox unneeded.

**Ruled 2026-08-08: A — multi-table, 6 tables.** Drops v1's 7th table, `SearchRateLimit`, outright: `P-16` removed search as a user action entirely, so there is nothing left to rate-limit that way. The remaining six keep v1's own "every GSI tied to a named access pattern" discipline (`HANDOFF.md` §3), which survives this decision unchanged.

**Left open, not decided here:** each table's actual field list and GSI definitions — including how `P-57`+`P-16` force cursor-based pagination (position-based paging breaks when new photos can appear mid-scroll) and how `P-85`'s storage-byte counter stays correct across `P-44`/`P-52`/`P-38`/`P-55` — is a following sub-decision, not this one.

**Cross-reference to `HANDOFF.md`:** keeps §3's stated design philosophy ("single-purpose tables... easier to reason about... every GSI justified against a named access pattern") deliberately, rather than trading it for single-table's join-reduction, which this project's shallow entity graph doesn't need enough to be worth the IAM ground `T-03` would otherwise give back.

## 5. Rekognition collection lifecycle

### `T-05` — Rekognition collection layout: one per event

**What Rekognition physically does, before naming anything:** face *detection* just finds rectangles around faces in a photo — it doesn't know whose faces they are. Face *recognition*, which Glimpses needs, is the part that can tell two photos show the same person. It works by never storing the photo of the face at all — it runs the pixels through a trained model and gets back a **vector**, a list of a few hundred numbers describing the geometry of that face, such that two photos of the same person produce close numbers and two different people produce numbers far apart. Comparing faces later is just comparing two lists of numbers for closeness (a similarity score 0–100 — `P-80`'s fixed threshold of 80 is a cutoff on this score).

**A "collection" is just a named bucket of these vectors — nothing more, and nothing forces one shape or another.** Four operations touch it: `IndexFaces` (compute a photo's face vector(s) and store them in a named collection — this is `IndexOnePhoto`, once per photo), `SearchFaces`/`SearchFacesByImage` (compare a face against every vector in one named collection, one call, whatever the collection holds — `P-20`'s `D-96` box already established this), `DeleteFaces` (remove specific vectors by id from a collection — what `P-52`'s forced consequence needs), and `DeleteCollection` (delete the entire named bucket at once, instantly — what `P-32` relies on for archiving). The name (`CollectionId`) is a string you choose; the API doesn't care whether you use one collection for everything or one per event.

**The actual question, run through the cast:**

- **A — One collection per event.** `create_event` creates a collection; `IndexOnePhoto` indexes into it; a search only ever queries that one collection; archiving is one `DeleteCollection` call.
- **B — One shared, account-wide collection.** Created once, in Terraform; every vector tagged with an `ExternalImageId` (a free-text label Rekognition attaches and returns with results) carrying the `eventID`; a search returns matches from *every* event ever run, filtered down to one event in application code.

| | Meera searches (her one event) | `P-32` archive (collection must die) | `P-52` deletes one photo (must remove just its vectors) | Sam self-deploys via Terraform | Cross-event leak risk |
|---|---|---|---|---|---|
| A — Per-event | ✅ search physically cannot see another event's vectors — `P-07`'s boundary enforced by AWS | ✅ one `DeleteCollection` call | ✅ `DeleteFaces` against the one relevant collection | ⚠️ collections created/destroyed at runtime by app code, invisible to Terraform | ✅ structurally impossible |
| B — Shared | ⚠️ every result must be correctly filtered by tag in application code before display | ⚠️ must find and `DeleteFaces` exactly that event's vectors out of a shared bucket | ⚠️ same tag-targeting requirement | ✅ one static, Terraform-managed resource | ❌ one filtering bug away from showing one event's photos to another event's attendee |

**Why A won, and why it wasn't close:** `P-07` already rules "no cross-event visibility, ever" as a hard permission boundary. Under A that boundary is a property of the AWS API itself — a `SearchFaces` call against one collection cannot return another collection's vectors, full stop. Under B the exact same boundary would depend entirely on application code correctly filtering every single search result, forever, with a real data leak (one event's attendee seeing another event's photos) as the failure mode of a filtering bug anywhere in that path. `P-32`'s archive design — already locked in the product spec's table as "Rekognition collection exists: Yes → Deleted" — is a single API call under A; under B it becomes a targeted deletion job that has to find exactly the right subset of a shared bucket. B's only genuine advantage is operational: a collection created once in Terraform is visible to infrastructure tooling in a way a runtime-created one isn't — real, but a lifecycle-tracking convenience, not a reason to share a security boundary across every event an account will ever run.

**Ruled 2026-08-08: A — one collection per event.** Design obligation carried over from `HANDOFF.md` §4/§9 (v1 hit this same fork point): collections are created and destroyed by application code at runtime, not Terraform, since a collection is tied to a dynamic `eventID` rather than being static infrastructure — Terraform has zero visibility into it either way. The collection's id is tracked on the `Events` table (`rekognitionCollectionID`, exactly as v1 already did) specifically so a teardown script can enumerate and clean up orphaned collections without depending on Terraform state, closing the gap v1 discovered only during a real manual teardown.

**Cross-reference to `HANDOFF.md`:** directly answers §9's named fork point ("rely on Terraform... or keep the DynamoDB-tracked approach... and build a teardown script around that from the start, rather than discovering it as a manual step during a real teardown") by choosing the DynamoDB-tracked approach deliberately, before any teardown is needed.

## 6. Terraform state and naming

### `T-06` — Terraform state backend, module layout, deploy discipline, CI/CD granularity, and naming

**What Terraform physically manages.** A `.tf` file is made of **resource blocks** — each one describes one real thing that should exist in AWS (e.g. `resource "aws_lambda_function" "profile" { memory_size = 256, ... }`). Terraform juggles three things at once: the `.tf` files (what you *want*), AWS itself (what's *actually there*), and a **state file** — Terraform's own private memory of what it last knew to be true. Every `apply` does the same three-way comparison: ask AWS what's real, check the state file for what was last recorded, check the `.tf` files for what's wanted — then change only the differences. This comparison is why a resource that already matches produces zero AWS calls on a re-run — not a special "already exists" case, just an empty diff.

**Modules are folders, not magic.** A module is just a folder of `.tf` files that's inert on its own — nothing in it deploys until something calls it. The root folder (here, `/infrastructure`) is the one place with no resources of its own; its entire job is `module` blocks in `imports.tf`, one per child module, that call every folder into existence. A module only sees what's explicitly handed to it via a `variable` block (its `input.tf`), and only exposes what it explicitly returns via an `output` block (its `output.tf`) — the same discipline as a function's parameters and return value, nothing implicit crosses the folder boundary.

**Sub-decision 1 — where does the state file live, and how is it locked?**

State locking exists because two overlapping `apply` runs, without it, can silently destroy each other's work: run #1 reads state version 10, starts changing AWS; run #2 starts before #1 finishes, also reads version 10 (unaware of #1's in-progress changes); #1 finishes and writes version 11; #2 finishes and writes version 12 — computed from the stale version 10, silently erasing everything #1 did. A lock is nothing more than a marker written the instant an `apply` starts, checked by every other `apply` before it's allowed to proceed; if the marker's present, it refuses cleanly with an error instead of racing.

| | A — Local state | B — S3 + DynamoDB lock | C — S3 + native lock |
|---|---|---|---|
| Sam deploys from a fresh laptop | ❌ no shared memory of what's built; recreates or needs a manual state-file handoff | ✅ points at the same bucket, sees the same picture | ✅ same |
| Overlapping-apply protection | ❌ none | ✅ | ✅ |
| Extra AWS resource to create/manage | none needed | a DynamoDB table | none |
| Requires Terraform version | any | any | ≥1.10 |

**Ruled: C.** Same protection as B, one fewer resource to create and IAM-permission, at the cost of a Terraform-version floor that's a non-issue on any current install. **Versioning turned on** as separate, cheap insurance — a rollback path if a bad apply ever needs undoing, unrelated to locking. **Load-bearing correction made in-session:** committing the state file to Git is never a substitute for this, regardless of which backend is chosen — state files store real values in plaintext even for Terraform variables marked `sensitive` (that flag only suppresses the value from being *printed* to console/log output — it does nothing to the value as stored in the file), and the file is a single unmergeable JSON blob rewritten wholesale on every apply. `terraform.tfstate*` stays gitignored, matching what v1 already did.

**Sub-decision 2 — module layout.** v1 used one centralized `infra/modules/functions/` module that looped over every Lambda via a map — one shared piece of code computing each Lambda's shape and name. That centralization is the direct cause of `HANDOFF.md` §7's naming bug: a name computed once, centrally, had to be independently recomputed by the deploy script, and the two silently drifted apart (a `glimpse-dev-` prefix and a hyphen/underscore convention the script had to strip by hand). **Ruled:** each of the 8 Lambdas (`T-03`) gets its own folder, `Backend/<name>/`, holding its code plus a self-contained `infra/` child module (`lambda.tf`, `iam_role.tf`, `iam_policies.tf`, `cloudwatch.tf`, `input.tf`, `output.tf`) — nothing about one Lambda's shape or name is computed anywhere a second, independent piece of code has to separately agree with. `cloudwatch.tf` living inside each Lambda's own folder specifically closes a second, related `HANDOFF.md` §7 bug: a centralized alarm list that let new Lambdas silently ship with no alarm attached.

**Sub-decision 3 — deploy discipline: who builds the state machine?** "State machine" is just the Terraform-side name for the Step Function `T-02` already ruled on (Distributed Map ingestion orchestration) — a distinct AWS resource, separate from the Lambdas it calls, whose definition has to embed the real ARNs of the Lambdas it invokes (`PipelineHandler`, `db-api`). Those ARNs only exist once Terraform has already created those Lambda resources — via `CreateFunction`, the one-time AWS call that brings a Lambda into existence and hands back its ARN. This is a **different, earlier** moment than a Jenkins code push: `UpdateFunctionCode` (what Jenkins calls to push real code into an already-existing Lambda) is a separate AWS call that fails outright if the Lambda doesn't already exist — concrete proof that Jenkins never creates the resource itself, only refreshes what's inside one that Terraform already made.

The complication: `-target` (as in `terraform apply -target=module.pipeline_lambda`) tells Terraform to only look at that one module and whatever *it* needs — never anything that *depends on* it. So a targeted apply, run any number of times, from any Lambda's own Jenkinsfile, will never build or update the state machine, since the state machine depends on the Lambdas, not the other way around.

| | A — dedicated CI job runs the untargeted apply | B — piggyback on one Lambda's pipeline (prior-company pattern) | C — decouple via `data` lookup by name |
|---|---|---|---|
| Correctly handles a *new* cross-cutting change later (e.g. a 9th Lambda the state machine needs) | ✅ always, by design | ❌ only if that one special-cased Lambda happens to be involved | ✅ no ordering dependency to break |
| Routine single-Lambda deploys stay fast | ✅ unaffected | ❌ every deploy of that one Lambda also runs a full apply | ✅ unaffected |
| Review checkpoint at the riskiest moment (multi-module wiring change) | ✅ — plan output shown before confirming | weak — buried in a routine deploy | none — no dependency forces a review |
| Drift risk (the actual `HANDOFF.md` §7 bug shape) | low | low | higher — a typo'd name lookup fails silently, no compile-time check the way `module.x.arn` has |

**Ruled: A.** A separate, dedicated CI job — belonging to no single Lambda — runs the plain, untargeted `apply` whenever module wiring changes (first build, or later additions). Every Lambda's own Jenkinsfile stays targeted, plus its code push, and never triggers this. B was considered directly (it's the pattern used at the user's prior company) and set aside for the general case: it depends on remembering an indirect trigger ("wiring changed → go run *that unrelated* Lambda's job"), which is easy to get wrong the moment the change involves a Lambda other than the one special-cased. C was set aside as reintroducing exactly the class of silent-drift risk this whole decision exists to close.

**Sub-decision 4 — CI/CD granularity.** Resolving distinction: a Jenkinsfile's job (GitHub → zip → S3 → `update-function-code`) only makes sense for something with actual application code — the state machine and DynamoDB tables are pure Terraform config, nothing to zip or push. **Ruled: 9 CI/CD jobs** — 8 per-Lambda Jenkinsfiles (targeted apply + code push each) + 1 dedicated job for the Option-A untargeted apply, which is what actually builds the state machine and DynamoDB tables. Not one shared v1-style Jenkinsfile with a `DEPLOY_TARGET` parameter, and not a per-AWS-resource pipeline either — granularity follows "has code," not "is a Terraform resource." **Flagged separately, not itself a sub-decision:** the Terraform state bucket is a bootstrapping special case — it can't be created by an `apply` that depends on it already existing as a backend, so it's created once, by hand or a small one-off script, outside all 9 jobs.

**Sub-decision 5 — naming convention, the actual mechanism behind `HANDOFF.md` §7's bug.** v1's deploy script stripped a `glimpse-dev-` prefix and converted hyphens to underscores to translate between the Terraform resource name and the zip/AWS function name — three-plus spellings of the same Lambda, generated independently, kept in sync by a hand-written script rather than by a single rule.

| | A — one name, fixed prefix, no transform | B — environment-prefixed (v1's pattern) | C — centralized mapping file |
|---|---|---|---|
| Sam figures out which AWS Lambda a folder became | ✅ trivial — folder name *is* the AWS name (minus the fixed prefix) | needs to know/trust the prefix convention | has to open the mapping file |
| Adding a 9th Lambda later | rename folder, everything else follows | rename folder, prefix rule still has to be remembered | rename folder **and** add a mapping row — a forgettable extra step, same shape as v1's actual bug |
| Needed only if multiple environments share one AWS account | insufficient alone | ✅ this is what it solves | could also solve it |

**Ruled: A, with a fixed `glimpses-` prefix, applied identically everywhere, never conditionally.** Folder name is the single source of truth; the AWS-visible name is `"glimpses-" + folder_name` with underscores swapped to hyphens (the one unavoidable, but fixed and exception-free, translation — AWS Lambda names conventionally use hyphens, Python folders conventionally use underscores). B wasn't adopted since this project has no multiple-environment requirement the added indirection would pay for. C was set aside as still requiring a manual, forgettable step per new Lambda — centralizing the drift risk rather than removing it.

**Full naming table (all 8 Lambdas + DynamoDB tables + state machine + buckets) recorded in `LOCKED_TECH_DECISIONS.md`.**

**Cross-reference to `HANDOFF.md`:** this whole decision is a direct, deliberate response to §7's two concrete v1 bugs — the naming mismatch (closed by sub-decisions 2 and 5: nothing is computed twice, in two places, that has to agree) and the silent-missing-alarm problem (closed by sub-decision 2's per-Lambda `cloudwatch.tf`) — plus §2's local-state-only item, flagged there as never actually hardened (closed by sub-decision 1).

## 7. Observability, IAM, CORS, secrets

### `T-07` — Observability (ruled 2026-08-09; IAM granularity, CORS, secrets still open)

**Logging vs. tracing vs. metrics — three different questions, easy to conflate.** A **log line** is one event, in its own words: "photo `abc123` indexed at 14:02:03." A **trace** is a timeline: how long each hop of one request took, and in what order, across every service it touched. A **metric** is a number tracked over time that can be graphed and, critically, alarmed on: "count of failed photos this hour." All three describe overlapping ground, but only a metric is the kind of thing CloudWatch can watch and act on automatically.

**Structured logging, concretely.** `print(f"Indexed photo {photoID}")` writes one line of plain text to CloudWatch — findable only by text search. Powertools' `Logger` instead writes one line of **JSON**: `{"message": "Indexed photo", "photoID": "abc123", "jobID": "job-9", "eventID": "evt-4", "timestamp": "..."}`. CloudWatch Logs Insights can then query it like a small database — `filter jobID = "job-9"` returns every line, from every one of the 8 Lambdas, that touched that one job, in order. That specifically matters here because a single upload from Arjun crosses `Upload/status` → `PipelineHandler` (4 internal steps) → `db-api` (4 separate writes) → `IndexOnePhoto` (once per photo) — 8 Lambdas' worth of otherwise-separate log streams to reconstruct by hand under plain `print()`.

**Why this was cheap to add here, unlike v1.** `HANDOFF.md` §7 lists `aws-lambda-powertools` and `pydantic` as dependencies v1 shipped in every Lambda's layer but never actually used — pure cold-start weight, paid for and ignored. `T-01` already commits this rebuild to Powertools for API routing, so turning on its `Logger` isn't a new dependency, just using a piece of one already paid for.

**Ruled 2026-08-09: Powertools `Logger`, structured JSON, on all 8 Lambdas.**

**The "log everything vs. log deliberately" question.** Powertools has a convenience decorator, `@logger.inject_lambda_context(log_event=True)`, that auto-logs the *entire* incoming request — full body, headers — on every single invocation, no extra code. The alternative is leaving that off and only logging fields chosen deliberately (`jobID`, `photoID`, etc.). The concrete stakes: the `Profile` Lambda's request body carries the **selfie image** (`P-19`), and `P-68` already treats that selfie as sensitive enough that a user can delete it on demand and destroy the biometric template built from it. Turning `log_event` on means a copy of that selfie — and on other endpoints, raw auth tokens — lands in CloudWatch by default, a place nobody thinks to go scrub, structurally the same shape of mistake as v1's committed CloudFront private key (`HANDOFF.md` §6).

**Ruled: `log_event=True` — the full request is auto-logged, against the recommendation** (which was to log only explicit fields, given the selfie/token exposure above). **Direct consequence, decided in the same exchange:** CloudWatch log retention set to **3 days** per Lambda's log group — CloudWatch's own default is to never expire logs, so leaving it unset would mean selfie/token data accumulating indefinitely. This wasn't a separate open question; it followed necessarily from the `log_event=True` ruling.

**Tracing — what X-Ray adds that logs alone don't.** Even with structured `jobID` correlation, answering "which of the 8 hops was slow" from logs means manually comparing timestamps. X-Ray (via Powertools' `Tracer`) draws the same request as an actual timeline diagram — each hop shown as a segment with its own duration, e.g. "batch took 40 seconds, 35 of them were one slow `IndexFaces` call." AWS's X-Ray free tier (100,000 traces/month) comfortably covers this project's scale, so the real cost isn't money — it's the same "wired up but never opened" risk `HANDOFF.md` flagged for the unused Powertools/pydantic dependencies: a trace map only pays off if someone actually looks at it.

**Ruled: no X-Ray, against the recommendation** (which favored it, given the pipeline's fan-out shape — one request touching 8 Lambdas and dozens of `IndexOnePhoto` calls — is exactly what tracing is built to untangle). Cross-Lambda debugging stays a manual reconstruction from structured log timestamps.

**Custom metrics — why they're really a prerequisite, not a standalone win.** Lambda already emits some metrics for free with zero setup: `Errors`, `Duration`, `Invocations`, `Throttles`. A *custom* metric (via Powertools' `Metrics` class) would be something like a per-batch `PhotosFailedPercent`, tracking `P-100`'s tolerated-failure-percentage as a number CloudWatch could alarm on automatically — but a metric nobody's watching is no better than a log line nobody's reading. Since X-Ray was ruled out on the same cost/effort grounds, custom metrics were the smaller remaining win.

**Ruled: no custom metrics — AWS-default Lambda metrics only.** `P-100`'s failure threshold stays a manual read of Step Functions execution history, not an automatically-alarmable number.

**Alarms — fixing v1's actual documented bug, not a hypothetical one.** `HANDOFF.md` §7 records two distinct, real failures: *"no SNS topic was attached to any CloudWatch alarm — alarms existed but nothing was subscribed"* (an alarm is just a rule that flips a state — `OK` → `ALARM` — nothing more; without SNS, that flip happens in a console nobody's looking at) and *"the monitoring module's per-Lambda alarm list was hardcoded in root `main.tf`... new Lambdas silently get no alarm."*

**SNS, explained plainly:** an SNS "topic" is like a mailing list — CloudWatch publishes to it the moment an alarm flips state, and anyone subscribed (an email address, here) gets notified. Setup is one topic and one email subscription (a one-time "confirm subscription" click).

**Ruled: every alarm wired to an SNS topic with an email subscribed.** Given `P-81` — alarms are for the operator only, nothing here is ever user-facing — this closes the loop entirely to Sam/the operator's own inbox, never to Meera, Arjun, Priya, or Rohan.

**The hardcoded-list bug — already closed, not a fresh decision.** `T-06`'s per-Lambda module layout means each Lambda's `cloudwatch.tf` lives inside that Lambda's own folder, next to `lambda.tf` — not in a separate, centralized list disconnected from the actual Lambda inventory. Creating a 9th Lambda later means copying an existing module's folder as a template, and the alarm file comes along with it by construction; there is no second, unrelated file someone has to remember to also update. This was flagged out loud as already-settled by an earlier ruling, rather than silently assumed or re-litigated.

**Alarm content — kept deliberately narrow, matching the metrics ruling.** `Errors > 0` over a 5-minute evaluation window: every 5 minutes, CloudWatch sums that Lambda's `Errors` count for the window just passed; if the sum exceeds zero — i.e. at least one invocation failed — the alarm flips to `ALARM` and the SNS email fires. Same shape on all 8 Lambdas. No duration or throttle alarms were added — consistent with `P-81`'s operator-only scope and the same minimalism already applied to metrics (a few meaningful signals, not a dashboard).

**What's still open under `T-07`:** IAM granularity, CORS, and secrets hygiene — not yet discussed.

## 8. Testing approach and CI/CD
