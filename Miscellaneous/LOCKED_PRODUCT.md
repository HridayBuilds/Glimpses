# Glimpses — Locked Product Specification

**What this file is:** the settled, agreed description of what Glimpses does. Everything here has been explicitly decided by the project owner.

**What this file is not:** a place for options, alternatives, or open questions. Those live in `PRD.md`, the working decision space. When a question is ruled there, the decision moves here.

**Scope:** product behaviour only. Technology choices — language, runtime, AWS service shapes, data model, deployment — are deliberately excluded and will be decided after the product is locked.

**Last updated:** 2026-08-06 — **100 rulings, `P-01`–`P-100`.** `P-75` and `P-76` are dissolved: their ids and reasoning are retained in place, but they describe nothing the product does.

---

## 1. What Glimpses is

> *"Here is my face — show me every photo I appear in."*

After an event, photos exist but are effectively unusable: a 2,000-photo shared drive that nobody scrolls. Glimpses solves **retrieval**, not storage.

**`P-01` — Face-recognition-based photo retrieval is the core product.** Glimpses is not a general photo-sharing or photo-storage app. Any feature that does not serve "find my photos" or "collect our photos in one place" is a candidate for cutting.

---

## 2. The two shapes of event

Glimpses serves two genuinely different situations. They share one data model but pull defaults in opposite directions. **Every product decision must be sanity-checked against both.**

| | **Broadcast event** | **Collaborative outing** |
|---|---|---|
| Example | Wedding, conference, college fest | Friends' trip, birthday, road trip |
| Photo source | One photographer/organizer, bulk upload | Everyone, individually, from their phone |
| Scale | Hundreds–thousands of photos, many attendees | Tens–low hundreds of photos, small group |
| Attendees are | Strangers to each other | Already friends |
| The real pain | Finding yourself among 2,000 photos | Photos scattered across six phones, nobody collects them |
| Face matching is | The star feature | A bonus; aggregation is the main value |

---

## 3. Identity and roles

**`P-02` — Email and password, with email verification.** One identity system covers organizers and attendees alike. **Amended by `P-84`:** signup also collects a display name.

**`P-03` — No social sign-in.** No Google, no Apple, no federated identity providers. *(v1's Google OAuth never worked end-to-end and consumed significant debugging time for no product value. Deliberately dropped rather than re-attempted.)*

**`P-51` — The product sends email for authentication only, and only to the account holder's own address.** Two messages exist in the entire product: **signup verification** (P-02) and **password reset**. Nothing else is ever emailed — not lobby alerts, not invitations, not contribution notices, not retention warnings. Every other thing a user needs to be told is told in the app.

- **Password reset is in scope.** An account that becomes permanently unreachable on a forgotten password destroys the user's events, their gallery access, and their face reference, with signing up under a different address as the only recourse. That fails P-22's test outright. It also costs nothing extra — it rides the same sender already doing verification.
- **Why nothing beyond auth:** the two auth messages are sent to someone who pressed a button seconds ago and is actively watching their inbox, so even a spam-foldered message gets found. Every other candidate message is sent to someone who was not looking — and **P-30 gave away the ability to make those land.** Mail servers decide whether to trust a message by checking DNS records on the sending domain; with no custom domain there are no such records to publish, so unsolicited mail from Glimpses is unreliable in exactly the cases that need it. A notification that silently fails half the time is worse than no notification, because the product's behaviour then depends on something neither user can see.
- **Emailing invitations was rejected on more than deliverability.** It is the only feature here that would let Glimpses send mail to people who have no relationship with it, on the say-so of any account holder. P-41 removed the admin role, so nobody inside the product could respond to abuse of it. P-01 also marks it for cutting — it serves neither "find my photos" nor "collect our photos in one place", and an organizer with 200 addresses in a spreadsheet already has a better tool for mailing them than anything Glimpses would build.
- **Cost was not the deciding factor.** Email is rounding-error money at this workload (~$0.10 per 1,000 messages). The real costs are deliverability and abuse surface, and both are structural rather than financial. P-25 is not what ruled this.
- **Accepted cost, restated 2026-08-05 as permanent.** An organizer on `APPROVAL_REQUIRED` learns about waiting join requests only by opening the event itself. Someone can therefore sit in the lobby for days. This was originally written as though `D-63` might soften it with an in-app signal; **`P-81` ruled that no signal is built**, so the delay is the product's settled behaviour rather than a gap awaiting a fix. Narrowed only by `P-26` defaulting `joinPolicy` to `OPEN`, so it bites organizers who deliberately chose approval.
- **Reversible in one direction only.** Adding transactional email later is additive and breaks nothing. It would, however, require a custom domain first to be worth doing, so it is gated behind reversing P-30.

**`P-81` — There are no notifications of any kind. No badges, no unread counts, no notification feed, no push.** State is discovered by looking at the thing itself: pending join requests are visible inside the event, new photos are at the top of the gallery under `P-57`, matches surface silently under `P-16`, and an upload's progress and result are on the upload screen and the event under `P-100`. *(Last clause added 2026-08-06 by `D-126` — `P-100` shows state to someone already looking, which is this ruling's principle rather than an exception to it. Nothing is sent, and no read state is stored.)*

- **Nothing is stored to support it.** No per-user last-seen marker, no read state, no notification records — and therefore no retention policy for any of it. This keeps the data model to events, photos, memberships and match sets.
- **`P-16` already covers the case that matters most.** An attendee's own photos appear without being asked for, which is the one thing the product promises to tell them. `P-57`'s newest-first ordering puts new arrivals where they are seen.
- **Accepted cost, and it is real rather than theoretical.** `P-51` gave up email, and `P-81` gives up the in-app replacement, so **an organizer using `APPROVAL_REQUIRED` has no signal at all** — a person can wait in the lobby for days until the organizer happens to open the event. `P-51`'s accepted-cost bullet has been restated to say this is settled behaviour, not a gap `D-63` might close.
- **Reversible and additive.** A badge needs one stored timestamp per membership and breaks nothing. If lobby delay proves to be the product's worst real-world behaviour, this is the cheapest ruling to revisit.

**`P-82` — The organizer sees their event's attendee and pending-request lists as display name *and* email address.** *(Rewritten 2026-08-06 by `D-112`; the original withheld emails.)* Profile selfies remain invisible to everyone under `P-15`.

- **The controls require identity, and `P-84` established that the name is not it.** `P-29` lets the organizer eject an attendee and deny a pending one, and `P-10` requires approving them. `P-84` then made the display name **freely editable, not unique and never verified** — its own accepted-cost bullet admits "a user can set any name they like, including someone else's". Approving three lobby requests reading "Meera", "Meera N" and "meera" is guesswork. The email address is the only field on an account that has been checked against the outside world, via `P-02` signup and `P-91`'s numeric code.
- **The original "harvestable mailing list, in both directions" objection did not survive inspection.** "Both directions" requires attendees to see each other, and `P-83` rules they do not.
- **`P-51` means the product itself has no use for the address** — Glimpses emails nobody but the account holder. It is shown for a human to read while deciding whom to admit, not for the system to act on.
- **Accepted cost:** under `P-26`'s `OPEN` default, joining hands your address to whoever created the event.
- **Attendee-to-attendee visibility is not ruled here.** `P-83` covers the roster, `P-86` covers the gallery.

**`P-83` — There is no member list for attendees. The roster screen is visible to the organizer alone.** *(Rewritten 2026-08-06 by `D-113`. The original said attendees cannot see who else is in an event, which `P-86` made false.)*

- **Uploaders are identifiable** by name and email from `P-86`'s attribution; attendees who have never uploaded are not named anywhere.
- **The roster screen stays organizer-only because of the controls, not for privacy.** `P-82` gives the organizer the list because `P-29` and `P-10` need someone to act on. An attendee has no such control, so a roster is information with no action attached, and `P-62` removed the social layer it would otherwise attach to.
- **The original wording is retired rather than defended.** It claimed attendees cannot see who else is in an event, which `P-86` makes untrue wherever people upload.

**`P-84` — Every account has a display name, collected at signup alongside email and password. It is freely editable, not unique, and never verified.** This amends `P-02`, which established email and password only.

- **Signup was the only workable moment.** `P-82` shows the organizer a name at the *lobby request*, and for many users that is the first join — so a name prompted on first join (as `P-19` does for the selfie) would be empty exactly when it is needed. `P-19` keeps signup minimal and never asks for a face; one text field is a materially smaller ask and is the standard shape of a signup form.
- **Deriving it from the email address was rejected, and this is the sharp point.** Using the local part of `meera.nair.com` yields `meera.nair` — the address minus its domain. `P-82` refused to show emails at all, on `P-45` grounds that the access code reaches unvetted people. A derived name quietly returns most of what that ruling withheld, and would sometimes produce `mn2027` anyway.
- **Editable, not unique, not verified — chosen to be boring.** People change names and nothing in the product depends on the value being stable; two guests with the same name at a wedding is ordinary; and there is no mechanism to verify a name against anything. `P-82` already records that this supports *recognition*, not identification, and `P-29`'s blocklist is what actually enforces exclusion.
- **Accepted cost:** a user can set any name they like, including someone else's. Under `P-10` an organizer approving a lobby request is trusting a self-declared label. This is bounded by the same reasoning as `P-67` — under `P-07` the code already grants everything, so a misleading name buys admission theatre rather than access, and `P-29` reverses it.

**`P-85` — The organizer sees three numbers on their event: photo count, attendee count, and total storage used. Nothing else.** *(Rewritten 2026-08-06 by `D-116`.)* No search counts, no activity charts, no analytics of any kind. All three are **informational — none of them is a limit**, since `P-40` removed every cap.

- **The photo count lost its denominator, not its purpose.** It previously read "412 / 1,000" and now reads "412". The original ruling justified it as making `P-40`'s cap legible; with no cap, it stands on the plainer ground that an organizer should be able to see how much is in their event — particularly since `P-55` reports batch failures as a count, and a total is what that count has to be compared against.
- **Storage was added because the argument against it has gone.** The original refused it on the grounds that `P-40` bounded events in photos rather than bytes, so megabytes *"would imply a lever that does not exist."* `P-40` now bounds nothing in either unit, and for anyone self-deploying under `P-40`'s reasoning the bytes figure is the one that maps to their own AWS bill.
- **Stated honestly as informational.** Nothing throttles at any storage figure and no warning fires. It is a number to look at, not a budget.
- **Search count is still dead** — `P-16` removed searching from the product entirely, so there is nothing to count. **Charts remain cut by `P-01`**, needing time-series aggregation the product has no other reason to build.
- **Accepted cost, and it is a correctness risk rather than a privacy one.** A running byte total must stay accurate across `P-44` deletion, `P-52` bulk deletion, `P-38` dedup skips and `P-55` partial batch failures. **A counter that drifts is worse than no counter**, because it is silently wrong and `P-81` means nothing surfaces the discrepancy. Whether it is maintained incrementally or recomputed is a technology decision, but correctness across all four paths is a product obligation.

**`P-86` — Every photo carries visible uploader attribution: the uploader's display name and email address, shown to every admitted attendee.** *(Rewritten 2026-08-06 by `D-113`; the original showed attribution to nobody.)* Attribution records **who performed the upload action**, identically whether that was a `P-38` ZIP or a `P-37` multi-file selection — Arjun's 400-photo ZIP stamps all 400, Meera's six-photo selection stamps those six.

- **It closes the gap the original ruling itself named.** `P-86`'s own accepted-cost bullet called this "the clearest case in the spec of the wedding shape being served at the trip shape's expense" — in Priya's collaborative album, "who took this?" had no answer anywhere in the product. Organizer-only attribution would not have fixed it, because the person asking is an ordinary attendee.
- **No new data is created.** The uploader was already recorded internally, because `P-44` needs it to let people delete their own photos. This reveals an existing field rather than adding one, which is why it is among the cheapest rulings in the spec to implement.
- **`P-83` was rewritten rather than contradicted.** The original `P-86` was right that public attribution reveals membership through a second surface. That consequence is accepted here and `P-83` now states it accurately: uploaders are identifiable, non-uploaders are not.
- **The recommendation was name-to-everyone and email-to-organizer-only, and it was overridden** in favour of one consistent identity everywhere rather than a field that changes shape by viewer.
- **Accepted cost:** since `P-45` lets the access code travel, an uploader's email is readable by anyone who ends up holding the code. This is the ordinary shape of a shared album where people can see who contributed what, and it was ruled as such.
- **Design obligation: attribution must not become a delete-by-contributor control.** `P-52` refused "delete everything this person added", and attribution plus a filter is that control. **The gallery offers no filtering or selection by uploader.**
- **Design obligation: attribution belongs on the opened photo, not on every thumbnail**, or `P-57`'s single grid turns into a credits list.

**`P-99` — Uploader attribution persists unchanged after the uploader is ejected.** The photo continues to show the same display name and email address it always showed. *(Amended 2026-08-06 by `D-125`: this also covered account deletion, which `P-74` has since removed. Ejection is now the only way a person departs, so this ruling has one case instead of two — and it binds harder, because attribution can no longer be escaped by leaving.)*

- **It is the forward-only rule again.** `P-20` (selfie changed), `P-68` (selfie deleted, match sets kept), `P-73` (no re-match) and `P-98` all behave this way: no withdrawal action reaches backwards into what the product already recorded. `P-99` extends that to attribution rather than carving out an exception.
- **`P-74` and `P-47` already left the photos in place.** `P-74` severs the account link but keeps contributed photos in their events; `P-47` keeps an ejected attendee's photos. This ruling settles only what those photos *say*, which was previously nothing and is now a name and an address.
- **The recommendation was to drop the email and keep the name, and it was overridden** in favour of one rule with no exceptions and a label that does not silently change meaning.
- **Accepted cost:** a departed user's name and address stay visible on their photos until the event expires under `P-33`.
- **Design obligation:** the privacy page must state that the name and email on contributed photos remain. Same class as `P-44`'s "deletion is not retroactive". *(Amended 2026-08-06 by `D-125` — this used to sit on `P-74`'s account-deletion screen, which no longer exists; it now lives on `P-72`'s privacy page, alongside the statement that accounts cannot be deleted at all.)*

**`P-87` — There is no per-attendee upload quota.** *(Amended 2026-08-06: this ruling previously read "`P-40`'s 1,000-photo event cap is the only limit". `P-40` removed that cap, so **there is now no limit of any kind on how much one attendee uploads.**)*

- **The remedies are the ones the spec already built.** `P-52` bulk-deletes by multi-select and `P-29` ejects and blocks. No new mechanism, no per-membership counter, no number to invent — a per-attendee cap would have been a `§10` tuning-table guess rather than a measured value.
- **It is consistent with what the spec already accepts about the access code.** `P-45` lets attendees pass it on and `P-26` defaults `joinPolicy` to `OPEN`, so the product has repeatedly accepted that unvetted people get in. `P-13` already lets them post without review. A quota would have bounded the volume of that accepted risk without changing its nature.
- **Accepted cost, and `P-40` made it materially worse.** Previously one attendee could consume the event's 1,000-photo allowance and lock the organizer out of uploading. With no cap, the failure mode changes from *denying the organizer a capability* to **spending money without bound** — every uploaded photo is billed on arrival at Rekognition's per-image rate. `P-81` still guarantees nothing tells anyone. This is the same accepted risk `P-40` records, reached through a different door.
- **Reversible, and now the first thing to add if abuse appears.** A per-membership counter is one number and breaks nothing. With `P-40`'s cap gone this is no longer a refinement — it is the only remaining place a volume guard could go, alongside `P-81`.

**`P-88` — There is no pre-approved guest list. An organizer using `APPROVAL_REQUIRED` approves every arrival by hand.** No list of addresses, no auto-admission, no bulk approval path.

- **It completes `P-51`'s dismantling of the invitation feature.** That ruling cut the sending half — Glimpses never emails an invitation. `P-88` cuts the surviving half, so the product has no concept of a guest known in advance. The access code is the only way anyone reaches an event.
- **Matching on email address would have failed silently.** A guest listed as `meera.com` who signed up as `meera.n.com` waits in the lobby with no explanation, and `P-24` means the product will not ask her about it. That is the silent-partial-failure pattern `P-55` and `P-56` were written to avoid.
- **Accepted cost, and `P-81` sharpens it considerably.** With no notification of any kind, an organizer on `APPROVAL_REQUIRED` learns of waiting guests only by opening the event — and now has no mechanism to admit anyone in advance either. **`APPROVAL_REQUIRED` is therefore a materially heavier setting than when `P-10` was ruled**: every guest waits until the organizer manually looks and taps. Narrowed by `P-26` defaulting `joinPolicy` to `OPEN`, so the normal case never touches this.
- **Bulk approval of a waiting queue is not ruled here** and remains an ordinary interface question — `P-88` removes the *pre*-approval concept, not the ability to approve several waiting people at once.

**`P-89` — An event has a name and an optional description, both editable by the organizer while `ACTIVE`. It has no user-set date: the system records when the event was created and labels it "Created". The two policy dials remain editable while `ACTIVE`; nothing is editable once `ARCHIVED`.**

> **Rewritten 2026-08-06 by `D-121`, `D-122` and `D-123`** — three separate rulings, taken one at a time. The original fixed the name and date permanently at creation and had no description field at all. Its own closing bullet already conceded the name half was *"reversible — one field"*.

- **The name is editable (`D-121`).** The original was ruled on *identity stability*: under `P-28` a pending user sees only name, date and organizer, so a rename could turn the thing they asked to join into something else while they waited. **That protection was found to be thin** — the only person who can rename is the organizer, who already controls every photo in the event and whether the person is admitted at all. Weighed against it were two certain costs: a mistyped name ("Wedidng") greeting every attendee for the event's ~60-day `P-77` life, and Priya's trip album keeping a place name the trip no longer goes to. Renaming only when nobody has joined yet was offered and rejected — the need for a rename almost always arrives *after* people join.
- **Renaming does not disturb anything physical.** `P-90` establishes that the QR image is fully determined by the join link and that the join code never changes, so printed table cards and shared links survive a rename untouched.
- **A description exists, and it is optional (`D-122`).** Free text, blank by default, written and edited by the organizer on the same `P-24` settings screen as the name. **It is shown in the lobby under `P-28` as well as inside the event** — that placement is the reason it was ruled, not an afterthought. `P-28` exists because mistyped-but-valid codes drop people into strangers' events, and a description is the cheapest way for someone to confirm they are in the right place without being shown a single photo.
- **Optional and blank by default is load-bearing, not a nicety.** `P-24` cuts ceremony from event creation; a required description would put a writing task in front of every organizer for a field most will leave empty.
- **It is the product's first free-text field that other people read.** Only the organizer can write it, and they already control every photo in the event, so the exposure is small — but it is a new surface, and under `P-81` nothing alerts anyone about its contents. Noted so it is not discovered later as a surprise.
- **There is no event date (`D-123`).** The organizer types no date at creation. The system records a creation timestamp and the interface labels it **"Created"**, never "Date". **The label is the ruling, not decoration:** a creation timestamp displayed as an event's date tells Meera something subtly false — Arjun makes the album on 1 September for a wedding on the 12th. Showing "Created 1 Sept" is honest; showing "1 Sept" under a "Date" heading is not.
- **The lobby loses nothing, because the description replaces it.** A date was one of only three things `P-28` gave a waiting user to identify the event by. `D-122` was ruled first and deliberately: *"Ravi & Sneha's wedding, Udaipur"* identifies the event far better than any date did.
- **This closes the assumption `P-89` was carrying.** The original flagged "the date is treated identically to the name" as an assumption open to override. It is now ruled, and the date is no longer editable-or-not — the system owns it, so it can neither be mistyped nor go stale.
- **Two thirds of the original ruling were already settled elsewhere and are restated here only for completeness.** `P-24` mandates the settings screen where the dials are changed later; `P-32` makes archived events permanently read-only, so nothing is editable there — including the name and description.
- **Accepted cost:** an organizer can now change what the event is called after people have joined, and nobody is told (`P-81`). Judged acceptable on the same grounds the rename was: the organizer already holds every stronger power in the event.

**`P-91` — Email verification uses a numeric code typed back into the app, not a clickable link.** The same applies to password reset, the only other message `P-51` permits.

- **`P-30` is the deciding constraint.** With no custom domain there are no SPF/DKIM/DMARC records to publish, so Glimpses' mail carries no sending reputation. A bare numeric code is close to the least spam-triggering content an email can hold; a clickable link to a `cloudfront.net` address is among the most. `P-51` already accepted that these two messages work only because the recipient is watching their inbox — this ruling avoids spending that thin margin on a link.
- **It keeps signup on one screen.** `P-04` records account creation as the largest drop-off point in the attendee funnel. A link opens a browser tab and abandons the screen the user was on; a code lets them switch to mail, read six digits, and come back. The hop is exactly where the drop-off lives.
- **It is also Cognito's default behaviour**, so nothing has to be built to get it.
- **Accepted cost:** typing six digits is marginally more work than one tap, in the case where the mail arrives cleanly and the user is on a device where switching apps is easy.

**`P-92` — Glimpses is mobile-web first. The phone is the design target; desktop is the same layout given more room.** There is no native app (`P-01`) and no separately designed desktop interface.

- **Ruled on headcount, not on task count.** An event has one organizer and dozens to hundreds of attendees, and every attendee action in the spec is a phone action: scanning the QR (`P-09`), joining, browsing, toggling the `P-64` filter, saving individual photos to the camera roll (`P-60`). Arjun uploads once; Meera browses for weeks.
- **`P-19`'s selfie has no desktop equivalent worth designing for.** Nobody takes a profile selfie on a laptop, and `P-67` explicitly declined camera-capture requirements, so the flow must work well exactly where people already point a camera at themselves.
- **Accepted cost, and it lands on the organizer.** The two most laborious operations in the product — the `P-38` ZIP upload and `P-52`'s bulk delete by multi-select — are realistically desktop tasks (photos live in Lightroom on a Mac, not on a phone), and they get a layout not drawn for them. Multi-select across hundreds of thumbnails is materially worse in a single-column-derived grid.
- **Designing both properly was rejected on time, not merit.** It roughly doubles the interface work, and `P-25`'s six-month credit clock is the project's binding constraint.
- **This is the deferral `P-60` was waiting on.** That ruling noted the right download path differs by device — individual saves land in the camera roll on a phone, a ZIP lands in Files — and left the primary target open. `P-92` sets it.

**`P-93` — Target scale is 1,000 photos per event, 100 attendees per event, and roughly 10 concurrent active events.** *(Amended 2026-08-06: `P-40` removed every enforced cap, so this ruling is now the **only** statement of scale anywhere in the product — it inherits the photo and event figures `P-40` used to enforce, as design targets rather than limits.)*

- **These are planning figures, and nothing enforces them.** After `P-40` there are no enforced limits at all; `P-93` is purely what the system is *designed and tested against*. The ~10 concurrent figure implies roughly two or three simultaneously active organizers under `P-40`'s 5-event allowance — which is an honest description of a portfolio project's real load rather than a contradiction with it.
- **The number that actually drives cost is attendees, because of `P-16`.** Matching re-runs for every attendee each time a batch lands, so a batch at a 100-person event is ~100 search calls rather than one. `P-93` therefore caps the fan-out `D-96` is pricing, and is the figure that decision must be checked against.
- **Deliberately modest, and that is the point.** `P-25`'s six-month credit clock is the binding constraint, and designing for a load that never arrives spends the scarcest resource on the wrong thing. Higher targets were available and declined.
- **Accepted cost:** a genuinely large wedding or a mid-size conference — 200 to 300 guests — exceeds the design target. Nothing *stops* them, and after `P-40` nothing stops any size at all, but performance, `P-63`'s paging, and the `P-16` fan-out are not tuned for it, and the product should not be presented as handling that scale.

**`P-94` — Design targets: a 1,000-photo batch may take up to ~30 minutes to ingest, and matches may appear within a few minutes of a batch completing.** Relaxed targets, chosen deliberately over a faster pipeline.

- **They are targets to design against, not promises made to users.** Nothing in the interface states a duration; `P-53` supplies the hard ceiling with its mandatory batch lifetime, and `P-56`'s silent retry budget must fit inside that rather than inside this.
- **It buys the simplest pipeline that satisfies `P-55` and `P-56`.** A relaxed target does not force aggressive parallelism, which is where Rekognition throttling and the poison-message handling `P-56` exists to absorb become genuinely hard. The SQS versus Step Functions Distributed Map comparison the v1 analysis calls for is still worth making — but on correctness and observability grounds, since throughput no longer forces it.
- **Accepted cost, rewritten 2026-08-06 by `D-117`.** This bullet used to say the window was *dead time*, because `P-31` made the event unshareable throughout it and bulk upload was therefore a before-the-event task. **That is no longer true.** `P-31` now imposes no block, so Arjun can hand out the code the moment he starts the upload and the thirty minutes run in the background. What remains is milder and belongs to the guest, not the organizer: someone who joins during the window sees a gallery that is still filling, and under `P-81` is told nothing about it. Uploading during the event is now workable, which is what the §2 collaborative trip needed.
- **Match latency is the mild half.** `P-16` surfaces matches silently and `P-65` opens events on them once ready, so a few minutes' delay is invisible to anyone not already staring at the gallery.
- **Reversible.** Tightening the target later is an implementation change with no product consequence — no ruling depends on ingestion being slow.

**`P-95` — One AWS region — `ap-south-1` (Mumbai) — and one environment. There is no staging environment; deployments go directly to production.**

- **The region is ruled, not assumed.** *(Added 2026-08-06 by `D-124`.)* `ap-south-1` is nearest the user and the events being photographed, which is what matters for upload time on a 900-photo ZIP and for gallery latency. Rekognition, Cognito, DynamoDB, S3, Lambda and Step Functions are all available there. **Verify `ap-south-1` Rekognition availability against AWS's region table before building** — recorded as a check rather than asserted from recall.
- **Multi-region was never live.** It multiplies cost and complexity against `P-25`'s clock, and a Rekognition collection does not span regions — the face data underpinning `P-16` is inherently regional.
- **The Terraform obligation now matters more, not less.** Resource names must still be parameterised by region. A ruled region makes it tempting to hardcode `ap-south-1`, which is exactly what would make `P-95` expensive to revisit and what would break `Sam`, who self-deploys and may want a region near himself.
- **Accepted cost, and it is the largest operational risk in the spec.** Every change is tested against the live system. With real events in it under `P-77`'s 60-day retention, a bad deploy can destroy photos that exist nowhere else — `P-44` already establishes that deletion does not reach downloaded copies, but an attendee who never downloaded has no other copy. **There is no rollback target and no rehearsal.**
- **The Jenkins pipeline can only deploy, not promote.** With a single environment there is nothing to promote from, so continuous delivery here means build, test and apply — not a staged progression.
- **The cost argument did not carry it.** An idle staging environment bills close to nothing: S3 and on-demand DynamoDB charge for use, Lambda per invocation, Cognito is free at this scale. The recommendation was to build one and was overridden; the real saving is Terraform effort and setup time, not money.
- **Reversible, and the cheapest way back is Terraform discipline now.** Adding an environment later is straightforward *if* resource names are parameterised from the start. **Hard-coding names would make this ruling expensive to reverse** — worth carrying into the infrastructure work as a concrete obligation.

**`P-96` — Browser floor is the current version of Safari, Chrome, Firefox and Edge. Accessibility is basic and untested: semantic markup, alt text where meaningful, keyboard-navigable, sensible contrast. No WCAG target, no audit, no screen-reader testing.**

- **`P-92` sets the floor, not browser age.** Mobile-first means the primary browsers are phone browsers, which update themselves. Supporting older engines would mean polyfills and fallbacks for browsers nobody in the target audience is using.
- **Image formats are not part of this.** `P-35` already converts HEIC server-side precisely because Chrome and Firefox cannot render it, so the browser floor is a question about CSS and JavaScript features only.
- **WCAG 2.1 AA was considered seriously and declined on `P-22`.** That ruling builds consent and deletion as genuine features while putting heavyweight compliance machinery out of scope, and an accessibility standard is an audit discipline rather than a checklist — tooling, audit passes, remediation. Basic accessibility done honestly captures most of the real benefit at a fraction of the effort.
- **Accepted cost:** no compliance can be claimed, and the gallery grid — the most complex interactive surface in the product, with `P-63`'s infinite scroll and `P-64`'s filter toggle — has untested screen-reader behaviour and probably real gaps.
- **One gap is structural rather than a matter of effort.** Alt text for user-uploaded photos does not exist and cannot be generated under `P-25`'s budget. A photo gallery is therefore inherently limited for a screen-reader user, whatever the target — worth stating rather than leaving as an implied failure.

**`P-97` — Access-code attempts are the only thing rate-limited, per account and per IP. Uploads, joins and account creation carry no application-level limits.**

- **It is the only true breach in the list.** `P-07` makes admission grant every photo in an event, and `P-26` defaults `joinPolicy` to `OPEN` — so a correctly guessed code is immediate full access, with no lobby in the way. `P-27`'s ~1 billion combinations are only a defence if guessing is bounded. Everything else on the original list is a nuisance with an existing remedy: `P-40` caps total volume, `P-52` clears it, `P-29` ejects the person.
- **Face search dropped out of this question entirely.** `P-16` made matching automatic, `P-73` removed manual re-match and `P-79` removed per-event opt-out, so **no user action triggers a search.** The `P-16` fan-out is driven by batches arriving, which makes it a pipeline concurrency concern under `P-56`, not user rate limiting. `P-18` has been amended accordingly.
- **It leaves the API Gateway choice open, which is worth preserving.** Usage plans and API keys exist only on API Gateway REST API, not HTTP API. Limiting code attempts in application code — a counter in DynamoDB — means the cheaper HTTP API with its native JWT authorizer stays available. Ruling more broadly would have pushed that decision toward REST before it was taken.
- **Accepted cost, widened 2026-08-06 by `P-40`:** with `P-87` allowing unlimited uploads per attendee and no upload rate limit, a flood is now bounded only by the attacker's connection — `P-40`'s 1,000-photo cap, previously the backstop named here, no longer exists. The organizer's remedies are entirely after the fact, and `P-81` means nothing alerts them.
- **Thresholds are not fixed here.** The mechanism is locked; the numbers belong in §10's tuning table and should be set when the join flow is built.

**`P-04` — Attendees must have an account.** Anonymous "code plus selfie" access is not supported.

- **Accepted cost:** account creation is the largest drop-off point in the attendee funnel.
- **What it buys:** a stable identity for the lobby to approve, reliable per-user rate limiting, and a persistent face reference that works across every event.

**`P-74` — Account deletion does not exist. There is no way to delete a Glimpses account, and none will be added.** The account, its display name, its email address and its `P-86` attribution on every photo persist for as long as the deployment does.

> **Rewritten 2026-08-06 by `D-125`.** The original ruled what happens to a departing user's photos, and openly carried the note *"forced, not ruled — that account deletion exists at all… it remains open to override."* The user overrode it. This dissolves `P-75` and `P-76`, which existed only to answer questions raised by deletion.

- **The exit that mattered survives untouched, and it is the reason this is coherent.** `P-68` lets any user delete their profile selfie at any time, which **destroys the face template**. §7 point 5 makes that a real product feature. So the biometric data a user can be asked to worry about is still removable on demand — what is gone is the ability to remove the *account*, which holds an email address and a self-chosen display name. That is a materially smaller thing than the face data, and it is why removing deletion does not overturn `P-22`'s privacy position.
- **`P-44` and `P-52` are now the only removal paths, and they are enough for photos.** A user who wants their contributions gone deletes them individually or by multi-select. Nothing about that changed; the original `P-74` already refused to make photo deletion a side effect of closing an account, so no capability is lost here that the original granted.
- **Accepted cost, stated in one line and not softened:** a user who wants to leave Glimpses entirely cannot, and their name and email stay visible under `P-86` and `P-99` on every photo they uploaded, until the event expires under `P-33`. `P-99` already ruled that attribution persists after a user leaves; there is now no way to leave.
- **Ruled on build cost and scope, consistently with `D-115` and `D-119`.** Account deletion is not one screen — it is a cascade through memberships, organized events (`P-75`), match sets (`P-76`), Cognito identities and every `P-86` attribution, each with a correctness question of its own. For a portfolio project on a 6-month credit clock, the user judged it not worth building. Stated as the reason so it is not later mistaken for a privacy position.
- **Consequence — the deletion-screen design obligation is void.** The original required a confirmation screen stating that contributed photos and their name and email remain. There is no such screen. **What that obligation protected must move to `P-72`'s public privacy page instead**, which is now the only place a user can learn that their contributions and identity are permanent.
- **Reversible, but not cheaply.** Adding deletion later reopens `D-106` and `D-107` — organized events and match sets — which `P-75` and `P-76` answered and which are now dissolved. Their reasoning is preserved in the log rather than deleted, so a future reversal starts from the answers rather than from scratch.

**`P-75` — DISSOLVED 2026-08-06 by `D-125`.** *(Was: when a user deletes their account, every event they organize is archived immediately.)* **`P-74` removed account deletion**, so the question this answered — what happens to an event whose organizer leaves — can no longer arise. Nothing replaces it: an organizer is permanent because an account is permanent. **The reasoning is kept below rather than deleted**, because it is the answer a future reversal of `P-74` would need, and because its rejection of ownership transfer stands on `P-41` and `P-05` independently of deletion.

> *Original text and reasoning, retained for reference:*

- **It introduces no new concept.** `P-32`'s archived state already means *this event is finished — look, don't touch*, and `P-33` already deletes on a timer. An organizer's departure maps onto a state the product has rather than inventing an ownerless one.
- **It makes the departure cost what it actually costs.** Deleting the event would have destroyed 1,000 photos for 200 attendees because one person closed an account. Under `P-75` the loss is future uploads only.
- **Transfer of ownership was rejected.** `P-41` leaves no admin to receive it, and `P-05` makes the organizer role a property of the user–event relationship rather than a transferable asset. Handing it to an attendee — earliest-joined, or any other rule — gives a guest `P-44`'s power to delete any photo in a photographer's event, and `P-05` would need rewriting to allow role reassignment at all.
- **Accepted cost:** an archived ownerless event has no one who can delete a photo from it, since `P-44`'s organizer path went with the account and the uploader path only covers their own photos. A takedown request landing in that window has no route — bounded by the event already being read-only and on a deletion clock, and consistent with `P-70` already declining a removal path.
- **Consistent with `P-74`:** neither ruling destroys other people's content as a side effect of one person leaving.

**`P-76` — DISSOLVED 2026-08-06 by `D-125`.** *(Was: account deletion destroys the face template and leaves computed match sets in place.)* **`P-74` removed account deletion.** The behaviour itself is unchanged and still reachable — `P-68` already rules that deleting the profile selfie destroys the template and leaves match sets alone, which is the exit that still exists. Only the account-deletion framing is gone. **Its §7 obligation survives and has been moved to `P-68`'s wording**, since that is now the only path it describes.

> *Original text and reasoning, retained for reference:*

- **One rule, no exceptions.** `P-20` (selfie changed), `P-68` (selfie deleted), `P-73` (no re-match), `P-75` (account deleted, events archived) and now `P-76` all behave the same way — forward-only. The product has no operation that revises computed match history, which is the same simplicity `P-73` was ruled on.
- **Accepted cost, and it is the sharpest version of `P-68`'s.** A stored record continues to say which photos a departed user appeared in, after they took the strongest withdrawal action the product offers. Unlike `P-68`'s case there is no longer a user who could view it — `P-69`'s frozen toggle needs an account to render — so these sets are **unreachable by anyone and serve no purpose until they expire.** The recommendation was to delete them and was overridden in favour of the single rule.
- **What bounds it:** the record is not a face template — that is genuinely destroyed — and `P-33` deletes the event, its photos, its collection and everything derived from it within roughly 60 days. The residue is inert, unviewable, and self-terminating.
- **§7 point 5 must not overstate this.** It says deleting the profile selfie deletes the face template, which is true. It must not be read — or worded — as a claim that leaving Glimpses erases the record of which photos you appeared in. `P-68` already carried this obligation; `P-76` extends it to account deletion.

**`P-05` — One account, role scoped per event.** There is no global "organizer" or "attendee" account type. A user is the *organizer* of events they created and an *attendee* of events they joined. Role is a property of the user–event relationship, never of the account.

- **Why:** the collaborative-outing case makes a global role incoherent — the person who created the trip album is obviously also on the trip. A photographer who attends a friend's wedding must not need a second account.
- **Accepted cost:** every permission check must be scoped to a specific event and can never be answered globally from a token claim alone. This is the trickiest part of the permission model and is designed explicitly in §8.

---

## 4. Access control

**`P-41` — There is no platform administrator role. The product has exactly two roles: organizer and attendee, both scoped per event.** Operator tasks — abuse response, removal requests from non-users, debugging — are performed out of band through the AWS console.

- **It grants no power that does not already exist.** Owning the AWS account already means being able to read or delete anything in S3 and the database. An admin role would be a UI wrapper around powers held regardless, not a new capability.
- **It keeps §7 literally true.** P-07 states admission is the only access control, and §7 point 3 states nobody can search for another person's face or see another person's match set. An in-product admin is a second, universal access path that would force both claims to be amended to "except the administrator." P-22's test is *"could this be pointed at a real wedding without embarrassment?"* — and "the developer has a button showing him every wedding" fails it. *(Citation corrected 2026-08-06: this bullet previously cited "no user is discoverable by another", which `P-86` made false. `P-41` itself does not depend on that claim and is unaffected.)*
- **It removes the highest-value target in the system.** A single compromised admin credential would expose every private event on the platform, including those that enabled approval specifically to stay private. No such credential exists.
- **P-22 puts audit logging out of scope**, and an administrator able to view any photo with no audit trail is worse than having no administrator.
- **Accepted cost:** abuse response and support are manual, performed against raw identifiers in the console rather than a purpose-built screen. Acceptable for a single-operator portfolio project, and reversible — adding a role later invalidates nothing.

**`P-39` — An event has exactly one organizer: the user who created it. There are no co-organizers and no ownership transfer.**

- **Why:** event administration serves neither "find my photos" nor "collect our photos in one place", so P-01 marks it for cutting. More importantly the cost lands precisely where P-05 warns the product is most delicate — co-organizers would double every "the organizer can X" rule in §8 and add three genuine security questions of their own: may a co-organizer delete the entire event (P-34), promote further co-organizers, or eject the creator (P-29)? Each is a real escalation path, not a formality.
- **Keeps §8 to two roles**, organizer and attendee, which is the single largest simplification available to the permission model.
- **Accepted cost:** a photographer who creates the event owns it, even though the wedding is not theirs — the couple cannot moderate their own album. An abandoned event cannot be handed to anyone and simply runs out P-33's clock. Several people shooting one event must all work through whoever created it.
- **Reversible:** adding ownership *transfer* later touches no roles and is cheap. Adding true co-organizers later would be a rewrite of §8, so that door is the one being closed.

**`P-06` — Access to an event is governed by two independent dials**, set per event by the organizer.

| Dial | Values | Controls |
|---|---|---|
| `joinPolicy` | `OPEN` / `APPROVAL_REQUIRED` | Whether the organizer must admit an attendee before they get in |
| `contributionPolicy` | `ORGANIZER_ONLY` / `ATTENDEES_CAN_ADD` | Whether attendees may add photos |

**`P-07` — Every admitted attendee sees every photo in the event.** There is no per-attendee photo visibility: admission grants the whole gallery, and no photo is ever withheld from an admitted attendee.

> **Wording corrected 2026-08-06 by `D-118`.** This ruling's second sentence read *"and no mode in which an attendee sees only their own matches"* — written before `P-64` existed and flatly contradicted by it ever since. **This is a correction to how the ruling was written, not a change to what was ruled.** `P-07` is about *permission*; `P-64` is about *presentation*, and the spec had been using one ruling's words to deny the other's feature.

- **The two views are the product, not an exception to it.** `P-64` gives one toggle with two positions: **every photo in the event**, or **only the photos you are in**. `P-65` opens on the second when matches are ready. Both are views over the same single dataset that `P-07` already grants in full — the toggle changes what you are *looking at*, never what you are *entitled to*.
- **The distinction that keeps this straight:** a filter is reversible by the person using it and hides nothing they could not immediately show again. A permission is not. `P-07` rules out the second; it has never ruled out the first.

- **Why:** the audience for "I want to be in this event but only see myself" is small, and supporting it forced a per-photo permission model, a search-before-you-see gate, and a large test matrix through the entire product. Not worth the cost.
- **Consequence:** admission is now the *only* access control in the product. Getting in means seeing everything, which raises the importance of the access code's strength and of the organizer's ability to remove an attendee.
- **Sensitive events are served by turning approval on**, not by hiding photos — the same model as a shared album.

**`P-08` — Attendees join via a short access code**, which is the primary sharing mechanism. The event ID is never required in a URL and is resolved server-side.

**`P-09` — A QR code encodes the join link**, so an organizer can put it on a screen, a table card, or in a group chat.

**`P-90` — The QR code is generated server-side and stored as an image file, served through CloudFront like any other asset.** Not drawn in the browser on demand.

- **Ruled for the share-into-a-group-chat case, which `P-09` explicitly names.** A stored image is a real file an organizer can download, attach, or drop into WhatsApp. Client-side rendering would have left them screenshotting their own screen — a workaround for one of the uses the QR exists to serve.
- **What it costs, and this is the part to carry into implementation.** One stored object per event, a generation step at creation time, and — importantly — **a cleanup obligation: the QR image must be deleted when `P-33` deletes the event.** It joins `P-60`'s expiring ZIP archives on the list of stored artifacts that need a lifecycle, rather than being pure computation with nothing to tidy.
- **The image is fully determined by the join link**, so it is a cache rather than a source of truth. **The join code never changes**, so the file never needs regenerating. *(Corrected 2026-08-06 by `D-121`: this bullet also cited `P-89` fixing the name and date, which is no longer true — the name is now editable. It never mattered here. The QR encodes the link alone, so a rename leaves every printed card and shared QR valid.)*
- **`P-51` did not decide this.** The original framing of this question gave server-side the advantage of being "emailable", which `P-51` removed entirely — Glimpses sends two auth emails and neither carries an attachment. The ruling stands on in-app sharing instead.

**`P-10` — The organizer can require approval before an attendee joins**, MS-Teams-lobby style, toggleable per event.

**`P-27` — The access code is 6 alphanumeric characters, excluding lookalikes** (`0`/`O`, `1`/`I`/`l`). Roughly a billion combinations from a ~32-character alphabet.

- **Why:** short enough to read aloud or type off a table card, while making enumeration impractical. Under P-07 the code alone grants full access whenever `joinPolicy` is `OPEN` — which is the default — so 6 digits (1M combinations, walkable in under a day by a scripted attacker) was too weak.
- Join attempts are rate-limited regardless; the code's strength is defence in depth, not the only defence.

**`P-46` — An attendee can leave an event at any time, and may rejoin later with the code.** Photos they contributed remain in the event.

- **Why an exit is necessary:** `joinPolicy` defaults to `OPEN` (P-26) and the code is six characters (P-27), so mistyping into a *valid* code admits someone to a stranger's event instantly, with full access to every photo under P-07. P-28 already acknowledges that mistyped-but-valid codes happen, but only protects the `APPROVAL_REQUIRED` path — the default path had no remedy at all.
- **What leaving does:** membership ends, the gallery becomes inaccessible, and matching stops for that event.
- **What it does not do:** it does not remove the person from photos already indexed — P-42 makes that unavoidable. The §7 guarantees still hold: nobody can search for them, and P-32/P-33 destroy the collection on archive or expiry. The interface must not imply leaving erases them from other people's photos.
- **Contributed photos stay**, because they are part of a shared album. P-44 already lets someone delete their own photos before leaving, so no special case is needed to give them control.
- **Rejoining is allowed.** Treating a voluntary exit as a P-29 blocklist entry would make one mis-tap permanently unrecoverable, and would conflate "left" with "unwanted".

**`P-45` — Admitted attendees can see and share the access code and QR.** Sharing is not an organizer-only capability.

- **Why:** an attendee necessarily *knows* the code already — they entered it to get in, or followed a link they can forward. Hiding it in the interface would remove no capability, only the convenience of finding it. That is theatre, not access control.
- **Consequence, stated plainly:** under P-07 the code is the entire security boundary, so its reach is every admitted attendee and whoever they choose to tell. An organizer who needs control over arrivals must use `joinPolicy = APPROVAL_REQUIRED` (P-10); ejection and blocking (P-29) are the only other recourse. This is a property of P-07, and no restriction on code visibility would have changed it.

**`P-28` — A user waiting in the lobby sees the event's identity and nothing of its contents.** Name, description, organizer, creation date, and a clear waiting state. *(Amended 2026-08-06 by `D-122`/`D-123`: the description was added here deliberately — it is now the strongest signal a waiting user has for confirming they are in the right event — and "date" became the system-set "Created" timestamp, which identifies far less.)*

- **Why:** enough to confirm they entered the right code, so a mistyped-but-valid code doesn't leave them waiting forever on an approval that will never come. No cover photo and no photo count, because both leak real information about a private event to someone the organizer has not vetted and may deny.

**`P-29` — The organizer can eject an admitted attendee or deny a pending one, and either action blocks that user from rejoining with the code.** One per-event blocklist serves both.

- **Why:** since admission grants access to everything (P-07), the organizer needs a genuine undo. A denial that can simply be retried also lets a persistent requester spam the lobby indefinitely.
- **Accepted cost:** photos the user already downloaded are gone and cannot be recalled. The interface must say this plainly rather than implying removal is retroactive.

**`P-30` — Join links and QR codes use the CloudFront default domain** (e.g. `d1a2b3c4.cloudfront.net/j/K7M2QX`). No custom domain.

- **Why:** P-25. A custom domain is the one part of this stack that costs real money (~$12–15/year for the name plus ~$6/year for a hosted zone), and it buys appearance rather than function.
- **Accepted cost:** the URL looks untrustworthy printed on a wedding table card, which is a real adoption obstacle for the broadcast persona.
- **Second accepted cost, found 2026-08-04 and re-ruled:** a domain is also what makes email deliverable to people who are not actively watching their inbox — the SPF/DKIM/DMARC records mail servers check live on a domain you own. Without one, the product cannot reliably notify anyone. **The ruling stands anyway**, because the capability a domain would buy back is precisely the one P-51 cut on its own merits. Buying a domain to enable a feature that was deliberately removed is backwards.
- **Registration is the only charge in the entire stack that AWS credits do not cover.** *(Recalled, not verified against primary sources — flagged rather than asserted.)* Promotional credits apply to AWS's own services; domain registration is AWS reselling a name from a registry, and sits on the standard exclusion list. The ~$0.50/month hosted zone **is** credit-covered, and the ACM certificate is free. So the true out-of-pocket is a one-time ~$12–15 on a real card, not the ~$18/year originally stated.
- **The money was not what ruled it.** $12 is not a budget question under any reading of P-25, and saying otherwise would make P-25 carry more than it can. It was ruled on the domain buying back an unwanted capability.
- **Cheaply reversible:** adding a custom domain later is a certificate and an alias record. Nothing else in the product depends on the domain, so this is not a one-way door — it can be reversed the week before the project is shown to anyone.

---

## 5. Photos going in

**`P-11` — The organizer uploads photos in bulk as a ZIP archive**, because the broadcast case involves hundreds or thousands of files at once.

**`P-12` — Attendees can contribute photos when the organizer allows it**, serving the collaborative-outing case where there is no single photographer.

**`P-13` — Attendee contributions appear immediately; the organizer can delete anything afterwards.** There is no moderation queue.

- **Why:** trust-first. A review queue is absurd among friends on a trip, and at scale it makes the organizer a bottleneck while contributors see nothing happen after uploading — which kills the contribution habit immediately.
- **Accepted cost:** an unwanted photo is briefly visible before the organizer removes it.

**`P-42` — Every photo is face-indexed identically, regardless of who uploaded it.** There is no distinction between organizer-uploaded and attendee-uploaded photos for matching purposes.

- **Why the uploader is irrelevant:** the concern behind this question was that an attendee uploading a group shot causes biometric indexing of people who consented to the organizer rather than to them. But the organizer's own photos contain non-consenting strangers just as much — **who pressed upload does not change whose faces are in the frame.**
- **Indexing only organizer photos would be fatal to half the product.** In the collaborative outing of §2 there is no organizer batch — every photo is attendee-uploaded — so matching would do nothing at all for that entire persona. It would also produce a gallery where some photos match and others silently do not, with no visible reason.
- **A consent checkbox was rejected as theatre.** It changes no behaviour, protects nobody, adds friction to the flow P-26's default exists to encourage, and cannot honestly be answered — an attendee has no way to know whether every stranger in the background consented.
- The honest privacy position that follows is stated in §7 point 1.

**`P-43` — An attendee must be admitted before they can contribute photos.** A user waiting in the lobby cannot upload.

- **Why:** P-28 gives a pending user the event's identity and nothing of its contents. Letting them write into a gallery they cannot see would be incoherent, and would let a user the organizer is about to deny (P-29) place photos in the event first.

**`P-40` — There are no product limits. No photo cap per event, no cap on active events per organizer, no attendee cap.** *(Rewritten 2026-08-06 by `D-115`; the original set 1,000 photos/event and 5 active events/organizer.)* The only ceiling anywhere is a per-file size guard, and that one is **not a product choice** — Rekognition's 15 MB S3-object limit is documented as unraisable, so a file above it cannot be indexed no matter what the spec says.

- **Ruled on the project's actual shape.** Glimpses is a portfolio deployment that will be torn down with `terraform destroy`, and it is published so others can stand up their own. Caps chosen for one person's credit budget become friction for everyone who clones the repo — the design goal is that someone runs the Terraform and the documented steps and gets a working system without editing application source.
- **`P-93`'s figures survive and are now the only statement of scale.** 1,000 photos per event and 100 attendees remain what the system is *designed and tested against*. Nothing enforces them. Exceeding them is permitted and untuned rather than blocked.
- **The parameterised-limits option was offered and declined.** Keeping the caps as Terraform variables with today's values as defaults would have given self-deployers the same freedom while retaining the guard. It was rejected in favour of no limits at all.
- **Accepted cost, and it is the sharpest in the spec, because it is the one that spends real money.** The original ruling called the per-organizer cap *"the only real guard against a scripted abuser"* and that guard is now gone. `P-97` rate-limits only access-code attempts, `P-87` sets no per-attendee upload quota, and `P-81` means nothing alerts anyone. **Rekognition indexing is billed on arrival at ~$0.001/image and is roughly 6× the cost of storing a photo for its whole life — so `terraform destroy` recovers nothing already spent.** A script creating events and uploading can consume `P-25`'s $200 credit allowance before the teardown that was supposed to bound it. This is accepted as a portfolio-deployment risk, not mitigated.
- **What still bounds cost in practice:** `P-33`'s ~60-day retention, `P-95`'s single deployment, and the fact that reaching the event at all requires `P-27`'s 6-character code or an organizer account.

**`P-38` — Duplicate photos are detected by content hash, scoped per event, and the uploader is told.** A hash of the file's bytes is computed on ingest and checked against the photos already in that event. An exact match is skipped — not stored, not converted, not indexed.

- **Why hashing and not a similarity check:** an exact-byte match has no threshold to tune and no false positives, so a duplicate is *certain*. Perceptual hashing would additionally catch re-compressed copies (a photo forwarded through WhatsApp), but it measures similarity — and burst shots taken a second apart look similar. A false positive there silently destroys a photo the user wanted, which is a far worse failure than one extra photo in the gallery.
- **Cost is not a concern.** Measured: SHA-256 over a 3.6 MB photo is ~1.2 ms locally and ~2–3 ms on a full-vCPU Lambda, against ~127 ms for the P-35 conversion and a Rekognition call of several hundred milliseconds — roughly **1% of per-photo work**. The bytes are already in memory for conversion, so no extra I/O. A stored hash is 32 bytes against a multi-megabyte photo.
- **The check runs first**, so a duplicate skips conversion, thumbnailing, storage, and the Rekognition call. **Duplicates are cheaper than new photos, not more expensive** — which matters because a duplicate otherwise costs twice under P-25: once in storage, once in Rekognition.
- **Why per-event and not global:** global dedup would make two events share one stored file, which breaks P-34. An organizer deleting an event to remove a photo they regret must get a complete answer; if another event references those bytes, the file cannot be deleted. Avoiding that needs reference counting, and it puts a hedge on a deletion promise that §7 and P-22 require to be absolute. Per-event keeps deletion trivially correct, and the storage saved by global dedup is negligible — the identical file rarely lands in two events.
- **Accepted cost:** a re-compressed copy of a photo already present (typically via a messaging app) is not detected and appears twice. The copy is the lower-quality version and the original remains, so nothing is lost.
- **The uploader is told:** *"26 photos added, 4 were already in the event."* Reporting the selected count would be a lie and reporting only the stored count reads as a failed upload.

**`P-36` — Both organizers and attendees can upload either a multi-file selection or a ZIP archive.** Neither role is restricted to one mechanism.

- **Why attendees need multi-select:** an iPhone has no practical way to zip photos from the camera roll. ZIP-only would not add friction to attendee contribution — it would end it, silently gutting P-12 and making P-26's `ATTENDEES_CAN_ADD` default untrue in practice.
- **Why attendees also get ZIP:** an attendee may be on a laptop with a folder of photos from their own camera, which is the same situation P-11 built ZIP for. The path already exists for organizers, so offering it to both is a permission, not a second implementation.
- **Why organizers also get multi-select:** "I found three more photos" is a normal follow-up, and zipping three files to add them is exactly the ceremony P-24 exists to remove.

**`P-37` — A multi-file selection is one batch, grouped at the moment the user confirms the upload.** Twenty photos selected together produce one ingestion job, not twenty.

- **Why:** it matches what the user believes they did — they added photos once. It also keeps D-37 (partial failure) and D-87 (organizer notification) behaving identically whether the photos arrived in a ZIP or a picker. *(Amended 2026-08-06 by `D-117` — `P-31` was listed here too, back when batch state governed sharing; it no longer does.)* The alternative sends the organizer twenty notifications for one action.

**`P-35` — Accepted formats are JPEG and PNG. HEIC is accepted and converted to JPEG on ingest; the original HEIC is discarded.** This applies everywhere an image enters the product — organizer ZIPs, attendee contributions, and the profile selfie of P-15.

- **Why HEIC must be handled at all:** iPhones shoot it by default, and it is unusable twice over. Rekognition reads only JPEG and PNG, *and* Chrome and Firefox cannot render HEIC — so a stored-as-is HEIC is an invisible photo, which breaks P-07's promise that every admitted attendee sees every photo. Rejecting it would also break P-19's selfie prompt at the exact moment it was designed to succeed.
- **Why JPEG and not PNG:** the question was raised on the grounds that PNG is lossless. It was ruled against on evidence. HEIC is *already* lossy, so PNG preserves degraded pixels rather than recovering quality; PNG on photographic data measured **~12× the size of JPEG q90** at iPhone resolution (12.14 MB vs 1.02 MB on a real 12MP photo), which attacks the storage constraint P-33 exists to contain; and a 12MP PNG lands at 12–25 MB against **Rekognition's documented, unraisable 15 MB S3-object limit** — so PNG would intermittently fail to index the crowded, detailed photos that matter most. PNG is also strictly dominated on fidelity: it is far larger than the source HEIC while containing no more information than it.
- **Generation loss is answered with quality, not format.** JPEG is written at **quality 90–95**, not a default 75–85. One re-encode from a good source at that quality is visually indistinguishable at any zoom the gallery offers, for roughly 30% more size rather than 12×.
- **RAW is rejected** with a clear message. Vendor-specific formats, an entirely separate decode path, and enormous files — and a photographer shooting RAW exports JPEGs to share anyway.
- **Consequence:** ingestion now has a mandatory image-processing stage. This is not purely a cost — thumbnails are needed regardless, so the transcode and the thumbnail generation are one pass.
- **Accepted cost:** downloads return a transcoded file, not the camera original. Judged acceptable; retaining originals was considered and rejected as roughly 1.6× storage against P-25.

**`P-44` — The uploader of a photo can delete it. The organizer can delete any photo in their event.** Deletion is not retroactive: anyone who has already downloaded the photo keeps their copy, and the interface must say so plainly rather than imply removal reaches backwards *(the same obligation P-29 places on ejection)*.

- **Why:** P-34 already establishes that deletion must be immediately available because *"the moment someone most wants photos gone is seconds after uploading them."* That reasoning applies identically to a contributor. Since P-13 makes contributions instant and public with no moderation queue, the undo must be equally instant.
- **Accepted cost:** in a collaborative album the photos someone contributed become everyone's memories, and this lets one contributor withdraw them unilaterally — a group can lose a meaningful share of an event's photos. Judged the lesser harm: refusing to let someone remove their own photograph is the failure that gets screenshotted.
- **A time-limited window was rejected** — it introduces a magic number and a state no other part of the product has (*"why could I delete this yesterday?"*), while failing the case that most deserves help: someone asked to take a photo down a week later.
- **This is the first permission in the product that a role alone cannot answer.** Both an uploader and any other attendee hold the same role; only the user–resource relationship distinguishes them. See §8.

**`P-52` — Photos can be deleted in bulk by multi-selection.** The gallery supports selecting several photos and deleting the selection in one action, using the rights `P-44` already grants — an attendee over photos they uploaded, the organizer over anything in the event. There is no action that deletes photos by contributor.

- **Why bulk deletion is required, not a nicety:** `P-47` accepted the cost that an ejected attendee's photos must be cleared *manually*. Manual has to mean possible. Clearing forty junk photos one tap at a time is not a cost an organizer pays — it is a cost they refuse, and they live with the junk instead, which would make `P-47` wrong retroactively.
- **Multi-select needs no explanation.** Every phone photo gallery already works this way, so it introduces no new concept — consistent with `P-24`'s stance against ceremony.
- **"Delete everything this person added" was rejected.** It looks like the natural companion to `P-47`, but `P-47` deliberately declined to auto-delete an ejected person's photos, on the grounds that ejection covers two unrelated situations — moderating a spammer and a personal falling-out — and that automatic deletion serves the first while weaponising the second. Putting the same action behind a button changes the mechanism, not the harm. Multi-select reaches the same outcome with the organizer actually looking at what they are destroying.
- **Still holds after `P-86`.** *(Added 2026-08-06.)* Attribution now shows whose photos are whose, which puts this rejected control one filter away from existing. **That filter must not be built** — the organizer reaches the same outcome by multi-select, looking at what they destroy.
- **This is not a cost lever, and must not be argued as one.** Rekognition's indexing charge is paid on arrival and is roughly 6× the cost of storing a photo for its entire life (`P-33`). Deleting recovers only the small ongoing portion. Bulk deletion is a moderation and privacy feature.
- **Accepted cost:** select-all followed by delete is instant, unrecoverable, and — per `P-44` — reaches nobody who already downloaded. There is no trash can and no undo anywhere in this product.
- **Forced consequence, not a separate ruling:** deleting a photo must also remove that photo's face vectors from the event's Rekognition collection. §7 point 5 and `P-22` require deletion to be complete; a deleted photo whose biometric data survives would make the privacy position false. This obliges the system to retain the face identifiers produced when each photo was indexed, so they can be deleted later — a data-model consequence recorded here so it is not discovered during implementation.

**`P-63` — The gallery is an infinite scroll.** Photos load continuously as the reader reaches the bottom. There are no page numbers and no "load more" control.

- **`P-24`'s instinct settles it.** That ruling stripped configuration and ceremony wherever it appeared, and pagination controls are ceremony placed around the one screen the entire product exists to deliver. It is also what every phone photo gallery already does, so it needs no explanation.
- **Numbered pages were ruled out** as a filesystem metaphor applied to photographs, with small controls at the bottom of a long scroll on exactly the device the selfie flow lives on.
- **Consequence — paging must be cursor-based, and this is forced by `P-57` and `P-16` together, not chosen.** `P-57` puts the newest uploads at the top and `P-16` has photos arriving silently while someone is already browsing, so the list shifts under the reader. Requesting photos by position — *"items 100 to 150"* — would show them photos they already scrolled past, or skip some entirely, whenever a batch lands mid-scroll. Requests must instead be *"the next 50 after this specific photo."*
- **Accepted cost, and it is the thing that actually goes wrong:** returning from a full-size photo to a gallery scrolled several hundred photos deep only works if scroll-position restoration is built deliberately. It is routinely omitted, and when missing the gallery feels broken in a way users cannot articulate — they simply stop scrolling deep, which silently defeats `P-40`'s 1,000-photo ceiling.

**`P-62` — There is no social layer and no favourites.** No likes, no comments, no reactions, and no private starring of photos. The gallery is a gallery.

- **Likes and comments are structurally contradicted, not merely cut.** Comments require moderation, `P-41` deliberately removed the only role that could moderate, and `P-51` removed the channel that would tell anyone a comment exists. It would be a conversation nobody is notified about and nobody can police. `P-01`'s cutting test disposes of it independently — it serves neither "find my photos" nor "collect our photos in one place".
- **Private favourites were a genuinely close call, ruled out on redundancy rather than principle.** `P-60`'s multi-selection already lets a user pick out the five photos they want from forty and download them immediately, so a persistent star only adds value for someone who marks photos in one session and returns in another — on an event that `P-33` destroys in roughly 60 days.
- **Accepted cost:** on a 1,000-photo event, shortlisting depends on a multi-selection that lives only as long as the browsing session. An accidental tap or a page refresh loses it, and there is no sturdier alternative. Favourites remain the cheapest thing that would fix this — one flag per user-photo pair, with no privacy surface since nobody else can see it — so this is the most likely candidate for a later addition of anything ruled out tonight.

**`P-61` — There is no external sharing of individual photos. Glimpses mints no public URLs.** A photo leaves the product only as a file the user downloaded (`P-59`, `P-60`) and sent themselves.

- **The capability was never in question, only who hosts it.** A user can already download a full-resolution photo in one tap and pass it on through their phone's share sheet. A share link adds no ability — it moves the hosting of that photo from the sender to Glimpses.
- **A public link would be the first account-free access path in the product.** `P-04` requires an account and `P-07` made admission the *only* access control — a ruling the spec has leaned on repeatedly since, including `P-41`'s removal of the admin role, which was justified partly on keeping §7 literally true. Every one of those rulings would need an "except shared links" clause.
- **A permanent link would additionally break `P-33`.** Retention exists so photos and face data reliably disappear after roughly 60 days. A permanent URL either outlives the event, making that promise false, or dies with it, producing dead links people shared months earlier.
- **The decisive point is who does the publishing.** A photo of two people typically contains several more who were never asked. When the user downloads and forwards it, *they* publish it, exercising their own judgement about the strangers they can see in the frame. When the product mints a public URL, the product publishes it, and §7's face-privacy guarantee gets quietly weaker without anyone deciding that it should — which matters more now that `P-86` puts an uploader's name and email on the photo itself.
- **`P-01`'s cutting test applies cleanly:** sharing outward serves neither "find my photos" nor "collect our photos in one place". It is a social feature on a retrieval product.
- **Accepted cost:** sending one photo to someone outside the event takes a download and a share sheet rather than a single link. The product also gives up its most natural growth mechanism — a shared link is how photo products spread — but `P-22` and `D-75` already ruled this a portfolio project rather than one chasing adoption, so there is little to give up.

**`P-60` — Photos can be downloaded singly, as a multi-selection of individual files, or as a server-built ZIP archive.** All three paths exist; the user chooses. Combined with the "my photos" filter and a select-all, this is what delivers *"download every photo I appear in"* as one action.

- **This completes `P-01`'s promise.** The product exists so someone can say *"show me every photo I appear in"* and walk away with them. Downloading is the last step of that journey, and the archive is what makes it a single action rather than three hundred.
- **The three paths are not redundant, because the right answer differs by device.** On a phone, saving individual photos places them in the camera roll, ready to post; a ZIP lands in the Files app and iOS will not unpack it into the camera roll without steps most people will not take. On a laptop the reverse holds — 300 individual downloads trigger browser permission prompts and throttling, while one archive is exactly right. Offering both is what serves both, and `D-72` (mobile-web first) does not need to be settled to proceed.
- **Multi-selection is a reused control, not a new concept.** `P-52` already put multi-select in the gallery for bulk deletion; downloading the selection sits alongside deleting it.
- **Accepted cost — this is the most expensive thing in the gallery to build, and it was chosen knowingly.** A 300-photo archive is roughly 300 MB. It cannot be assembled in memory and must be streamed, written to temporary storage, served through an expiring link, and cleaned up afterwards. Every photo in the selection is read from storage a second time. Against `P-25`, whose real constraint is time on a 6-month clock rather than money, this is the largest single build item ruled so far.
- **Consequence — archive generation is an asynchronous job and inherits `P-53`'s obligations.** It cannot complete within a single request, so it needs a terminal state and a maximum lifetime for the same reason ingestion did: a build that neither finishes nor fails leaves the user waiting forever. Temporary archives must also expire and be deleted, or they become unbounded storage that `P-33`'s retention rules never see.
- **Bandwidth doubles for archived downloads** relative to `P-59`'s per-photo figure — once to build the archive, once to serve it. Still small in absolute terms, and still the only cost in the product unbounded by `P-40`.

**`P-59` — A download is the full-resolution transcode, unwatermarked.** `P-35` already established that originals are discarded, so a download is always the converted JPEG — but it is the stored file at full size, not a reduced copy, and nothing is stamped onto it.

- **`P-01` decides this.** The product exists so someone can say *"show me every photo I appear in"* and walk away with them. A photo that cannot be printed is a weak answer to that, and it fails at the very last step of the journey the whole product was built to serve.
- **Downsizing optimises the wrong end.** It would cut bandwidth — the cheapest thing in the system — while requiring a **third stored rendition** per photo alongside the full transcode and the thumbnail, which means more work in the per-photo ingestion pass, which is where the real cost lives (`P-40`, `P-33`).
- **Watermarking breaks the collaborative persona outright.** §2 requires every decision to survive both event shapes, and stamping a watermark across friends' holiday photos fails immediately. It also implies a paid tier that removes it — a business model this product does not have.
- **Bandwidth scales with how many people download how often, which nothing limits.** *(Until 2026-08-06 this was the only cost not bounded by `P-40`; after `P-40` removed every cap, no cost is bounded by the product.)* Measured: a 12 MP q90 JPEG is ~1 MB and CloudFront transfer is ~$0.085/GB, so 100 guests each taking 200 photos is ~20 GB ≈ **$1.70** — still well under the ~$1.26–2.58 that indexing the same event cost. Not a constraint, but it is the one line item that grows with success rather than with photo count.
- **Accepted cost:** a professional photographer's work leaves Glimpses unprotected and, after `P-58`, without embedded copyright metadata either. Judged acceptable because they chose to place those photos in a gallery `P-07` shares with every admitted attendee — a watermark would be defending against people they deliberately invited.

**`P-58` — All EXIF metadata is stripped on ingest.** Photos are stored, served, and downloaded carrying no hidden metadata — no GPS coordinates, no timestamps, no camera or software fields.

- **The leak this closes is structural, not hypothetical.** `P-07` makes admission grant every photo, `P-26` defaults `joinPolicy` to `OPEN`, and `P-45` lets any attendee pass the code on. The spec has repeatedly and deliberately accepted that the access code will reach people the organizer never vetted. Phone GPS is accurate to a few metres, so preserving it would hand each of those people the exact address where the getting-ready photos were taken. That fails `P-22`'s test — *"could this be pointed at a real wedding without embarrassment?"* — more squarely than anything else in the spec.
- **Nothing in the product reads EXIF.** `P-57` ordered the gallery by upload time, removing the only consumer. Location is never displayed, never searched, and no map feature is in scope. Metadata was pure passthrough — it entered, sat unused, and escaped only on download.
- **Stripping only GPS was considered and rated the worst of the three options.** It preserves fields nothing reads, in exchange for maintaining a per-field allowlist indefinitely, and EXIF carries vendor-specific extension blocks that can hold location redundantly. A partial strip that misses one is *worse* than no strip, because it is believed to be safe.
- **Neither choice was free.** `P-35`'s HEIC-to-JPEG conversion discards EXIF unless it is deliberately copied, so stripping is the default on that path — but a directly uploaded JPEG is stored as-is and needs explicit removal. There was no lazy option; one path required work either way.
- **Accepted cost:** a photographer's embedded copyright and attribution fields are destroyed across their whole batch. Softened but not erased by two facts — `P-35` already discards originals and returns transcodes, so these were never master files, and social platforms strip EXIF on upload anyway, so the notice rarely survived sharing regardless.

**`P-57` — The gallery is ordered by upload time, newest first.** Capture time from EXIF is not used for ordering.

- **New photos are always visible.** `P-16` makes photos arrive silently while people are already browsing, and this ordering guarantees every arrival lands at the top of the gallery where someone scrolling will actually see it. Chronological ordering would drop a friend's late upload of Day 1 photos into the middle of the gallery, where nobody would ever notice it appeared.
- **It cannot be wrong, because it does not depend on data the product does not control.** EXIF capture time is missing entirely from screenshots, scans, and anything forwarded through a messaging app, and it is silently wrong whenever a camera's clock or timezone was never set. Upload time is recorded by Glimpses, is always present, and is always correct. This ruling removes an entire class of "why is this photo dated 2019" behaviour rather than accepting it.
- **Accepted cost, stated plainly:** the collaborative outing of §2 reads in the order people found wifi rather than the order the trip happened. Six friends uploading across three days produce a gallery interleaved by upload convenience, and a wedding opens on the last dance rather than the ceremony. This is a real loss of narrative for both personas, and it was ruled against chronology deliberately, not by oversight.
- **Consequence — a tiebreak is required and is not optional.** `P-37` makes a multi-file selection one batch, and a ZIP arrives as a single upload, so hundreds of photos share one upload time. Order within a batch must fall back to something stable, and filename is the natural choice: camera-assigned names such as `IMG_0001` generally follow capture order, so it recovers much of the chronology this ruling gave up, for free and without trusting a clock.
- **Consequence — EXIF preservation is no longer load-bearing.** Had capture time been used, `P-35`'s HEIC-to-JPEG conversion would have had to carry EXIF across deliberately or every iPhone photo would silently lose its timestamp. That risk disappears here. Preserving EXIF remains optional and is now governed only by the privacy question of what should be *stripped*.
- **Reversible, but not cheaply after the fact.** Switching to capture time later requires EXIF that was never captured at ingest, so photos already stored could not be reordered retroactively.

**`P-56` — Transient failures are re-attempted silently before a batch is declared finished.** A photo that fails for a temporary reason — rate limiting, a timeout, a momentary service error — is retried a small number of times with a growing delay. A photo that fails deterministically — corrupt, unreadable, or over Rekognition's unraisable 15 MB limit — is retried, fails identically, and is given up on. Nothing about any of this is shown to the user; the batch simply takes marginally longer.

- **This is what makes `P-55`'s failure count mean anything.** Without it the number reported to the uploader partly measures Glimpses throttling itself, and the user cannot tell the difference — `P-55` gives them a count and no causes. Retrying makes *"6 could not be processed"* mean *"your files are broken"* rather than *"we were busy."*
- **Rate limiting is the expected case here, not an edge case.** Firing several hundred Rekognition calls at once is what a large ZIP does by definition, and absorbing that burst is already the stated reason a queue or Step Functions sits in this architecture at all.
- **It is invisible in both directions.** Success and failure look identical to the user whether or not retry exists, so this adds no concept, no screen, and no message. *(Amended 2026-08-06 by `D-126`: `P-100` now lets a batch in progress say that photos are being retried and that this is why it is slower. The per-photo mechanism stays invisible — no filenames, no error text — but the fact of retrying no longer is.)*
- **Cost is negligible:** a handful of extra Rekognition calls per batch, measured in fractions of a cent.
- **Accepted cost:** deterministic failures now cost their retries too — a corrupt file is decoded and rejected several times before being abandoned — and the batch's worst-case duration grows, which `P-53` caps with a hard lifetime. The retry budget has to fit inside that lifetime. *(Amended 2026-08-06 by `D-117` — this bullet also cited `P-31` hiding sharing for the duration; `P-31` no longer blocks sharing, so a longer batch now costs only a gallery that fills more slowly.)*

**`P-100` — An upload in progress shows its progress on screen, and its result survives the uploader leaving. Ingestion never depends on anyone staying.** *(New ruling 2026-08-06 by `D-126`.)* While the upload screen is open it shows how far the batch has got and, when photos are being retried, says so and says that it is why this is taking longer. If the user closes the tab, walks away or shuts the laptop, **the batch continues server-side and the photos appear in the event as they finish.** The `P-55` result is stored on the event and shown whenever they next open it.

- **This is not a notification, and `P-81` is untouched.** `P-81` bans things that reach a user who is not looking — push, badges, unread counts, a feed. This rules only what a screen shows to someone already looking at it, which is precisely `P-81`'s own principle: *"state is discovered by looking at the thing itself."* Nothing is sent anywhere, and no per-user read state, last-seen marker or notification record is stored — `P-81`'s data-model bullet stands unchanged.
- **The durable half is the load-bearing half, and it closes a real hole.** `P-94` allows ~30 minutes and `P-81` tells nobody anything, so before this ruling there was no stated place where Arjun could ever learn his batch finished or that 6 photos failed — `P-55` defined the message without saying where it lived. **Nobody waits thirty minutes at a screen.** Uploading must therefore be fire-and-forget: hand over the ZIP, leave, come back to photos.
- **It is what makes `P-31` honest.** `D-117` removed the share block so Arjun can hand out the code mid-upload and walk off. That only works if walking off is safe.
- **Retries become visible where they were silent (`P-56`).** `P-56` ruled that transient failures are retried with nothing shown. That stands for the *mechanism* — no per-photo detail, no filenames, no error text — but the batch may now say *"3 photos are being retried, this may take a little longer"*. The point is explaining a delay the user can already see, not reporting failures individually.
- **`P-55`'s contract is unchanged.** Counts, never filenames. This ruling gives that message a home and a moment; it does not expand it.
- **Mechanism follows the ingestion-stack decision, deliberately.** What the user sees is ruled here. Whether progress and retry state come from a counter maintained by an SQS consumer or from Step Functions execution state is a technology decision — and this ruling is a genuine input to it, since retry state is native to Step Functions Distributed Map and bookkeeping under SQS. **Do not let the stack choice quietly narrow what this ruling promises.**
- **Live push was rejected.** WebSockets or AppSync subscriptions would smooth a thirty-minute job nobody watches second-to-second, cost `Sam` real infrastructure to self-deploy, and edge toward the push `P-81` removed. Polling while the screen is open is enough.
- **Accepted cost:** a progress figure implies more precision than a pipeline gives — a batch can appear stalled at 412 of 900 while a slow retry runs. The display must degrade honestly rather than freeze, and `P-53`'s hard deadline remains the guarantee that it always ends.

**`P-55` — A partially failed batch reports counts, not filenames.** *"594 photos added, 6 could not be processed."* The uploader is told how many failed and nothing about which.

- **A partial success is still a terminal state**, so it satisfies `P-53` and lets this ruling report its final count. A batch that finished imperfectly is finished. *(Amended 2026-08-06 by `D-117` — this used to add "and unblocks sharing under `P-31`"; sharing is never blocked now.)*
- **Consistent with `P-38` and `P-54`:** the uploader gets a count they can reconcile against what they selected. This ruling declines to go further than that.
- **Accepted cost, and it is the largest accepted cost in the ingestion path.** With no filenames, a user whose batch partially failed cannot identify which photos are missing without comparing the gallery against their own folder by eye. For a 600-photo wedding that is not realistic, so the rational response is re-uploading the entire archive. `P-38` makes that safe — the successful photos are detected as duplicates and skipped before conversion or indexing, so nothing is corrupted and nothing is double-charged — but the user re-uploads gigabytes to recover a handful of photos, and learns nothing about why they failed.
- **Why it was ruled this way anyway:** per-photo status has to be tracked, stored, and surfaced through the whole ingestion path to name failures, and filenames are a weak handle regardless — a failed photo has no thumbnail, so `IMG_4471.jpg` still leaves the user hunting through a folder. The simpler contract was preferred over a partial improvement.
- **Reversible.** Adding filenames later changes a message and a stored field. It closes no doors.

**`P-54` — A ZIP is read for the photos sitting at its top level, and everything else is skipped. Subfolders are not opened. The requirement is stated up front, wherever a ZIP can be chosen: *"put all the photos directly in the ZIP — folders inside it are not opened."* Skips are reported only when the user could plausibly have known the file was there.**

> **Rewritten 2026-08-06 by `D-119`.** The original recursed into subfolders and flattened them, on the grounds that `P-14`'s single gallery gives folder structure nothing to become, so photos inside folders "must still be found". **Ruled the other way on build cost:** walking arbitrary nesting is real work — depth limits, path traversal in archive entry names, name collisions once flattened, ZIP-bomb shapes — and is not worth carrying in a portfolio project. The requirement is now stated to the user in advance instead of absorbed by the pipeline.

- **The instruction is the mitigation, and it must actually be shown.** Nothing else in the product tells the uploader this; if the line is dropped from the upload screen during build, the ruling becomes a silent trap. It belongs anywhere a ZIP can be selected — organizer upload and `P-36` attendee contribution alike.
- **A ZIP whose top level yields no photos says why.** *"No photos found — folders inside a ZIP aren't opened. Zip the photos directly."* This is the one case that would otherwise be a dead end: Arjun zips the *folder* rather than the photos inside it — the more common of the two habits — and would see only `0 photos added` with nothing to act on. **It costs nothing to detect:** the archive's entry labels are already read to find the top-level files, so nested entries are known without opening anything. An `if`, not a folder walk.
- **Accepted cost, stated plainly:** that re-zip is still a real re-do. Arjun exports from Lightroom into `Ceremony/` and `Reception/`, zips the parent folder, and **nothing is ingested at all**; the message tells him what to change, but he has to make a second archive. This is the deliberate trade: a rare re-do for him, against nested-archive handling nobody sees.
- **It partly solves the junk problem it used to fight.** `__MACOSX/` is a top-level *directory*, so its contents are now out of scope automatically. `.DS_Store` sits at the top level and still needs the known-junk list below.
- **Rejecting an archive that contains anything unexpected was disqualified, not merely rated worse.** Compressing a folder on macOS *always* inserts a `__MACOSX/` entry and `.DS_Store` files, and both are invisible in Finder. Strict rejection would mean the most common way a person produces a ZIP yields an upload that always fails, blaming files the user cannot see and cannot remove — an unfixable dead end for exactly the user `P-11` built ZIP upload for.
- **Two kinds of "not a photo", handled differently.** Operating-system metadata is dropped in silence and never mentioned, because a report of *"201 files skipped"* is technically honest and practically alarming, and invites a question with no useful answer. A video or a RAW file **is** reported, because the user selected it deliberately and would otherwise be left wondering where it went.
- **This is `P-38`'s principle reapplied.** The duplicate ruling required telling the uploader *"26 photos added, 4 were already in the event"* on the grounds that reporting the selected count is a lie and reporting only the stored count reads as failure. The same test governs here: report what the person can reconcile against what they chose, and stay silent about what they never knew existed.
- **Folder structure cannot survive, and this is forced rather than chosen.** `P-14` already established that the gallery is one continuous stream and that ingestion structure is never a browsing concept, so `Ceremony/` and `Reception/` have nothing to become. *(Rewritten 2026-08-06 by `D-119`. This bullet used to conclude "but photos inside them must still be found, which makes recursion mandatory." It does not follow — that photo names cannot be preserved is a reason folders are useless here, not a reason to open them. The requirement is stated to the uploader instead.)*
- **Consequence — file type is determined by content, not by file extension.** *(Stated as forced, not ruled separately.)* Extensions lie routinely, and `P-35`'s conversion step must know the true format before it can decode anything. A `.jpg` that is really a HEIC, or really a text file, has to be identified correctly or the pipeline fails downstream.
- **Accepted cost:** the known-junk list is a maintained list of patterns, so something novel will eventually be reported as a skipped file with an unfamiliar name. Harmless — one confusing line inside a success message, not a failure.

**`P-53` — An ingestion batch cannot be cancelled once started. Every batch has a maximum lifetime, after which it is marked failed.** An upload that turns out to be wrong runs to completion and is then cleared with `P-52`.

- **The gap cancellation would close is small.** `P-52` already removes anything that landed, in one gesture. The only photos cancellation additionally saves are those not yet processed — which the user is waiting on regardless. Cost plays no part: indexing is charged on arrival and is not refundable, so stopping a 600-photo batch partway saves at most about $0.60.
- **Cancelling in-flight distributed work is deceptively expensive.** Units of work are already dispatched and running in parallel, so cancellation is a race, and photos caught mid-flight land in half-states — converted but not indexed, indexed but not recorded. That is a poor use of a project whose real deadline is a 6-month credit clock.
- **A cancel that leaves processed photos behind was rejected outright.** It is not an undo, it is a partial that invites *"I cancelled it — why are 200 photos still there?"* If cancellation existed it would have to roll the whole batch back.
- **The timeout is the load-bearing half of this ruling, not a detail.** *(Re-founded 2026-08-06 by `D-117`.)* This bullet used to rest on `P-31`: a wedged batch would leave the event permanently unshareable. `P-31` no longer blocks sharing at all, so that justification is gone — **but the timeout stays**, now resting on `P-55`. `P-55` promises the organizer a final count of what succeeded and what failed, and a batch that neither finishes nor fails can never produce one; the organizer would watch an in-progress state forever, with `P-81` guaranteeing nothing ever tells them otherwise. Every batch must therefore reach a terminal state on its own, with no user action and no operator intervention.
- **Accepted cost:** a wrong upload stays visible in a live gallery until it finishes processing — minutes, for a large ZIP. `P-34` argued that *"the moment someone most wants photos gone is seconds after uploading them"*, and this ruling does make that person wait. Judged acceptable because the remedy is immediate once the batch lands, and because the case is rare.

**`P-14` — A second batch creates a new ingestion job, but photos land in the same single gallery.** Batches are an ingestion concept, never a browsing concept. Attendees see one continuous gallery regardless of how many uploads produced it. *(Carried from v1 as a correct decision.)*

---

## 6. Face matching

> **Rewritten 2026-08-03.** An earlier ruling discarded the selfie after every search and stored no biometric data. It was reversed deliberately: per-event, per-search selfie uploads were tedious, and they left match sets silently stale whenever a new batch arrived. The privacy guarantee changed shape rather than disappearing — see §7.

**`P-15` — Each user has one account-level face reference, set once and reused everywhere.**

- The user uploads **one selfie to their profile**. It is not per-event and not per-search.
- It is stored as a **private profile image, never visible to any other user** — not to other attendees, not to organizers.
- A face template derived from it is **retained**, which is what makes automatic matching possible.
- It can be **changed only in profile settings**. No event or gallery flow ever asks for a selfie.

**`P-16` — Matching is automatic and silent. The user is never asked to search.**

- Joining an event surfaces the user's own photos without any action from them.
- When new photos are added to an event the user has joined, their matches **update on their own**.
- There is no "Find my photos" button and no search step anywhere in the attendee journey.

*(This is the largest departure from v1, which treated face search as an explicit, user-initiated, per-event action.)*

**`P-17` — The profile selfie is optional. Without one, the user gets the complete product minus the "my photos" filter.**

Because of P-07, matching is a **convenience filter over a gallery the user already has full access to** — never a gate. A user who declines to upload a face still browses everything and downloads everything.

- **Why this matters:** it makes biometric consent a genuine opt-in rather than a de-facto requirement to use the app.
- **Second-order benefit:** matching accuracy stops being high-stakes. A missed match costs the user some scrolling, not access to their own photos.

**`P-18` — Face matching is rate-limited and cost-bounded.** Rekognition bills per operation, and automatic matching multiplies calls across every attendee each time a batch arrives. **Amended 2026-08-05 by `P-97`:** this is *not* user rate limiting. No user action triggers a search — `P-16` made matching automatic, `P-73` removed manual re-match, `P-79` removed per-event opt-out. The fan-out is driven by batches arriving, so the constraint is **pipeline concurrency** under `P-56`, bounded by `P-93`'s 100-attendee target and `P-40`'s photo cap. The constraint itself is locked; the concurrency figures belong with the ingestion design.

**`P-19` — The profile selfie is offered contextually, the first time photos are on screen.** Signup stays minimal and never asks for a face. A dismissible prompt offers it: *"want to see just the photos you're in?"*

The rule is **ask when the value is visible**, which lands at a different moment per role:

- **Attendee:** the first time they open an event gallery after joining.
- **Organizer:** the first time their own gallery fills, right after their first batch finishes ingesting — because the ZIP they uploaded will often contain photos of themselves too.

**Why:** the ask arrives when its value is self-evident, with photos already on screen — rather than demanding someone's face before they have seen anything, which is the worst possible moment for a consent request. Signup is never blocked or delayed by it.

**`P-20` — Changing the profile selfie applies to future photos only.** Existing match sets in existing events are left alone; the new face reference is used for photos added from that point forward.

- **Why, as originally recorded — now known to be factually wrong; see the `D-96` box below.** Recomputing every event on a profile edit was believed to fan out Rekognition calls proportional to (events joined × photos in each), triggered by a trivial user action and trivially abusable by editing a selfie repeatedly — "the single easiest way to blow `P-25`'s budget". **It is one call per event, not per photo.** The abuse case survives in weakened form (repeated selfie edits still cost one call per event per edit, against a 1,000/month free-tier allowance), but the budget threat does not.
- **Accepted cost, restated 2026-08-05 when `P-73` closed the mitigation.** A match set can end up computed against two different reference images. Both are the same person, so results stay correct — but they are uneven. The full cost is heavier than this bullet originally admitted: **a user who changes their selfie because matching was poor gets no improvement in any event that has stopped receiving photos**, and under `P-32`/`P-33` that is every event within 30 days of its last upload. "Future photos only" is not a delay — for a completed event it is *never*. `P-73` accepts this with no remedy.

> **`D-96` resolved 2026-08-05 against AWS primary sources. The caveat was correct: the original reasoning above was wrong.** Two facts were checked.
>
> **1. A collection search is one call, whatever the collection holds.** `SearchFaces` takes a `CollectionId` and a `FaceId` and "searches for matching faces in the collection the face belongs to", returning an array of matches ordered by similarity. The request has no `NextToken` and no pagination — one call evaluates the entire collection. `MaxFaces` (default behaviour capped at 4096) limits how many matches come *back*, not how much is scanned. **So matching one person against an event is one call regardless of whether the event holds 10 photos or 1,000.**
>
> **2. Searching by stored face ID bills exactly like searching by image.** `SearchFaces` and `SearchFacesByImage` are both **Group 1** operations at the same tiered rate (~$0.001/image for the first million), and both draw on the same 1,000-image/month Group 1 free-tier allowance. Submitting no image buys no discount. This answers `D-96`'s original question: **no, there is no cheaper stored-ID path.**
>
> **What this changes.** Recomputing one attendee across every event they have joined costs about **one call per event** — for a five-event attendee, roughly **$0.005**, plus one `IndexFaces` call for the new selfie. Not the budget threat `P-20` was ruled against. One caveat on that figure: it assumes one collection per event, which is a technology decision **not yet ruled** — a different collection layout changes the arithmetic.
>
> **`P-20` and `P-73` both stand — but no longer on this reason.** `P-73` was ruled by the user on interface coherence with `P-16`, which never depended on billing. `P-20`'s cost argument is now known to be false and has been rewritten above. Whether `P-20` should be *re-ruled* was put to the user as `D-111` and **confirmed — see `P-98`.**

**`P-98` — `P-20` stands after `D-96`, on structural grounds rather than cost.** Changing the profile selfie still applies to future photos only. The budget justification is withdrawn; the ruling is re-founded on the reasons that survive.

- **What the ruling now rests on.** Two things, neither economic. First, **the product has no operation anywhere that reaches backwards into a computed match set** — `P-20`, `P-68`, `P-73` and `P-99` all behave identically, and that single rule is the point. Second, `P-16` states there is no search step; an automatic recompute is a search, however it is triggered. Recompute was affordable and was declined anyway.
- **The accepted cost is now a chosen one, and should be read that way.** `P-20`'s standing admission — that an attendee who fixes a bad selfie gets no improvement in any event that has stopped receiving photos, which under `P-32`/`P-33` is every event 30 days after its last upload — was previously softened by "and recomputing would be expensive". **It would not be. It costs roughly $0.005 for a five-event attendee.** The inert remedy is being kept because a simpler system is worth more than the fix, not because the fix was unaffordable. That is a harder thing to defend and the spec should not pretend otherwise.
- **The abuse case survives, weakened, and is no longer load-bearing.** Repeated selfie edits would cost one call per event per edit against a 1,000-image/month Group 1 allowance — a nuisance, not the "single easiest way to blow `P-25`'s budget" `P-20` originally claimed. It is recorded here for accuracy, not as a reason.
- **This is the cheapest ruling in the spec to reverse, and that is worth knowing.** Nothing about `P-20` forecloses recompute later: the face vectors persist under `P-51`, the call is one per event, and the change would be additive. If real use shows the inert-remedy complaint actually biting, reopening this costs a background job and about a cent — unlike most rulings here, it is not a door that closes.
- **One figure is assumption, not fact.** The per-event arithmetic assumes **one Rekognition collection per event**, which is a technology decision that has not been ruled. A different collection layout changes it. Flagged rather than absorbed.

**`P-73` — There is no manual re-match. No control anywhere re-runs face matching for an event, and `P-20`'s cost is accepted without mitigation.** A user whose matches are poor has exactly one action available — set a better profile selfie — and it affects only photos that arrive afterwards.

- **What this means for a real person, stated without softening.** An attendee who appears in 40 photos and matches 6 of them, then corrects the selfie that caused it, keeps matching 6. There is no path back for that event, and the event is deleted before any circumstance changes. **The product's own remedy is inert in the case that motivates using it.**
- **Why no button, on the user's ruling.** A refresh control would be a search step, and `P-16` states there is none — the spec calls that its largest departure from v1. `P-73` keeps `P-16` literally true rather than adding a repair action that would need explaining as "not really a search". It also leaves nothing to rate-limit, keeping `D-35` free of a face-refresh case.
- **Automatic recompute was the other option and was declined.** It would have re-ruled `P-20` outright. Declining it keeps one rule for what a face-reference change does — forward-only — shared by `P-20`, `P-68` and now `P-73`. **The product has no operation that reaches backwards into computed matches**, which is a simpler system to reason about and to build than one with a single bounded exception.
- **Accuracy of the reference photo is now load-bearing at the moment of upload**, because it is the only moment that matters. `P-66`'s one-face check is the sole quality gate that exists, and it checks *count*, not quality — it cannot tell a clear selfie from a dim, half-turned one. Any interface work on `P-19`'s selfie prompt should carry this weight: the guidance shown when the photo is chosen is the entire remedy.
- **The cost premise behind this cluster was checked and did not hold — see the `D-96` box under `P-20`.** Recompute is about a cent per attendee across all their events, not a budget threat. `P-73` is unaffected: it was ruled on interface coherence with `P-16`, which never depended on billing. `P-20` was affected, because cost was its whole stated reason — the user re-looked at it under `D-111` and confirmed it on structural grounds instead (`P-98`). The forward-only rule this bullet relies on therefore still holds.
- **Reversible in one direction only, and worth knowing which.** Adding a refresh later is easy. Nothing depends on its absence except `P-16`'s wording. But matches never computed are not recoverable after `P-33` deletes the event — **the data this ruling declines to improve has a 60-day life and then is gone.**

**`P-79` — There is no per-event opt-out from face matching. The face reference is account-level under `P-15` and applies to every event the user joins; the only control is the `P-64` filter toggle, and the only opt-out is `P-17`'s global one.**

- **A per-event opt-out would protect a user from their own button.** §7 point 3 guarantees no match set is ever visible to anyone else and no interface accepts a search for another person. Matching therefore produces nothing any other user can see — so the only thing an opt-out suppresses is a filter the user can simply decline to switch on.
- **It would not deliver the privacy it appears to.** `P-42` indexes every face in every photo regardless of uploader, so a user who appears in other people's photos is in that event's collection whether or not they opt out. The control would stop the *search* while feeling like it stopped the *indexing* — the same looks-real-but-isn't failure `P-67` rejected in camera-capture, `P-71` in the consent notice, and `P-42` in the consent checkbox.
- **It would add a fourth filter state.** `P-69` already carries active, absent and frozen. A per-event suppression on top of an account-level reference (`P-15`) is state the product has deliberately avoided everywhere else.
- **Accepted cost:** a user who wants matching in general but not in one specific event cannot express that. Under `P-16` their matches for that event are computed silently and sit there, unviewed but existing. Their only remedies are the global `P-17` opt-out — delete the selfie, losing matching everywhere — or simply never opening the filter.

**`P-80` — The similarity threshold is fixed at 80 and exposed to nobody.** Not organizer-configurable, not attendee-adjustable. Changing it is a code change.

- **Low stakes by `P-07`.** A false match shows a user a photo they already have full access to; a missed match costs them some scrolling. The dial cannot affect access, only filter quality.
- **Organizer configuration was the weakest option.** It would let one person tune a knob affecting every attendee's private filter, with nothing to judge it by — `P-15` keeps profile selfies invisible, so an organizer cannot see the inputs or the results of the thing they would be tuning.
- **An attendee slider collides with `P-73`.** Match sets are computed once and never recomputed, so a slider could not re-run matching. It would have to re-filter a stored list by score, which means **persisting a similarity score per match** — a data-model obligation created solely to serve a control nobody asked for. It would also reintroduce the search-tuning step `P-16` exists to delete.
- **Accepted cost:** 80 is inherited from v1 and has never been measured against real photos. If it proves too loose or too tight there is no runtime remedy and no per-event escape — it is a redeploy. Recorded in §10's tuning table.

**`P-69` — The "my photos" toggle renders whenever the user has a face reference *or* an existing match set for that event. A match set with no face reference behind it is frozen, and the interface must say so.** This amends `P-64`'s rendering condition.

- **It is what makes `P-68` mean anything.** Retaining match sets while hiding the only control that displays them would keep biometric-derived data for no user and no purpose — the outcome `P-68` was ruled against. Either the sets are reachable or retaining them was pointless.
- **`P-17` is untouched.** A user who never set a selfie has no reference and no match set, so no toggle appears and they still get "the complete product minus the my-photos filter". This clause only affects someone who *had* a reference and removed it.
- **The frozen state must be visible, and this is the load-bearing half of the ruling.** The set no longer grows: `P-68` stopped future matching, so photos arriving under `P-16` will never join it. A filter that silently stops updating is precisely the failure `P-16`'s automatic matching exists to prevent, so the toggle has to state that matching is off and that the set is fixed — with the path to restoring it being to set a new profile selfie, which under `P-20` resumes matching for future photos only.
- **Accepted cost:** the product now carries a third state for the filter — active, absent, and frozen — where `P-64` alone had two.

**`P-68` — Deleting the profile selfie deletes the face reference and the face template, and stops all future matching. Match sets already computed are left in place.** Deletion is forward-looking: it ends the product's ability to identify the user in anything new, and does not reach backwards into work already done.

- **It is the mirror image of `P-20`, and consistent with it.** That ruling established that changing the face reference applies to future photos only and never recomputes existing match sets. Deletion behaves the same way — the reference stops being used from that moment, and history stands. The product now has one rule for what a face-reference change does, rather than two opposite ones.
- **It avoids an irreversible destruction that `P-20` would make permanent.** Under the alternative, deleting and re-uploading the identical photo five minutes later would restore nothing, because `P-20` forbids the recompute that would rebuild those match sets. A user correcting a mis-tap would permanently lose their matches across every event they had joined. This ruling removes that trapdoor entirely.
- **Asking the user at deletion time was rejected.** `P-24` establishes that the product does not put policy questions to people, and this would put one at the worst possible moment — someone deleting their face data being handed a second question about their face data, where the reassuring-sounding answer is not obviously the safe one.
- **Accepted cost, stated plainly:** a stored record continues to say which photos a user appears in, after that user has taken the only action the product offers for withdrawing from face matching. §7 point 5 remains true as written — the template *is* deleted — but the withdrawal is narrower than a reader might assume, and §7's wording must not imply otherwise.
- **Resolved consequence — `P-69`.** `P-64` rendered the toggle only when a face reference existed, which would have left these retained match sets unreachable. `P-69` amends that condition so the toggle survives, and requires the frozen state to be shown.

**`P-66` — A profile selfie must contain exactly one detectable face.** Zero faces is rejected with a clear message; two or more is rejected with an equally clear one. Nothing is guessed.

- **Automatically choosing between several detected faces was rejected outright, not merely rated lower.** Picking the wrong one produces exactly the outcome §7 point 3 promises cannot happen — one person receiving another person's photos — and produces it invisibly, with no error and nothing for the user to notice. Weeks of wrong matches would follow with no way to diagnose them. A loud refusal is far better than a silent wrong answer.
- **A face picker was considered and cut on ceremony.** Detecting, cropping, rendering and selecting among faces is a real piece of interface built for a case that one sentence of guidance resolves. `P-24`'s instinct applies.
- **The cost to the user is small because of where this lives.** `P-15` puts the selfie in profile settings, never in an event flow, so a rejection blocks nothing and there is no time pressure — the user crops the photo or takes another. "A photo of just you" is what the word selfie already means.
- **Cost is negligible:** one face-detection call per selfie set or changed, roughly $0.001, on an action that happens once per user in most cases.
- **Accepted cost:** someone whose only good photo of themselves includes another person must crop it before uploading.

**`P-65` — An event opens on the user's own photos whenever they have a face reference and their matches are ready. Otherwise it opens on the full gallery.** The `P-64` toggle starts on, not off.

- **This makes `P-16` literal.** That ruling promises *"joining an event surfaces the user's own photos without any action from them"*, and any other default would have left it unfulfilled — the matches would exist but wait behind a control the user had to know to press. `P-01`'s entire pitch is *"here is my face — show me every photo I appear in"*, and this is the moment that sentence either happens or does not.
- **It resolves a real conflict between two locked rulings rather than overruling either.** `P-16` and `P-21` disagreed about what an event opens on. The split is now by readiness: **`P-21` governs until matches exist** — no face reference, or matching still running, means the full gallery opens immediately and stays fully usable — and **`P-16` governs the moment they do.** Neither ruling is rewritten.
- **The first visit is unaffected, and this is forced.** `P-19` offers the profile selfie *"the first time they open an event gallery after joining"*, so at first open there is by definition no face reference. Every first visit opens on the full gallery regardless of this ruling; the behaviour here begins on the return visit.
- **A user with no selfie is untouched.** `P-64` does not render the toggle for them, so `P-17`'s promise of "the complete product minus the my-photos filter" is unchanged.
- **Accepted cost, and it is a significant one:** a user who has a face reference but appears in no photos — anyone who held the camera rather than standing in front of it — opens a 300-photo album onto an **empty screen**. In the collaborative outing of §2 that is not a rare user. This was ruled with the case in view.
- **Obligation that follows from that cost:** the empty filtered state cannot be a bare blank grid. It must say plainly that the filter found no photos of them, must show that the filter is on and reversible, and must offer the full gallery directly. Under `P-22`'s test, a user with full rights to 300 photos being shown nothing, with no explanation, is indefensible — the ruling is only safe if this state is designed deliberately.

**`P-64` — "My photos" is a filter toggle over the single gallery, not a tab and not a separate screen.** One grid, one scroll, one dataset; a control switches between every photo and the user's own matches.

- **It is the only presentation that stays honest about `P-07`.** Tabs and separate sections both imply two collections of photos. There is one. Presenting the feature as literally what it is — a filter — means the interface cannot drift out of step with the permission model as the product changes.
- **It is what makes `P-17` true.** That ruling promises a user without a profile selfie "the complete product minus the my-photos filter". With a toggle, the control simply is not rendered and there is no hole where it used to be. A tab bar would have to either show a tab that cannot be used or collapse to a single pointless tab — furniture built around an absence.
- **An empty filter reads correctly; an empty tab lies.** A user who has a selfie but appears in no photos sees an empty grid with the toggle visibly on, which says *"nothing matched this filter"* and is obviously reversible. An empty tab says *"you have no photos"* — a heavier claim, and a false one, since `P-07` gives them full access to every photo in the event.
- **It absorbs `P-21`'s timing.** Matches populate after the gallery is already usable, so the toggle can show a working state while the gallery beneath it stays fully browsable. A tab that is empty and then is not looks like a defect.
- **Accepted cost:** a toggle is less prominent than a labelled destination, so the product's signature capability sits behind a control rather than announcing itself. This is what makes the default view a consequential decision in its own right.
- **`P-69` amends this rule:** the toggle renders when the user has a face reference **or** an existing match set for the event. Without `P-69`'s clause, `P-68`'s retained match sets would be unreachable.

**`P-21` — Joining an event never blocks on matching.** The full gallery is usable immediately; the "my photos" view shows a working state and populates when ready.

- **Why:** P-07 already grants full access to every photo, so making a user wait on a computation they never requested, to see photos they already have rights to, contradicts P-16's silent matching.

---

## 7. The privacy position

The product stores biometric data. Stated plainly rather than softened — and defensible for specific reasons:

1. **The guarantee is directional, not absolute.** *(Rewritten 2026-08-04 — the original claim was false.)* Faces in event photos **are** indexed, including those of people who are not users and never consented, exactly as in v1. This is unavoidable: retrieval cannot find "photos containing this person" without first analysing the faces in every photo. What Glimpses guarantees instead is the *direction* of search — every search runs against a face the searcher supplied themselves, and **the product offers no interface for searching by anyone else's face.** A non-user's vector exists only inside one event's collection, is never linked to a name or an account, and is destroyed automatically when the event is archived or deleted (P-32, P-33) — a hard expiry of roughly 60 days requiring action from nobody. **That expiry is also the only remedy** — `P-70` gives a non-user no way to request removal, and the spec does not claim otherwise.
2. **It is optional** (P-17). Declining costs the user a convenience filter, nothing more.
3. **There is no way to search for another person, and no result set is ever shared.** No screen, no control, and no API accepts "find photos of that person". A user sees only matches against their own profile face; an organizer has no face search over their attendees; nobody can see anybody else's match set. **What this does not claim** — see P-67 — is that the face a user supplies is verifiably their own. Glimpses cannot establish that, and does not pretend to.
4. **The profile selfie is never shown to anyone else.**
5. **Deleting the profile selfie deletes the face template.** A real product feature, not a support request — and, since `P-74` removed account deletion, **the only withdrawal action in the product.** **Scope, stated rather than glossed:** it destroys the template. It does *not* reach backwards into match sets already computed — see `P-68` — and it does not remove the account, the display name, the email address, or `P-86`'s attribution on photos already uploaded, none of which can be removed at all. Match-set records expire with the event under `P-33`. *(Amended 2026-08-06 by `D-125`.)*
6. **These are guarantees about faces, not about anonymity between users.** *(Added 2026-08-06 by `P-86`.)* Uploaders are identified by name and email on their photos, as in any shared album. Points 1–5 are unaffected: no searching by another person's face, no shared match sets, no visible profile selfies.

**`P-67` — Glimpses cannot verify that a user's profile selfie is a photo of themselves, and this limitation is stated rather than defended against.** A user who sets their face reference to a photo of another person will be shown that person's matches. This is accepted, deliberately.

- **What it does and does not grant.** It grants **no access whatsoever**: `P-07` already gives every admitted attendee every photo in the event, so the impersonator could find that person by scrolling. What it grants is *efficiency* — "which of these 1,000 photos contain this specific person", answered instantly and repeatedly. It is a surveillance capability, not an access breach, and it opens no door `P-07` had not already opened deliberately.
- **§7 points 1 and 3 were rewritten rather than defended.** This is the second time a §7 guarantee has been found to claim more than the system delivers, and it was handled the same way as the first: make the words true. The honest guarantee — no interface to search by another person's face, no organizer search over attendees, no shared match sets, profile images never visible, non-user vectors destroyed with the event — remains strong. It simply no longer asserts something unenforceable.
- **Liveness detection would genuinely close this and was rejected on cost.** Verifying a live person at capture time is a separate paid service, an SDK integration, and a multi-step flow — the largest technical addition anywhere in this spec — for a project whose binding constraint is a 6-month credit clock. `P-22` scopes this as portfolio-grade with real privacy features, not compliance machinery, and `P-17` made the whole face system optional precisely so it would not have to carry that weight.
- **Requiring camera capture *without* liveness detection was rejected as worse than doing nothing.** It imposes the full cost on every honest user — no using an existing photo — while stopping only an attacker unwilling to hold a phone up to a camera, and it is defeated outright by a virtual camera on desktop. A defence that looks real and is not is more dangerous than a stated limitation, because people rely on it.
- **Reversible.** Adding liveness verification later invalidates nothing; existing face references would simply predate it.

**Consent obligation:** because a template is retained, uploading a profile selfie must be an explicit, informed action that states what is stored and how to remove it. It cannot be a silently-required onboarding step.

**`P-70` — A person who appears in event photos but is not a user has no removal path. There is no in-product route, no stated out-of-band contact, and no advertised remedy.** Their face vector is destroyed with the event's collection under `P-32`/`P-33` — roughly 60 days — and that expiry is the only thing that happens.

- **The remedy that does exist is the organizer's, and it is undocumented.** Under `P-44` the organizer can delete any photo in their event, and deleting a photo deletes its face vectors (`P-52`). A non-user who knows someone in the event asks them; that path needs nothing built. What `P-70` declines to add is a route for someone who knows nobody — and after `P-71` the product never tells the organizer that the remedy exists or that faces are indexed at all. **Deletion is a capability an organizer must infer, not one they are informed of.** Stated here so this bullet is not read as a guarantee.
- **Removal is barely expressible even when requested.** To delete one non-user's vectors specifically, the product would have to *find* them — which means submitting a photo of their face and searching the collection. That is precisely the capability §7 point 3 says does not exist, built for the first time in order to serve a privacy request. The alternative reading of "removal" is deleting whole photos, which is `P-44` and already belongs to the organizer. **There is no third thing to build**, which is why a request flow would have been surface without substance.
- **Why an out-of-band contact was rejected too.** It was the recommendation and was overridden. The argument for it was honesty rather than capability — it would have ratified the arrangement `P-41` already assumes. The argument against, which ruled: publishing an address commits the project to answering it, and the honest answer in almost every case is "wait ~60 days." A stated channel that reliably delivers nothing is the same failure mode `P-67` rejected in camera-capture-without-liveness — **a remedy that looks real and is not.**
- **Accepted cost, stated without softening.** Glimpses holds biometric data derived from people who never consented and offers them nothing on request. This is the least defensible position in the spec against `P-22`'s test. What limits it: the vector is unlabelled and linked to no name or account, it exists inside one event only, it can never be searched for by anyone (§7 point 3), and it expires on a hard clock requiring action from nobody. **The exposure is bounded and self-terminating — it is simply not answerable on demand.**
- **`P-41` is what forces the shape.** With no platform administrator, any removal path is a human being reading mail and using the AWS console. `P-70` declines to advertise that as a product feature.
- **Reversible.** Adding a privacy contact page later invalidates nothing and requires no code — it is a static page and a runbook. This ruling is the cheapest one in the spec to revisit.

**`P-71` — No face-indexing notice is shown to organizers or uploaders anywhere in the product.** Creating an event is a name and a tap. Nothing in any flow states that photos are analysed for faces, that non-users are indexed, or that deletion removes face data.

- **This is disclosure, not consent, and the consent half was already settled.** An organizer cannot consent on a stranger's behalf, so no notice was ever going to make `P-42`'s position more defensible. `P-42` rejected a consent checkbox as theatre for exactly this reason; `P-71` declines the informational version as well.
- **`P-67`'s consent obligation is untouched and still binding.** That governs the user's *own* profile selfie — an explicit, informed action stating what is stored and how to remove it. A user consenting about their own face is a different thing from an organizer being told about other people's, and it remains a real feature.
- **The recommendation was a persistent notice and was overridden.** The case for it: `P-70` leaves `P-44` as the only remedy in the system, and a notice was the only thing that would make it discoverable. The case against, which ruled — a notice changes no behaviour and grants no capability. It cannot stop the indexing, cannot be acted on by the person affected, and does not alter what the organizer is able to do. It is text asserting good intent, which is what `P-42` already refused to ship.
- **Accepted cost, compounding with `P-70`.** Glimpses performs biometric analysis on non-consenting people, offers them no removal path, and informs nobody in the product that any of it happens. Against `P-22`'s test — *"could this be pointed at a real wedding without embarrassment?"* — **this pair is the weakest point in the spec, and no other ruling is close.** The bounding facts from `P-70` still apply: unlabelled vectors, one event only, unsearchable by anyone, destroyed on a ~60-day clock. They limit the exposure; they are not a defence of the silence.
- **What fills the gap is outside the product.** `P-72` rules a single public privacy page. In-product disclosure remains nil: no organizer, uploader or attendee is told anything about face indexing inside any flow they use. The page is reachable, not surfaced. `P-71` means the product currently discloses face indexing in no location whatsoever.
- **Reversible, and the cheapest reversal in the spec alongside `P-70`.** The notice is one paragraph of copy. Nothing depends on its absence.

**`P-72` — Glimpses publishes one public, plain-language privacy page, reachable without an account and linked from the signup screen and the site footer. It is linked, never blocking — no acceptance step, no checkbox.** It is the only disclosure of face indexing anywhere, and the only artifact in the product a non-user can reach.

- **What it must state**, in plain sentences rather than legal register: photos uploaded to an event are analysed to find faces; this includes people who are not users; a face record is linked to no name and no account; it exists inside one event only and is never searchable by anyone else's face (§7 point 3); it is destroyed with the event under `P-32`/`P-33`, roughly 60 days; a user's own profile selfie can be deleted at any time, which deletes the face template (§7 point 5). **It must also state that accounts cannot be deleted, and that a display name and email address stay visible on photos the user uploaded until the event expires** — *(added 2026-08-06 by `D-125`)*. This inherits the disclosure obligation `P-74`'s deletion screen used to carry; with that screen gone, this page is the only place the fact can be told.
- **Why the reach matters more than the words.** Everything else in Glimpses sits behind `P-04`'s account requirement and `P-07`'s admission. The person with the strongest interest in this information — someone photographed at an event who does not use the product — cannot get behind either. A public page is the only reachable surface, and it is why this was ruled where `P-71`'s in-product notice was declined: `P-71`'s audience already had every capability, this one has none.
- **It carries no contact address, deliberately.** `P-70` stands unchanged. The page describes what is held and offers no channel to ask about it — an unusual shape for a privacy page, recorded here so it reads as a decision rather than an omission. Its honest function is to make `P-70`'s bounding facts *knowable* by the affected person, not to give them a remedy they do not have.
- **It is not a terms of service, and not a legal document.** `P-22` puts formal compliance machinery out of scope; this is six or so sentences of description. If it ever needs a lawyer to read it, it has drifted.
- **Live maintenance obligation — the page states a duration `D-98` has not ruled.** The ~60-day figure comes from `P-33`'s current inactivity and deletion windows. **`D-98` is still open on those durations**, and any change to them changes this page. Treat the page as coupled to `P-32`/`P-33`, not as static copy written once.
- **This is the third and final ruling in the disclosure cluster** (`P-70`, `P-71`, `P-72`). Read together: no removal path, no in-product notice, one public page. The exposure `P-70` accepted is now at least *stated somewhere a non-user can find it*, which is the whole of what changed.

**`P-22` — Portfolio project, designed to be real-capable.** Consent notices and a face-data deletion path are built as genuine features. Heavyweight compliance machinery — formal DSAR workflows, audit logging, a DPO process — is out of scope.

The test for any privacy question: **"could this be pointed at a real wedding without embarrassment?"** — not *"is this GDPR-certified?"*

---

## 8. Permission model

**`P-48` — There are two roles but five membership states, and every permission check is scoped to a `(user, event)` pair.**

P-39 and P-41 reduced the product to two roles — organizer and attendee. That is true but insufficient on its own: a user stands in one of **five states** relative to any given event, and the two that are not roles are where the security-relevant bugs live.

| State | Meaning |
|---|---|
| `NON_MEMBER` | Authenticated, but has no relationship to this event |
| `PENDING` | Submitted the code, waiting in the lobby (P-10) |
| `ATTENDEE` | Admitted |
| `ORGANIZER` | Created the event (P-39 — exactly one, never transferred) |
| `BLOCKED` | Denied or ejected (P-29) |

### One modifier that sits above roles

It is evaluated **before** any role check.

| Modifier | Effect |
|---|---|
| Event is `ARCHIVED` | Every write is denied, for every state, **including the organizer** (P-32) |

*(Amended 2026-08-06 by `D-117`. There were two modifiers; the second — "a batch is in flight → share controls are hidden" — was removed when `P-31` dropped its block. Ingestion state no longer affects permissions anywhere.)*

### Event

| Action | `NON_MEMBER` | `PENDING` | `ATTENDEE` | `ORGANIZER` | `BLOCKED` |
|---|---|---|---|---|---|
| Submit an access code | ✓ | — | — | — | ✗ P-29 |
| See event identity | ✗ | ✓ P-28 | ✓ | ✓ | ✗ |
| See the gallery | ✗ | ✗ P-28 | ✓ P-07 | ✓ | ✗ |
| See / share access code and QR | ✗ | ✗ | ✓ P-45 | ✓ P-31 | ✗ |
| Change settings | ✗ | ✗ | ✗ | ✓ | ✗ |
| Archive or delete the event | ✗ | ✗ | ✗ | ✓ P-32/P-34 | ✗ |
| Leave the event | — | ✓ P-46 | ✓ P-46 | ✗ P-39 | — |

### Photo

| Action | `ATTENDEE` | `ORGANIZER` | Condition |
|---|---|---|---|
| View | ✓ | ✓ | P-07 — admission grants everything |
| Download | ✓ | ✓ | shape open, D-51/D-52 |
| Upload | ✓ **only if** `contributionPolicy = ATTENDEES_CAN_ADD` | ✓ always | must be admitted, P-43 |
| Delete | ✓ **only if they uploaded it** | ✓ any photo in the event | P-44 |
| See who uploaded it | ✓ name + email | ✓ name + email | P-86 — persists after deletion/ejection, P-99 |
| Filter or select by uploader | ✗ | ✗ **never** | P-86 obligation — would recreate what P-52 refused |

### Membership

| Action | `ATTENDEE` | `ORGANIZER` |
|---|---|---|
| See pending join requests | ✗ | ✓ |
| Approve or deny | ✗ | ✓ P-29 |
| Eject an attendee | ✗ | ✓ P-29 |
| See the attendee list | ✗ P-83 — but uploaders are identifiable via P-86 | ✓ display name + email — P-82 |

### Profile and face

This table contains no roles at all, which is the point.

| Action | Owner | *Anyone* else, organizer included |
|---|---|---|
| View the profile selfie | ✓ | ✗ **always** — P-15 |
| Set or change it | ✓ | ✗ |
| Delete the selfie and face template | ✓ | ✗ — §7 |
| See a match set | ✓ own only | ✗ — §7 point 3, no match set is ever shared |

### `P-49` — Order of evaluation

Every check runs these in order. **The order is part of the specification**, because getting it wrong is how privilege escalation happens.

```
1. Is the event ARCHIVED?             → deny all writes, before considering role
2. Is this user BLOCKED here?         → deny everything
3. Load membership for (user, event)  ← from storage, never from the token
4. Check the role
5. Check the resource condition       ← e.g. "did this user upload this photo?"
```

### `P-50` — Four invariants

1. **Every check takes `(userId, eventId)`.** P-05 scopes roles per event, so no permission is ever answerable globally.
2. **Role is re-read from the membership record on every request and never cached in a token claim.** A user who is organizer of event A and attendee of event B would otherwise carry organizer rights into B. **This is the escalation bug this design is most exposed to.**
3. **"Is this user admitted to this event?" is the most security-critical check in the product**, because P-07 makes admission grant everything at once.
4. **Photo deletion requires loading the photo first.** P-44's ownership condition cannot be inferred from a role, so there is no shortcut that skips the read.

### `P-47` — Ejection removes the person, not their photos

Photos contributed by an ejected attendee remain in the event. The organizer deletes any they do not want, using the same rights P-44 already grants them over every photo.

- **Why not delete automatically:** ejection covers two unrelated situations — moderating someone who uploaded junk, and a personal falling-out. Automatic deletion serves the first and destroys the second, taking genuine photos away from uninvolved people irreversibly.
- **Accepted cost:** where ejection *was* moderation, the organizer must clear the photos manually. This makes **D-34** — individual and bulk photo deletion — load-bearing rather than cosmetic.
- **Accepted cost:** once `BLOCKED`, the person loses the P-44 right to delete their own photos. Preserving it would mean granting a blocked user an API path back into the event, which is exactly what P-29's blocklist exists to prevent.

---

## 9. Event lifecycle

An event has two states and one terminal exit. There is no draft, no un-archive, and no resurrection.

```
   create
     │
     ▼
  ACTIVE ──── organizer archives ────► ARCHIVED ──── retention ────► DELETED
     │        or 30d inactivity            │           expiry          ▲
     │                                     │                           │
     └───────── organizer deletes ─────────┴───────────────────────────┘
```

**`P-23` — `ACTIVE` is the only state that accepts change.** Uploads, joins, contributions, and matching all happen here and nowhere else.

**`P-31` — An `ACTIVE` event is always shareable. There is no state in which the access code, QR or share controls are hidden.** Ingestion is irrelevant to sharing: the code is visible before any photo has been uploaded, while a batch is processing, and after it finishes.

> **Rewritten 2026-08-06 by `D-117`.** *(Previously rewritten 2026-08-04 by `D-99`.)* The 2026-08-04 rewrite removed the deadlock — the original rule gated sharing until the *first batch had finished*, so an organizer whose attendees are the only source of photos could never share the code, so no first batch could ever arrive — but it kept one block: sharing was hidden for the duration of an in-flight batch. `D-117` removed that too. **Both rewrites failed the same way: the rule was checked against the broadcast case only.**

- **Why the remaining block had to go.** `P-94` sized the in-flight window at up to **thirty minutes** for a 1,000-photo batch. Arjun uploads at the venue and cannot hand out the code for half an hour. Priya's trip has someone uploading nearly all the time, so the code flickers in and out of existence for reasons no one can predict — the same shape of failure `D-99` fixed, only intermittent instead of permanent.
- **The rule had inverted itself.** It permitted sharing a **completely empty** event (with a note) while forbidding sharing a **partly full** one. The hazard it named — a guest landing on an empty gallery and never returning — was worse in the case it allowed than in the case it blocked.
- **`P-16` does the work the block was doing.** Photos and matches appear automatically as they arrive, so Meera joining mid-batch watches the gallery fill in front of her rather than sitting at a fixed empty screen.
- **Accepted cost:** a guest who joins mid-batch sees a partial gallery and is told nothing about why. `P-81` forbids notifying her, and `P-24` forbids stopping her with ceremony, so the product simply shows fewer photos for a while. This is the deliberate choice; it is not a gap to be patched later with a banner.
- **Sharing an empty event still shows a note rather than a block:** *"No photos yet. Anyone who joins will see an empty gallery."* Informative, not obstructive — consistent with `P-24`. This is now the only sharing-related message in the product.
- Implemented as plain visibility on an `ACTIVE` event, **not** as a separate DRAFT state — no publish step exists, because a publish step is exactly the ceremony `P-24` rules out, and organizers would forget to press it.
- **Design obligation:** nothing else may reintroduce a share block. `P-53`'s batch timeout is no longer justified by this rule (see `P-53`), so a future change to batch handling must not quietly re-derive one.

**`P-32` — Archiving makes an event permanently read-only. It cannot be undone.**

| | `ACTIVE` | `ARCHIVED` |
|---|---|---|
| View and download existing photos | Yes | **Yes** |
| New attendees join | Yes | No |
| Upload or contribute photos | Yes | No |
| Face matching runs | Yes | No |
| Rekognition collection exists | Yes | **Deleted** |

- **Why permanent:** deleting the face collection on archive is the entire point — it stops the ongoing cost. Allowing un-archive would mean rebuilding that collection by re-indexing every photo, so a reversible archive saves nothing and the feature loses its purpose.
- **Attendees keep their access.** Archiving must never take away photos people were promised.
- **Accepted cost:** an accidental archive is unrecoverable, so it requires a genuine confirmation, not a casual one.

**`P-33` — Events auto-archive after inactivity, and archived events are eventually deleted.**

- **`P-77` — Durations confirmed 2026-08-05: archive after 30 days of no activity, delete 30 days after that.** An untouched event dies roughly **60 days** after its last activity. No longer a proposal.
  - **Ruled as a product and privacy question, not a cost one.** Storage for a 1,000-photo event is about **2¢ per month**, and indexing is a one-time charge retention cannot recover — so no plausible duration moves the budget. Longer retention was rejected on `P-70`/`P-72` (the privacy page states this figure, and "about two months" is a materially different claim from "about four", and would outlive `P-25`'s 6-month credit window). Shorter was rejected because remembering an event a month later is ordinary behaviour, not an edge case.
  - **Archiving is not a loss.** `P-32` keeps viewing and downloading alive, so the 30-day mark stops *uploads* only. The real deadline is deletion at 60 days.
  - **`P-78` — "Activity" means a photo being added, and nothing else.** Viewing, downloading, joining, and organizer visits do not reset the clock. An event archives 30 days after its **last upload**, whoever is still looking at it.
    - **This is what makes `P-77`'s number a bound rather than a description.** Had views counted, one person opening the gallery each month would keep the event — and every non-user's face vector in it — alive indefinitely, while `P-72`'s privacy page told them it expires in about two months. That would be a published claim the system does not honour, which is the failure mode §7 has already been corrected for twice.
    - **`P-70`'s defence depends on this clause specifically.** Its whole answer to a non-user is an expiry requiring action from nobody. An expiry any stranger can postpone by scrolling is not that.
    - **Cheap because archiving is not a loss.** `P-32` keeps viewing and downloading alive, so an event that archives while people are still looking takes nothing away from them — it only closes uploads.
    - **Accepted cost:** a genuinely long-running album — a trip that keeps going, a season of matches — archives mid-life and cannot be un-archived (`P-32`). The organizer's recourse is a new event. `P-40`'s 5-active-events cap makes that a real, if small, constraint.
- **Why:** without automatic removal, stored photos and retained face vectors grow without limit. This is the only rule that bounds either.
- **Reasoning corrected 2026-08-04.** This rule previously claimed storage was *the* binding cost under P-25. Measured, it isn't: Rekognition indexing is roughly **6× the cost of storing a photo for its entire 60-day life**, and indexing is a one-time charge paid on arrival that **retention cannot claw back**. Retention still earns its place — it caps S3 growth and ongoing face-vector storage — but it is a smaller cost lever than originally stated. The photo-count limits in P-40 are what actually bound the dominant cost.
- **Obligation:** because this means an untouched event dies roughly 60 days after its last activity, the lifetime must be stated plainly at creation and warned about before each transition. A product that silently deletes photos is indefensible under P-22.

**`P-34` — The organizer can permanently delete an event at any time, with confirmation.** Photos, face data, and match sets all go.

- **Why:** required by P-22. "I uploaded photos I shouldn't have" needs an immediate, complete answer, and archive is not one. Deletion is available directly from `ACTIVE` — not gated behind archiving first — because the moment someone most wants photos gone is seconds after uploading them.

---

## 10. Design principles

**`P-24` — No configuration questions at event creation.** The organizer supplies a name and is done. Every dial takes a default chosen to fit the majority case. Settings are changed later, by the minority who need restrictions, in an event settings screen.

- The organizer is never asked a policy question, and never asked to characterise their own event ("who's taking the photos?", "what type of event is this?"). Those questions push classification work onto someone who just wants to share photos from a party.
- **Consequence:** defaults must be genuinely right for most events, because most organizers will never change them.

**`P-26` — The locked defaults:**

| Setting | Default | Why this default |
|---|---|---|
| `joinPolicy` | `OPEN` | The access code is already a gate. Requiring approval by default would add a manual step to every casual event. |
| `contributionPolicy` | `ATTENDEES_CAN_ADD` | Optimised for the *less engaged* persona. A photographer running a wedding is deliberate and will happily flip one setting; a group of friends on a trip will never find the setting and would silently get a product that fails to do the one thing they wanted. |
| `similarityThreshold` | 80 | **Locked by P-80** — exposed to nobody; a code change. Carried from v1 and never measured against real photos. Low stakes under P-07 — a filter-quality knob, not an access decision. |

**Accepted cost of the contribution default:** a photographer's curated gallery can accumulate guest phone snaps before they notice the setting exists. Judged less damaging than silently breaking the collaborative-outing case, which is half the product's reason for existing.

**`P-25` — Must operate within the AWS Free Tier credit allowance.** A hard budget constraint that shapes product decisions, not just technical ones: retention, whether emails are sent, image resolution served, and whether a custom domain exists are all downstream of it.

> **Reasoning corrected 2026-08-04.** AWS restructured the Free Tier on 15 July 2025. The per-service allowances this rule originally assumed — 5 GB S3, 1,000 Rekognition images/month for 12 months — no longer apply to new accounts. The project runs on the current model: **$200 in credits, valid 6 months** from account creation, with no ongoing per-service allowance.

- **Measured costs** (S3 $0.023/GB/mo · Rekognition Group 1 $0.001/image · face vectors $0.00001/face/mo): a 1,000-photo wedding costs **~$1.26 for its entire 60-day life**; a 2,000-photo conference ~$2.58. The $200 allowance covers roughly **180 events**.
- **The binding constraint is time, not money — *at the intended workload*.** Credits will not be exhausted at `P-93`'s scale; the 6-month expiry arrives first, after which the account converts to paid or closes.
- **`P-40` removed the guard that kept that true, and this is stated rather than glossed.** *(Added 2026-08-06.)* With no photo cap and no per-organizer event cap, nothing in the product bounds spend. Indexing is billed **on arrival** at ~$0.001/image and is ~6× the whole-life storage cost, so `terraform destroy` recovers nothing already spent, and `P-81` means no signal precedes it. The $200 covers ~180 events at `P-93`'s shape and can be consumed far faster by a script. **This is an accepted portfolio-deployment risk, ruled deliberately, not an oversight** — the mitigation available and declined was keeping `P-40`'s caps as Terraform variables.
- **Indexing, not storage, is the dominant cost** — see P-33.

---

## 11. Decision log

| Date | Ruling | Note |
|---|---|---|
| 2026-08-06 | P-100 | **New ruling (D-126) — item 4.** An upload in progress shows progress on screen, and says when photos are being retried and that this is why it is slower. **Ingestion never depends on the uploader staying**: closing the tab does not stop it, photos appear in the event as they finish, and `P-55`'s result is stored on the event for whenever they next look. Ruled that this is *not* a notification — `P-81` bans reaching someone who is not looking, and its own principle is "state is discovered by looking at the thing itself". Closes a real hole: `P-94` allows ~30 min and `P-81` tells nobody, so `P-55`'s message previously had no stated home. Live push (WebSockets/AppSync) rejected — costs `Sam` infrastructure and edges toward what `P-81` removed. **Mechanism deliberately left to the ingestion-stack decision** and flagged as an input to it: retry state is native to Step Functions Distributed Map, bookkeeping under SQS |
| 2026-08-06 | P-74, P-75, P-76 | **Reversed and dissolved (D-125).** **Account deletion does not exist and will not be added.** The original openly carried "forced, not ruled — open to override"; the user overrode it. `P-75` (organized events archive on departure) and `P-76` (match sets survive it) are **DISSOLVED** — their questions cannot arise — with their reasoning retained in place for a future reversal. Ruled on build cost and scope, consistently with `D-115`/`D-119`: deletion cascades through memberships, organized events, match sets, Cognito identities and every `P-86` attribution. **Coherent because `P-68` survives** — deleting the profile selfie still destroys the face template, so the biometric exit remains; what is gone is removing an email and a display name. **Cascade:** §7 point 5 amended and now the product's only withdrawal action; `P-99` narrowed to ejection only; `P-74`'s deletion-screen disclosure obligation is void and **moved to `P-72`'s public privacy page**, which must now state that accounts cannot be deleted and that name and email stay on uploaded photos |
| 2026-08-06 | P-95 | **Completed (D-124).** The region is `ap-south-1` (Mumbai) — nearest the user and the events, which is what upload time and gallery latency turn on. Closes the "which region" item `P-95` had left explicitly unruled. **Verify Rekognition availability in `ap-south-1` before building** — recorded as a check, not asserted. The parameterise-resource-names obligation is now *more* important, not less: a ruled region invites hardcoding, which would break `Sam` and make `P-95` expensive to revisit |
| 2026-08-06 | P-89, P-28 | **Rewritten (D-121, D-122, D-123) — three rulings taken separately, not one change.** (a) **Name is editable** by the organizer while `ACTIVE`. The original's identity-stability argument was judged thin: only the organizer can rename, and they already control every photo and every admission. Costs it was blocking were certain — a permanent typo for ~60 days, and a stale place name on Priya's trip. "Rename only before the first join" was offered and rejected as arriving too late to help. `P-90` unaffected: the QR encodes the link, so printed cards survive. (b) **An optional description is added**, blank by default, organizer-editable, **shown in the `P-28` lobby as well as inside the event** — the lobby placement is the reason it was ruled, since `P-28` exists so people can tell they are in the wrong event. First free-text field others read; noted, not alarmed about. (c) **No user-set date.** The system records creation time and the interface labels it **"Created"**, never "Date" — a creation timestamp shown as an event date is subtly false. Closes the "date treated as name" assumption `P-89` was carrying |
| 2026-08-06 | P-29 | **Reopened and reaffirmed (D-120) — no change.** Dropping the blocklist was proposed on storage grounds and declined once the consequence was clear: `P-90` fixes the join code permanently and no rotation exists, so an ejected user would re-enter the same code and return within seconds at `P-26`'s default `OPEN` event. Also established that the blocklist is not separate storage — it is the `BLOCKED` label on the membership row that already exists. Removing it plus adding code rotation, and flipping the event to `APPROVAL_REQUIRED` on ejection, were both offered and declined. **Do not re-litigate without also solving code rotation** |
| 2026-08-06 | P-54 | **Rewritten (D-119).** Only the ZIP's top level is read; subfolders are not opened. **Ruled on build cost** — arbitrary nesting means depth limits, path traversal in entry names, collisions on flatten and ZIP-bomb shapes, which the user judged not worth carrying in a portfolio project. The requirement is stated up front wherever a ZIP can be chosen (*"put all the photos directly in the ZIP — folders inside it are not opened"*), which is the whole mitigation and must not be dropped during build. The rest of `P-54` was explicitly kept: OS junk silent, video/RAW reported, type sniffed from content. **Accepted cost:** a photographer who zips a parent folder of `Ceremony/` and `Reception/` ingests nothing and must re-zip. A ZIP yielding no top-level photos says why (*"folders inside a ZIP aren't opened"*) rather than reporting a bare zero — free, since entry labels are already read. Side effect: `__MACOSX/` is a top-level directory and now falls out of scope automatically |
| 2026-08-06 | P-07 | **Wording corrected (D-118) — not a product change.** `P-07`'s second sentence denied "any mode in which an attendee sees only their own matches", which `P-64` has contradicted since 2026-08-04. Confirmed by the user as two views over one collection — own photos, or the entire collection. `P-07` now speaks only to permission (admission grants the whole gallery, no photo is ever withheld) and explicitly names `P-64`'s two positions as views over that set. The distinction recorded: a filter is user-reversible and hides nothing they could not re-show; a permission is not. The 2026-08-03 log row that seeded the bad phrasing is annotated in place |
| 2026-08-06 | P-31, P-53 | **Rewritten (D-117).** The last remaining share block is gone: an `ACTIVE` event is shareable at all times, with no ingestion condition. `D-99` had already removed the deadlock but kept the in-flight block, which `P-94` then sized at up to ~30 minutes — half an hour in which Arjun cannot hand out the code, and a code that flickers in and out for Priya's constantly-uploading trip. The rule had also inverted itself: it permitted sharing a completely empty event while forbidding a partly-full one. **Recommendation followed.** Accepted cost: a guest joining mid-batch sees a partial gallery and, under `P-81`, is told nothing — `P-16` fills it in front of her. **Cascade:** `P-53`'s timeout re-founded on `P-55` (it can no longer cite an unshareable deadlock, but a batch with no terminal state can never produce `P-55`'s final count); `P-94`'s accepted cost rewritten — bulk upload is no longer a before-the-event-only task; `P-56` and `P-55` citations amended; §8 drops from two role modifiers to one; `P-37`'s citation corrected |
| 2026-08-06 | P-40 | **Reversed (D-115).** All product limits removed — no photo cap per event, no active-event cap per organizer, no attendee cap. Only Rekognition's external, unraisable 15 MB per-file ceiling remains, which is a physical constraint rather than a product choice. Ruled on the project's shape: it is torn down with `terraform destroy` and published for others to self-deploy, so caps sized for one credit budget become friction for everyone cloning the repo. **Recommendation overridden** — keeping both caps as Terraform variables with today's values as defaults was offered and declined. **Accepted cost, the spec's sharpest because it spends real money:** the original called the per-organizer cap "the only real guard against a scripted abuser", and with P-97 limiting only code attempts, P-87 setting no upload quota and P-81 alerting nobody, nothing bounds spend. Rekognition bills on arrival at ~6x whole-life storage cost, so teardown recovers nothing already spent. **Cascade:** P-93 becomes the sole statement of scale, P-85 loses its denominator, P-87 and P-97 lose their stated bound, P-25 carries the spend risk |
| 2026-08-06 | P-85 | **Revised (D-116).** Now three numbers: photo count (no denominator, since P-40 removed the cap), attendee count, and total storage used — all informational, none a limit. Storage was originally refused because P-40 bounded events in photos rather than bytes, so megabytes "would imply a lever that does not exist"; P-40 now bounds nothing in either unit, and the byte figure is what maps to a self-deployer's own AWS bill. Search count stays dead (P-16 removed searching); charts stay cut (P-01). **Obligation:** the running byte total must stay correct across P-44, P-52, P-38 and P-55 — a drifting counter is worse than none, since P-81 surfaces no discrepancy |
| 2026-08-06 | P-99 | *(Narrowed 2026-08-06 by D-125 — account deletion no longer exists, so this covers ejection only.)* **New ruling (D-114).** Uploader attribution persists unchanged after account deletion (P-74) and ejection (P-47). Ruled on the forward-only rule shared with P-20/P-68/P-73/P-75/P-76/P-98. **Recommendation overridden** — dropping the email and keeping only the name was declined in favour of one rule with no exceptions. Adds a disclosure line to P-74's deletion screen |
| 2026-08-06 | P-86 | **Reversed (D-113).** Uploader attribution is now shown — display name **and** email — to every admitted attendee, stamped by upload action (a P-38 ZIP stamps all its photos, a P-37 multi-select stamps its own). Closes the gap the original ruling itself named: Priya's "who took this?" had no answer. No new data — the uploader was already stored for P-44. **Recommendation overridden** — name-to-everyone with email-to-organizer-only was declined in favour of one consistent identity everywhere. **Cascade:** P-83 rewritten, §7 point 6 added, P-41's citation corrected, P-52 given a guard against filter-by-uploader, P-74's disclosure extended, §8 tables updated |
| 2026-08-06 | P-83 | **Rewritten (D-113).** The original claim — attendees cannot see who else is in an event — was made false by P-86. Now: no member-list screen for attendees, but uploaders are identifiable from the gallery; never-uploaded attendees are not named. The screen stays organizer-only on the control argument (P-29/P-10 need someone to act on), not on privacy |
| 2026-08-06 | P-82 | **Reversed (D-112).** The organizer's attendee and pending lists now show display name **and** email. The original withheld emails on "harvestable mailing list, in both directions" grounds; "both directions" does not apply, since P-83 gives attendees no list. Decisive reason: P-84 made the display name freely editable, non-unique and never verified, so the P-10 approval and P-29 ejection controls had nothing reliable to act on — the email is verified via P-02 and P-91 |
| 2026-08-03 | Initial product concept | Core pitch, two personas, free-tier and portfolio constraints |
| 2026-08-03 | Auth and accounts | Email/password only, no social, attendee accounts required |
| 2026-08-03 | P-05 | One account, role scoped per event |
| 2026-08-03 | P-13 | Attendee uploads visible immediately, organizer deletes after |
| 2026-08-03 | P-15, P-16 | **Reversal:** face reference is account-level and persistent; matching is automatic and silent |
| 2026-08-03 | P-07 | **Removal:** matches-only gallery *mode* dropped entirely — as a separate screen with its own permission. *(Read with care: `P-64` later added a matches-only **filter** over the one gallery, which is a different thing. `P-07`'s wording was corrected 2026-08-06 by `D-118` because this row's phrasing had leaked into the ruling and read as banning the filter too.)* |
| 2026-08-03 | P-17 | Profile selfie optional — follows from P-07 making matching a filter, not a gate |
| 2026-08-03 | P-24 | No configuration questions at event creation |
| 2026-08-04 | P-19 | Profile selfie offered contextually when photos first appear, not at signup — attendees on first gallery open, organizers after their first batch lands |
| 2026-08-04 | P-20 | Selfie changes apply to future photos only — no recompute fan-out |
| 2026-08-04 | P-21 | Joining never blocks on matching |
| 2026-08-04 | P-26 | Locked event defaults: open join, attendees can add, threshold 80 |
| 2026-08-04 | P-47–P-50, §8 | **Permission model designed.** Five membership states, two modifiers above roles, four resource tables, a specified order of evaluation, and four invariants. Ejection leaves photos in place |
| 2026-08-04 | P-46 | Attendees can leave and rejoin; contributed photos stay. Closes the gap where a mistyped valid code admitted someone permanently |
| 2026-08-04 | P-45 | Attendees can see and share the access code — they already know it, so hiding it was theatre |
| 2026-08-04 | P-44 | The uploader may delete their own photo; the organizer may delete any. First permission requiring a user–resource condition rather than a role |
| 2026-08-04 | P-42, §7 | All photos indexed identically regardless of uploader. **§7 point 1 rewritten** — its claim that Glimpses does not index non-users was false; the real guarantee is that search is directional |
| 2026-08-04 | P-43 | An attendee must be admitted before contributing |
| 2026-08-04 | P-41 | No platform administrator. §8 is confirmed at two roles — organizer and attendee |
| 2026-08-04 | P-39 | One organizer per event — no co-organizers, no transfer. Keeps §8 to two roles |
| 2026-08-04 | P-40 | *(Reversed 2026-08-06 — see the P-40 row above.)* Limits: 1,000 photos/event, 5 active events/organizer. Counted in photos because Rekognition bills per image regardless of size |
| 2026-08-04 | P-25, P-33 | **Reasoning corrected** after research: the AWS Free Tier changed on 15 Jul 2025 to $200/6 months, and indexing — not storage — is the dominant cost. Both rulings stand; only their justifications were wrong |
| 2026-08-04 | P-38 | Duplicates detected by content hash, per-event scope, reported to the uploader. Perceptual hashing rejected on burst-shot false positives; global scope rejected because it breaks P-34 |
| 2026-08-04 | P-31 | *(Superseded 2026-08-06 — see the P-31 row above; the remaining block was removed too.)* **Correction:** sharing is blocked only while a batch is processing, not until a first batch exists. The original rule permanently deadlocked the collaborative-outing case — the first ruling to fail the §2 two-persona test |
| 2026-08-04 | P-36, P-37 | Both roles may upload multi-file selections or ZIPs; a multi-file selection is one batch |
| 2026-08-04 | P-35 | Formats: JPEG/PNG accepted, HEIC converted to JPEG q90–95 on ingest, RAW rejected. PNG-as-target ruled out on measured size and Rekognition's 15 MB limit |
| 2026-08-05 | P-98, P-20 | D-111 ruled: **P-20 stands, re-founded on structural grounds** — one forward-only rule shared with P-68/P-73/P-75/P-76, plus P-16's "no search step". Recompute was confirmed affordable (~$0.005 for a five-event attendee) and declined anyway, so the inert-remedy cost is now an explicit product choice rather than a budget consequence. Noted as the cheapest ruling in the spec to reverse if real use argues against it |
| 2026-08-05 | P-20 (reasoning only) | **D-96 answered from AWS primary sources — no ruling changed.** A collection search is one call regardless of photo count, and searching by stored face ID bills identically to searching by image. P-20's cost justification was therefore false and has been rewritten; recompute is ~$0.005 for a five-event attendee. P-73 unaffected (ruled on interface coherence). **Opens D-111** — whether P-20 should be re-ruled now its stated reason has gone |
| 2026-08-05 | P-97, P-18 | Access-code attempts are the only rate-limited action, per account and per IP. The only true breach in the list — P-07 plus P-26 make a guessed code immediate full access. **Face search dropped out of the question**: no user action triggers a search after P-16, P-73 and P-79, so P-18 is amended to pipeline concurrency rather than user rate limiting. Keeps API Gateway HTTP API available, since usage plans are REST-only. Accepted cost: no upload rate limit, so P-87 floods are bounded only by P-40 |
| 2026-08-05 | P-96 | Browser floor is current Safari, Chrome, Firefox, Edge; accessibility basic and untested — semantic markup, alt text, keyboard paths, contrast. WCAG 2.1 AA declined on P-22, which puts compliance machinery out of scope. Browser age is not the constraint since P-92 targets self-updating phone browsers and P-35 already handles HEIC server-side. Noted as structural: alt text for user-uploaded photos cannot exist under this budget |
| 2026-08-05 | P-95 | One region, one environment, no staging — deploys go straight to production. **Recommendation overridden**; the saving is Terraform effort and setup time rather than money, since an idle staging environment bills near zero. Accepted cost is the spec's largest operational risk: no rehearsal and no rollback target, against live events holding photos that exist nowhere else. Which region is left unruled. Obligation: parameterise resource names so this stays reversible |
| 2026-08-05 | P-94, P-31 | Design targets: ~30 min to ingest 1,000 photos, matches within minutes of batch completion. **Recommendation overridden** in favour of the simplest pipeline — throughput no longer forces the SQS vs Step Functions question, though correctness still merits it. **P-31's accepted cost restated**: the unshareable window is up to ~30 minutes, not "minutes", making bulk upload a before-the-event task and serving §2's collaborative shape poorly *(this half superseded 2026-08-06 by D-117 — there is no unshareable window; the ~30 min target itself stands)* |
| 2026-08-05 | P-93 | *(Amended 2026-08-06 by P-40 — nothing is enforced any more; P-93 is now the only statement of scale.)* Target scale: 100 attendees/event, ~10 concurrent active events. Planning figures, not caps — P-40 remains the only enforced limit. Attendee count is the cost driver because P-16 fans matching out across every attendee per batch, so this is the figure D-96 must be checked against. Deliberately modest against P-25's clock. Accepted cost: a 200–300 guest event exceeds the target and is untuned for it |
| 2026-08-05 | P-92 | Mobile-web first; desktop is the same layout with more room. Ruled on headcount — one organizer versus hundreds of attendees, and every attendee action is a phone action. Resolves the deferral P-60 was waiting on. Accepted cost falls on the organizer: ZIP upload and P-52 bulk multi-select are desktop tasks getting a phone-derived layout. Designing both properly rejected on P-25's time constraint, not merit |
| 2026-08-05 | P-91 | Email verification by numeric code, not a clickable link; same for password reset. Ruled on P-30 — with no sending domain there is no mail reputation, and a link is the most spam-triggering content available while a bare code is the least. Also keeps signup on one screen, where P-04 locates the funnel's largest drop-off. Cognito default, so nothing to build |
| 2026-08-05 | P-90 | QR generated server-side and stored as an image, served via CloudFront. **Recommendation overridden** — ruled on the share-into-a-group-chat case P-09 names, which client-side rendering answers only with a screenshot. Accepted cost: one stored object per event plus a cleanup obligation when P-33 deletes the event, joining P-60's archives on the lifecycle list. The "emailable" argument this question was originally framed on had already been removed by P-51 |
| 2026-08-05 | P-89 | *(Superseded 2026-08-06 — see the P-89 row above. Name now editable, description added, date replaced by a system "Created" timestamp.)* Event name and date fixed at creation, permanently. **Recommendation overridden** — ruled on identity stability: name and date are what a pending user sees under P-28, and cannot change beneath them. Policy dials stay editable while ACTIVE per P-24; nothing editable once ARCHIVED per P-32. Accepted cost: a typo'd name persists for the event's whole ~60-day life, remedied only by deleting and recreating. Date treated as name — flagged as an assumption |
| 2026-08-05 | P-88 | No pre-approved guest list; APPROVAL_REQUIRED organizers approve every arrival by hand. **Recommendation overridden.** Completes P-51's removal of invitations — the product now has no concept of a guest known in advance. Email matching would have failed silently on address mismatch. Accepted cost: with P-81 removing notifications too, APPROVAL_REQUIRED is materially heavier than when P-10 was ruled |
| 2026-08-05 | P-87 | No per-attendee upload quota; P-40's event cap is shared first-come. **Recommendation overridden** — remedies are P-52 bulk delete and P-29 ejection, and a cap would have meant inventing an unmeasured number. Accepted cost is the spec's sharpest abuse case: one attendee can fill the event and lock the organizer out of uploading, with P-81 ensuring nobody is told |
| 2026-08-05 | P-86 | *(Reversed 2026-08-06 — see the P-86 row above.)* No visible uploader attribution anywhere; the uploader is still recorded internally for P-44. Public attribution would contradict P-83 by leaking membership through the gallery; organizer-only attribution recreates the "delete everything this person added" control P-52 refused. Accepted cost falls on §2's collaborative trip persona — "who took this?" has no answer |
| 2026-08-05 | P-85 | *(Revised 2026-08-06 — see the P-85 row above.)* Organizer sees photo count against P-40's 1,000 cap and attendee count — nothing else. Ruled as making an existing limit legible rather than as a dashboard: P-53 + P-55 make crossing the cap mid-batch undiagnosable. Search count is dead (P-16 removed searching); storage is unactionable (P-40 counts photos, not bytes); charts cut by P-01 |
| 2026-08-05 | P-84, P-02 | Display name collected at signup, editable, not unique, not verified. Amends P-02. Deriving it from the email local part was rejected — it hands back most of the address P-82 deliberately withheld. First-join prompting fails because the lobby request often is the first join. Accepted cost: a self-declared label, bounded by P-29 and by P-07 already granting access anyway |
| 2026-08-05 | P-83, §8 | Attendees cannot see each other; the member list is the organizer's alone. Identity is exposed only where a control needs it, and P-45 makes any all-member roster a guest list readable by anyone who obtained the code. §8 cell closed |
| 2026-08-05 | P-82, §8 | *(Superseded 2026-08-06 — see the P-82 row above.)* Organizer sees attendee and pending lists as display names only; emails never shown to another user. Ruled on P-45 — the code reaches unvetted people, so exposing addresses turns an event into a harvestable mailing list, and P-51 means the product itself never emails anyone. **Introduces a display name the product did not have** (D-109). Attendee-to-attendee visibility left open as D-110 |
| 2026-08-05 | P-81, P-51 | No notifications of any kind — no badges, unread counts, feed or push. State is found by looking at the thing itself. **Recommendation overridden**; keeps the data model free of read state and last-seen markers. **P-51's accepted cost restated as permanent** — with email gone and no in-app signal, an APPROVAL_REQUIRED organizer has no lobby alert at all. Reversible: a badge is one timestamp per membership |
| 2026-08-05 | P-80 | Similarity threshold fixed at 80, exposed to nobody. Organizer configuration would tune every attendee's private filter with nothing to judge it by; an attendee slider collides with P-73 (no recompute) and would force a per-match score into the data model. Accepted cost: 80 is inherited from v1, unmeasured, and changing it is a redeploy |
| 2026-08-05 | P-79 | No per-event opt-out from matching. §7 point 3 means a match set is visible to nobody but its owner, so an opt-out would only suppress a filter the user can decline to press — while P-42 indexes their face in that event regardless, making it feel like it stopped the indexing. Would also add a fourth filter state to P-69's three. Accepted cost: no way to want matching everywhere but one place |
| 2026-08-05 | P-78 | "Activity" means a photo being added — views, downloads, joins and organizer visits do not reset the clock. Makes P-77's 60 days a bound rather than a description: under any other reading, one viewer a month keeps a non-user's face vector alive indefinitely while P-72's page claims it expires. P-70's defence depends on this clause. Accepted cost: a long-running album archives mid-life and P-32 makes that irreversible |
| 2026-08-05 | P-77 | Retention durations confirmed at 30 days to archive, 30 more to delete — ~60-day event lifetime. Ruled on privacy and product grounds, not cost: storage is ~2¢/event/month and indexing is unrecoverable, so no duration moves the budget. Longer would weaken P-72's published figure and outlive P-25's credit window. Completed by P-78: activity means uploads only |
| 2026-08-05 | P-76, §7 | Account deletion inherits P-68: template destroyed, computed match sets remain. **Recommendation overridden** in favour of one forward-only rule shared by P-20/P-68/P-73/P-75/P-76 — no operation anywhere revises computed matches. Accepted cost: records unreachable by anyone, since P-69's frozen toggle needs an account to render. §7 point 5 amended so it cannot be read as "leaving erases what you appeared in" |
| 2026-08-05 | P-75 | Deleting an account archives every event that user organizes under P-32; it expires on its normal P-33 clock. No deletion, no ownership transfer — P-41 leaves no admin to receive it and P-05 makes the role a relationship, not an asset. Reuses an existing state rather than inventing an ownerless one. Accepted cost: no one can delete a photo from an ownerless archived event |
| 2026-08-05 | P-74 | Account deletion exists (*forced, not ruled*); photos contributed to events remain, account link severed. Refuses to make photo deletion a side effect of an action aimed elsewhere — P-44 + P-52 already let a departing user remove them deliberately. Taking the photos would have cost the group the album without recalling downloaded copies. **Confirmation screen must state that photos remain.** D-09 split: D-106 (organized events), D-107 (match sets) |
| 2026-08-05 | P-73, P-20 | No manual re-match; P-20's cost accepted unmitigated. **Recommendation overridden** — ruled on keeping P-16's "no search step" literally true, and on the product having no operation that reaches backwards into computed matches. **P-20's accepted-cost bullet restated**: "future photos only" means *never* for an event that has stopped receiving photos, which is every event within 30 days. **P-20's stated fan-out reasoning flagged as likely wrong pending D-96**, whose scope was widened to cover it |
| 2026-08-05 | P-72 | One public plain-language privacy page, linked from signup and footer, never blocking. The only disclosure of face indexing anywhere, and the only artifact a non-user can reach — which is why it was ruled where P-71's notice was declined. Carries no contact address (P-70 stands). **Its stated ~60-day figure is coupled to P-32/P-33 and D-98 has not ruled those durations** |
| 2026-08-05 | P-71 | No face-indexing notice shown to organizers or uploaders anywhere. **Recommendation overridden** — a notice changes no behaviour and grants no capability, the same objection P-42 used to kill the consent checkbox. P-67's selfie consent obligation is unaffected. Compounds with P-70 into the spec's weakest position against P-22's test, stated openly. Opens D-105 (is there a terms/privacy page at all?) |
| 2026-08-05 | P-70, §7 | Non-users get no removal path — the ~60-day expiry under P-32/P-33 is the only remedy. **Recommendation (a stated out-of-band contact) was overridden**, on the grounds that a published channel whose honest answer is "wait 60 days" is the same looks-real-but-isn't failure P-67 rejected. Accepted cost stated plainly: the least defensible position in the spec against P-22's test. Cheapest ruling to reverse |
| 2026-08-04 | P-69 | Amends P-64: the toggle renders on a face reference **or** an existing match set, so P-68's retained sets stay reachable. Introduces a third filter state — frozen — which must be visible |
| 2026-08-04 | P-68 | Deleting the selfie removes the reference and template and stops future matching; existing match sets survive. Mirrors P-20 and removes the delete-then-re-upload trapdoor. Leaves D-104 open — whether the toggle still renders |
| 2026-08-04 | P-67, §7 | **§7 points 1 and 3 rewritten — the second false guarantee found there.** A supplied face cannot be verified as the user's own, so impersonation yields another person's matches. Accepted: it grants efficiency, not access, since P-07 already grants everything. Liveness rejected on cost; camera-only rejected as security theatre |
| 2026-08-04 | P-66 | Profile selfie must contain exactly one detectable face. Auto-picking among several rejected — it would silently deliver another person's photos, the one thing §7 point 3 promises cannot happen |
| 2026-08-04 | P-65 | Events open on the user's matches when ready, else the full gallery. Resolves the P-16/P-21 conflict by readiness rather than overruling either. Accepted cost: the zero-match user opens onto an empty screen, so that state carries a design obligation |
| 2026-08-04 | P-64 | "My photos" is a filter toggle over the one gallery, not a tab. Only shape that stays honest about P-07's single dataset and lets P-17's no-selfie user see no leftover furniture |
| 2026-08-04 | P-63 | Gallery is an infinite scroll. Cursor-based paging forced by P-57 + P-16 — a position-based page breaks when photos arrive mid-scroll. Scroll-position restoration flagged as the likely-omitted failure |
| 2026-08-04 | P-62 | No social layer, no favourites. Comments contradicted P-41 (nobody to moderate) and P-51 (nobody notified); favourites cut as redundant against P-60's multi-select, but noted as the likeliest later addition |
| 2026-08-04 | P-61 | No external photo sharing and no public URLs. Would have been the first account-free access path, contradicting P-04 and P-07; permanent links would also have broken P-33's deletion promise |
| 2026-08-04 | P-60 | Downloads: single, multi-select individual files, and a server-built ZIP. All three kept because phone and laptop want opposite things. Largest build item ruled so far; archive generation inherits P-53's terminal-state and lifetime obligations |
| 2026-08-04 | P-59 | Downloads are the full-resolution transcode, unwatermarked. Downsizing rejected — it saves the cheapest cost and adds a third rendition to the expensive per-photo pass. Bandwidth noted as the only cost unbounded by P-40 |
| 2026-08-04 | P-58 | All EXIF stripped on ingest. Ruled on P-07 + P-26 + P-45 together putting a precise home address in the hands of anyone the code reaches. GPS-only stripping rejected as the worst option — believed safe, silently partial |
| 2026-08-04 | P-57 | Gallery ordered by upload time, newest first — chosen so P-16's silent arrivals are always visible, and to avoid depending on EXIF the product cannot trust. Accepted cost: both §2 personas lose chronological narrative. Filename is the within-batch tiebreak |
| 2026-08-04 | P-56 | Transient failures retried silently; deterministic ones abandoned. Makes P-55's failure count mean "your file is broken" rather than "we were busy". Retry budget must fit inside P-53's batch lifetime |
| 2026-08-04 | P-55 | Partial batch failure reports a count, not filenames. Accepted cost: recovering a few failed photos realistically means re-uploading the whole archive, which P-38 makes safe but wasteful |
| 2026-08-04 | P-54 | *(Subfolder half superseded 2026-08-06 by D-119 — top level only, no recursion. The rest stands.)* ZIPs are mined for photos; subfolders recursed and flattened; OS metadata skipped silently, user-visible files like video and RAW reported by name. Strict rejection disqualified because macOS always inserts invisible junk |
| 2026-08-04 | P-53 | No batch cancellation; every batch has a maximum lifetime and a terminal state. The timeout is required — without it a wedged batch leaves an event permanently unshareable under P-31 *(justification re-founded 2026-08-06 by D-117 on P-55's final count; the timeout itself stands)* |
| 2026-08-04 | P-52 | Bulk photo deletion by multi-selection. "Delete everything this person added" rejected — it re-introduces behind a button the harm P-47 declined to automate. Deleting a photo must also delete its face vectors |
| 2026-08-04 | P-30 | **Re-ruled, unchanged.** Reopened once the email decision revealed a second cost — no domain means no deliverable notifications. Stands: the capability a domain restores is the one P-51 deliberately cut. Registration is also the only stack charge AWS credits don't cover |
| 2026-08-04 | P-51 | Email is authentication-only: verification and password reset, to the account holder alone. Lobby alerts and email invitations both cut. Ruled on deliverability under P-30 and abuse surface under P-41 — not on cost |
