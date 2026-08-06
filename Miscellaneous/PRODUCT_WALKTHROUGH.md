# Glimpses — Product Walkthrough

**What this file is:** a readable, end-to-end description of what Glimpses does, organised the way the product is actually used rather than the order decisions were made. Every statement carries its ruling id (`P-nn`) so you can jump to the full entry in `LOCKED_PRODUCT.md`.

**What this file is not:** the source of truth, and not a record of reasoning. It deliberately leaves out *why* each option was chosen over the alternatives — that lives in `LOCKED_PRODUCT.md`, which stays authoritative if the two ever disagree.

**How to use it:** read §1–§7 as a story, then use §10's checklist to tick off all 100 rulings. If a section describes behaviour you did not intend, that is the thing to reopen.

**Covers:** all 100 rulings, `P-01`–`P-100` *(`P-75` and `P-76` are dissolved, not live)*. **Written:** 2026-08-05. **Revised:** 2026-08-06 — `P-82`, `P-83`, `P-86`, `P-40`, `P-85`, `P-31`, `P-53`, `P-07`, `P-54`, `P-89`, `P-95`, `P-74` changed, `P-99` and `P-100` added; see the decision log in `LOCKED_PRODUCT.md`.

---

## 1. What the product is

> *"Here is my face — show me every photo I appear in."*

Glimpses solves **retrieval**, not storage. After an event, the photos exist but nobody scrolls 2,000 of them. Face recognition is the core product, and anything that serves neither *"find my photos"* nor *"collect our photos in one place"* is a candidate for cutting — `P-01`.

It must work for **two different situations at once**, and every decision was checked against both:

| | **Broadcast event** | **Collaborative outing** |
|---|---|---|
| Example | Wedding, conference, college fest | Friends' trip, birthday, road trip |
| Who uploads | One photographer, in bulk | Everyone, from their phone |
| Scale | Hundreds–thousands of photos | Tens–low hundreds |
| Attendees are | Strangers to each other | Already friends |
| The real pain | Finding yourself among 2,000 photos | Photos scattered across six phones |
| Face matching is | The star feature | A bonus; aggregation is the point |

It is a **portfolio project built to be real-capable** — `P-22`. Consent and deletion are genuine features; formal compliance machinery (DSAR workflows, audit logs, a DPO process) is out of scope. The test for any privacy question is *"could this be pointed at a real wedding without embarrassment?"*

It is **mobile-web first** — `P-92`. The phone is the design target; desktop is the same layout with more room. No native app. Browser floor is the current version of Safari, Chrome, Firefox and Edge; accessibility is basic and untested — semantic markup, alt text where meaningful, keyboard navigation, sensible contrast, no WCAG target — `P-96`.

It must run inside the **AWS free-tier credit allowance** — `P-25`. This shapes product decisions, not just technical ones. The design target is **1,000 photos per event, 100 attendees per event, ~10 active events across the whole product** — `P-93`. These are planning figures only: **`P-40` enforces no limits at all**, so nothing stops an event or an account exceeding them.

---

## 2. Accounts

**Everyone has one account, and there is only one kind.** You are the *organizer* of events you create and an *attendee* of events you join — role belongs to the user–event pair, never to the account — `P-05`. There is no platform administrator anywhere in the product — `P-41`.

| Step | Behaviour | Ruling |
|---|---|---|
| Sign up | Email, password, and a display name | `P-02`, `P-84` |
| Verify | A **numeric code typed back into the app** — not a clickable link | `P-91` |
| Social sign-in | None. No Google, no Apple, no federated identity | `P-03` |
| Attendees | Must have an account. There is no anonymous "code plus selfie" access | `P-04` |

The **display name** is freely editable, not unique, and never verified — `P-84`. It supports recognising someone, not proving who they are.

**Email is used for authentication only** — `P-51`. Exactly two messages exist in the entire product: signup verification and password reset, both to the account holder's own address. Nothing else is ever emailed — no invitations, no lobby alerts, no retention warnings, no contribution notices.

**There are no notifications of any kind** — `P-81`. No badges, no unread counts, no feed, no push. You discover state by looking at the thing itself.

### Leaving

**There is no way to delete your account** — `P-74`. Not hidden, not by email request: it does not exist, and none will be added.

What you *can* do is delete your profile selfie. That destroys your face template, so nothing new is ever matched to you again — `P-68`. It is the only withdrawal action in the product.

| What stays | Ruling |
|---|---|
| Your account: email and display name | `P-74` |
| Photos you contributed, in their events, with your name and email on them | `P-74`, `P-86` |
| Match sets already computed, until the event expires on its normal clock | `P-68`, `P-33` |
| The privacy page **must say both of these plainly** — a required design obligation | `P-72` |

---

## 3. The organizer's journey

### Creating an event

**You supply a name and you are done** — `P-24`. No configuration questions, no "what type of event is this?", no publish step. Every dial has a default chosen to fit the majority case, changed later by the minority who need it.

**The name and an optional description are both editable while the event is `ACTIVE`** — `P-89`. **You never type a date:** the system records when the event was created and shows it as *"Created"*, never as the event's date. The description is blank by default and appears both inside the event and on the lobby screen, where it is what tells a waiting stranger whether they are in the right event at all. The two policy dials stay editable while `ACTIVE`; nothing is editable once archived.

The two dials — `P-06`, with defaults from `P-26`:

| Dial | Values | Default | What it controls |
|---|---|---|---|
| `joinPolicy` | `OPEN` / `APPROVAL_REQUIRED` | **`OPEN`** | Whether you must admit each attendee |
| `contributionPolicy` | `ORGANIZER_ONLY` / `ATTENDEES_CAN_ADD` | **`ATTENDEES_CAN_ADD`** | Whether attendees may add photos |

There is **exactly one organizer** — the person who created the event. No co-organizers, no transfer — `P-39`.

Limits: **none** — `P-40`. No photo cap, no event cap, no attendee cap. The only ceiling is Rekognition's unraisable 15 MB per-file limit, which is external rather than a product choice.

### Sharing the event

| Mechanism | Behaviour | Ruling |
|---|---|---|
| Access code | 6 alphanumeric characters, lookalikes (`0`/`O`, `1`/`I`/`l`) excluded | `P-08`, `P-27` |
| QR code | Encodes the join link; generated server-side and stored as an image file | `P-09`, `P-90` |
| Link format | CloudFront default domain — e.g. `d1a2b3c4.cloudfront.net/j/K7M2QX`. No custom domain | `P-30` |
| Who can share | **Any admitted attendee**, not just the organizer | `P-45` |

**An `ACTIVE` event is always shareable** — `P-31`. The code and QR are never hidden: not before the first photo is uploaded, not while a batch is processing. Sharing an empty event shows a note (*"No photos yet. Anyone who joins will see an empty gallery."*), not a block.

### Uploading photos

| | Behaviour | Ruling |
|---|---|---|
| Mechanisms | ZIP archive **or** multi-file selection — both available to organizers and attendees alike | `P-11`, `P-36` |
| Batching | One multi-file selection = **one** ingestion job, not twenty | `P-37` |
| Formats | JPEG and PNG. HEIC is accepted and converted to JPEG on ingest; the original is discarded. RAW is rejected with a clear message | `P-35` |
| Inside a ZIP | **Only the top level is read — folders inside the ZIP are not opened**, and you are told so before you choose the file. If a ZIP turns out to hold no loose photos, it says why: *"No photos found — folders inside a ZIP aren't opened. Zip the photos directly."* OS junk (`.DS_Store`) skipped silently. A video or RAW file **is** reported, because you chose it deliberately | `P-54` |
| Duplicates | Detected by exact content hash, scoped per event, skipped before conversion. You are told: *"26 photos added, 4 were already in the event"* | `P-38` |
| EXIF | **All metadata stripped on ingest** — no GPS, no timestamps, no camera fields | `P-58` |
| Cancellation | **Not possible once started.** Every batch has a maximum lifetime, after which it is marked failed | `P-53` |
| Partial failure | Reported as counts only: *"594 photos added, 6 could not be processed."* Never filenames. The result is **stored on the event**, so it is there whenever you next open it | `P-55`, `P-100` |
| Retries | The mechanism stays invisible — no filenames, no error text — but the batch may say *"3 photos are being retried, this may take a little longer"* | `P-56`, `P-100` |
| Progress | Shown while the upload screen is open. **Closing the tab does not stop anything**: the batch runs on and the photos appear in the event as they finish | `P-100` |
| Speed | Design target: up to **~30 minutes** for a full 1,000-photo batch | `P-94` |

**Practical consequence:** ingestion never blocks anything and never depends on anyone staying. The organizer hands out the code the moment the upload starts and walks away — **uploading during the event works as well as uploading before it** (`P-31`), and nobody waits thirty minutes at a screen (`P-100`). The visible effect of `P-94`'s ~30 minutes is that someone who joins mid-batch sees a gallery still filling up; `P-81` means *they* are told nothing about why, while the uploader is.

Every photo is **face-indexed identically regardless of who uploaded it** — `P-42`. A second batch creates a new job but lands in the same single gallery; batches are never a browsing concept — `P-14`.

### Managing the event

| Capability | Behaviour | Ruling |
|---|---|---|
| See who's in | Attendee and pending lists, showing **display name and email address** | `P-82` |
| Numbers shown | Photo count, attendee count, and **total storage used** — all informational, none of them a limit. Nothing else: no charts, no analytics | `P-85` |
| Approve / deny | Manual, one at a time, only if `joinPolicy = APPROVAL_REQUIRED` | `P-10` |
| Pre-approved guest list | **Does not exist.** No list of addresses, no auto-admission | `P-88` |
| Eject or deny | Either action blocks that user from rejoining with the code | `P-29` |
| Ejection and photos | Photos an ejected person contributed **remain**; you delete them yourself if you want | `P-47` |
| Delete a photo | Any photo in your event | `P-44` |
| Bulk delete | By multi-selection. There is **no** "delete everything this person added" | `P-52` |
| Per-attendee quota | None — and since `P-40` removed the event cap, nothing bounds how much one attendee uploads | `P-87`, `P-40` |
| Uploader shown | **Yes.** Every photo shows who added it — display name and email — to everyone | `P-86` |

Since there are no notifications (`P-81`) and no email beyond auth (`P-51`), **an organizer using `APPROVAL_REQUIRED` learns about waiting guests only by opening the event.** Someone can sit in the lobby for days. This is settled behaviour, not a gap.

### Event lifecycle

```
   create
     │
     ▼
  ACTIVE ──── organizer archives ────► ARCHIVED ──── retention ────► DELETED
     │        or 30d without upload        │           expiry          ▲
     │                                     │                           │
     └───────── organizer deletes ─────────┴───────────────────────────┘
```

- **`ACTIVE` is the only state that accepts change** — uploads, joins, contributions and matching happen here and nowhere else — `P-23`.
- **Archiving is permanent and cannot be undone** — `P-32`. Attendees keep viewing and downloading; uploads, joins and matching stop; the Rekognition collection is deleted.
- **Auto-archive after 30 days, delete 30 days after that** — an untouched event dies roughly **60 days** after its last activity — `P-33`, `P-77`.
- **"Activity" means a photo being added, and nothing else** — `P-78`. Viewing, downloading, joining and organizer visits do **not** reset the clock.
- **The organizer can permanently delete an event at any time**, with confirmation, straight from `ACTIVE`. Photos, face data and match sets all go — `P-34`.
- **The lifetime must be stated at creation and warned about before each transition** — `P-33`.

---

## 4. The attendee's journey

### Getting in

1. Enter the **6-character code**, or scan the **QR**, which opens the join link — `P-08`, `P-09`, `P-27`.
2. An account is required — sign up if you don't have one — `P-04`.
3. Then, depending on the organizer's setting:
   - **`OPEN`** (the default) — you are in immediately — `P-26`.
   - **`APPROVAL_REQUIRED`** — you wait in a lobby, seeing the event's **name, description, organizer, creation date and a clear waiting state, and nothing of its contents** — `P-10`, `P-28`.
4. A pending user **cannot upload** — `P-43`.
5. Code attempts are rate-limited, per account and per IP — `P-97`.

**You can leave an event at any time and rejoin later with the code** — `P-46`. Leaving ends membership, closes the gallery and stops matching for that event. Photos you contributed remain. **Leaving does not remove you from photos already indexed**, and the interface must not imply otherwise.

### Seeing photos

**Every admitted attendee sees every photo in the event** — `P-07`. There is no per-photo visibility: no photo is ever withheld from someone who has been admitted. **Admission is the only access control in the product.** `P-64`'s two views — your own photos, or the entire collection — are ways of *looking at* that gallery, never limits on what you may see.

| | Behaviour | Ruling |
|---|---|---|
| Layout | One gallery, infinite scroll. No page numbers, no "load more" | `P-63` |
| Order | Upload time, newest first. Filename breaks ties within a batch | `P-57` |
| Capture time | Not used for ordering | `P-57` |
| Who uploaded | Shown on the opened photo — display name and email. Stays there even if they are ejected | `P-86`, `P-99` |
| Other attendees | **No member list.** You can identify anyone who uploaded, from their photos; anyone who never uploaded is not named | `P-83` |
| Likes, comments, favourites | None. The gallery is a gallery | `P-62` |

### Face matching

**Matching is automatic and silent — you are never asked to search** — `P-16`. There is no "Find my photos" button anywhere.

| Step | Behaviour | Ruling |
|---|---|---|
| Your face reference | **One selfie on your profile**, set once, reused in every event. Never per-event, never per-search | `P-15` |
| Who can see it | **Nobody.** Not other attendees, not organizers | `P-15` |
| Optional? | Yes. Without a selfie you get the complete product minus the "my photos" filter | `P-17` |
| When you're asked | Contextually, the first time photos are on screen — *"want to see just the photos you're in?"* — never at signup, never blocking | `P-19` |
| Selfie requirement | Exactly one detectable face. Zero or two-plus is rejected with a clear message; nothing is guessed | `P-66` |
| Joining | Never blocks on matching. The gallery is usable immediately | `P-21` |
| Presentation | A **filter toggle** over the single gallery — not a tab, not a separate screen | `P-64` |
| Default view | The event opens **on your own photos** whenever you have a face reference and matches are ready; otherwise on the full gallery | `P-65` |
| Match quality | Similarity threshold fixed at **80**, exposed to nobody. Changing it is a code change | `P-80` |
| Per-event opt-out | Does not exist. The reference is account-level; the only opt-out is not having a selfie at all | `P-79` |

**The forward-only rule — this is the single most important behaviour to be sure about.** Nothing in the product ever reaches backwards into matches already computed:

| Action | Effect on future photos | Effect on existing match sets |
|---|---|---|
| Change your selfie (`P-20`, `P-98`) | Uses the new face | **Unchanged** |
| Delete your selfie (`P-68`) | Matching stops | **Kept** |
| Delete your account (`P-74`) | **Does not exist** — there is no account deletion | — |
| Manual re-match (`P-73`) | **Does not exist** — no control anywhere re-runs matching | — |

**What this means in practice:** if your matching is poor and you fix your selfie, you get better results **only for photos that arrive afterwards**. For an event that has stopped receiving photos — which is every event 30 days after its last upload — the fix does nothing at all, ever. This is a deliberate choice for a simpler system, not a cost saving; recomputing would cost about half a cent (`P-98`).

If you delete your selfie but have existing matches, the toggle **still renders**, and must visibly say the set is **frozen** — matching is off and the list will not grow — `P-69`.

An **empty filtered view** (you have a selfie but appear in no photos) must say plainly that the filter found nothing, show that it is on and reversible, and offer the full gallery directly — `P-65`.

### Getting photos out

| Path | Behaviour | Ruling |
|---|---|---|
| Single photo | Full-resolution, unwatermarked | `P-59`, `P-60` |
| Multi-selection | Several individual files at once | `P-60` |
| ZIP archive | Server-built, streamed, served through an expiring link | `P-60` |
| Combined | "My photos" filter + select-all + ZIP = *"download every photo I appear in"* in one action | `P-60` |
| Quality | Always the stored transcode at full size — originals were discarded at ingest | `P-35`, `P-59` |
| External sharing | **None.** Glimpses mints no public URLs. A photo leaves only as a file you downloaded and sent yourself | `P-61` |

### Contributing photos

Allowed when `contributionPolicy = ATTENDEES_CAN_ADD`, which is the default — `P-12`, `P-26`. Contributions **appear immediately; there is no moderation queue** — the organizer deletes anything unwanted afterwards — `P-13`. You may upload by multi-select or ZIP, exactly like the organizer — `P-36`.

**You can delete photos you uploaded** — `P-44` — individually or by multi-select — `P-52`. Deletion is **not retroactive**: anyone who already downloaded the photo keeps it, and the interface must say so plainly. There is no trash can and no undo anywhere in the product — `P-52`.

---

## 5. The person who is not a user

This is the part of the spec most worth reading closely, because it is where the product is weakest by its own admission.

**Faces in event photos are indexed, including those of people who are not users and never consented** — §7 point 1. This is unavoidable: you cannot find "photos containing this person" without analysing the faces in every photo. Every photo is treated identically regardless of who uploaded it — `P-42`.

What is guaranteed instead is the **direction of search** — §7 points 1 and 3:

- Every search runs against a face the searcher supplied themselves.
- **No screen, control or API accepts "find photos of that person."**
- No organizer has face search over their attendees.
- Nobody can see anybody else's match set.
- A non-user's face record is linked to no name and no account, exists inside one event only, and is destroyed when the event is archived or deleted — roughly 60 days, requiring action from nobody — `P-32`, `P-33`.

**What is not claimed** — `P-67`: Glimpses cannot verify that your profile selfie is a photo of *you*. Someone who sets their reference to another person's face will be shown that person's matches. This grants **no access** — `P-07` already gives every admitted attendee every photo — but it does grant efficiency. It is stated openly rather than defended against.

**The three disclosure rulings, read together:**

| | Ruling |
|---|---|
| A non-user has **no removal path** — no in-product route, no stated contact, no advertised remedy. Expiry is the only thing that happens | `P-70` |
| **No face-indexing notice** is shown to organizers or uploaders anywhere in the product | `P-71` |
| **One public, plain-language privacy page**, reachable without an account, linked from signup and the footer — never blocking, no checkbox | `P-72` |

The privacy page must state, in plain sentences: photos are analysed to find faces; this includes non-users; a face record is linked to no name or account; it exists in one event only; it is never searchable by anyone else's face; it is destroyed with the event in about 60 days; and your own selfie can be deleted at any time, which deletes the template — `P-72`. **It deliberately carries no contact address.**

**Stated plainly in the spec:** performing biometric analysis on non-consenting people, offering them no removal path, and informing nobody in-product that it happens is **the weakest point in the product against `P-22`'s test, and no other ruling is close.** What bounds it: the records are unlabelled, single-event, unsearchable, and self-terminating.

**Deleting your own selfie deletes the face template** — a real feature, not a support request — §7 point 5, `P-68`. It does not reach backwards into match sets already computed, and §7's wording must not imply it does.

**Consent obligation:** uploading a profile selfie must be an explicit, informed action stating what is stored and how to remove it. It can never be a silent onboarding step — `P-67`.

---

## 6. Permissions

Two roles, but **five states**, and every check is scoped to a `(user, event)` pair — `P-48`:

| State | Meaning |
|---|---|
| `NON_MEMBER` | Authenticated, no relationship to this event |
| `PENDING` | Submitted the code, waiting in the lobby |
| `ATTENDEE` | Admitted |
| `ORGANIZER` | Created the event — exactly one, never transferred |
| `BLOCKED` | Denied or ejected |

**One modifier evaluated before any role check:**

| Modifier | Effect |
|---|---|
| Event is `ARCHIVED` | Every write denied, for every state, **including the organizer** — `P-32` |

Ingestion state affects no permission anywhere — `P-31`.

**Order of evaluation is part of the specification** — `P-49`:

```
1. Is the event ARCHIVED?             → deny all writes, before considering role
2. Is this user BLOCKED here?         → deny everything
3. Load membership for (user, event)  ← from storage, never from the token
4. Check the role
5. Check the resource condition       ← e.g. "did this user upload this photo?"
```

**Four invariants** — `P-50`:

1. Every check takes `(userId, eventId)` — no permission is answerable globally.
2. **Role is re-read from the membership record on every request and never cached in a token claim.** This is the escalation bug the design is most exposed to.
3. *"Is this user admitted to this event?"* is the most security-critical check in the product.
4. Photo deletion requires loading the photo first — ownership cannot be inferred from a role.

**Who can do what:**

| Action | `NON_MEMBER` | `PENDING` | `ATTENDEE` | `ORGANIZER` | `BLOCKED` |
|---|---|---|---|---|---|
| Submit an access code | ✓ | — | — | — | ✗ |
| See event identity | ✗ | ✓ | ✓ | ✓ | ✗ |
| See the gallery | ✗ | ✗ | ✓ | ✓ | ✗ |
| See / share code and QR | ✗ | ✗ | ✓ | ✓ | ✗ |
| Change settings | ✗ | ✗ | ✗ | ✓ | ✗ |
| Archive or delete the event | ✗ | ✗ | ✗ | ✓ | ✗ |
| Leave the event | — | ✓ | ✓ | ✗ | — |
| Upload a photo | ✗ | ✗ | ✓ *if* `ATTENDEES_CAN_ADD` | ✓ always | ✗ |
| Delete a photo | ✗ | ✗ | ✓ *only their own* | ✓ any | ✗ |
| See pending requests | ✗ | ✗ | ✗ | ✓ | ✗ |
| Approve, deny or eject | ✗ | ✗ | ✗ | ✓ | ✗ |
| See the attendee list | ✗ | ✗ | ✗ | ✓ display name + email | ✗ |

**Profile and face — this table has no roles at all, which is the point:**

| Action | Owner | Anyone else, organizer included |
|---|---|---|
| View the profile selfie | ✓ | ✗ **always** |
| Set or change it | ✓ | ✗ |
| Delete the selfie and template | ✓ | ✗ |
| See a match set | ✓ own only | ✗ |

Once `BLOCKED`, a person loses the right to delete their own photos — preserving it would mean giving a blocked user a path back into the event — `P-47`.

---

## 7. What Glimpses deliberately does not do

A single list, because absences are harder to notice than features — and easier to disagree with.

| Not built | Ruling |
|---|---|
| Social sign-in of any kind | `P-03` |
| Anonymous access without an account | `P-04` |
| A platform administrator or support console | `P-41` |
| Co-organizers or ownership transfer | `P-39` |
| Per-photo visibility, or a matches-only *access mode* — a screen with its own permission. *(`P-64`'s matches-only **filter** does exist; it restricts the view, not the access)* | `P-07` |
| A moderation queue for attendee uploads | `P-13` |
| A pre-approved guest list, or emailed invitations | `P-88`, `P-51` |
| Notifications, badges, unread counts, push | `P-81` |
| Any email except signup verification and password reset | `P-51` |
| A member list for attendees | `P-83` |
| Filtering or selecting photos by uploader | `P-86`, `P-52` |
| Per-attendee upload quotas | `P-87` |
| Analytics and charts | `P-85` |
| A "Find my photos" button or any search step | `P-16` |
| Manual re-match, or recompute after a selfie change | `P-73`, `P-20`, `P-98` |
| A per-event opt-out from face matching | `P-79` |
| A user-adjustable similarity threshold | `P-80` |
| Likes, comments, reactions, favourites | `P-62` |
| Public share links for individual photos | `P-61` |
| Watermarking or downsized downloads | `P-59` |
| Retained camera originals | `P-35` |
| RAW support | `P-35` |
| Batch cancellation | `P-53` |
| Filenames in failure reports | `P-55` |
| A user-set event date — the date is the creation time, system-set *(the name and description **are** editable)* | `P-89` |
| Account deletion | `P-74` |
| Un-archiving | `P-32` |
| A trash can or undo, anywhere | `P-52` |
| A removal path for non-users | `P-70` |
| An in-product face-indexing notice | `P-71` |
| A contact address on the privacy page | `P-72` |
| A custom domain | `P-30` |
| A native app or a separate desktop design | `P-92`, `P-01` |
| A staging environment | `P-95` |
| Liveness detection or camera-capture requirements | `P-67` |
| Rate limits on uploads, joins or account creation | `P-97` |

---

## 8. Known weak points, stated by the spec itself

These are accepted costs the spec records openly. None is a bug; each is a decision that could be revisited.

1. **Non-user privacy is the weakest point, and no other ruling is close.** Biometric analysis of people who never consented, no removal path, no in-product disclosure — `P-70` + `P-71`.
2. **A bad selfie can never be fixed retroactively.** The product's own remedy is inert exactly when someone needs it — `P-20`, `P-73`, `P-98`.
3. **`APPROVAL_REQUIRED` is heavy.** No notification of any kind means guests can wait days — `P-51`, `P-81`, `P-88`.
4. **One attendee can upload without limit.** `P-40` removed the cap that used to bound this, `P-97` rate-limits only access-code attempts, and `P-81` tells the organizer nothing — so a flood is bounded only by the uploader's connection, and Rekognition bills on arrival — `P-87`, `P-40`, `P-97`, `P-81`.
5. **A partially failed batch cannot be diagnosed.** Counts without filenames means the rational response is re-uploading everything — `P-55`.
6. **The collaborative persona is served worse than the wedding one** in upload-time ordering rather than trip chronology — `P-57`. *(Uploader attribution was the second and was fixed by the `P-86` rewrite on 2026-08-06; the third was `P-94`'s ~30-minute window, which `D-117` and `P-100` made survivable — you can share and leave mid-batch.)*
7. **Deployments go straight to production with no rollback target and no rehearsal**, against live events holding photos that exist nowhere else — `P-95`.
8. **Anyone who obtained the code sees everything**, and any attendee can pass it on — `P-07`, `P-45`.
9. **Someone who held the camera opens a 300-photo album onto an empty screen** — mitigated only by the required empty-state design — `P-65`.
10. **An account can never be deleted** — the only withdrawal is deleting the profile selfie, which stops future matching but leaves the account, the contributed photos and the attribution on them — `P-74`, `P-68`, `P-86`.
11. **A progress figure can sit still while a slow retry runs**, looking stalled when it is not — `P-100`.

---

## 9. Not yet settled — carried into the technology discussion

Flagged in the spec as assumptions or explicitly unruled. **None is a locked decision.**

| Open point | Where |
|---|---|
| Rate-limit **thresholds** for access-code attempts — the mechanism is locked, the numbers are not | `P-97` |
| Whether there is **one Rekognition collection per event** — assumed by `P-98`'s cost arithmetic; deferred to the technology phase by the user on 2026-08-06 | `P-98` |
| How progress and retry state are actually produced — SQS bookkeeping vs Step Functions execution state. `P-100` is a deliberate **input** to that choice | `P-100` |
| Bulk approval of a waiting queue — `P-88` removed *pre*-approval, not approving several waiting people at once | `P-88` |

**Design obligations that are easy to lose during implementation** — each is load-bearing, not cosmetic:

- Scroll-position restoration in the gallery — `P-63`.
- The empty "my photos" state — `P-65`.
- The frozen-filter state — `P-69`.
- The privacy page must say plainly that accounts cannot be deleted, and that your name and email stay on photos you uploaded — `P-72`, `P-74`.
- **Verify Rekognition is available in `ap-south-1` before building** — it is not offered in every region — `P-95`.
- Progress must degrade honestly rather than freeze when a retry is slow — `P-100`.
- "Deletion is not retroactive" wording on photo deletion and ejection — `P-44`, `P-29`.
- Event lifetime stated at creation and warned before each transition — `P-33`.
- Deleting a photo must also delete its face vectors, which means retaining face identifiers — `P-52`.
- QR images and temporary ZIP archives both need a cleanup lifecycle — `P-90`, `P-60`.
- Terraform resource names must be parameterised, or `P-95` becomes expensive to reverse — `P-95`.

---

## 10. Coverage checklist — all 100 rulings

Tick through this to confirm nothing is missing. Grouped by area; each line is the ruling in one sentence.

### Product definition and constraints
- `P-01` Face-recognition photo retrieval is the core product; anything else is a candidate for cutting.
- `P-22` Portfolio project built to be real-capable; consent and deletion are real, compliance machinery is not.
- `P-25` Must operate within the AWS free-tier credit allowance.
- `P-92` Mobile-web first; no native app, no separate desktop design.
- `P-93` Target scale: 100 attendees/event, ~10 concurrent events (planning figures).
- `P-94` Ingestion target ~30 minutes for 1,000 photos; matches within a few minutes after.
- `P-95` One region — `ap-south-1` (Mumbai) — one environment, no staging.
- `P-96` Current browsers; basic untested accessibility.

### Accounts and identity
- `P-02` Email and password with verification.
- `P-03` No social sign-in.
- `P-04` Attendees must have an account.
- `P-05` One account; role scoped per event.
- `P-84` Display name collected at signup — editable, not unique, not verified.
- `P-91` Email verification by numeric code, not a link.
- `P-51` Email for authentication only, to the account holder alone.
- `P-81` No notifications of any kind.
- `P-74` Account deletion does not exist and will not be added.
- `P-75` *(Dissolved by `P-74` — organizers cannot depart.)*
- `P-76` *(Dissolved by `P-74`. `P-68` still destroys the template on selfie deletion.)*

### Events, roles and lifecycle
- `P-24` No configuration questions at event creation.
- `P-26` Locked defaults: `OPEN`, `ATTENDEES_CAN_ADD`, threshold 80.
- `P-06` Two independent policy dials.
- `P-89` Event name and optional description editable while `ACTIVE`; no user-set date, only a system "Created" timestamp.
- `P-39` Exactly one organizer; no co-organizers, no transfer.
- `P-41` No platform administrator role.
- `P-40` No limits of any kind; only Rekognition's external 15 MB per-file ceiling.
- `P-23` `ACTIVE` is the only state that accepts change.
- `P-31` Always shareable while `ACTIVE`; ingestion imposes no block.
- `P-32` Archiving is permanent; viewing and downloading survive.
- `P-33` Auto-archive on inactivity, deletion after.
- `P-77` Durations: archive at 30 days, delete 30 days later.
- `P-78` "Activity" means an upload, and nothing else.
- `P-34` The organizer can permanently delete an event at any time.

### Joining and access
- `P-08` Join by short access code; event ID never in a URL.
- `P-27` Code is 6 alphanumeric characters, lookalikes excluded.
- `P-09` A QR code encodes the join link.
- `P-90` QR generated server-side and stored as an image file.
- `P-30` CloudFront default domain; no custom domain.
- `P-10` Optional approval lobby.
- `P-28` A pending user sees identity only, never contents.
- `P-29` Eject or deny, and either blocks rejoining.
- `P-45` Admitted attendees can see and share the code and QR.
- `P-46` An attendee can leave and rejoin; contributed photos stay.
- `P-88` No pre-approved guest list.
- `P-43` Must be admitted before contributing.
- `P-97` Access-code attempts are the only rate-limited action.

### Photos going in
- `P-11` Organizers upload in bulk as a ZIP.
- `P-12` Attendees contribute when allowed.
- `P-36` Both roles get both mechanisms — multi-select and ZIP.
- `P-37` One selection is one batch.
- `P-13` Contributions appear immediately; no moderation queue.
- `P-35` JPEG and PNG; HEIC converted on ingest; RAW rejected.
- `P-38` Duplicates detected by content hash, per event, and reported.
- `P-54` ZIPs are mined for photos at the top level only, stated up front; OS junk skipped silently, real files reported.
- `P-53` No cancellation; every batch has a maximum lifetime.
- `P-55` Partial failures report counts, never filenames.
- `P-56` Transient failures retried without per-photo detail; `P-100` may say a retry is under way.
- `P-100` Progress is shown on screen; ingestion never depends on the uploader staying.
- `P-58` All EXIF stripped on ingest.
- `P-14` A second batch is a new job but the same single gallery.
- `P-87` No per-attendee upload quota.
- `P-42` Every photo face-indexed identically, regardless of uploader.

### The gallery and getting photos out
- `P-07` Every admitted attendee sees every photo.
- `P-57` Ordered by upload time, newest first; filename breaks ties.
- `P-63` Infinite scroll; cursor-based paging is forced.
- `P-62` No social layer and no favourites.
- `P-86` Uploader attribution — name and email — shown to everyone.
- `P-99` Attribution persists after ejection.
- `P-85` The organizer sees photo count, attendee count and storage used — informational only.
- `P-82` The organizer sees display names and email addresses.
- `P-83` No member list for attendees; uploaders are identifiable from the gallery.
- `P-44` Uploader deletes their own; organizer deletes anything. Not retroactive.
- `P-52` Bulk delete by multi-selection; no delete-by-contributor.
- `P-59` Downloads are the full-resolution transcode, unwatermarked.
- `P-60` Single, multi-select and server-built ZIP; all three exist.
- `P-61` No external sharing; no public URLs.

### Face matching
- `P-15` One account-level face reference, private to its owner.
- `P-16` Matching is automatic and silent; no search step.
- `P-17` The selfie is optional; without it, everything except the filter.
- `P-18` Matching is cost-bounded by pipeline concurrency, not user rate limiting.
- `P-19` The selfie is offered contextually, never at signup.
- `P-20` Changing the selfie applies to future photos only.
- `P-98` `P-20` re-founded on structural grounds after `D-96` disproved its cost argument.
- `P-21` Joining never blocks on matching.
- `P-64` "My photos" is a filter toggle over one gallery.
- `P-65` Events open on your own photos when ready; empty state must be designed.
- `P-66` The selfie must contain exactly one detectable face.
- `P-68` Deleting the selfie deletes the template, keeps existing matches.
- `P-69` The toggle survives as a visibly *frozen* state.
- `P-73` No manual re-match anywhere.
- `P-79` No per-event opt-out from matching.
- `P-80` Similarity threshold fixed at 80, exposed to nobody.

### Privacy
- §7 The five-point privacy position — directional guarantee, optional, no search for others, selfie never shown, template deletable.
- `P-67` Glimpses cannot verify the selfie is of you; stated, not defended against.
- `P-70` No removal path for non-users.
- `P-71` No in-product face-indexing notice.
- `P-72` One public privacy page, linked and never blocking.

### Permission model
- `P-48` Two roles, five membership states, every check scoped to `(user, event)`.
- `P-49` Order of evaluation is part of the specification.
- `P-50` Four invariants, including never caching role in a token.
- `P-47` Ejection removes the person, not their photos.
