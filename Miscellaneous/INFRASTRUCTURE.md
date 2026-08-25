# Infrastructure

Terraform, AWS provider `~> 6.0`, `required_version >= 1.10`. Region: `ap-south-1`. State: S3 backend, bucket `glimpses-terraform-state`, key `glimpses/terraform.tfstate`, native S3 lock (`use_lockfile = true`).

## Module layout

Root (`Infrastructure/`) wires everything via `imports.tf`. Two kinds of modules:

- **Shared modules** — live under `Infrastructure/modules/`: `dynamodb`, `buckets`, `alarms`, `cloudfront`, `cognito`, `api_gateway`, `state_machine`.
- **Per-Lambda modules** — live under `Backend/<lambda>/infra/`, one per Lambda (10 total): `heic_converter`, `db_api`, `download`, `ingestion`, `profile`, `events`, `membership`, `upload_status`, `gallery`, `cascadeDelete`.

Each per-Lambda module has the same file shape: `lambda.tf`, `iam_role.tf`, `iam_policies.tf`, `cloudwatch.tf`, `input.tf` (variables), `output.tf`. `cascadeDelete` and `ingestion` additionally have `event_source_mapping.tf` (DynamoDB Streams triggers). `events` additionally has `scheduler.tf` (EventBridge Scheduler).

```
Infrastructure/
├── providers.tf, variables.tf, imports.tf
├── modules/
│   ├── dynamodb/        (7 tables)
│   ├── buckets/          (2 buckets)
│   ├── alarms/           (1 SNS topic)
│   ├── cloudfront/       (1 distribution)
│   ├── cognito/          (1 user pool + 1 client)
│   ├── state_machine/    (1 Step Functions state machine + EventBridge rule)
│   └── api_gateway/      (1 REST API, 30 routes, WAF, Cognito authorizer)
└── cicd/seed.groovy      (Jenkins job-seeding script)

Backend/<lambda>/infra/   (× 10, one per Lambda)
```

Dependency order (`imports.tf`): `dynamodb`/`buckets`/`alarms` (no deps) → `cloudfront` (needs `buckets`) → `heic_converter` → `db_api` → `download`/`ingestion`/`profile`/`upload_status` → `events`/`membership`/`gallery` → `cascade_delete` → `state_machine` (needs `ingestion`, `db_api`) → `cognito` → `api_gateway` (needs every Lambda + `cognito`).

## Lambda function config (common to all 10)

`runtime = python3.13`, `architectures = ["x86_64"]`, deployed from `s3://<name_prefix>-deploy-artifacts/<lambda>/build.zip`, `handler = routeHandler.lambda_handler` (or the equivalent step-entry handler for `ingestion`), `lifecycle { ignore_changes = [s3_key, source_code_hash] }` (Jenkins updates code out-of-band of `terraform apply`). Each gets its own `aws_cloudwatch_log_group` (3-day retention) and an `Errors > 0` `aws_cloudwatch_metric_alarm` wired to the shared SNS topic.

## DynamoDB (`modules/dynamodb`) — 7 tables, all `PAY_PER_REQUEST`

| Table | Hash key | Range key | GSIs | Stream | TTL |
|---|---|---|---|---|---|
| `Users` | `userID` | — | — | — | — |
| `Events` | `eventID` | — | `organizerID-status-index`, `accessCode-index`, `status-lastUploadAt-index` | `OLD_IMAGE` | `deleteAt` |
| `Photos` | `photoID` | — | `eventID-uploadedAtFilename-index`, `eventID-contentHash-index` | — | — |
| `Faces` | `rekognitionFaceID` | — | `eventID-photoID-index` | — | — |
| `EventAttendees` | `userID` | `eventID` | `eventID-status-index` | `NEW_AND_OLD_IMAGES` | — |
| `Jobs` | `jobId` | — | `eventUploaderKey-startedAt-index` | — | — |
| `Downloads` | `downloadId` | — | — | — | — |

Streams consumed by:
- `Events` stream → `cascadeDelete` Lambda (`event_source_mapping.tf`), filtered to `eventName = REMOVE` where `userIdentity.type = Service` / `principalId = dynamodb.amazonaws.com` (TTL-driven deletes only).
- `EventAttendees` stream → `ingestion` Lambda's `MatchOneAttendee` entry point, filtered to `OldImage.status != ATTENDEE` AND `NewImage.status = ATTENDEE`.

## S3 (`modules/buckets`) — 2 buckets

- `<name_prefix>-photos` — public access fully blocked, EventBridge notifications enabled (`aws_s3_bucket_notification.photos_eventbridge`), lifecycle rule expires `downloads/` prefix after `var.downloads_expiration_days` days. Prefixes: `uploads/`, `photos/`, `thumbnails/`, `qrcodes/`, `selfies/`, `downloads/`.
- `<name_prefix>-deploy-artifacts` — public access fully blocked, holds each Lambda's `build.zip`.

## CloudFront (`modules/cloudfront`)

1 distribution, single S3 origin (`photos` bucket) via Origin Access Control (OAC, sigv4). `default_cache_behavior`: `GET`/`HEAD` only, no query strings, no cookies forwarded, `redirect-to-https`. Default CloudFront cert (no custom domain). Bucket policy scopes CloudFront's OAC access to exactly `photos/*`, `thumbnails/*`, `qrcodes/*` — `uploads/`, `selfies/`, `downloads/` are never CloudFront-fronted.

## Cognito (`modules/cognito`)

1 User Pool: `username_attributes = [email]`, auto-verify email, `mfa_configuration = OFF`, password policy (min 8, upper/lower/number required, symbol not required), custom-required `name` schema attribute, account recovery via verified email. 1 App Client: no secret, auth flows `ALLOW_USER_PASSWORD_AUTH` / `ALLOW_REFRESH_TOKEN_AUTH` / `ALLOW_USER_SRP_AUTH`, 30-day refresh token, `prevent_user_existence_errors = ENABLED`.

## API Gateway (`modules/api_gateway`)

1 REST API (`REGIONAL`), 1 `COGNITO_USER_POOLS` authorizer applied uniformly to all 30 routes, 1 request validator (`validate_request_body = true`) applied wherever a JSON-schema model exists, 1 `prod` stage, WAF Web ACL attached to that stage.

**WAF** (`waf.tf`): 1 Web ACL, default action `allow`, 1 rate-based rule (`rate-limit-per-ip`, 2000 req / 5 min per IP → block), CloudWatch metrics + sampling on.

**Request validation models** (`models.tf`): `ProfileUpdate`, `EventCreate`, `EventUpdate`, `PhotoIDsBody`, `DownloadKickoffBody`.

**Route tree** (30 routes total — full request/response shapes documented in `BACKEND.md`):

```
/profile                                    GET, PUT
/profile/selfie                             PUT, DELETE
/profile/selfie/confirm                     POST

/events                                     POST, GET
/events/{eventId}                           GET, PUT, DELETE
/events/{eventId}/archive                   POST
/events/{eventId}/stats                     GET
/events/{eventId}/qrcode                    GET

/events/{eventId}/join                      POST
/events/{eventId}/leave                     POST
/events/{eventId}/attendees                 GET
/events/{eventId}/attendees/{userId}/admit  POST
/events/{eventId}/attendees/{userId}/deny   POST
/events/{eventId}/attendees/{userId}/eject  POST

/events/{eventId}/upload-url                POST
/events/{eventId}/jobs/{jobId}/status       GET
/events/{eventId}/jobs/latest               GET

/events/{eventId}/photos                    GET
/events/{eventId}/photos/{photoId}          GET, DELETE
/events/{eventId}/photos/download-urls      POST
/events/{eventId}/photos/bulk-delete        POST

/events/{eventId}/photos/download           POST
/events/{eventId}/downloads/{downloadId}/status  GET
```

Each Lambda gets an `aws_lambda_permission` granting `apigateway.amazonaws.com` invoke rights scoped to `<rest_api_execution_arn>/*/*`.

```
Browser
  │  Authorization: Bearer <Cognito ID token>
  ▼
CloudFront (photos/thumbnails/qrcodes only, GET/HEAD)   API Gateway (prod stage, WAF → Cognito authorizer)
  │                                                            │
  ▼                                                            ▼
S3 photos bucket                                    Lambda (profile / events / membership /
                                                      upload_status / gallery / download)
                                                            │
                                                            ▼
                                                      DynamoDB / S3 / Rekognition
```

## Step Functions (`modules/state_machine`) — ingestion pipeline

1 `STANDARD` state machine, definition in JSONata (`QueryLanguage: JSONata`), template at `templates/ingestion_pipeline.asl.json.tftpl`. Triggered by an EventBridge rule (`eventbridge.tf`) on `aws.s3` `Object Created` matching key pattern `uploads/event/*/user/*/job/*/original.zip`, which starts an execution via a dedicated `events.amazonaws.com`-assumed IAM role.

State flow:

```
InitializeJob (db_api: create)
      │
      ▼
UpdateStatusExtracting (db_api: mark_extracting)
      │
      ▼
Extract (ingestion: step=extract)
      │
      ▼
UpdateStatusIndexing (db_api: mark_indexing)
      │
      ▼
IndexPhotos ── Distributed Map, S3 ItemReader over manifest ──▶ IndexOnePhoto (ingestion: step=index_one_photo)  [× N photos, MaxConcurrency=rekognition_index_max_concurrency]
      │
      ▼
Finalize (ingestion: step=finalize → succeededCount/failedCount)
      │
      ▼
CheckIndexingOutcome ─── succeededCount = 0 ──▶ JobFailed (db_api: mark_failed) ──▶ IngestionFailed
      │ else
      ▼
UpdateStatusMatching (db_api: mark_matching)
      │
      ▼
ListAttendees (ingestion: step=list_attendees)
      │
      ▼
MatchAttendees ── Distributed Map over attendeeIDs ──▶ MatchOneAttendeeBatch (ingestion: step=match_attendees)  [× N attendees, MaxConcurrency=rekognition_search_max_concurrency]
      │
      ▼
UpdateJobStatus (db_api: mark_success, unconditional)
      │
      ▼
IngestionSucceeded (Succeed)
```

Any state's `Catch` (except `InitializeJob`'s, which has no `Jobs` row yet to update) routes to `JobFailed` → `db_api: mark_failed` → `IngestionFailed` (`Fail` state). Every `Task` state retries 3× (`IntervalSeconds=2`, `BackoffRate=2`) on `States.ALL` before falling through to `Catch`.

IAM: state machine's execution role can `lambda:InvokeFunction` on `ingestion` and `db_api` only, `s3:GetObject` on `uploads/*`, and self-manage its own Distributed Map executions (`states:StartExecution`/`DescribeExecution`/`StopExecution` scoped to its own state machine ARN).

## CascadeDelete + MatchOneAttendee — stream-driven flows

```
DELETE /events/{id}  or  DELETE .../photos/{id}          EventAttendees row: status → ATTENDEE
      │ (async invoke)                                          │ (DynamoDB Stream)
      ▼                                                          ▼
CascadeDelete Lambda                                     ingestion Lambda (MatchOneAttendee entry point)
      │                                                          │
      ▼                                                          ▼
tears down Photos/Faces/EventAttendees rows,            SearchFaces against event's Rekognition
S3 objects, Rekognition collection as needed             collection, updates matchedPhotoIDs

Events table TTL expiry (deleteAt) ──▶ Stream REMOVE event ──▶ CascadeDelete Lambda (same path as above)
```

## Alarms (`modules/alarms`)

1 SNS topic (`<name_prefix>-alerts`), 1 email subscription (`var.alarm_email`). Every Lambda's `Errors > 0` alarm (1 evaluation period, 5 min) publishes here.

## CI/CD (Jenkins, local/Homebrew-installed, not AWS-provisioned)

17 jobs, one per module, each with its own `cicd/Jenkinsfile` (`agent any`, `AWS_PROFILE = glimpses` env var, stages: `terraform init` → `terraform validate` → `terraform apply -target=module.<x> -auto-approve`, all run from the `Infrastructure/` directory regardless of which module's Jenkinsfile it is). `Infrastructure/cicd/seed.groovy` reads `jenkinsfiles.txt` and auto-creates a `pipelineJob` per path via the JobDSL/XML API, pointed at `HridayBuilds/Glimpses` on `main`.

Fixed run order: `dynamodb` / `buckets` / `alarms` → `cloudfront` → all 10 per-Lambda jobs → `state_machine` → `cognito` → `api_gateway` (last — depends on every other module's output).
