# Glimpses — Open Decisions & Working Notes

**What this file is:** the working space where product decisions get made. Options, tradeoffs, and unresolved questions live here.

**What this file is not:** the spec. Once a question is ruled, the decision moves to **`LOCKED_PRODUCT.md`** and the row here is marked RULED with a pointer. Read `LOCKED_PRODUCT.md` first — it is the source of truth for what Glimpses does.

**How we work:** AI presents options with real tradeoffs; the project owner rules. Nothing gets decided by default or by implementation drift.

**Status:** 79 ruled · 4 dissolved · 1 answered · **0 open** · 3 other *(87 rows total)*

> **Counts corrected 2026-08-04.** This line previously read "53 ruled · 4 dissolved · 23 open" while the file actually held 37 open rows — it had been undercounting by 14 for some time, and rulings were being subtracted from an already-wrong figure. The numbers above are counted directly from the table rows. **Recount rather than decrement.**
>
> The 3 "other" are `D-30` (superseded by `D-80`), `D-45` (partly ruled, remainder tracked as `D-91`), and `D-09` (partly ruled → `P-74`, remainder tracked as `D-106` and `D-107`).

**Dissolved** means the question stopped existing because of a later ruling, rather than being answered.

---

## How to read the register

Each question has a stable `D-nn` id that never changes, so decisions stay traceable. Questions are grouped by area, not priority. Items marked **blocking** gate other work and should be answered before the areas that depend on them.

---

## Actor & account model

| id | Question | Status |
|---|---|---|
| D-01 | Do attendees need an account at all? | **RULED → P-04** — account required |
| D-02 | Separate account types, or a per-event capacity? | **RULED → P-05** — role scoped per event |
| D-03 | Can one user organize their own event *and* attend someone else's? | **RULED → P-05** — yes |
| D-04 | Can an event have multiple organizers / co-hosts / delegated uploaders? | **RULED → P-39** — no. One organizer, the creator; no co-organizers and no transfer |
| D-05 | Is there a platform administrator role? What can it see and do? | **RULED → P-41** — no admin role; operator acts out of band via the AWS console. §8 therefore has exactly two roles |
| D-06 | Does the organizer's own face reference match against their own event, so they get a "my photos" filter too? | **RULED → P-19** — yes; their uploaded ZIP will often contain photos of themselves, and they get the same prompt an attendee does. *(Whether an organizer is bound by their own `contributionPolicy` is trivially no, and folds into the RBAC pass.)* |

## Account lifecycle

| id | Question | Status |
|---|---|---|
| D-07 | Email verification via numeric code or clickable link? | **RULED → P-91** — numeric code. Ruled on `P-30` deliverability and on keeping signup to one screen |
| D-08 | Is password reset in scope? | **RULED → P-51** — yes. One of exactly two emails the product sends |
| D-09 | Can a user delete their own account? What happens to their events, their match sets, and photos they contributed? | **Partly ruled → P-74** — deletion exists (*forced, not ruled — open to override*); contributed photos remain in their events, account link severed. Remainder split out as `D-106` (organized events) and `D-107` (match sets) |
| D-106 | **Split from `D-09` 2026-08-05.** A user deletes their account while organizing a live event with attendees in it — what happens to the event? `P-41` means there is no admin to transfer ownership, and `P-05` scopes the organizer role to the user–event relationship, so the role cannot simply be reassigned | **RULED → P-75** — the event archives immediately under `P-32` and expires on its normal `P-33` clock. No deletion, no ownership transfer. Accepted cost: nobody can delete a photo from an ownerless archived event |
| D-107 | **Split from `D-09` 2026-08-05.** On account deletion, `P-68` implies the face template goes and computed match sets stay. Confirm deliberately rather than by inheritance — `P-68`'s accepted cost bites harder here, since a record continues to say which photos a departed user appeared in | **RULED → P-76** — inherits `P-68` unchanged: template destroyed, match sets remain. Ruled on keeping one forward-only rule across P-20/P-68/P-73/P-75/P-76. Accepted cost: unreachable biometric-derived records for a departed user, bounded by `P-33`'s ~60-day expiry |

## Access & join policy

| id | Question | Status |
|---|---|---|
| D-10 | One collapsed access concept or independent dials? | **RULED → P-06** — two dials (`joinPolicy`, `contributionPolicy`); `galleryScope` removed by P-07 |
| D-11 | What does an attendee waiting in the lobby actually see? | **RULED → P-28** — event identity only, no contents |
| D-12 | Access code format? | **RULED → P-27** — 6 alphanumeric, lookalikes excluded |
| D-13 | Is the QR generated client-side (free, ephemeral) or server-side and stored (durable, emailable)? | **RULED → P-90** — server-side, stored, served via CloudFront. Ruled on in-app sharing, not emailability (`P-51` removed that). Carries a deletion obligation under `P-33` |
| D-14 | Custom domain or CloudFront default? | **RULED → P-30** — CloudFront default; reversible later |
| D-15 | Can the organizer invite specific people by email as pre-approved, alongside the open code? | **Partly ruled → P-51** — the *sending* half is cut; Glimpses never emails an invitation. The *pre-approval* half survives and is untouched: whether an organizer can list an email address in advance so that person skips the lobby when they arrive with the code. **Now RULED → P-88** — no pre-approval either. The whole invitation concept is gone; the access code is the only route in |
| D-16 | Can an organizer remove an admitted attendee? | **RULED → P-29** — yes, and they are blocked from rejoining |
| D-17 | Is a denial permanent? | **RULED → P-29** — yes, same blocklist |

## Event lifecycle

| id | Question | Status |
|---|---|---|
| D-18 | What are the event states? Is there a DRAFT state? | **RULED → P-23/P-31** — ACTIVE and ARCHIVED only; no DRAFT, sharing hidden until first batch lands |
| D-19 | Can an event be edited after creation? Which fields, at which states? | **RULED → P-89** — name and date fixed permanently; policy dials editable while `ACTIVE` (already implied by `P-24`); nothing editable when `ARCHIVED` (`P-32`) |
| D-20 | What does "archived" mean per role? | **RULED → P-32** — read-only; attendees keep view+download, everything else stops |
| D-21 | Can an archived event be un-archived? | **RULED → P-32** — no, permanent |
| D-22 | Can an event be permanently deleted? | **RULED → P-34** — yes, by the organizer, with confirmation, from any state |
| D-23 | Do events auto-expire? | **RULED → P-33** — auto-archive on inactivity, then auto-delete. Durations are D-98 |
| D-99 | **Reopened P-31:** the original rule hid sharing until a first batch existed, which permanently deadlocked an organizer whose attendees are the only source of photos. | **RULED → P-31 (rewritten)** — block sharing only while a batch is processing; allow sharing an empty event with a note |
| D-108 | **Split from `D-98` 2026-08-05.** What resets an event's inactivity clock — uploads only, or views too? If viewing counts, an event people keep opening never archives, and `P-77`'s ~60-day figure (published on `P-72`'s privacy page) stops being a bound at all | **RULED → P-78** — uploads only. Views, downloads, joins and organizer visits do not reset it. Ruled on keeping `P-77`'s published figure a real bound, which `P-70` depends on |
| D-98 | **Sub-decision of P-33:** confirm the exact retention durations. Proposed 30 days inactivity → archive, 30 days later → delete. | **RULED → P-77** — 30/30 confirmed, ~60-day lifetime. Ruled on privacy and product grounds; cost is not a factor at ~2¢/event/month. Completed by **`P-78`** — activity means uploads only |

## Upload & ingestion

| id | Question | Status |
|---|---|---|
| D-30 | ZIP only, or also direct multi-file upload? | Superseded by D-80 |
| D-31 | Limits: max ZIP size, max photos per event, max events per organizer? | **RULED → P-40** — 1,000 photos/event, 5 active events/organizer; counted in photos, not bytes |
| D-32 | Accepted formats — JPEG, PNG, **HEIC** (iPhone default, needs conversion), RAW? | **RULED → P-35** — JPEG/PNG accepted; HEIC converted to JPEG q90–95 on ingest, original discarded; RAW rejected. Applies to the profile selfie too |
| D-33 | Behaviour for non-image files, nested folders, and OS metadata junk inside a ZIP? | **RULED → P-54** — skip non-photos, recurse and flatten subfolders, report only skips the user could have known about. File type read from content, not extension |
| D-34 | Can the organizer delete individual photos after ingestion? Cancel an in-flight job? | **RULED.** Individual deletion → P-44. Bulk deletion → **P-52**, multi-select; delete-by-contributor rejected. Cancellation → **P-53**, no cancel, but every batch has a maximum lifetime and a terminal state |
| D-35 | What is rate-limited and at what thresholds — face search, uploads, join attempts, access-code guesses? | **RULED → P-97** — access-code attempts only, per account and per IP. Face search dropped out of the question entirely (no user-triggered search exists after `P-16`/P-73/P-79); `P-18` amended to pipeline concurrency. Thresholds belong in §10's tuning table |
| D-36 | Are duplicate photos across two uploads detected and de-duplicated? | **RULED → P-38** — content hash, scoped per event, skipped before conversion, and reported to the uploader |
| D-37 | What does the organizer see if a batch partially fails — which photos failed, can they retry just those? | **RULED → P-55** — a count, not filenames. A partial success is terminal and unblocks P-31 sharing |
| D-100 | **Split out of D-37, which bundled it badly:** when a photo fails for a *transient* reason (rate limiting, timeout) rather than a deterministic one (corrupt file, over Rekognition's 15 MB limit), does ingestion silently re-attempt it before the batch is declared finished? Invisible robustness, not a reporting choice — independent of P-55 | **RULED → P-56** — yes, retried silently; deterministic failures abandoned |

## Face search & matching

| id | Question | Status |
|---|---|---|
| D-40 | Is the attendee's selfie stored or discarded? | **RULED → P-15** — stored as a private profile image *(reversed from an earlier ruling)* |
| D-41 | Is a face template retained? | **RULED → P-15** — yes, retained; this is what enables automatic matching |
| D-42 | Is the similarity threshold organizer-configurable, fixed, or attendee-adjustable? | **RULED → P-80** — fixed at 80, exposed to nobody. Changing it is a code change |
| D-43 | Behaviour when the profile selfie contains zero faces, or more than one face? | **RULED → P-66** — exactly one detectable face, or rejected. No guessing, no face picker |
| D-103 | **Live gap in a stated guarantee, found 2026-08-04.** §7 point 3 and P-15 both promise "no user is ever discoverable by another" — but the face reference is only *self-supplied*, never verified to be *self*. Uploading a photo of another person as your profile selfie yields every photo they appear in, across every event you can join, and P-15 makes your profile image invisible to them so they can never discover it. **Not fixable by P-66's face-count check.** Needs a deliberate ruling | **RULED → P-67** — accepted and stated; §7 points 1 and 3 rewritten to be true. Liveness detection rejected on cost, camera-only rejected as theatre |
| D-44 | Behaviour when there are zero matches — dead end, or fallback to browsing? | **DISSOLVED by P-07** — the full gallery is always available, so zero matches is never a dead end |
| D-45 | Can a user change their face reference, and does that replace or merge the match set? | Partly ruled → P-15 (changeable in profile settings). Recompute behaviour is D-91 |
| D-46 | Can a person appearing in photos who is *not* a user demand removal of their face data? | RULED → `P-70` |
| D-47 | Do photographed people consent? Is a notice shown to organizers? | **RULED → P-71** — no notice anywhere. The consent half was already settled by P-42; the disclosure half is declined as text that changes no behaviour. P-67's selfie consent obligation is untouched |
| D-105 | **Opened 2026-08-05 by P-71.** Does Glimpses have a terms-of-service or privacy page at all? P-70 gives non-users no removal path and P-71 shows no in-product notice, so a static page is the last remaining location where face indexing could be disclosed. If the answer is also no, the product discloses it nowhere — which should be a deliberate ruling rather than an omission | **RULED → P-72** — yes, one public plain-language page, linked not blocking, no contact address. Ruled on reach: it is the only artifact a non-user can get to. **Its ~60-day claim depends on D-98** |
| D-48 | Matched photos inevitably contain other people's faces. Accepted, or mitigated? | **DISSOLVED by P-07** — everyone admitted sees every photo regardless |
| D-49 | How does an attendee get matches from a newly-uploaded batch? | **RULED → P-16** — automatically and silently, no prompt |

## Attendee contribution

| id | Question | Status |
|---|---|---|
| D-80 | Do attendees upload individual files, ZIPs, or both? Does the organizer also get a single-file path for adding stragglers? | **RULED → P-36/P-37** — both mechanisms for both roles; a multi-file selection counts as one batch |
| D-81 | Are attendee-uploaded photos face-indexed like organizer photos? (An attendee uploading a group shot causes biometric indexing of people who consented to the *organizer*, not to them.) | **RULED → P-42** — yes, identically. The uploader's identity does not change whose faces are in the frame. §7 point 1 rewritten as a consequence: the privacy guarantee is *directional*, not a claim that non-users go unindexed |
| D-82 | Are attendee uploads visible immediately, or held for organizer approval? | **RULED → P-13** — immediately; organizer deletes after |
| D-83 | Can an attendee delete a photo they uploaded, even after others have matched on or downloaded it? | **RULED → P-44** — yes. Organizer can delete anything; deletion is not retroactive and must say so |
| D-84 | Is uploader attribution shown ("added by Riya"), or are photos anonymous once in the gallery? | **RULED → P-86** — no attribution shown to anyone. Public attribution contradicts `P-83`; organizer-only recreates what `P-52` refused |
| D-85 | Per-attendee upload quota — count, bytes, or none? Needed against both abuse and free-tier limits. | **RULED → P-87** — none. `P-40`'s event cap is the only limit; `P-52` and `P-29` are the remedies |
| D-86 | In `MATCHES_ONLY` scope, can an attendee see a photo they uploaded themselves? | **DISSOLVED by P-07** — `MATCHES_ONLY` no longer exists |
| D-87 | Is the organizer notified when an attendee contributes? | **DISSOLVED by P-81** — there are no notifications of any kind anywhere in the product. New photos are simply at the top of the gallery under `P-57` |
| D-88 | Must an attendee be past the lobby before contributing? Presumably yes — confirm. | **RULED → P-43** — yes. Forced by P-28; a pending user cannot write into a gallery they cannot see |

## Gallery & download

| id | Question | Status |
|---|---|---|
| D-50 | Gallery ordering and pagination — infinite scroll or pages, by capture time or upload time? | **RULED.** Ordering → **P-57**, upload time newest first, filename as within-batch tiebreak. Pagination → **P-63**, infinite scroll, cursor-based |
| D-101 | **Split out of D-50:** EXIF carries GPS coordinates. Under P-07 every admitted attendee gets every photo, so a wedding photo can pin a stranger's home address. Is location metadata stripped on ingest? A P-22 privacy ruling, independent of P-57 | **RULED → P-58** — all EXIF stripped on ingest, not just GPS |
| D-51 | Download options — single photo, multi-select, "all my photos" as a ZIP? | **RULED → P-60** — all three. Archive generation is an async job inheriting P-53's terminal-state and expiry obligations |
| D-52 | Downloads at full original resolution or downsized? Watermarked? | **RULED → P-59** — full-resolution transcode, no watermark. "Original" was already off the table via P-35 |
| D-53 | Can an attendee share a single photo outside the app via link? | **RULED → P-61** — no. Download and forward it yourself; Glimpses mints no public URLs |
| D-54 | Favourites, likes, comments — in scope or explicitly out? | **RULED → P-62** — all out, including private favourites. Favourites noted as the likeliest later addition |

## Organizer dashboard & notifications

| id | Question | Status |
|---|---|---|
| D-60 | What metrics does the organizer see — photo count, attendee count, search count, storage used? | **RULED → P-85** — photo count against `P-40`'s cap, plus attendee count. Nothing else. Search count dead by `P-16`; storage unactionable under `P-40`; charts cut by `P-01` |
| D-61 | Can the organizer see the attendee list, with names and emails? Does that conflict with attendee privacy? | **RULED → P-82** — display names only, never emails. Introduces a display name the product lacked (`D-109`); attendee-to-attendee visibility split out as `D-110` |
| D-109 | **Opened by `P-82` 2026-08-05.** `P-82` requires a display name, which `P-02` (email + password only) never established. Where is it collected — at signup, against `P-19`'s minimal-signup goal, or later? Is it editable? Is it unique or verified in any way? | **RULED → P-84** — collected at signup, freely editable, not unique, never verified. Amends `P-02` |
| D-110 | **Split from `D-61` 2026-08-05.** Can attendees see each other in an event, or only the organizer sees the list? `P-82` ruled the organizer side only; the §8 membership table cell for `ATTENDEE` is still open | **RULED → P-83** — no. Organizer only. Identity is exposed only where a control requires it, and `P-45` would make an all-member roster readable by anyone holding the code |
| D-62 | Are any emails sent by the product? Free-tier cost implications. | **RULED → P-51** — authentication only: verification and password reset, to the account holder alone. Cost was not the deciding factor; deliverability under P-30 was |
| D-63 | How does the organizer learn a join request is waiting — in-app badge, push, or email? | **RULED → P-81** — no signal at all. No badges, counts, feed or push anywhere in the product. `P-51`'s lobby-delay cost is therefore permanent, not pending a fix |

## Non-functional

| id | Question | Status |
|---|---|---|
| D-70 | Target scale — photos per event, attendees per event, concurrent events? | **RULED → P-93** — 100 attendees/event, ~10 concurrent events; photos-per-event already fixed at 1,000 by `P-40`. Planning figures, not enforced caps |
| D-71 | Acceptable ingestion time for a large batch, and acceptable face-search latency? | **RULED → P-94** — ~30 min for a 1,000-photo batch; matches within a few minutes of completion. Targets, not promises. Restated `P-31`'s cost as a ~30-minute unshareable window |
| D-72 | Is this mobile-web first? The selfie flow is inherently a phone action. | **RULED → P-92** — yes. Phone is the design target, desktop is the same layout with more room. Resolves the deferral inside `P-60` |
| D-73 | Single region, single environment? Is there a staging environment? | **RULED → P-95** — one region, production only, no staging. Which region is left as an implementation choice, flagged unruled |
| D-74 | Browser support floor and accessibility target? | **RULED → P-96** — current Safari/Chrome/Firefox/Edge; basic untested accessibility, no WCAG target |
| D-75 | Portfolio or real users? | **RULED → P-16** — portfolio, real-capable |

---

## Face reference & matching (new — from P-15/P-16/P-17)

| id | Question | Status |
|---|---|---|
| D-90 | Where is the profile selfie offered? | **RULED → P-19** — nudged contextually on first event join |
| D-91 | Are match sets recomputed when the selfie changes? | **RULED → P-20** — no; future photos only |
| D-92 | Does joining an event with thousands of existing photos block on matching? | **RULED → P-21** — no; gallery immediate, matches fill in |
| D-97 | **Mitigation for P-20's accepted cost:** should a per-event manual "refresh my photos" action exist, letting a user who improved their selfie re-run matching for one event at a time — user-triggered, bounded to one event, rate-limitable? | **RULED → P-73** — no. No manual re-match anywhere; `P-20`'s cost accepted unmitigated. Ruled on keeping `P-16`'s "no search step" literally true. **`P-20`'s accepted-cost bullet was restated** to admit that "future photos only" means *never* for a completed event |
| D-93 | How is "my photos" presented — a tab, a filter toggle over the same grid, or a separate section? P-07 means it is a view over the full gallery, not a different dataset. | **RULED → P-64** — a filter toggle over the one gallery |
| D-102 | **Split out of D-93:** which view opens by default when an attendee enters an event — the full gallery, or the "my photos" filter already applied? P-01 argues for matches; P-17, P-21 and the zero-match case argue for the full gallery | **RULED → P-65** — matches, when ready; full gallery otherwise. P-16 and P-21 now split by readiness |
| D-94 | Does deleting the profile selfie also delete existing match sets, or just stop future matching? | **RULED → P-68** — template and reference deleted, future matching stops, existing match sets survive |
| D-104 | **Forced by P-68, and it blocks implementation.** P-64 renders the "my photos" toggle only when a face reference exists. After deletion the reference is gone but match sets remain — does the toggle still render? If no, P-68 preserves data no screen can reach. If yes, P-64 must be amended | **RULED → P-69** — the toggle renders; P-64 amended. Introduces a frozen filter state that must be shown |
| D-95 | Can a user opt out of matching for one specific event while keeping their face reference for others? | **RULED → P-79** — no. The account-level reference of `P-15` applies everywhere; the only controls are `P-64`'s filter toggle and `P-17`'s global opt-out |
| D-96 | **Needs verification, not opinion:** does a Rekognition face search by stored face ID (no image submitted) count against the image-processing free tier the same way an image-based search does? The whole cost model of automatic matching depends on this. | **ANSWERED 2026-08-05** — research task, not a decision; resolved against AWS primary sources. **(a)** No cheaper stored-ID path: `SearchFaces` and `SearchFacesByImage` are both Group 1, same rate, same 1,000-image/month free-tier pool. **(b)** A collection search is **one call regardless of photo count** — `SearchFaces` has no pagination and evaluates the whole collection in one call; `MaxFaces` caps results returned, not collection scanned. `P-20`'s recorded reasoning was therefore wrong and has been rewritten; the re-look it triggers is `D-111` |
| D-111 | **Opened 2026-08-05 by `D-96`'s answer.** `P-20` (selfie changes apply to future photos only) was ruled entirely on a cost argument now known to be false — recompute is ~1 call per event, ~$0.005 for a five-event attendee, not a budget threat. Should `P-20` stand on its remaining reasons (one forward-only rule shared with `P-68`/`P-73`/`P-75`/`P-76`; `P-16`'s "no search step"), or be re-ruled now that the cost objection has gone? Note `P-73` is *not* in question — it was ruled on interface coherence, which never depended on billing | **RULED → P-98** — `P-20` stands, re-founded on the forward-only rule and `P-16`'s no-search-step. Recompute confirmed affordable and declined anyway; the inert remedy is now an explicit choice. Flagged as the cheapest ruling in the spec to reverse |

---

*(Event defaults are now ruled — see P-26 in `LOCKED_PRODUCT.md`.)*

---

## Deferred / likely out of scope

Carried from v1 as candidates, **not yet confirmed as exclusions**: native mobile apps, payments, photo editing, video support, cross-event search, public sharing outside the access code.
