<p align="center">
  <img src="assets/marketing/hero.png" alt="Glimpses" width="720" />
</p>

<h1 align="center">Glimpses</h1>
<p align="center"><b>A Serverless Image Retrieval System.</b></p>
<p align="center">Drop in all the photos. It shows you the ones you're in.</p>

<p align="center">
  <a href="#product-walkthrough">Product walkthrough</a> ·
  <a href="#core-features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#running-it-yourself">Deploy it yourself</a>
</p>

---

### Table of contents

| Sr No. | Title |
|---|---|
| 1 | [What it does](#what-it-does) |
| 2 | [Product walkthrough](#product-walkthrough) |
| 3 | [Core features](#core-features) |
| 4 | [Who it's for](#whos-it-for) |
| 5 | [Tech stack](#tech-stack) |
| 6 | [Architecture](#architecture) |
| 7 | [Project structure](#project-structure) |
| 8 | [The Lambdas](#the-lambdas) |
| 9 | [The database (DynamoDB)](#the-database-dynamodb) |
| 10 | [The ingestion pipeline (Step Functions)](#the-ingestion-pipeline-step-functions) |
| 11 | [Triggers and edge cases](#triggers-and-edge-cases) |
| 12 | [The knowledge graph (`graphify`)](#the-knowledge-graph-graphify) |
| 13 | [Cost: built entirely on the AWS Free Tier](#cost-built-entirely-on-the-aws-free-tier) |
| 14 | [Scaling past the defaults](#scaling-past-the-defaults) |
| 15 | [Running it yourself](#running-it-yourself) |
| 16 | [CI/CD (Jenkins)](#cicd-jenkins) |
| 17 | [License](#license) |

---

## What it does

An organizer creates an event and shares a join code or QR code. Guests join and upload their photos, either one at a time or all at once as a zip straight off their camera roll, and everyone in the event can browse the shared gallery right away.

Every guest also gets a **"Photos of me"** tab, built automatically. Glimpses compares each guest's selfie against every face detected in every uploaded photo, so nobody has to scroll through hundreds of photos looking for the ones they're actually in. No manual tagging, and no "can someone send me the ones with me in them" group chat message.

It's built entirely on serverless AWS: no servers to provision or patch, nothing idling between events, and it scales comfortably from a 10 person dinner to an 800 photo wedding without anyone touching a config file.

<p align="center">
  <img src="assets/product/how-it-works.png" alt="How Glimpses works" width="720" />
</p>

---

## Product walkthrough

A guest and organizer's path through Glimpses, start to finish.

**Getting in.** Sign up once, then log in for every event after that — the same account works across all of them.

<p align="center">
  <img src="assets/product/sign-up.png" width="430" alt="Sign up" />
  <img src="assets/product/login.png" width="430" alt="Log in" />
</p>

**Sharing and joining an event.** The organizer hands out a join code or QR code; guests scan or enter it to request access. On approval-required events, they sit in the lobby until the organizer admits them.

<p align="center">
  <img src="assets/product/share-event.png" width="260" alt="Sharing an event via join code / QR" />
  <img src="assets/product/join-event.png" width="260" alt="Joining an event" />
  <img src="assets/product/event-lobby-admit.png" width="260" alt="Attendee lobby, admitting an attendee" />
</p>

**My events.** Every event an organizer has created, in one dashboard.

<p align="center">
  <img src="assets/product/events-dashboard.png" width="430" alt="My events dashboard" />
</p>

**Event settings, analytics, and downloads.** Who can join, who can upload, and the archive/delete lifecycle, next to live stats for the event and one-click ZIP downloads for a batch of photos.

<p align="center">
  <img src="assets/product/event-settings.png" width="260" alt="Event settings" />
  <img src="assets/product/event-analytics.png" width="260" alt="Event analytics" />
  <img src="assets/product/download-zip.png" width="260" alt="Downloading photos as a ZIP" />
</p>

**Privacy.** Guest-level controls over who can see what.

<p align="center">
  <img src="assets/product/privacy.png" width="430" alt="Privacy controls" />
</p>

**Uploading photos.** Upload one at a time or in bulk, with confirmation of what made it in.

<p align="center">
  <img src="assets/product/uploading.png" width="260" alt="Uploading photos" />
  <img src="assets/product/photos-added.png" width="260" alt="Photos added" />
</p>

**Everything, and Photos of me.** Every uploaded photo lands in the shared gallery immediately, while "Photos of me" is built automatically by matching faces against each guest's selfie.

<p align="center">
  <img src="assets/product/gallery.jpg" width="380" alt="Everything gallery" />
  <img src="assets/product/photos-of-me.jpg" width="380" alt="Photos of me" />
</p>

**Profile.** Manage your own selfie and account details anytime.

<p align="center">
  <img src="assets/product/profile.png" width="260" alt="Profile" />
</p>

---

## Core features

- **Event creation and join flow.** Organizers create events with a join code or QR code. Guests join instantly on open events, or wait for organizer approval on approval-required events.
- **Public Google Drive imports.** In Add Photos, choose From Google Drive and paste a folder link shared with Anyone with the link. Only direct photo children are imported. Subfolders, shortcuts, junk files, and non-photo files are skipped. Imports continue after the browser closes.
- **Bulk photo upload.** Upload photos one by one, or bundle hundreds into a zip and let the pipeline sort it out. Common metadata files from macOS (`__MACOSX/`, `._*`, `.DS_Store`), Windows (`Thumbs.db`, `desktop.ini`), Android (`.nomedia`), and iPhone exports (`.AAE` sidecars) are ignored before photo processing, so they do not appear as failed uploads.
- **Automatic face matching.** Every guest with a selfie on file gets a personal "Photos of me" view, built by comparing their selfie against every face in the event.
- **HEIC support.** iPhone photos (`.HEIC`/`.HEIF`) are converted to JPEG automatically, with no failed uploads and no visible extra step for the guest.
- **Duplicate detection.** Identical photos (same content, even under different filenames) are never stored twice, even if two guests upload the exact same photo at the same time.
- **Signed, time-limited photo URLs.** Nobody can grab a permanent public link to someone else's event photos. Every URL the gallery hands out expires in 45 minutes.
- **Full event lifecycle management.** Events move from active, to archived (read-only, no new uploads, face-matching costs stop immediately), to automatically deleted after a cooling-off window, with every trace in storage cleaned up along the way.
- **Organizer moderation.** Admit, deny, or eject attendees; delete single or multiple photos; see live event stats (photo count, storage used, attendee count).
- **Server-side ZIP downloads.** Select photos and download them as one ZIP, built on the server rather than one by one in the browser.
- **Mobile-first gallery viewer.** Swipe left and right between photos, pinch to zoom, double-tap to zoom, alongside a proper desktop experience with keyboard navigation.
- **A genuinely production-shaped face-recognition pipeline.** Deduplication, EXIF-aware thumbnailing, format sniffing, and a fan-out ingestion pipeline, all built to handle real batch uploads at real event scale, not a scaled-down demo.

---

## Who's it for

- **Event organizers** running weddings, trips, meetups, and parties who want one shared place for everyone's photos, without WhatsApp compression ruining quality or a Google Drive folder nobody can find themselves in.
- **Guests and attendees** who want to find their own photos in a large shared album without scrolling through everything someone else took.
- **Anyone curious how a real face-recognition pipeline gets built on AWS.** The whole thing is open, including the Terraform and every Lambda's source, so it also works well as a reference architecture for serverless, event-driven systems.

---

## Tech stack

**Backend**
- **AWS Lambda** (Python 3.13): every piece of business logic, 10 functions in total
- **Amazon API Gateway** (REST): 31 explicit routes, each with a JSON-schema request validator where a body is expected
- **Amazon DynamoDB**: 8 tables, on-demand billing, GSIs for every query pattern, Streams for event-driven triggers
- **Amazon S3**: one bucket, six prefixes (`photos/`, `thumbnails/`, `qrcodes/`, `selfies/`, `uploads/`, and staging areas)
- **Amazon CloudFront**: signed-URL delivery for photos and thumbnails, public delivery for QR codes
- **AWS Step Functions** (Standard, JSONata): the photo ingestion pipeline, with Distributed Map fan-outs
- **Amazon Rekognition**: `IndexFaces` and `SearchFacesByImage` power the face-matching engine
- **Amazon Cognito**: user authentication, wired into API Gateway as a `COGNITO_USER_POOLS` authorizer
- **Amazon EventBridge** (rule and Scheduler): triggers the ingestion pipeline on upload, and runs a daily sweep that auto-archives stale events
- **Amazon SNS and CloudWatch Alarms**: operator alerting
- **Amazon SES**: personalized transactional email to guests and organizers

**Frontend**
- **React 19** with **Vite**
- **Tailwind CSS**
- **Framer Motion** (`motion/react`): gesture-driven UI, including swipe to dismiss, pinch to zoom, and spring animations
- **TanStack Query**: server state, polling, and cache invalidation

**Infrastructure and tooling**
- **Terraform** (1.10 or newer, native S3 state locking, no DynamoDB lock table): 21 independently deployable modules
- **Jenkins** (local, Homebrew-installed): one CI/CD job per Terraform module, seeded automatically from a Job DSL script
- **Python** (`boto3`, `Pillow`, `pillow-heif`, `cryptography`) for Lambda logic
- **moto** for AWS-mocked unit and integration testing: every Lambda has its own `test/unit` and `test/integration` suite

---

## Architecture

<p align="center">
  <img src="assets/architecture/tech-stack.png" alt="AWS services and supporting tools, grouped by category" width="900" />
  <br />
  <sub><i>Every AWS service used, grouped by category (compute, database, object storage, API, auth, content delivery, orchestration, eventing, AI/ML, security, monitoring), alongside the supporting tools and libraries that build and run it (Terraform, Jenkins, Python, boto3, pytest, moto, JSONata, and the frontend stack).</i></sub>
</p>

At a glance, here's the shape of a request:

```
        Browser (React SPA on CloudFront)
                    │
             API Gateway (REST, Cognito-authorized)
                    │
     ┌──────────────┼──────────────────────────────┐
     │              │                              │
 13 Lambdas    Step Functions            EventBridge (upload trigger,
 (business     (ingestion pipeline,       daily archive sweep)
  logic)        Distributed Map fan-out)
     │              │
     └──────┬───────┘
            │
   DynamoDB (8 tables)   S3 (1 bucket, 6 prefixes)   Rekognition   CloudFront
```

Nothing runs unless something's actually happening. There are no EC2 instances and no containers idling between requests. A quiet event costs nothing, and a busy upload burst scales out automatically through Lambda concurrency and Step Functions' Distributed Map.

---

## Project structure

```
Glimpses/
├── Backend/                 13 Lambdas, each with the same internal shape:
│   ├── events/                 routeHandler.py -> Handler/ -> Manager/ -> (Converter/) -> DAO/
│   │   ├── src/
│   │   ├── test/unit/       moto-backed unit tests
│   │   ├── test/integration/  moto-backed integration tests
│   │   ├── infra/            this Lambda's own Terraform module
│   │   └── cicd/Jenkinsfile  this Lambda's own CI/CD job
│   ├── drive_import/
│   ├── ingestion/            same shape, repeated for every Lambda
│   ├── selfie_match_dispatcher/
│   ├── notifications/
│   ├── gallery/
│   ├── membership/
│   ├── profile/
│   ├── upload_status/
│   ├── download/
│   ├── db_api/
│   ├── cascadeDelete/
│   └── heic_converter/
├── Frontend/                 React 19 + Vite SPA
├── Infrastructure/
│   ├── imports.tf            the composition root, wires all 21 modules together
│   ├── providers.tf          Terraform/AWS provider config, S3 backend
│   ├── variables.tf          top-level variables (region, alarm email, etc.)
│   ├── cicd/seed.groovy      Jenkins Job DSL seed script
│   └── modules/               shared modules: dynamodb, buckets, alarms, email,
│                               cloudfront, state_machine, cognito, api_gateway
├── assets/                   README media: marketing, product screenshots,
│                               architecture diagrams, step function graph
└── graphify-out/             pre-built knowledge graph of this entire codebase
```

---

## The Lambdas

| Lambda | What it does |
|---|---|
| **events** | Creates, lists, and updates events; generates QR codes and join codes; computes event stats (photo count, storage used, attendee count); handles archiving and the daily auto-archive sweep |
| **membership** | Handles joining and leaving an event, listing attendees, admitting/denying/ejecting requests, and access-code based joining |
| **profile** | Uploads, replaces, and deletes a selfie; reads and updates basic profile info |
| **selfie_match_dispatcher** | After selfie confirmation, finds every event where the user is admitted and invokes ingestion matching for each one |
| **notifications** | Reads completed changes from DynamoDB Streams and event deletion, creates a short HTML and text email for each recipient, and sends through SES |
| **drive_import** | Imports photos directly inside public Google Drive folders. Owns a separate Standard workflow, paginated discovery, and streaming downloads to S3; reuses the ingestion workflow template for photo processing, indexing, and matching |
| **upload_status** | Mints presigned S3 upload URLs, and is polled by the frontend to show live upload and processing progress |
| **ingestion** | The engine room. Unpacks uploaded zips, converts, hashes, and thumbnails each photo, indexes faces via Rekognition, and matches attendees to the photos they appear in. Invoked as discrete steps by the Step Functions pipeline below |
| **heic_converter** | Converts iPhone `.HEIC`/`.HEIF` photos to JPEG, called synchronously by `ingestion` mid-pipeline |
| **gallery** | Lists event photos (everything, or just "photos of me"), returns time-limited CloudFront-signed URLs, and handles single or bulk photo deletion |
| **download** | Builds a ZIP of selected photos server-side (bundling belongs with `Downloads`, not `Photos`, so it lives here rather than in `gallery`) |
| **db_api** | The only Lambda allowed to write `Jobs.status`. Owns the status enum, and is called by Step Functions through named actions (`mark_extracting`, `mark_success`, and so on) rather than a literal status string |
| **cascadeDelete** | Tears down everything belonging to a deleted or expired event: S3 photos and thumbnails, `Faces` rows, and the Rekognition face collection. Also handles single-photo and bulk-photo deletion, since it's the Lambda with that IAM reach |

Every Lambda follows the same internal shape: `routeHandler.py` → `Handler/handler.py` → `Manager/manager.py` → an optional `Converter/` for pure computation → `DAO/dao.py` for AWS I/O, each with its own `test/unit` and `test/integration` suite (`moto`-backed) and its own Terraform module under `infra/`.

---

## The database (DynamoDB)

8 tables, all on-demand billing (pay per request, not per provisioned capacity):

| Table | Primary key | GSIs | Notes |
|---|---|---|---|
| **Users** | `userID` | none | Stores the current `selfieKey`, `selfieVersion`, and email preference after confirmation |
| **Events** | `eventID` | `organizerID-status-index`, `accessCode-index`, `status-lastUploadAt-index` | Stream enabled (`NEW_AND_OLD_IMAGES`) for archive emails and TTL-based cascade deletion. TTL on `deleteAt` |
| **Jobs** | `jobId` | `eventUploaderKey-startedAt-index` | Tracks upload progress and streams terminal `SUCCESS`/`FAILED` changes for email |
| **Photos** | `photoID` | `eventID-uploadedAtFilename-index`, `eventID-contentHash-index` | The content-hash index backs duplicate detection |
| **Faces** | `rekognitionFaceID` | `eventID-photoID-index` | One row per face Rekognition indexed |
| **EventAttendees** | `userID` + `eventID` | `eventID-status-index` | Stream enabled (`NEW_AND_OLD_IMAGES`), drives automatic face-matching for new or rejoining attendees, described below. Rows are never deleted, only status-transitioned (`PENDING`/`ATTENDEE`/`LEFT`/`BLOCKED`). Also stores `matchedPhotoIDs` and `matchedSelfieVersion` |
| **Downloads** | `downloadId` | none | Tracks server-built ZIP download jobs |
| **Notifications** | `notificationID` | none | Deduplicates email delivery attempts; TTL expires records after 90 days |

---

## The ingestion pipeline (Step Functions)

Every device upload, whether a single photo or an 800 photo zip, runs through the original ingestion Step Functions state machine. Google Drive imports use a separate workflow described below. It's written in **JSONata** (Step Functions' newer, more expressive query language) rather than the older JSONPath dialect.

<p align="center">
  <img src="assets/step-function/pipeline-graph.png" alt="Step Functions ingestion pipeline" width="800" />
</p>

| Step | What it does |
|---|---|
| **InitializeJob** | Creates the `Jobs` row. `jobId`, `eventID`, and `uploaderID` are parsed straight out of the S3 upload key, since no `Jobs` row exists yet to read them from |
| **UpdateStatusExtracting** | Flips job status to `EXTRACTING`, what the frontend's progress screen reads |
| **StageUpload** | Opens the zip, copies each raw file to S3, and writes a manifest listing every file, without touching image content yet |
| **ProcessPhotos** *(fan-out)* | For every photo, in parallel: sniff the format, hash it for dedup, convert HEIC to JPEG if needed, generate a thumbnail with EXIF rotation applied, save it, and write a `Photos` row. Results are written straight to S3 via `ResultWriter` rather than carried inline through the execution's own state data |
| **BuildPhotosManifest** | Reads those results back from S3, filters down to the photos that actually succeeded, and writes a fresh manifest for the next fan-out |
| **UpdateStatusIndexing** | Status → `INDEXING` |
| **IndexPhotos** *(fan-out)* | For every successfully saved photo, tells Rekognition to learn the faces in it (`IndexFaces`). Also uses `ResultWriter` |
| **SummarizeResults** | Reads the `IndexPhotos` results back from S3 and tallies succeeded and failed counts across the whole batch |
| **CheckAnyPhotosSucceeded** | If literally zero photos made it through, skips straight to failure, since there's nothing left to match attendees against |
| **UpdateStatusMatching** | Status → `MATCHING` |
| **BuildAttendeesManifest** | Writes a manifest of who's currently attending the event, for the next fan-out to read |
| **MatchAttendees** *(fan-out)* | For every attendee, compares their selfie against every indexed face in the event and updates their personal `matchedPhotoIDs` |
| **UpdateStatusSuccess** | Status → `SUCCESS`, with final succeeded and failed counts written to the `Jobs` row |
| **UpdateStatusFailed** | The shared failure path. Anything going wrong anywhere in the pipeline routes here, so a job never gets stuck silently "in progress" forever |

**Why fan out with a Distributed Map, and why `ResultWriter`.** A single Lambda invocation can't process 800 photos within its own timeout, so `ProcessPhotos`, `IndexPhotos`, and `MatchAttendees` each run the same small task once per item, many at once, capped by `MaxConcurrency` (tuned to this AWS account's actual measured service quotas: Rekognition's real TPS limit turned out to be 5, not the published default of 50). For the two largest fan-outs (`ProcessPhotos`, `IndexPhotos`), each item's result is written directly to S3 instead of being carried forward through the state machine's own execution data. Otherwise a few hundred photos' worth of individual results would balloon every subsequent step's state payload, and Step Functions enforces a hard 256KB limit per state.

**Named actions, not raw status strings.** The pipeline never writes a literal `Jobs.status` value itself. It only ever sends a named action (`mark_extracting`, `mark_success`, and so on) to the `db_api` Lambda, which owns the action-to-status mapping and enum enforcement internally. An unrecognized action raises an error rather than silently corrupting the status field.

---

## Triggers and edge cases

**Google Drive imports.** The separate `glimpses-drive-import` Standard workflow is packaged with the `drive_import` Lambda module. `POST /events/{eventID}/drive-import` authenticates the contributor, validates an HTTPS Google Drive folder link, and returns a job ID. The request ID makes submission retries idempotent. Public access is checked asynchronously; a private, deleted, or invalid folder produces a clear error through the existing job-status API. There is no Google sign-in or access to a user's private Drive.

The workflow lists one page of direct children per task, writes that page to S3, and downloads its photos through a Distributed Map with four concurrent workers. Each worker streams bytes into an S3 multipart upload, verifies the transferred size when available, and aborts incomplete transfers on failure. Access is rechecked against the event's contribution policy as work progresses. Subfolders are never traversed. A failed download is counted without discarding successful downloads. Page manifests are combined into the staged-photo manifest expected by `ProcessPhotos`.

Terraform derives the downstream states from the existing ingestion template at deployment time. The original `state_machine` module and ZIP workflow are not changed. Conversion, thumbnails, content-based duplicate detection, indexing, and matching invoke the existing ingestion Lambda actions. Redeploy `drive_import` whenever a shared ingestion template change should also reach the Drive workflow. Its matching map fails the import if attendee tasks fail after retries. The `db_api` Lambda remains the only writer of job statuses; it adds named actions for Drive discovery and progress. The existing job-status API exposes download, duplicate, skipped-file, and skipped-folder counts. Results are partial when some photos fail; a job with only duplicates completes without reindexing them. No supported photos produces an actionable error.

The frontend's dedicated Drive screen polls every five seconds and retains the job ID in its URL so a refresh can resume progress. The existing job-completion notifications also cover Drive imports. Temporary Drive objects under `uploads/drive/` expire after seven days; originals and thumbnails use the usual permanent photo prefixes. The bucket-wide incomplete multipart cleanup remains a fallback if a worker is terminated before it can abort.

There are no application-imposed byte or photo-count caps on Drive imports. Service limits still apply: the new worker has 1024 MB and a 300-second timeout; the reused ingestion Lambda still uses 1024 MB and 300 seconds and processes image bytes in memory. Very large images, very slow downloads, large manifest aggregation, Step Functions execution/history limits, or Google quotas can therefore cause failures. A folder listing is not an immutable snapshot: keep its contents and public access stable during import. No paid download intermediary is used, but AWS usage still consumes allowances or credits and can incur charges. [Google Drive API quotas and pricing](https://developers.google.com/workspace/drive/api/guides/limits) apply independently.

**Upload trigger.** An EventBridge rule watches for new objects landing under the S3 uploads prefix and starts the Step Functions execution. There's no polling and no manual kick-off.

**Deleting an event: two different paths, one shared cleanup Lambda.**
- **Manual delete.** The organizer clicks delete, and the `events` Lambda invokes `cascadeDelete` directly and immediately. Permanent, with no waiting.
- **Automatic delete (TTL-driven).** An archived event isn't deleted right away. It gets a `deleteAt` TTL set 30 days out. When that TTL expires, DynamoDB itself deletes the `Events` row, acting as the `dynamodb.amazonaws.com` service principal rather than a human or IAM caller. The `Events` table's stream picks that up and is filtered specifically for `REMOVE` events carrying that service principal, so only genuine TTL expiries trigger `cascadeDelete` this way. A normal application-level delete already went through the direct-invoke path above, so it never double-fires here.

**Archiving versus deleting.** Archiving an event (manually by the organizer, or automatically through a daily EventBridge Scheduler sweep for events inactive 30 or more days) makes it permanently read-only, with no new uploads, and immediately deletes its Rekognition face collection so indexing and matching costs stop right away, while keeping all photos browsable. Only archiving starts the 30-day countdown to eventual deletion, so nothing gets silently deleted without first passing through this read-only stage.

**Matching new attendees: two DynamoDB Stream patterns feeding the same entry point.** The `EventAttendees` table's stream is filtered with two separate patterns, both routed into the same `MatchOneAttendee` matching logic.
1. An existing row transitioning onto `ATTENDEE` (`MODIFY`), for example an organizer approving a pending request, or someone rejoining after leaving.
2. A brand-new row created directly at `ATTENDEE` (`INSERT`), for example a first-time join on an open, no-approval-needed event. This needs its own pattern because an `INSERT` record has no "old" image to compare against, so the first pattern's before/after comparison can't match it.

Without both patterns, someone joining an open event directly would never get matched against the event's existing photos until the next full batch re-match.

**Matching after a selfie is added or replaced.** The browser uploads to a temporary `selfies/pending/` key. Profile confirms that the image has exactly one face, copies it to a versioned permanent key, updates the current selfie pointer in `Users`, and asynchronously invokes `selfie_match_dispatcher`. The dispatcher queries all of that user's `EventAttendees` rows and invokes ingestion's existing `match_attendees` step for each `ATTENDEE` event. Event photos are not reprocessed or reindexed. On a new selfie version, ingestion replaces that attendee's previous matched-photo set; concurrent searches using the same version can add results. A DynamoDB transaction checks the current selfie version before writing, so work from an older version cannot overwrite newer results. Archived events are skipped because their Rekognition collections have been deleted. Invalid candidates leave the previous selfie intact, and abandoned temporary uploads expire after two days.

**Guest email notifications.** `EventAttendees`, `Jobs`, and `Events` streams feed the `notifications` Lambda after records are saved. It emails the organizer when a join request arrives, the guest when a pending request is approved or declined, a guest when new matched photos appear (at most one email per event per day), the uploader when a job succeeds or fails, and admitted attendees after an event is archived. The deletion cascade captures admitted attendee IDs before removing their rows and invokes `notifications` only after cleanup succeeds. The deletion email has no event link because the event is gone. Emails use escaped, short HTML with inline CSS and a plain-text alternative. They contain a login-required event link where the event still exists, not photos or face data. Transactional emails are enabled by default for signed-up guests; they can turn them off in Profile. A `Notifications` row prevents normal stream retries from sending the same message twice. Email and DynamoDB cannot provide atomic exactly-once delivery, so a rare retry around the SES response can still need operator review.

---

## The knowledge graph (`graphify`)

<p align="center">
  <img src="assets/graphify/graph-overview.png" alt="Codebase knowledge graph" width="800" />
</p>

This repo's `graphify-out/` folder holds a pre-built knowledge graph of the entire codebase: every file, function, and cross-file relationship, with community detection grouping related code together. It's committed to the repo so anyone cloning it gets it immediately, without regenerating it themselves.

If you have the `graphify` CLI installed, you can query it directly instead of grepping through source:

```bash
graphify query "how does the ingestion pipeline trigger face matching"
graphify path "events Lambda" "cascadeDelete Lambda"
graphify explain "EventAttendees stream"
```

`graphify-out/GRAPH_REPORT.md` also has a full written architecture review, for anyone who'd rather read than query.

---

## Cost: built entirely on the AWS Free Tier

Every service here fits comfortably inside AWS's Free Tier at this project's scale: Lambda's million free requests a month, DynamoDB on-demand's free read and write allowance, S3's free storage tier, CloudFront's free data transfer allowance, and Rekognition's free monthly face-processing allowance. Real spend during development stayed effectively at $0, entirely within what the Free Tier already covers. The two things worth watching as usage grows are Rekognition's per-image indexing cost once past the free monthly allowance, and S3 storage once past the free tier's cap. Compute stays essentially free at this scale, since nothing runs when nobody's uploading.

---

## Scaling past the defaults

Two numbers in this project are deliberately set to match a fresh AWS account's real, low default limits. This isn't a ceiling Glimpses needs, it's simply what a new account actually has until you ask AWS to raise it.

- **Lambda's account-wide concurrent execution limit.** New accounts often start around 10 concurrent executions total, shared across every Lambda in the account. `photo_processing_max_concurrency` (Step Functions, `state_machine` module) is tuned down to stay under that.
- **Rekognition's `IndexFaces`/`SearchFacesByImage` TPS quota.** Measured at 5 for this account, against a published default of 50.

For faster ingestion on larger events, request a service quota increase for both from the AWS Service Quotas console (`Lambda` for concurrent executions, `Rekognition` for the two TPS quotas above), then raise the corresponding Terraform variables to match. The pipeline's correctness doesn't depend on these numbers either way: Distributed Map's retry and backoff behavior, along with its tolerated-failure percentage, handle slower throughput gracefully regardless.

---

## Running it yourself

This is the deployment path for the repository as written: AWS region `ap-south-1`, AWS CLI profile `glimpses`, and AWS resource names beginning with `glimpses`. It uses two Terraform states and three kinds of Jenkins jobs: 21 backend/infrastructure modules, `frontend` for hosting, and `frontend-app` for the built React app. The fixed S3 bucket names must be available in your AWS account and globally; if another account already owns one, change the bucket names and matching hard-coded Jenkins S3 destinations before deploying.

The order matters: create the Terraform state bucket, deploy shared backend resources, deploy frontend hosting, deploy the Lambda code, deploy orchestration/auth/API Gateway, then build and publish the React app. In particular, `events` needs the frontend CloudFront domain for QR join links, while `frontend-app` needs Cognito and API Gateway outputs.

### 1. Prepare AWS access and local tools

Use a dedicated IAM principal with permission to create the AWS services in this repository; do not use root access keys. The original deployment used these AWS-managed policies: `AmazonDynamoDBFullAccess`, `AWSLambda_FullAccess`, `IAMFullAccess`, `AmazonS3FullAccess`, `AmazonAPIGatewayAdministrator`, `AWSStepFunctionsFullAccess`, `AmazonRekognitionFullAccess`, `CloudWatchFullAccess`, and `CloudFrontFullAccess`. It also used this custom policy for SNS, Cognito, EventBridge, EventBridge Scheduler, and WAF:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sns:*", "cognito-idp:*", "cognito-identity:*", "scheduler:*", "events:*", "wafv2:*"],
      "Resource": "*"
    }
  ]
}
```

These permissions are broad and intended for a dedicated deployment identity. Create its access key in IAM and keep the secret out of the repository.

The `email` Jenkins job additionally needs permission to create, read, and delete SES email identities. The SES production-access request also needs account-level SES permissions. Give these to the deployment identity before running the new job; the notification Lambda itself has only `ses:SendEmail` permission for the configured sender identity.

Install AWS CLI, Terraform 1.10 or newer, Python with `pip` and `zip`, Node.js with `npm`, and Jenkins with the Job DSL and Pipeline plugins. Jenkins must have access to the same AWS profile and tools. Configure the AWS CLI profile that the existing Jenkinsfiles use:

```bash
aws configure --profile glimpses
# Enter your access key, secret key, ap-south-1, and json when prompted.
aws sts get-caller-identity --profile glimpses
export AWS_PROFILE=glimpses
terraform version
```

Set `AWS_PROFILE=glimpses` in each new shell used for manual Terraform or AWS CLI commands. The Jenkinsfiles already set this profile internally, so it must also exist for the user running Jenkins.

### 2. Create the Terraform state bucket

Both `Infrastructure/providers.tf` and `Frontend/frontend/providers.tf` expect the same S3 bucket, `glimpses-terraform-state`, in `ap-south-1`. Terraform cannot create its own backend bucket. If you do not already own this bucket, create it once:

```bash
aws s3api create-bucket \
  --bucket glimpses-terraform-state \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1
aws s3api put-bucket-versioning \
  --bucket glimpses-terraform-state \
  --versioning-configuration Status=Enabled
aws s3api put-public-access-block \
  --bucket glimpses-terraform-state \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

The backend files use separate state keys: `glimpses/terraform.tfstate` for the backend and `glimpses/frontend/terraform.tfstate` for frontend hosting. Keep `use_lockfile = true` in both. If the bucket name is unavailable, pick a globally unique name and update **both** backend files before running `terraform init`.

### 3. Set deployment values and check quotas

Set `alarm_email` in `Infrastructure/variables.tf` to an address you control, or supply it as a Terraform variable for every backend apply. Confirm the SNS subscription email after the alarms module deploys. The guest email sender is the separate `ses_sender_email` variable, currently set to `hriday.mulchandani2027@gmail.com`; change the Terraform variable to use another sender. Keep `aws_region` aligned with the backend bucket region; this guide uses the default `ap-south-1` throughout.

Check the account's Rekognition quotas before deploying the state machine:

```bash
aws service-quotas list-service-quotas --service-code rekognition \
  --query "Quotas[?contains(QuotaName, 'IndexFaces') || contains(QuotaName, 'SearchFaces')]"
```

Set `rekognition_index_max_concurrency` and `rekognition_search_max_concurrency` in `Infrastructure/modules/state_machine/variables.tf` no higher than the corresponding quotas. Also check the Lambda concurrency limit against `photo_processing_max_concurrency`. The current defaults were tuned for the original account.

### Google Drive setup and deployment

1. In [Google Cloud Console](https://console.cloud.google.com/apis/library/drive.googleapis.com), select your project and enable Google Drive API. Create an API key under APIs & Services → Credentials and restrict its API access to Google Drive API. Glimpses uses API-key access to public folders only; no OAuth consent flow or service account is needed. This key is unrelated to Graphify's Gemini key.
2. In AWS Systems Manager → Parameter Store in `ap-south-1`, create a **Standard SecureString** parameter named `/glimpses/google-drive/api-key` and paste the key as its value. Use the default SSM encryption key. The secret is not stored in Terraform, source code, or the frontend. The new Lambda has access only to this parameter. Restart/redeploy its runtime after rotating the key because it caches the decrypted value per execution environment.
3. Give the Jenkins deployment identity `ssm:GetParameter` on that parameter for its presence check. The `drive_import` job checks the parameter name without printing or decrypting the secret before it builds and deploys the Lambda and workflow.
4. On an existing deployment, rerun `glimpses-seed`, then run **`buckets → db_api → drive_import → upload_status → api_gateway → frontend-app`**. `ingestion` must already be deployed. The original `state_machine` job does not need to run for this feature. On a fresh deployment, complete the Google/SSM setup before the new job in the normal order below.
5. Test a small public folder, an inaccessible folder, mixed photos/non-photos/subfolders, a duplicate import, and a larger folder that requires pagination. Check both the gallery and job counts. Local mocked tests and workflow validation do not replace a live Google/AWS smoke test.

### 4. Create the Jenkins jobs

The Lambda Terraform modules point at ZIP files in `glimpses-deploy-artifacts`. Their Jenkins jobs build and upload those ZIPs **before** applying each module, then update the Lambda code. A bare `terraform apply` for a Lambda on a fresh account will fail because its deployment ZIP does not exist yet.

In `Infrastructure/cicd/seed.groovy`, set `repoUrl` to your Git repository and `credentialsId` to a Jenkins Git credential that can read it. The generated jobs check out `main`; update `branch` there if your deployment branch has a different name. Commit and push configuration changes before running those jobs, because Jenkins reads the remote branch rather than your local working tree. Create a Jenkins job named `glimpses-seed` that checks out this repository, then runs `Infrastructure/cicd/seed.groovy` as its Job DSL script. The seed script reads the tracked `Infrastructure/cicd/jenkinsfiles.txt` from that checkout. An existing seed job that uses a workspace-root `jenkinsfiles.txt` still works: the updated script adds the dispatcher, email, notifications, and Drive import paths if that older list lacks them. If your seed job uses a pasted Job DSL script, update that script from the repository before rerunning it.

Run or rerun `glimpses-seed`. It creates or updates jobs named from the folder preceding `cicd`, including `email`, `notifications`, `frontend`, and `frontend-app`. Wait for each deployment job to succeed before starting the next one; they share Terraform state and should not apply concurrently.

### 5. Deploy shared backend resources, then frontend hosting

Run these Jenkins jobs in order:

```text
dynamodb → buckets → alarms → email → cloudfront → frontend
```

These jobs create the tables, S3 buckets, alerts, SES sender identity, and signed-photo CloudFront distribution. `frontend` applies `Frontend/frontend`, creating the separate `glimpses-frontend` S3 hosting bucket and its CloudFront distribution. It does **not** build or upload the React app yet. Verify that the frontend hosting output exists:

```bash
cd Frontend/frontend
terraform init
terraform output -raw distribution_domain_name
cd ../..
```

After the `email` job, open the AWS verification email sent to `hriday.mulchandani2027@gmail.com` and click its link. Check the identity's status in SES in `ap-south-1`. Request SES production access in that Region before running `notifications`: while SES is in its sandbox, it can only send to verified recipient addresses. AWS reviews production-access requests; Terraform cannot grant approval. In the request, describe the six transactional messages, the Profile preference, and the app URL. SES forwards bounce and complaint feedback to the sender mailbox; monitor that mailbox and stop sending to addresses that bounce or complain. Do not deploy the stream consumer until the identity is verified and production access is granted.

### 6. Deploy Lambda code and remaining backend services

Run these jobs in order:

```text
heic_converter → db_api → download → ingestion → drive_import → selfie_match_dispatcher → notifications → profile → upload_status
→ cascadeDelete → events → membership → gallery
→ state_machine → cognito → api_gateway
```

`selfie_match_dispatcher` needs ingestion deployed before it, and profile needs the dispatcher deployed before it. `cascadeDelete` must be ready before `events` and `gallery`, which invoke it. The `events` job reads the frontend distribution domain from the frontend Terraform state and passes it into its Terraform apply. `state_machine` needs the ingestion and `db_api` Lambda ARNs. `api_gateway` needs the API Lambda ARNs and Cognito user pool, so it comes last among backend jobs.
`notifications` reads the frontend distribution domain from the frontend Terraform state. Run `dynamodb` before it because the new Notifications table and Jobs stream are required. Run `cascadeDelete` after `notifications` because it invokes that Lambda when event cleanup succeeds. Rerun `api_gateway` and `frontend-app` to expose the Profile email switch.

The backend outputs needed by the browser should now be available:

```bash
cd Infrastructure
terraform init
terraform output -raw cognito_user_pool_id
terraform output -raw cognito_user_pool_client_id
terraform output -raw api_gateway_invoke_url
cd ..
```

### 7. Build and publish the React app

Run the **`frontend-app`** Jenkins job last. It reads the three backend outputs above and the `frontend` hosting bucket/distribution outputs, writes `Frontend/.env.production`, runs `npm ci` and `npm run build`, syncs `Frontend/dist/` to the hosting bucket, and invalidates CloudFront. The Vite build needs `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, and `VITE_API_BASE_URL`; the job fills them from Terraform, so you do not need to type them manually.

Get the live URL from the hosting state:

```bash
cd Frontend/frontend
terraform output -raw distribution_domain_name
```

Open the resulting domain over HTTPS, sign up, create an event, and test a photo upload. For later changes, rerun the job for the changed backend module, then rerun `frontend-app` when the React code or its Cognito/API configuration changes. Keep `frontend` for hosting infrastructure changes and `frontend-app` for the browser application.

---

## CI/CD (Jenkins)

Glimpses uses Jenkins running locally on a laptop, installed through Homebrew for the original deployment. The decision was practical: the deployment already used a local AWS CLI profile, and the project was built as independently deployable Terraform modules. Jenkins let each module keep its own visible build log and rerun path, while the seed script created the jobs from the repository. It also avoided repeating a long sequence of manual package, upload, and Terraform commands during development.

GitHub Actions could run these pipelines too. It would require a different runner and AWS authentication setup, plus workflows to replace the existing Jenkinsfiles and Job DSL seed. There is no GitHub Actions workflow in this repository. Jenkins was chosen for this project's local development workflow and for the clear one-module-per-job layout, not because GitHub Actions cannot deploy the architecture.

| Job group | Count | What a job does |
|---|---:|---|
| Shared infrastructure | 8 | Applies one Terraform module: DynamoDB, buckets, alarms, SES email identity, photo CloudFront, state machine, Cognito, or API Gateway. |
| Backend Lambdas | 13 | Packages that Lambda's Python code for AWS, uploads its ZIP to `glimpses-deploy-artifacts`, applies its Terraform module, and updates the deployed code. |
| Frontend hosting | 1 | Applies `Frontend/frontend` to create the S3 bucket and CloudFront distribution for the site. |
| React app | 1 | Reads Terraform outputs, builds `Frontend/`, syncs `dist/` to S3, and invalidates CloudFront. |

There are **21 backend/infrastructure module jobs plus `frontend` and `frontend-app`**, for 23 deployment jobs. Each Jenkinsfile lives beside the part it deploys. The `glimpses-seed` Job DSL script reads the tracked `Infrastructure/cicd/jenkinsfiles.txt` and creates or updates those jobs with their repository URL, Git credential, branch, and Jenkinsfile path. The exact file list, setup, and first-deploy order are in [Running it yourself](#running-it-yourself). The seed job creates jobs; it does not run the deployment sequence for you.

The jobs share Terraform state, so run dependent deployments in the documented order and do not run applies against the same state concurrently. On later changes, run only the affected job and any downstream job that needs its new outputs. For example, a React-only change needs `frontend-app`; a change to the frontend hosting distribution needs `frontend`, and may require `events` if the distribution domain changes because QR join links use that domain.

**Local Jenkins note:** a background service can have a smaller `PATH` than your interactive shell. Ensure Jenkins can find `python3`, `zip`, `terraform`, `aws`, and `npm`; the Lambda Jenkinsfiles use `python3 -m pip` rather than a bare `pip` command. Jenkins also needs access to the `glimpses` AWS CLI profile under the account that runs its jobs.

---

## License

Freely licensed, with no restrictions. Use this however you'd like: as a reference, as a starting point for your own event photo app, or deployed as-is for your own events. No attribution required, though it's always appreciated.
