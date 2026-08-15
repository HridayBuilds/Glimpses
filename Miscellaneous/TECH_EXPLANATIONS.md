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

**Revised again 2026-08-13, while scoping implementation folders: `InitializeJob` moved out of the pipeline Lambda entirely, into `db-api`; the pipeline Lambda renamed `ingestion`.** The trigger was noticing `InitializeJob` was the *only* reason the pipeline Lambda's IAM role needed `Jobs`-table access at all — `Extract`/`IndexOnePhoto`/`Finalize` never touch `Jobs`, and every other write to that table already lived in `db-api`. Since `InitializeJob`'s entire body is a single `PutItem` on `Jobs` — exactly the kind of one-table write `db-api` exists to hold — moving it there removes `Jobs` from the pipeline Lambda's manifest completely (now just `Photos`, `Events`, S3, Rekognition) and puts all 5 `Jobs` writes behind one role instead of two. Renamed the folder `pipeline` → `ingestion` at the same time, since "pipeline" stopped being as apt a name once job creation moved out, and "ingestion" was already the term used elsewhere in these docs for this exact state machine. The pipeline Lambda's three remaining steps still share one physical function, same `step`-branching mechanism as above — this change only moves *which* Lambda owns the first step, not how the rest are consolidated.

**Why this is a different call than the API consolidation question above, not a contradiction of it:** Option B there (fully consolidate the API) was rejected because *"one IAM role carries the union of every permission any endpoint needs"* — real risk, because any external caller can hit an API Lambda directly through API Gateway. The pipeline Lambdas have **no external invocation path whatsoever** — the only thing that ever calls them is Step Functions, with input Step Functions generates itself. Remove the "a stranger can reach this directly" scenario, and a wide IAM role stops being the same kind of risk. What's left is a smaller, real cost: `IndexOnePhoto` runs far more often than the other three steps (once per photo, potentially hundreds of times a batch) and now carries the whole pipeline's dependencies — Pillow/`pillow-heif` for HEIC, zip handling — in its package even on invocations that never touch that code. Accepted as minor, since cold start is already amortized across a long batch. Also accepted: CloudWatch logs for all four steps now land in one log group instead of four, so isolating one step's logs takes a little more filtering than before.

**Two shared utility Lambdas, and a real distinction worth keeping straight: a shared code *library* vs. a shared Lambda *function* are not the same reuse.**

- A **library** (e.g. a `jobs_dao.py` imported into several Lambdas, extending `T-01`'s DAO-layer convention) runs *inside* whichever Lambda imports it — same process, same invocation. If the Lambda's real work succeeds, the library call succeeds or fails as part of that same atomic step.
- A **separate Lambda function**, called as its own state, is a genuinely separate execution — over the network, with its own chance to fail *independently* of the step that called it.

Both count as "reuse" (one place the logic lives, not copy-pasted), but only the second introduces a gap where real work can succeed while the follow-up call fails on its own. This was worked through directly for **`db-api`** — a generic `Jobs`-table writer, called as its own state from four points in the ingestion pipeline (marking `EXTRACTING`, `INDEXING`, the terminal outcome, `FAILED`) rather than embedded in each pipeline Lambda's own code. **The user's explicit choice was the separate-Lambda version**, accepting the gap it introduces — a `db-api` call failing right after `Extract` finishes could abort a batch whose 1,000 photos are already safely in S3 — on the grounds that Step Functions' own `Retry` makes this rare in practice, and `db-api`'s narrow scope (one table, nothing else) keeps its IAM role tight regardless of how many places call it.

**A fifth touch point joined these four on 2026-08-13:** `InitializeJob`, moved into `db-api` from the pipeline Lambda (see the `T-03` revision above) — the same reasoning applies, since it's also a single write to `Jobs` and nothing else. `db-api`'s handler now branches on an `action` field (`create` for `InitializeJob`, `update_status` for the other four) — the same shape of internal branching the pipeline Lambda already uses for `step`, just one level smaller.

The **HEIC→JPEG converter** is the same shape of shared Lambda, called from `Extract` (batch ingestion) and `Profile` (selfie upload) — `P-35` requires the conversion everywhere an image enters the product, so one function serving both call sites avoids writing the conversion logic twice.

**Folder naming settled 2026-08-13:** the pipeline Lambda's folder is `ingestion` (renamed from `pipeline` the same day `InitializeJob` moved out, to match the term already used elsewhere in these docs for this state machine); `db-api`'s folder name stays `db_api`, unchanged — it was never named for the status-only shape, so gaining a `create` action alongside its four `update_status` calls doesn't make the name inaccurate.

**Total: 8 Lambdas** — 5 API-facing, 1 consolidated pipeline, 2 shared utility. v1 had roughly 16 (9 business + 7 pipeline).

**Cross-reference to `HANDOFF.md`:** directly answers §9's named fork point ("one-Lambda-per-endpoint again, or a grouped/router pattern... at the cost of a slightly heavier single function"), choosing the middle position deliberately rather than re-inheriting v1's shape or over-correcting to full consolidation.

### API Gateway flavour — HTTP API vs REST API (left open at `T-03`, ruled 2026-08-09)

**Left open deliberately at the time** — `P-97` leaves both viable, and the choice didn't block anything else on the agenda. Picked back up after the technology agenda closed, as one of two loose threads explicitly named as still open (the other, `T-04`'s per-table fields/GSIs, is separate and unrelated).

**Worth flagging before the ruling itself: a real drift risk was caught here, not just a stylistic wrinkle.** `T-01`'s locked text names Powertools' `APIGatewayRestResolver` for routing — a class specific to the REST API event shape, not interchangeable with `APIGatewayHttpResolver` (HTTP API's equivalent; the two Gateway flavors send Lambda a differently-shaped event payload, so the resolver has to match). Had REST API shipped by default just because that resolver happened to get named first, that would have been exactly the kind of implementation-drift decision this rebuild exists to prevent — v1's React 18/19 mismatch in a new outfit. Surfaced explicitly instead of resolved silently; it turned out to point at the same answer the ruling below reaches anyway, so `T-01`'s text needs **no correction**.

**What API Gateway is, and what an authorizer does.** API Gateway is the internet-facing front door — every request from a browser or the Glimpses frontend hits it first, before anything reaches a Lambda. Before forwarding a request, it can run an **authorizer**: a check answering "is this caller even allowed to knock?" Without one, every request — logged in or not — reaches the Lambda, and the Lambda's own code has to do the rejecting itself, on every endpoint, every time.

**What a JWT is, since both authorizer types are built around it.** When Meera logs in through Cognito, Cognito hands her browser a **JWT** (JSON Web Token) — a signed block of text carrying claims like "this is user `meera-123`, issued 10:00, expires 11:00." It's cryptographically signed, so nobody can forge one or edit the expiry without the signature breaking. Every request Meera's browser makes afterward carries this token; the authorizer's job is checking that signature and expiry before letting the request through.

**Cognito User Pool authorizer (REST API) vs JWT authorizer (HTTP API) — the actual difference, once the names are stripped away.** Both check the exact same Cognito-issued JWT the same way, for the same purpose. REST API's **User Pool authorizer** is purpose-built — it already knows the shape of a Cognito token specifically. HTTP API's **JWT authorizer** is generic — it works with any standards-compliant token issuer (Cognito, Auth0, anything), by being pointed at that issuer's public verification key. Cognito publishes tokens in the standard format either one expects, so for Glimpses' actual login check, **both produce an identical outcome** — this sounds like a real differentiator and isn't one.

**The differences that are real, verified against current AWS pricing and docs (2026-08-09):**

| | HTTP API | REST API |
|---|---|---|
| Price per request | $1 per million | $3.50 per million (3.5x more) |
| AWS WAF (edge firewall) | Not supported | Supported |
| Response caching at the gateway | Not supported | Supported |
| API keys / usage plans (rate-limit specific external clients) | Not supported | Supported |
| Resource policies (restrict calls to a specific VPC/IP range) | Not supported | Supported |
| Request-body schema validation at the gateway | Not supported | Supported |
| Cognito login check | Works (JWT authorizer) | Works (User Pool authorizer) — identical outcome |

**What a WAF actually does, and why it's the one differentiator that maps to something real here.** AWS WAF sits in front of API Gateway and inspects every incoming request for known-malicious shapes — SQL-injection-looking payloads, known-bad IP ranges, rate-based rules ("block an IP making 1,000 requests in 5 minutes") — rejecting them **before they ever reach the authorizer or a Lambda.** This matters specifically for Glimpses because **Rohan is a named adversarial persona in this project** — `P-07`'s access-control boundary exists because of exactly this kind of actor. Without WAF, a rate-based probe from Rohan still reaches a Lambda and gets rejected by the app's own auth code — same end result, but every one of his requests costs a real Lambda invocation and shows up in `T-07`'s `Errors`/`log_event=True` logging as noise to sift through. With WAF, many of those requests are stopped at the edge for free, before they cost anything.

The other REST-only features don't map to anything Glimpses actually does: no third-party API consumers exist to need usage plans/API keys, no product ruling calls for response caching, and there's no private-VPC requirement for resource policies — WAF is the one line item actually worth the price gap.

**Ruled: REST API**, accepting the 3.5x per-request cost over HTTP API, specifically for AWS WAF's edge-level protection against exactly the adversarial actor (Rohan) this project already designs around. `T-01`'s `APIGatewayRestResolver` was correct as written; no change needed.

Sources checked: [AWS API Gateway docs — choosing between REST and HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html); [AWS API Gateway pricing breakdown](https://amnic.com/blogs/aws-api-gateway-pricing); [Cognito authorizers with API Gateway](https://oneuptime.com/blog/post/2026-02-12-cognito-authorizers-api-gateway/view).

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

**Cross-reference to `HANDOFF.md`:** keeps §3's stated design philosophy ("single-purpose tables... easier to reason about... every GSI justified against a named access pattern") deliberately, rather than trading it for single-table's join-reduction, which this project's shallow entity graph doesn't need enough to be worth the IAM ground `T-03` would otherwise give back.

### `T-04` follow-up — per-table fields, PK/SK, GSI definitions (RULED 2026-08-09 → 2026-08-12, all 6 tables — closed)

**DynamoDB operations, in full, before ruling any table's keys:** beyond PK/SK/GSI above — `GetItem` takes an exact key and returns one item, the cheapest possible read. `Query` takes an exact PK plus an optional condition on SK (`=`, `<`, `between`, `begins_with`) and returns a sorted set, touching only the requested partition. `Scan` reads the *entire table* with no key involved, filtering afterward — slow, billed by table size not result size, avoided unless nothing else works. An **LSI (Local Secondary Index)** is a same-PK, different-SK alternate sort order sharing the base item's partition — unlike a GSI it must be declared at table creation and can never be added later, which is why GSIs are used far more often in practice. `BatchGetItem`/`BatchWriteItem` bundle up to 100 reads / 25 writes into one round trip. `UpdateItem` writes a partial change to one item and supports **atomic counters** (increment a field by N without reading it first) — the mechanism `P-85`'s storage-byte counter and `Events.photoCount`/`attendeeCount` will use. `TransactWriteItems` commits several writes atomically, all-or-nothing, reached for only when correctness genuinely requires it.

**`Users` — ruled 2026-08-09.** PK = `userID` (Cognito's `sub`), no SK, no GSI. Fields: `userID`, `displayName` (`P-84`), `email` (full-mirrored from Cognito, not just a pointer to it). The mirror-vs-pointer choice: a minimal mirror (only what Cognito doesn't already hold) avoids any sync risk but forces an `AdminGetUser` Cognito call anywhere an email is needed (`P-82`'s organizer view); a full mirror (email copied into DynamoDB too) is faster and cheaper to read at the cost of a second copy that could drift if email were ever editable. **Ruled: full mirror.** The drift risk that would otherwise be a design obligation is moot — Glimpses does not allow email changes post-signup. No GSI, because every access path to `Users` already arrives holding a `userID` (JWT for "my own profile," `EventAttendees` rows for "who's pending/admitted") — nothing ever starts from an email or display name and needs to find the user.

**`Events` — ruled 2026-08-09.** PK = `eventID`, no SK. Fields: `eventID`, `organizerID`, `name`, `accessCode`, `joinPolicy`, `contributionPolicy`, `status`, `lastUploadAt`, `archivedAt`, `photoCount`, `attendeeCount`, `storageBytes`, `qrCodeURL`. `similarityThreshold` deliberately excluded — `P-26`/`P-80` lock it as a single hardcoded constant for the whole product, not per-event data, so it never becomes a column.

- **GSI 1 — `organizerID` (PK), `status` (SK).** Answers "show this organizer their events" for the dashboard. Originally proposed on the reasoning that `P-40`'s old 5-active-events cap made this necessary — that cap no longer exists (`P-40` removed all limits), but the access pattern itself is independent of any cap: the dashboard needs this list regardless of how many events an organizer has.
- **GSI 2 — `accessCode` (PK), no SK.** Answers "which event does this 6-character code (`P-27`) belong to" for the join flow. Codes are unique by design (~1B combination space), so this always resolves to exactly one event.
- **GSI 3 — `status` (PK), `lastUploadAt` (SK).** Answers `P-77`/`P-78`'s "which `ACTIVE` events are >30 days past their last upload" — a scheduled Lambda runs `Query(status="ACTIVE", lastUploadAt < now-30d)` and flips matches to `ARCHIVED`.

**The archive-to-delete transition (`P-77`'s second 30 days) — ruled 2026-08-09.** Two options considered, walked through Arjun's wedding event hitting day 30 then day 60:

| | Day-30 archive | Day-60 delete | Extra moving parts |
|---|---|---|---|
| A — pure scan | GSI 3 query, scheduled Lambda | Second scheduled query (`status="ARCHIVED", archivedAt < now-30d`), same Lambda cascades the teardown itself | One Lambda handles both transitions |
| B — GSI for archive, TTL for delete | Same as A | `archivedAt + 30d` written as a `deleteAt` TTL attribute at archive time; DynamoDB expires the item itself, for free, no scheduled query | A DynamoDB Stream on `Events` fires a cleanup Lambda on item removal |

**Ruled: B.** TTL deletes cost nothing and run in the background rather than on a paid schedule. TTL's known imprecision (AWS: typically within 48 hours of expiry, best-effort) is compatible with `P-77`'s own "roughly 60 days" / privacy page's "about two months" wording — neither promises an exact boundary. The Stream-triggered cleanup Lambda (tear down S3 photos, the Rekognition collection, and rows across all 6 tables) is not new incremental work: `P-34`'s organizer-triggered manual delete needs the identical cascade, just invoked directly instead of via a Stream event — so Option B gets automatic deletion by reusing a Lambda `P-34` requires anyway, in exchange for one Stream wiring.

**A gap surfaced by the deletion mechanism, not caused by it — ruled 2026-08-09: a 9th Lambda, `EventTeardown`** (renamed `CascadeDelete` 2026-08-12, see the `Faces` section below). Both `P-34`'s manual delete and the automatic TTL-triggered delete above need to touch `Events`, `Photos`, `Faces`, `EventAttendees`, S3, and the Rekognition collection — a cascade nothing in `T-03`'s original 8 Lambdas can do, since every API Lambda is deliberately IAM-scoped to exactly one table. This gap existed the moment `P-34` was ruled; it only became visible now because the TTL/Stream design forced the question of *which* Lambda the Stream should invoke.

Two ways to close it: (1) a dedicated 9th Lambda with the broader cross-table/S3/Rekognition role, invoked both directly (by `Events`' delete endpoint) and via the `Events` Stream (for the automatic path); (2) widen the existing `Events` Lambda's own role to cover the same reach. **Ruled: (1).** The whole case for multi-table over single-table in the base `T-04` ruling rested on "one Lambda, one table = structural IAM isolation, free" — widening `Events`' role to touch 4 tables plus S3 plus Rekognition would give back exactly the blast-radius guarantee that argument was built on, to save a single Lambda's worth of count. A dedicated Lambda keeps every other Lambda's role exactly as narrow as originally reasoned, at the cost of `T-03`'s Lambda count moving from 8 to 9 and `T-06`'s CI/CD job count moving from 9 to 10 — both updated in `LOCKED_TECH_DECISIONS.md`.

**`Jobs` — ruled 2026-08-12.** PK = `jobId`, no SK. Fields: `jobId`, `eventID`, `uploaderID`, `status` (`P-53`/`P-55`, in-progress → terminal), `succeededCount`/`failedCount` (`P-55`), `startedAt` (`P-53`'s hard lifetime ceiling). The status-polling endpoint (`GET /events/{eventId}/jobs/{jobId}/status`) reads this by `jobId` directly — no index needed there. **No retry/backoff field** — this was originally sketched for `P-100`'s retry-visibility clause; that clause was removed 2026-08-15 by `D-127` (see `LOCKED_PRODUCT.md`'s decision log) while scoping `db_api`, so there's no longer anything for a field like this to back.

**The GSI question, run through Meera and Sam.** `P-100` requires a batch's result to stay visible to **the uploader specifically** whenever they next open the event — including from a fresh tab where no `jobId` survives client-side (the UI plan is a "come back later" button, not a link carrying the job's id forward). A GSI keyed on `eventID` alone, sorted by time, sounds like it answers "give me the newest job for this event" — but with two people uploading around the same time to Priya's trip, it returns whichever job finished last, which could show Meera Sam's result instead of her own — the wrong person's batch.

**Ruled: a GSI keyed on a composite partition key, `eventUploaderKey = "{eventID}#{uploaderID}"`, with `startedAt` as the sort key.** `Query(eventUploaderKey = "evt_123#user_456", ScanIndexForward=false, Limit=1)` returns exactly that uploader's own most recent job in that event, with no cross-contamination between concurrent uploaders. Confirmed as a GSI, not an LSI — an LSI must share the base table's partition key (`jobId`), which cannot express "group by event+uploader" at all. Two lesser costs were named and accepted as non-issues at Glimpses' scale: (1) write amplification — every `Jobs` write touching the GSI's key attributes also writes to the GSI's copy, negligible at a few batches per event; (2) GSI reads are only ever eventually consistent, irrelevant here since the check-back-later flow is minutes-to-days later, not milliseconds after the write.

**A second option was weighed and rejected: a pointer written directly onto the uploader's `EventAttendees` row** (that table already models "this user, this event" as one item, so the latest job's result could live there instead of behind an index — a plain `GetItem` in place of a `Query`). Rejected because it would give the ingestion Lambda IAM write access to a second table it doesn't otherwise touch — the same one-table-per-Lambda isolation `CascadeDelete` (then `EventTeardown`) was built to protect, not something to give back here to save one index.

**`Photos` — ruled 2026-08-12.** PK = `photoID`, no SK — the base-table key `T-04`'s original ruling already fixed. Fields: `photoID`, `eventID`, `uploaderID`, `uploaderDisplayName`, `uploaderEmail` (see attribution below), `uploadedAt`, `filename`, `contentHash`, `sizeBytes`, `s3Key`, a thumbnail key. No `status` field — a photo that fails (`P-56`) or is caught as a duplicate (`P-38`) is never written here at all, so every row that exists succeeded.

**GSI 1 — the gallery, and where `P-57`+`P-16`'s forced cursor pagination actually lands.** PK = `eventID`, SK = `"{uploadedAt}#{filename}"`. `P-57` orders the gallery newest-first with filename as the within-batch tiebreak (hundreds of photos can share one upload timestamp); a composite string sort key gives that ordering directly — identical timestamp prefixes fall back to filename automatically. The pagination mechanism itself is DynamoDB's own: `Query(eventID, ScanIndexForward=false, Limit=50, ExclusiveStartKey=<cursor>)`, where the cursor **is** `LastEvaluatedKey` — literally "the next 50 after this specific photo," which is exactly what `P-57`+`P-16` require and nothing had to be built to get it.

**GSI 2 — dedup.** PK = `eventID`, SK = `contentHash`. `P-38` requires an exact-content-hash check scoped per event before a photo is stored, converted, or indexed; `Query(eventID, contentHash=X)` at ingest returns 0 (store it) or 1 (skip it, tell the uploader).

**Uploader attribution — the one real decision here, not forced by anything already ruled.** `P-84` made display names freely editable. `P-99` requires attribution to keep "showing the same display name and email address it always showed," even after the uploader is ejected. Two ways to satisfy that:

| | Meera renames herself mid-event | Read cost |
|---|---|---|
| A — snapshot at upload (`displayName`/`email` copied onto the `Photos` row at write time) | Old photos keep the old name; new uploads show the new one | Free — already on the row |
| B — live join (only `uploaderID` stored, resolved against `Users` at read time) | Every photo she's ever uploaded relabels instantly | A `BatchGetItem` to `Users` per gallery page |

**Ruled: A.** `P-99`'s "always showed" reads as a frozen snapshot, not "whatever the current name happens to be" — under B the word "always" would mean nothing, since the name could differ from what it showed originally. B also costs an extra table read per gallery page for a behavior nothing in the product ruled for.

**The storage-byte counter (`P-85`) closes here.** `sizeBytes` is stored per `Photos` row specifically so `Events.storageBytes` can be maintained as an atomic counter (`UpdateItem` increment on write, decrement on delete) rather than recomputed by scanning — the mechanism the `T-04` follow-up's DynamoDB primer already named. Correctness across `P-44` (single delete), `P-52` (bulk delete), `P-38` (dedup skip — never incremented, so nothing to reverse) and `P-55` (partial batch failure — same, failed photos are never written) falls out of "every write and delete touches the counter," not a separate mechanism per path.

**`Faces` — ruled 2026-08-12.** PK = `rekognitionFaceID` — the base-table key `T-04`'s original ruling already fixed, chosen specifically so `SearchFaces`'s result (a ranked list of `rekognitionFaceID`s) resolves straight to a row via `GetItem`/`BatchGetItem`, no index needed for that direction. One row per detected face-vector — a photo with 3 people produces 3 rows.

**A gap surfaced, same shape as `EventTeardown`'s — ruled 2026-08-12.** `P-44`/`P-52`'s photo-delete flow needs to (1) call Rekognition `DeleteFaces`, (2) delete the matching rows in `Faces`, and (3) decrement `Events.storageBytes`/`photoCount` — but `Gallery/photos`, the Lambda that owns photo deletion, is IAM-scoped to `Photos` only under `T-04`'s one-table-per-Lambda rule. Nothing had reach to `Faces`, `Events`, and Rekognition from a photo-delete call. Three options, run through Arjun (deletes one photo), Rohan (blast radius if a role is ever compromised), and Sam (Lambda/CI count):

| | Arjun deletes a photo | Rohan — blast radius | Sam — Lambda/CI count |
|---|---|---|---|
| A — widen `Gallery/photos`'s own role to also touch `Faces`, `Events`, Rekognition | one Lambda does it all, in-process | ❌ gives back exactly the isolation `T-04` was built for | ✅ no new Lambda/CI job |
| B — reuse `EventTeardown`, invoked by `Gallery/photos` for a single-photo cascade | `Gallery/photos` invokes it with one `photoID`; it does steps 2–3 | ✅ `Gallery/photos` only gains `lambda:InvokeFunction` on one function, not direct table/Rekognition access — the broad reach stays concentrated in the one Lambda already trusted with it | ✅ no new Lambda; existing CI job unchanged |
| C — a new dedicated Lambda, `PhotoTeardown`, mirroring `EventTeardown` for one photo | same effect as B | ✅ narrowest possible | ❌ 10th Lambda, 11th CI job, near-duplicates `EventTeardown`'s cascade logic |

**Ruled: B**, with `EventTeardown` renamed `CascadeDelete` to reflect that it now covers both whole-event and single-photo cascades rather than being event-only. Reusing the already-trusted broad-reach Lambda avoids both A's isolation cost and C's Lambda-count growth and duplicated logic. `Gallery/photos` gains a `DELETE` endpoint (not previously named in `T-03`'s Lambda table) that invokes `CascadeDelete` directly; `CascadeDelete`'s own role is unchanged, since it already held every permission this new call path needs. Lambda count stays **9**, CI/CD jobs stay **10** — see updated `CascadeDelete` write-up in section 3 (`T-03`) above.

**Fields and GSI, confirmed 2026-08-12.** Fields: `rekognitionFaceID`, `eventID`, `photoID` — nothing else. `Faces` itself stores no match results — **correction to how this was first written up:** matches are not computed live at read time either. `P-73`/`P-69` require match sets to be computed once (per batch) and persist even after a user deletes their face reference, which only makes sense as a stored, durable record — see the `MatchAttendees` write-up under `EventAttendees` below for where that record actually lives. `Faces` exists purely to let `CascadeDelete` find which Rekognition face-vectors to remove, and to let the (separately-run) per-attendee search resolve a matched `rekognitionFaceID` back to a `photoID`. One GSI: `eventID` (PK) + `photoID` (SK), serving both `CascadeDelete` lookups off the same index — a single-photo cascade (`Query(eventID, photoID)`) and a whole-event cascade (`Query(eventID)`).

**The GSI shape was the one real choice, run through Arjun and Sam.** Two options: (A) one GSI on `eventID`+`photoID`, or (B) two separate GSIs — one on `photoID` alone, one on `eventID` alone. B's only appeal would be if the single-photo delete caller didn't already know `eventID` — but it does: `Gallery/photos` reads its own `Photos` row (PK = `photoID`) before ever calling `CascadeDelete`, and that row already carries `eventID`. So B buys nothing and costs a second GSI's worth of write-amplification. **Ruled: A.**

**`EventAttendees` — mid-session, started 2026-08-12.** Base key fixed by `T-04`'s original ruling: PK = `userID`, SK = `eventID`, one row per person-per-event.

**A gap surfaced scoping this table, different in shape from `CascadeDelete`'s — ruled 2026-08-12.** `P-16`/`P-93` require a separate `SearchFaces` fan-out (one call per attendee with a face reference, re-run whenever a batch lands — distinct from `IndexOnePhoto`'s per-*photo* fan-out) whose answer must persist (`P-73`: computed once, never live; `P-69`: a match set must survive the user deleting the face reference behind it — only sensible if it's a stored record, not a recomputation). Nothing in the pipeline as designed runs this, and nothing was scoped to hold the answer.

Two questions, run through Meera (reliability) and Sam (Lambda/CI/IAM cost):

**Where the fan-out runs.** Options: (A) a new Distributed Map step, `MatchAttendees`, added to the existing `PipelineHandler` state machine, mirroring `T-02`'s reasoning exactly — a `SearchFaces` call is a Rekognition API call with the same account-wide throttle `IndexFaces` has, so it needs the same per-item retry/backoff and tolerated-failure-%; (B) a plain for-loop inside the existing `Finalize` step, no retry machinery beyond hand-written code; (C) a new dedicated Lambda triggered by a DynamoDB Stream on `Jobs` reaching `COMPLETE`, outside the Step Functions run entirely. **Ruled: A.** `PipelineHandler` already isn't one-table-scoped — that isolation only applies to the 5 API-facing domain Lambdas — so gaining `EventAttendees` on its manifest is a normal `T-07` permission-manifest addition, not a new IAM boundary crossing. No new Lambda, no new CI job; B and C both silently reopen the exact throttling/partial-failure problem `T-02` was already ruled to avoid, in a second place.

**Where the answer is stored.** `MatchAttendees` resolves each `SearchFaces` hit's `rekognitionFaceID` to a `photoID` via the `Faces` table's `eventID`+`photoID` GSI, then writes the result directly onto the attendee's own `EventAttendees` row — no new table, no new index, since that row already is the "this user, this event" record. Field-type choice: a **String Set** (`matchedPhotoIDs`), not a List — a List's only advantage (ordering) is unused since the gallery re-sorts by upload time (`P-57`) regardless, while a Set gets automatic dedup and an idempotent `ADD` update for free, guarding against a re-run accidentally double-counting a photo a List would need hand-written duplicate-checking for.

**Status field and leave/rejoin row semantics — ruled 2026-08-12.** `P-49`'s own permission table already fixes the vocabulary that matters here: `PENDING`, `ATTENDEE`, and `BLOCKED` are stored states (`NON_MEMBER` and `ORGANIZER` are not — the former is simply "no row exists," the latter is tracked on `Events.organizerID` instead). `P-29`'s blocklist forces one structural fact regardless of anything else: a `BLOCKED` row must survive a later access-code attempt, or the block does nothing — so rows can't always be deleted. The open question was only about the leave case specifically:

| | Meera's instant rejoin (no batch in between) | Rohan's block-evasion attempt | Priya's long-gap rejoin | Sam's cost |
|---|---|---|---|---|
| A — delete row on leave, recreate on rejoin | `matchedPhotoIDs` gone; gallery empty until the next batch triggers `MatchAttendees` again, which could be days away or never | Blocked regardless — irrelevant to A vs B, `BLOCKED` rows are never deleted either way | Same as B once the next batch lands (`SearchFaces` re-queries the whole collection every run, so it self-heals) | Negligible either way |
| B — never delete; add a 4th status value, `LEFT`; leaving/rejoining flips status in place | Matches reappear instantly, `matchedPhotoIDs` untouched | Blocked regardless | Same as A once the next batch lands | Negligible either way |

**Ruled: B.** Beyond winning Meera's case outright, B is also the *consistent* shape with what `P-29` already forces for `BLOCKED` — one mechanism (status flip on an always-present row) for every membership-lifecycle transition, rather than a delete/recreate special case for `LEFT` next to a never-delete rule for `BLOCKED`. **Status values: `PENDING`, `ATTENDEE`, `LEFT`, `BLOCKED`.** Transitions: `PENDING → ATTENDEE` (`P-10` approval) or `→ BLOCKED` (`P-29` denial); `ATTENDEE → LEFT` (`P-46`, self) or `→ BLOCKED` (`P-29`, ejection); `LEFT → PENDING`/`ATTENDEE` (`P-46` rejoin with code, per `joinPolicy`); `BLOCKED` is terminal — no ruling exists for un-blocking. The permission-check layer (`P-49`) treats `LEFT` identically to `NON_MEMBER` (deny everything); the only reason it's a distinct stored value rather than deletion is to keep `matchedPhotoIDs` and to let `P-46` (rejoin allowed) and `P-29` (rejoin blocked) diverge on the same row shape.

**The roster/lobby GSI — ruled 2026-08-12.** `P-82` and `P-83` fix what's actually needed: the organizer sees two separate lists (pending-request lobby, admitted roster), each with display name and email; attendees never see any roster at all. Neither ruling asks for an ordering (e.g., longest-waiting-first).

- **Option A — GSI as proposed: `eventID` (PK) + `status` (SK).** Lobby = `Query(eventID, status = PENDING)`. Roster = `Query(eventID, status = ATTENDEE)`. `MatchAttendees`' "who's currently admitted" lookup is the same `Query(eventID, status = ATTENDEE)` — one GSI, three callers.
- **Option B — same GSI, compound sort key `"{status}#{joinedAt}"`.** Same queries via `begins_with`, but results sort chronologically within each status (oldest-waiting-first in the lobby). Costs a new `joinedAt` field with no ruled requirement behind it.
- **Rejected outright:** a String Set of admitted `userID`s kept directly on the `Events` row, instead of a GSI. Duplicates data across two writes that must stay in sync (a real consistency risk on every status change), and doesn't cleanly serve the separate pending-list query at all.

**Ruled: A.** Nothing in `P-82`/`P-83` asks for ordering, so `joinedAt` would be exactly the kind of speculative field this phase has avoided elsewhere. Purely additive if a future ruling wants it — `B` is a superset of `A`, not a rework.

**`CascadeDelete` and stale `matchedPhotoIDs` — ruled 2026-08-12.** When a photo is deleted (`P-44`/`P-52`), does `CascadeDelete` also scrub that photo's id out of every attendee's `matchedPhotoIDs` set, or is it left to go stale?

- **Option A — eager scrub.** `CascadeDelete` queries the `eventID`+`status=ATTENDEE` GSI for every admitted attendee, then issues an `UPDATE ... DELETE matchedPhotoIDs :photoID` against each row (a safe no-op where absent). For `P-52`'s bulk delete (Arjun clearing 50 photos) that's up to 50 × 100 = 5,000 extra writes at `P-93`'s scale target.
- **Option B — lazy, read-time filtering.** Do nothing at delete time. The gallery already resolves each id in `matchedPhotoIDs` back to a real photo via `Photos` (`BatchGetItem`/`GetItem`) to render it; a deleted photo's row is simply gone, so it silently drops out — not a filter that has to be written, just what a missing item does. The stale id sits harmlessly in the set until the event expires under `P-33`.

**Ruled: B.** A buys nothing a user can perceive — correctness is already free, guaranteed by `BatchGetItem` not returning a deleted row — while costing real DynamoDB write capacity on every deletion at scale, for a cleanup that's invisible since `matchedPhotoIDs` is never displayed directly, only ever resolved through `Photos`. Consistent with `P-44`'s own "deletion is not retroactive" posture elsewhere in the product: stale references are tolerated rather than paid to eagerly scrub. Storage cost of leaving them is trivial regardless — bounded by `P-93`'s 1,000-photo target, worst case ~36KB of stray ids in one set, nowhere near DynamoDB's 400KB item limit.

**`EventAttendees` — fully ruled 2026-08-12. Fields:** `userID` (PK), `eventID` (SK), `status` (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`), `matchedPhotoIDs` (String Set, written by `MatchAttendees`). **One GSI:** `eventID` (PK) + `status` (SK). **This closes `T-04`'s follow-up — all 6 tables (`Users`, `Events`, `Jobs`, `Photos`, `Faces`, `EventAttendees`) are now ruled.**

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

**Sub-decision 3, corrected 2026-08-13 — one combined untargeted-apply job doesn't actually work.** Building `infrastructure/modules/dynamodb/` surfaced what Option A's original write-up missed: the state machine's Terraform embeds each Lambda's real ARN (`PipelineHandler`, `db-api`), which — per this same sub-decision's own paragraph above — only exists once Terraform has already run each Lambda's own targeted apply. A single combined job that builds *both* the DynamoDB tables and the state machine together would therefore fail outright on a from-scratch deploy: on the very first run, it would hit the state-machine resource before any Lambda exists to hand it an ARN. DynamoDB has no such dependency — the tables need nothing from the Lambdas or from each other.

**Ruled: split into two dedicated jobs, `dynamodb` and `state_machines`, each an untargeted apply scoped to its own module.** Fixed run order: **`dynamodb` → all 9 per-Lambda jobs → `state_machines`**. `dynamodb` has no ordering dependency on the Lambdas and could technically run anywhere before `state_machines`, but the order is locked as one fixed sequence rather than a partial one — a single sequence to remember beats reasoning about which subset of jobs is safe to reorder on a given deploy. Both stay manual, exactly as Option A already ruled — this correction changes job count and boundaries, not the "run by hand" discipline itself.

**Sub-decision 4 — CI/CD granularity.** Resolving distinction: a Jenkinsfile's job (GitHub → zip → S3 → `update-function-code`) only makes sense for something with actual application code — the state machine and DynamoDB tables are pure Terraform config, nothing to zip or push. **Ruled: 11 CI/CD jobs** *(corrected 2026-08-13 from 10 — see sub-decision 3's correction above)* — 9 per-Lambda Jenkinsfiles (targeted apply + code push each) + `dynamodb` + `state_machines`, the two untargeted-apply jobs that replace the original single Option-A job. Not one shared v1-style Jenkinsfile with a `DEPLOY_TARGET` parameter, and not a per-AWS-resource pipeline either — granularity still follows "has code," not "is a Terraform resource"; `dynamodb`/`state_machines` are the exception because they're the only cross-module resources with no code to push and a real ordering dependency between them. **Flagged separately, not itself a sub-decision:** the Terraform state bucket is a bootstrapping special case — it can't be created by an `apply` that depends on it already existing as a backend, so it's created once, by hand or a small one-off script, outside all 11 jobs.

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

### `T-07` — Observability, IAM granularity, CORS, secrets (ruled 2026-08-09)

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

### IAM granularity

**What "IAM granularity" means, concretely.** Every Lambda runs *as* an IAM role — a bundle of permissions ("can read table X," "can call `IndexFaces`"). AWS checks the role before allowing any action; no matching permission, the call is rejected, no exceptions. The question isn't *whether* to scope permissions tightly — `T-03`/`T-04` already committed to that shape, scoping each API Lambda to exactly one DynamoDB table — it's **how the tight permission list actually gets written.**

**The concrete failure mode from v1, worth walking through once:** `HANDOFF.md` §7 — *"several IAM roles were missing a specific permission discovered only at runtime."* Picture `PipelineHandler`'s `Extract` step gaining a new line of code, weeks into development, that reads a thumbnail back from S3 to check its dimensions. If its role only has `s3:PutObject` and not `s3:GetObject`, that line throws `AccessDenied` — but only the first time that exact code path actually executes, which could be days after the code shipped, on whichever attendee's upload happens to trigger it. The bug isn't visible at `terraform apply` time; it's only visible at the exact runtime moment the missing permission is needed.

**Three ways to arrive at "each Lambda's permissions are tight":**
- **A — Hand-written, strict, one-role-per-Lambda (v1's exact approach).** A developer writes out the AWS actions a Lambda needs, from memory/prediction. Tightest possible blast radius per Lambda; whatever wasn't anticipated becomes the exact `AccessDenied`-at-runtime problem above.
- **B — Start broader within a service boundary, tighten before launch.** e.g. grant `dynamodb:*` on a Lambda's own table rather than listing each action. Removes runtime surprises during active development, at the cost of a wider blast radius for however long "tighten before launch" takes — and `HANDOFF.md` §7 has a documented example of exactly this kind of "tighten later" note never actually being acted on (the Terraform IAM user's `AdministratorAccess`, flagged as "pragmatic for now, tighten later" and never tightened).
- **C — Strict, but derived from the code rather than guessed.** `HANDOFF.md` §7 names this directly: *"generating them from a manifest of each Lambda's actual AWS calls."* Each Lambda's folder carries a short, explicit list of every AWS call it actually makes; `iam_policies.tf` is written directly against that list. Same tight end-state as A, but the permission list has something concrete to be checked against, so a missing permission is a mismatch between two things sitting next to each other in the same folder — not a memory gap.

**Ruled: C.** It answers `HANDOFF.md`'s own diagnosis rather than repeating it (A) or trading it for the different, historically-documented-to-linger risk of B.

### CORS

**What CORS physically is.** A frontend running in a browser, at one address, and an API running at a different address — by default, browsers block a page from reading a response from a different address than its own. This is a browser rule, not something an app opts into; **CORS is the mechanism a server uses to say "responses to this specific address are OK to read."** Concretely, the server sends back a header, `Access-Control-Allow-Origin: https://app.glimpses.com` — and the browser only hands the response to the page's JavaScript if that header names the page's own address.

**The `*` shortcut.** A server can instead send `Access-Control-Allow-Origin: *` — "any website may read this API's responses." `HANDOFF.md` §7: *"CORS was hardcoded to `*`... despite an `app_urls` Terraform variable that implied origin-restriction was intended but never wired through"* — the scaffolding for a real allowlist existed and shipped disconnected.

**What `*` actually risks, through Rohan:** with `*`, Rohan can build his own page, embed calls to the real Glimpses API in it, and any logged-in Glimpses user visiting Rohan's page has their browser silently fire authenticated requests on Rohan's behalf. **Nuance that matters:** CORS is not the only thing standing between Rohan and real data — the API's own auth checks are the actual gate. CORS is specifically about which *websites' JavaScript* gets to read responses; it's defense-in-depth, not the whole defense.

**Ruled: restrict to the real frontend origin(s)**, via the `app_urls`-style Terraform variable v1 already had but never wired through — actually connecting it this time, not new infrastructure. Local development origins (e.g. `localhost`) need adding to the allowed list, or local frontend work against a deployed backend breaks.

### Secrets hygiene

**Two real incidents, not a hypothetical risk — worth naming exactly, since that's what makes the ruling cheap to justify.** `HANDOFF.md` §6: *"`infra/modules/cdn/` had both the CloudFront signing public key AND the private key committed as real PEM files on disk — contradicting the project's own documentation, which claimed the private key only ever lived in SSM SecureString."* And separately: *"a live AWS access-key CSV and Google OAuth client secret sit in plaintext across several scratch files."* Both share the same shape: documentation said "this lives somewhere safe," the actual repo said otherwise, and nothing was checking automatically for the gap.

**What a pre-commit secret scanner is, mechanically.** A small program (e.g. `gitleaks`) that runs automatically the moment `git commit` is invoked, scans every file about to be committed for patterns that look like secrets — AWS key formats, PEM file headers (`-----BEGIN PRIVATE KEY-----`), long random-looking tokens — and **refuses to let the commit complete** if it finds one. It runs locally, before anything reaches even local git history, let alone a remote.

**Why "from commit #1" is the load-bearing phrase.** Once a secret is committed, it stays in `git` history permanently unless someone does history-rewriting surgery to remove it — itself risky and disruptive. A scanner added after a leak already happened only protects the *next* mistake. This rebuild has no commits yet, which is the one moment "from the start" is free rather than retrofitted.

**Ruled: add a pre-commit `gitleaks` scanner from the repository's first commit.** Cheapest ruling on the whole `T-07` agenda — a few minutes of one-time setup — against two incidents that actually happened in this exact project's own history.

## 8. Testing approach and CI/CD

### `T-08` — Testing approach and CI/CD (ruled 2026-08-09)

**Three tiers, what each physically is.** A **unit test** calls one function directly, with every AWS call faked by `moto` (a library that intercepts `boto3` calls and simulates DynamoDB/S3/Rekognition/etc. in memory, so nothing leaves your laptop) — milliseconds, free. An **integration test** still fakes AWS, but calls a whole Lambda's `handler.py` the way API Gateway or Step Functions actually would, letting it run all the way down through its own `manager`/`service`/`dao` layers together instead of testing each one alone — this is what catches a bug where `handler` passes the wrong field name to `service`, which a unit test of `service` in isolation, given correct input by hand, would never see. An **E2E test** fakes nothing — it calls the real deployed API Gateway URL, which hits a real Lambda, which writes to real DynamoDB and calls real Rekognition; it's the only tier that can prove a real deployed auth check actually rejects an unauthenticated caller, or that Terraform actually built something that works.

**Ruled: keep all three tiers**, matching v1. The middle tier specifically earns its cost here because `T-02`'s Step Functions pipeline has real internal wiring — `PipelineHandler` branching on a `step` field, `db-api` writing status at four separate points — that a unit test of one function alone can't exercise together.

**Unit test mocking: why `moto` over the alternatives.** Hand-written `unittest.mock` requires the test author to already know and hardcode what AWS would do — e.g. that `GetItem` on a missing key returns `None` rather than raising — so the test only proves the code matches an assumption, not real AWS behavior; `moto` reproduces that behavior itself. LocalStack goes further, running actual Docker containers that imitate AWS services over real HTTP rather than just intercepting Python calls, which is more realistic still for DynamoDB and S3 — but Rekognition's `IndexFaces`, the single AWS service this app depends on most, is a LocalStack-Pro (paid) feature, so LocalStack wouldn't even help with the app's most central AWS call.

**Ruled: `moto`.** Matches v1, free, no Docker requirement, and covers the one service (Rekognition) that matters most here.

**Explicit failure-path tests — why v1 named specific scenarios instead of just chasing coverage.** `HANDOFF.md` §8 describes v1's approach as deliberately proving the *failure* branch works, not just the happy path — e.g. a deliberately-corrupted ZIP should drive the pipeline to `FAILED`, not silently succeed or hang. That list is walked through and re-ruled here rather than inherited wholesale, since `T-02` changed the underlying mechanism for one of them:

- **Corrupted ZIP → `FAILED`, kept as-is** — the extraction step didn't change.
- **DLQ → `COMPLETE_WITH_ERRORS`, adapted.** v1's SQS+DLQ setup meant a forced-failing message landed in a dead-letter queue and the batch was marked `COMPLETE_WITH_ERRORS`. `T-02` replaced this with Step Functions Distributed Map, which has no DLQ — instead it has `ToleratedFailurePercentage` (a threshold of allowed per-item failures before the whole execution is marked failed) and writes each item's individual result to an S3 output file. The adapted test: one deliberately-bad photo in a batch should fail only that item, the execution should still complete, and the failure should show up in the S3 results — same intent, new mechanism. Same compromise as v1 carried forward: verified by code review only, not a live test, since forcing Rekognition to fail on command mid-flow is impractical in a dev environment.
- **Rate limiter blocks the 11th search — dropped.** `P-16` removed search as a user action; there's nothing left to rate-limit.
- **Private S3 GET fails, expired signed URL fails, 401/403 — kept as-is.** None of these mechanisms changed.
- **New: each Lambda's IAM policy matches its manifest of actual AWS calls.** `T-07` ruled that IAM permissions are derived from a per-Lambda manifest of real AWS calls rather than hand-guessed — but a manifest is just a file someone writes; without a test that fails when the manifest and the code's real calls disagree, that file can silently drift out of sync with the code over time, landing back at `HANDOFF.md` §7's exact "permission missing, discovered only at runtime" problem, just one layer removed.

**Integration scope — why not cross-Lambda.** One option considered was invoking one Lambda's handler for real and feeding its real output into the next Lambda's handler in the same test, to test the actual handoff between them. Rejected: Step Functions itself already guarantees the shape of that handoff (it's the orchestrator's job to pass state correctly between steps) — re-testing that guarantee at the application level is mostly redundant with what the orchestration layer already provides, for a real ongoing cost in test-maintenance.

**Ruled: integration tests stay scoped to one Lambda's own internal chain**, `handler → manager → service/dao`, `moto`-backed at the AWS boundary only.

**E2E — the two questions that needed separate answers.** E2E is expensive in a way the other tiers aren't: every real run calls real Rekognition, which costs real money, and touches real DynamoDB rows that need cleaning up. Two things had to be ruled, not one: what it runs against, and how often.

*What it runs against:* a shared, long-lived test event (created once, reused across runs) is cheaper to set up but risks a previous run's leftover photo throwing off a later test's count-based assertion — a classic source of flaky, order-dependent test failures. A dedicated event created and torn down by the test itself avoids that entirely, at the cost of a bit more setup/teardown code per test.

**Ruled: a dedicated test event per run**, created and destroyed by the test itself, inside the project's one AWS account (there's no separate dev/prod split — `T-05`/`T-06` never introduced one).

*How often:* running E2E automatically on every one of `T-06`'s 9 Jenkins jobs would multiply real Rekognition spend by every ordinary commit. v1 itself described E2E as "a handful of high-value journeys," not a suite run constantly.

**Ruled: manual only** — E2E is never wired into an automatic Jenkins job; it's run by hand, kept for moments that actually warrant the cost.

**CI/CD wiring — why tests don't live in Jenkins here.** The natural default (and the recommendation) was that each of the 8 per-Lambda Jenkinsfiles runs tests before deploying, and a failure stops the pipeline — matching `HANDOFF.md`'s own "deployments are always intentional" framing, already the philosophy behind `T-06` (Terraform apply kept out of automatic triggers, always deliberate). Under that shape, if broken code were pushed, the Jenkins job would fail before ever deploying it, so a real upload from Arjun the next day would still hit the last-known-good version, not the break.

**Ruled against that recommendation: tests are not part of any Jenkinsfile at all.** The user's actual workflow is to test locally first and only push to trigger a Jenkins deploy once local tests already pass — so Jenkins here is purely a deploy mechanism (build → push code → `terraform apply -target`), not a CI test gate. This means a broken push *can* deploy if local testing is skipped, with nothing in Jenkins to catch it — a real, named tradeoff, not an oversight. The dedicated untargeted-apply job (`T-06`) is unaffected either way — it stays independent and manual, since it deploys shared infra (the state machine, DynamoDB tables), not app code, so gating it on per-Lambda test results wouldn't map to anything real.

**Coverage — why no tracked number.** A coverage percentage (via `pytest-cov`, checked locally) is a concrete, trackable signal, but a weak one: a function can hit 100% line coverage while never actually exercising its own error-handling branch, so the number can look reassuring while missing exactly the failure-path gaps this ruling already named explicitly above.

**Ruled: no formal coverage threshold.** Given testing here is already fully self-disciplined rather than CI-enforced, a tracked percentage adds bookkeeping without changing what actually gets tested — the named failure-path list is the real substance, and it's already explicit.

## 9. `T-03` follow-up (2026-08-15) — full endpoint paths, and a new `download` Lambda/`Downloads` table

**Why this surfaced now, not earlier.** `T-03`'s original Lambda table only sketched paths loosely (`GET /events/{eventId}/photos`, "admit/eject") — enough to scope which table each Lambda owns, not enough to actually build against. Building `heic_converter` first (a shared utility, invoked internally, no HTTP path at all) meant this gap never had to be closed until the first API-facing Lambda came up next.

### Endpoint paths — mostly a straightforward exercise, three real decisions inside it

Most of the path list (§3 of `LOCKED_TECH_DECISIONS.md`) is direct translation of already-ruled product behaviour into REST shape — `Profile`, `Events`, and most of `Membership`/`Gallery` needed no real judgment calls. Three did:

**1. The QR code — a field, or its own endpoint?** `P-90` already established the QR image is a cached S3 object, fully determined by the join link. The question was only how the frontend reaches it: a `qrCodeURL` field returned inline on `GET /events/{eventId}`, or a dedicated `GET /events/{eventId}/qrcode`. A field is cheaper (no new route) but reads awkwardly for the actual product goal — Arjun needs to hand this to people who aren't even using the app yet (printed table cards, a text message), which is a "download this file" action, not "display this field." **Ruled: a dedicated endpoint**, one that can set `Content-Disposition: attachment` so hitting it is a one-click download rather than opening an image in a new tab.

**2. Membership actions — did `deny`/`eject`/`block` need to be three separate actions, or fewer?** `EventAttendees` has 4 statuses (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`), and it looked at first like `P-29`'s "eject an attendee, deny a pending one, and block" might need three distinct organizer-facing endpoints plus `P-46`'s self-service leave — four total. Re-reading `P-29` closed this on its own: *"either action blocks that user from rejoining with the code. One per-event blocklist serves both."* Deny and eject were never two-step (deny-then-optionally-block) — each *is* a direct transition to `BLOCKED`. **Ruled: three organizer actions** (`admit`: `PENDING`→`ATTENDEE`; `deny`: `PENDING`→`BLOCKED`; `eject`: `ATTENDEE`→`BLOCKED`), plus the already-ruled self-service `leave` (`ATTENDEE`→`LEFT`, rejoinable, `P-46`). No separate `block` action exists.

**3. Bulk photo delete — how does a multi-select delete travel from browser to Lambda?** `P-52` needs to accept a batch of `photoId`s in one call. `DELETE` requests can carry a body, but it's non-standard enough that browsers/clients/proxies don't reliably support it — the safer alternative is a query string (`DELETE .../photos?photoIds=a,b,c`) or a `POST` with a JSON body. A query string has a practical length ceiling that becomes a real risk at `P-93`'s scale (up to ~1,000 photos/event, so a large multi-select could produce a very long URL). **Ruled: `POST /events/{eventId}/photos/bulk-delete`**, body-carried `photoIds` — reads correctly as a mutating action regardless, and has no length ceiling to worry about.

### Download — why it split into two mechanisms, not one

`P-60`/`P-92` name two different attendee actions that both read as "download," but they're mechanically nothing alike:

- **Downloading a handful of selected photos** needs no server processing at all — the objects already exist in S3 individually. `Gallery/photos` just needs to hand back pre-signed URLs for exactly the objects requested (`POST /events/{eventId}/photos/download-urls`), and the browser fires off N direct downloads. No new Lambda, no new table, no waiting.
- **Downloading a whole event (or a large selection) as one ZIP** is a different shape of problem: something has to actually assemble a zip container, which no S3 API does natively — S3 only has object-level operations (`GetObject`/`PutObject`/`CopyObject`), no "combine these objects into one archive" call. A zip file is just a byte format (per-file headers + the file's bytes + a trailing central directory index); building one means real compute has to stream the source objects through and write the container structure out — mechanically simple (no re-compression needed, since photos are already-compressed JPEGs; the zip's `STORED` method just wraps them) but it is genuine work that has to run *somewhere*, and API Gateway's 29-second synchronous timeout rules out doing it inline in the request/response cycle at any real scale.

**Which Lambda does the zip work — surfaced its own IAM question.** Under `T-04`'s one-table-per-Lambda isolation, `Gallery/photos` is scoped to `Photos` only. Giving it write access to a place to track a background zip job (status, result location) would be exactly the role-widening `T-04` exists to prevent — the same shape of gap that produced `CascadeDelete` for `Events`/`Faces` cross-table deletes. **Ruled: a dedicated 10th Lambda, `download`**, scoped to a new `Downloads` table (its own job-tracking record) plus read-only `Photos` (to look up each selected photo's `s3Key`) plus S3. `Gallery/photos`'s own IAM manifest is untouched.

**Step Functions, or a plain async Lambda invoke?** `T-02` already established Step Functions Distributed Map as the mechanism for per-item fan-out with a shared throttle (Rekognition's `IndexFaces` TPS limit) needing coordinated retry/tolerated-failure handling across many parallel invocations. Zip-building has neither property — it's one sequential job (read N objects, write one combined object), with no external per-call rate limit to coordinate against. Reaching for a second state machine here would be solving a problem this job doesn't have. **Ruled: a plain asynchronous Lambda invocation** (`InvocationType=Event`), the same category of mechanism `db-api` already uses as a plain Lambda rather than an orchestrated workflow. The `POST /events/{eventId}/photos/download` handler creates the `Downloads` row and returns a `downloadId` immediately; the actual zip build happens in the background invocation, checked via `GET /events/{eventId}/downloads/{downloadId}/status`.

**Does the build actually fit inside Lambda's limits?** Worked through at `P-93`'s top-of-scale case: 1,000 photos, ~3-4MB average JPEG, same-region S3↔Lambda traffic. Estimated total build time is on the order of a few minutes — well inside Lambda's 15-minute execution cap, and the reason a synchronous `Gallery/photos` endpoint was never viable (that would need to fit inside API Gateway's 29 seconds instead). One implementation detail flagged for build time, not a ruling: Lambda's `/tmp` scratch space defaults to 512MB (configurable to 10GB) — building the zip by downloading everything to disk first would need that raised at `P-93`'s scale, so the actual implementation should stream each S3 object directly into the zip's output stream, which is itself streamed to S3 via multipart upload, without ever staging the full batch on disk or in memory.

**Does `Downloads` need a GSI like `Jobs` has?** `Jobs`' `eventUploaderKey` GSI exists specifically because `P-100` requires an upload's result to be findable from a fresh session with no `jobId` in hand — someone can close the tab mid-upload and check back days later. **No equivalent product ruling exists for downloads** — a zip request is something the requester stays on the page for, holding the `downloadId` returned synchronously from the kickoff call. **Ruled: no GSI on `Downloads`** — PK-only lookup by `downloadId` is sufficient, a smaller table than `Jobs` for a smaller problem.

**Cleanup.** `P-90`'s own writeup already anticipated this: the QR image "joins `P-60`'s expiring ZIP archives on the list of stored artifacts that need a lifecycle." An S3 lifecycle rule expiring objects under the downloads prefix (defaulted to 48 hours, adjustable later) closes that obligation — not new ground, just implementing what the product docs already expected.

**Net effect on `T-03`/`T-04`/`T-06`:** Lambda count 9→**10**, DynamoDB tables 6→**7**, CI/CD jobs 11→**12** *(amended again 2026-08-15, same day, to **15** — see below)*. Tight answers in `LOCKED_TECH_DECISIONS.md`.

**CI/CD job count amended again, same day: 12 → 15.** Wiring `heic_converter`/`db_api`/`download` into root `imports.tf` surfaced that the shared resources they depend on — the deploy-artifacts bucket, the photos bucket, the alarm SNS topic, and CloudFront — didn't exist in Terraform yet. Each became its own module (`buckets`, `alarms`, `cloudfront`), kept deliberately separate rather than bundled into one "shared" module/job, for the same reason `T-04` keeps tables separate: smaller, individually-understandable pieces over one opaque one. Each gets its own dedicated CI job, same as `dynamodb`/`state_machines` — 12 → **15**. Tight answer and run order in `LOCKED_TECH_DECISIONS.md`.

## 10. `T-09` (2026-08-15) — S3 bucket/key layout, CDN, and the ingestion trigger

**Why these two were tackled together.** `Photos.s3Key` (ruled 2026-08-12) has always been a field with an undefined shape, and the `download` Lambda's zip objects (ruled the same day as this section) added a second undefined key shape on top of it. Separately, nothing had ever ruled what actually starts `ingestion` once a browser's direct-to-S3 upload finishes. The two turned out to be genuinely coupled: whichever trigger mechanism gets chosen decides what information the object key has to carry on its own, since the trigger has no other source of truth to consult.

### The trigger mechanism — S3 Event Notification vs a client callback

Two ways something could learn "the upload just finished":

- **A client "upload complete" callback** — after the browser's `PUT` succeeds, it makes a second call, e.g. `POST /events/{eventId}/jobs/{jobId}/complete`, and that endpoint calls `StartExecution`.
- **An S3 Event Notification** — S3 itself notices the object was created and fires an event with no client involvement at all.

Run against `P-100`'s own scenario (Arjun uploads a 400-photo ZIP at the venue, then closes his laptop — the batch must still complete): a callback depends on the browser surviving long enough to make that second call. If the tab closes or the network drops in the gap between the `PUT` finishing and the callback firing — which `P-100` explicitly names as a case that must work — the batch silently never starts, and `P-81` means nobody is ever told it didn't. An S3 Event Notification has no such gap: S3 is the witness, not the browser, so the trigger fires regardless of whether anyone is still looking. **Ruled: S3 Event Notification.** This also closes a lesser Rohan-shaped hole a callback endpoint would open — there would be nothing to stop a client calling `/complete` for a job whose files were never actually uploaded.

### Why EventBridge sits in the middle, not S3 → Lambda directly

S3's own native event-notification config can invoke a Lambda directly, but Step Functions isn't one of its native targets — reaching Step Functions from a raw S3 notification would need a small glue Lambda in between, whose only job is "receive this event, call `StartExecution`." Routing through EventBridge instead removes that Lambda entirely: the bucket is set to send all object-created events to the account's default EventBridge bus, an EventBridge Rule filters for the ones that matter (bucket + key prefix/suffix), and the rule's target is the state machine's ARN directly — EventBridge can invoke Step Functions natively, no Lambda needed as glue.

**The rule's filter, concretely:**

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": { "name": ["glimpses-photos"] },
    "object": { "key": [{ "prefix": "uploads/" }, { "suffix": "/original.zip" }] }
  }
}
```

The prefix condition alone would already be sufficient — no code path ever signs a pre-signed URL for anything under `uploads/` except `original.zip` — but the suffix check costs nothing and guards against a future code change accidentally writing something else there and silently starting executions for it.

### One batch, one object, one execution — why multi-file selections get zipped client-side

`P-37` already rules that a multi-file selection is one batch, not many. Under an event-driven trigger, "one batch" has to mean **one S3 object**, because one S3 `PUT` produces exactly one Object Created event, and the design needs exactly one `StartExecution` per batch — if Meera's six-photo selection instead uploaded as six separate objects, six separate events would fire and (absent some suppression mechanism nothing here provides) six separate executions would start for what the product considers a single job. **Ruled: the browser always builds a zip client-side before requesting the upload URL**, whether the user picked "upload a ZIP" or "select multiple files" — the server-side shape is identical either way, one object, one key, one trigger. This makes `Extract`'s "unzip" step unconditional rather than ZIP-only.

### Bucket count — one bucket, or split by purpose?

Two ways of splitting were considered and rejected before landing on one bucket:

- **One bucket per category** (six buckets: uploads/photos/thumbnails/selfies/qrcodes/downloads) — every isolation property this buys (scoped IAM, scoped lifecycle rules, scoped event notifications) is already available at the *prefix* level within a single bucket: S3 bucket policies accept prefix-scoped `Resource` ARNs, S3 lifecycle rules accept a prefix filter, and EventBridge rules filter on the key itself. Six buckets is six more Terraform resources for `Sam` to deploy for no capability a single bucket doesn't already have.
- **Split by axis, event-scoped bucket vs user-scoped bucket** (an option raised mid-session) — doesn't actually hold, because `uploads/` is scoped to event **and** user **and** job simultaneously. Whichever bucket it landed in, the other axis would still be nested inside it; the split wouldn't separate anything real for the one prefix that most needed separating.
- **The split that does draw a real line: publicly-servable-via-CloudFront vs never-public.** `photos/`, `thumbnails/`, `qrcodes/` are meant to be viewed repeatedly by every admitted attendee in a browser. `uploads/`, `selfies/`, `downloads/` are never meant to be reachable by anyone except through a Lambda-issued pre-signed URL — most notably `selfies/`, since `P-15`/`P-82` make selfies invisible to *everyone*, not just other users. This is a genuine security boundary, not a cosmetic one: a misconfigured CloudFront origin or an overly broad bucket policy could leak a selfie under a two-way split just as easily as under one bucket, **if enforcement relied on bucket separation alone**. It doesn't — the actual enforcement point either way is the bucket policy's `Resource` scoping (see OAC below), which works identically whether public/private live in one bucket or two. Given that, one bucket is strictly less Terraform for the same guarantee. **Ruled: one bucket, six prefixes**, enforcement done entirely through the bucket policy, not bucket existence.

### Origin Access Control (OAC) — how CloudFront is kept out of the other three prefixes

CloudFront needs to fetch an object from S3 on a cache miss before it can serve or cache it. Historically that meant either making the bucket public (defeating the point of gating access through CloudFront at all) or the older, now-superseded Origin Access Identity mechanism. **OAC is the current mechanism**: an AWS-managed identity that represents *this one CloudFront distribution and nothing else*. The S3 bucket policy grants that identity `s3:GetObject`, scoped to exactly the prefixes meant to be public:

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "cloudfront.amazonaws.com" },
  "Action": "s3:GetObject",
  "Resource": [
    "arn:aws:s3:::glimpses-photos/photos/*",
    "arn:aws:s3:::glimpses-photos/thumbnails/*",
    "arn:aws:s3:::glimpses-photos/qrcodes/*"
  ],
  "Condition": { "StringEquals": { "AWS:SourceArn": "<this distribution's arn>" } }
}
```

`uploads/`, `selfies/`, `downloads/` simply never appear in that `Resource` list — even a correctly-guessed CloudFront-style path under one of those prefixes gets rejected by S3 itself, not merely left uncached. The bucket additionally has all public access blocked at the bucket level, so no path — through CloudFront or directly — ever works without either OAC (for the three public prefixes) or a Lambda-issued pre-signed URL (for everything else).

### Why selfies still need a *read* path, despite being invisible to everyone

`P-82` rules selfies invisible to *other* people, not to their own owner — the profile page shows Meera her own selfie back, so she can see what's currently set before replacing it. Since `selfies/` is deliberately outside CloudFront's grant, this read has to go through the same pre-signed mechanism as every other non-public prefix: `Profile`'s `GET /profile` mints a pre-signed `GET` scoped to exactly the caller's own key (`Profile` derives `userId` from the authenticated request, so it structurally cannot sign anyone else's selfie).

**Making that actually cacheable took one more piece.** A pre-signed URL's signature is unique per call, so a fresh URL on every `GET /profile` would make the browser treat each response as a different resource and never reuse a cached copy across sessions. The fix is two-sided: `Cache-Control: private, max-age=86400` set on the selfie object itself at upload time (honored on any successful fetch, regardless of which signed URL retrieved it), plus a pre-signed expiry at least as long as that `max-age`, so the signature doesn't go stale before the browser's own cache would naturally expire it. `private` (not `public`) keeps any shared/intermediate cache from ever storing a piece of biometric reference data — only the requesting browser's local cache may.

### Net effect

No Lambda/table/CI-job counts change — this ruling is infrastructure shape (one S3 bucket, one CloudFront distribution, one EventBridge rule), not a new Lambda. `Photos.s3Key` (undefined since 2026-08-12) and the `download` Lambda's zip-key shape (undefined since its own ruling) are both now defined. Tight answer in `LOCKED_TECH_DECISIONS.md` §9.
