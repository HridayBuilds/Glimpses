# Backend

## API_RESPONSES

Every route below is fronted by API Gateway (`prod` stage), goes through the WAF Web ACL, and requires Cognito auth — **every single route uses the `COGNITO_USER_POOLS` authorizer**, no exceptions, no public routes. Confirmed in `Infrastructure/modules/api_gateway/api_gateway.tf`: `aws_api_gateway_method.route` sets `authorization = "COGNITO_USER_POOLS"` on every route in `local.routes` with no per-route override.

**Coverage check (2026-08-25):** all 30 routes across `local.routes` (`profile` ×5, `events` ×8, `membership` ×6, `upload_status` ×3, `gallery` ×5, `download` ×2 — verified against every `routes_*.tf`) are documented below — this file is the complete, current set of endpoints the frontend can call.

**Auth header:** `Authorization: Bearer <token>` — **must be the Cognito ID token, not the access token.** The authorizer checks the `aud` claim, which only ID tokens carry (access tokens carry `client_id` instead, no `aud`) — an access token here silently fails with a `401`. Get the ID token from `initiate-auth`'s `AuthenticationResult.IdToken` (or the browser SDK's equivalent).

**Error shape — important gap, not yet fixed:** no Lambda registers a Powertools exception handler, so any raised `ValueError` (not found, not authorized, bad state, etc.) isn't turned into a clean 4xx — it crashes the invocation and API Gateway returns a generic:
```json
{"message": "Internal server error"}
```
with **HTTP 502**, regardless of whether the real cause was "not found," "forbidden," or an actual bug. The frontend currently cannot distinguish these by status code — only the (currently unhelpful) response body. Treat `502` as "some `ValueError` was raised" until this is fixed with proper exception handling.

**IDs:** `userID` is always the Cognito `sub` claim (a UUID), taken server-side from the token — never something the client sends.

---

### `profile` — Lambda: `glimpses-profile`

#### `GET /profile`
No body. Looks up the caller's row in `Users`; if missing, creates it from the token's `sub`/`email`/`name` claims (lazy upsert), then returns it.

Response `200`:
```json
{
  "userID": "41637d5a-10c1-...",
  "displayName": "Hriday M",
  "email": "hridaymulchandani21@gmail.com",
  "selfieUrl": "https://...presigned-get-url... (only present if a selfie exists)"
}
```

#### `PUT /profile`
Request body (validated by API Gateway model `ProfileUpdate`):
```json
{ "displayName": "New Name" }
```
`displayName` required, non-empty. Response `200`:
```json
{ "userID": "41637d5a-10c1-..." }
```

#### `PUT /profile/selfie`
No body. Mints a pre-signed S3 PUT URL — the browser uploads the selfie JPEG directly to S3, this Lambda never sees the bytes.

Response `200`:
```json
{ "uploadUrl": "https://...presigned-put-url..." }
```

#### `POST /profile/selfie/confirm`
No body. Call after the browser's direct S3 PUT finishes. Runs Rekognition `DetectFaces` on what actually landed; if face count isn't exactly 1, deletes the object and raises (→ `502`, see error-shape note above).

Response `200`:
```json
{ "confirmed": true }
```

#### `DELETE /profile/selfie`
No body. Deletes the selfie object.

Response `200`:
```json
{ "deleted": true }
```

---

### `events` — Lambda: `glimpses-events`

Every route here requires the caller to be the event's `organizerID` (server-side check against the `Events` table) except creation itself.

#### `POST /events`
Request body (model `EventCreate`):
```json
{ "name": "Priya's Wedding", "description": "optional" }
```
`name` required. Creates a Rekognition collection, a unique 6-char access code, a QR code (stored to S3), and the `Events` row.

Response `200`:
```json
{
  "eventID": "uuid",
  "name": "Priya's Wedding",
  "description": "",
  "status": "ACTIVE",
  "joinPolicy": "OPEN",
  "contributionPolicy": "ATTENDEES_CAN_ADD",
  "accessCode": "7F3K9M",
  "createdAt": "2026-08-25T05:32:00+00:00"
}
```

#### `GET /events`
No body. Lists all events the caller organizes.

Response `200`: array of the same shape as the create response above.

#### `GET /events/{eventId}`
Response `200`: same single-event shape as above.

#### `PUT /events/{eventId}`
Request body (model `EventUpdate`, all fields optional):
```json
{
  "name": "New name",
  "description": "New description",
  "joinPolicy": "OPEN | INVITE_ONLY (P-nn values)",
  "contributionPolicy": "ATTENDEES_CAN_ADD | ORGANIZER_ONLY (P-nn values)"
}
```
Only `ACTIVE` events can be edited. Only fields actually present in the body get updated.

Response `200`:
```json
{ "eventID": "uuid" }
```

#### `DELETE /events/{eventId}`
No body. Fires `CascadeDelete` (async) to tear down the whole event (photos, faces, attendees, etc.).

Response `200`:
```json
{ "deleted": true }
```

#### `POST /events/{eventId}/archive`
No body. Deletes the Rekognition collection, marks the event `ARCHIVED`, sets a 30-day delete-at timestamp.

Response `200`:
```json
{ "archived": true }
```

#### `GET /events/{eventId}/stats`
Response `200`:
```json
{ "photoCount": 128, "storageBytes": 524288000 }
```

#### `GET /events/{eventId}/qrcode`
Response `200`:
```json
{ "qrcodeUrl": "https://<cloudfront-domain>/qrcodes/event/{eventId}/qrcode.png" }
```

---

### `membership` — Lambda: `glimpses-membership`

Attendee status enum: `PENDING` / `ATTENDEE` / `LEFT` / `BLOCKED` (rows are never deleted, only transitioned).

#### `POST /events/{eventId}/join`
No body. If the event's `joinPolicy` is `OPEN`, caller becomes `ATTENDEE` immediately; otherwise `PENDING` (needs organizer admit). Blocked users can't rejoin.

Response `200`:
```json
{ "eventID": "uuid", "status": "ATTENDEE" }
```

#### `POST /events/{eventId}/leave`
No body. Only valid if currently `ATTENDEE`.

Response `200`:
```json
{ "eventID": "uuid", "status": "LEFT" }
```

#### `GET /events/{eventId}/attendees`
Organizer-only. Query param: `?status=PENDING` (or `ATTENDEE`/`LEFT`/`BLOCKED`) — filters the list.

Response `200`:
```json
{
  "attendees": [
    { "userID": "uuid", "status": "PENDING", "displayName": "Meera", "email": "meera@example.com" }
  ]
}
```

#### `POST /events/{eventId}/attendees/{userId}/admit`
Organizer-only. Requires target is currently `PENDING`.

Response `200`:
```json
{ "userID": "uuid", "status": "ATTENDEE" }
```

#### `POST /events/{eventId}/attendees/{userId}/deny`
Organizer-only. Requires target is currently `PENDING`. Denying sets status to `BLOCKED` (not deleted).

Response `200`:
```json
{ "userID": "uuid", "status": "BLOCKED" }
```

#### `POST /events/{eventId}/attendees/{userId}/eject`
Organizer-only. Requires target is currently `ATTENDEE`. Sets status to `BLOCKED`.

Response `200`:
```json
{ "userID": "uuid", "status": "BLOCKED" }
```

---

### `upload_status` — Lambda: `glimpses-upload_status`

Job status enum: `CREATED → EXTRACTING → INDEXING → MATCHING → SUCCESS` / `FAILED` (two-way terminal).

#### `POST /events/{eventId}/upload-url`
No body. Mints a pre-signed S3 PUT URL for a zip of photos, and a new `jobId`.

Response `200`:
```json
{ "jobId": "uuid", "uploadUrl": "https://...presigned-put-url..." }
```

#### `GET /events/{eventId}/jobs/{jobId}/status`
Response `200`:
```json
{
  "jobId": "uuid",
  "status": "INDEXING",
  "startedAt": "2026-08-25T05:32:00+00:00",
  "succeededCount": 12,
  "failedCount": 0
}
```

#### `GET /events/{eventId}/jobs/latest`
No path param for job — returns the caller's most recent job for this event. Same response shape as above. Raises (→ `502`) if no jobs exist yet.

---

### `gallery` — Lambda: `glimpses-gallery`

Photo shape used across every route in this Lambda:
```json
{
  "photoID": "uuid",
  "eventID": "uuid",
  "uploaderID": "uuid",
  "uploaderDisplayName": "Meera",
  "filename": "IMG_1234.jpg",
  "uploadedAt": "2026-08-25T05:32:00+00:00",
  "sizeBytes": 2048576,
  "photoUrl": "https://<cloudfront-domain>/photos/...",
  "thumbnailUrl": "https://<cloudfront-domain>/thumbnails/..."
}
```

#### `GET /events/{eventId}/photos`
Query params:
- `?mine=true` — only photos matched to the caller's face (via `EventAttendees.matchedPhotoIDs`), sorted newest first, **no pagination** (`cursor` always `null`).
- `?cursor=<opaque base64 string>` — paginate the full event gallery (50/page) when `mine` isn't set.

Response `200`:
```json
{ "photos": [ /* photo objects above */ ], "cursor": "opaque-string-or-null" }
```

#### `GET /events/{eventId}/photos/{photoId}`
Response `200`: single photo object (shape above).

#### `POST /events/{eventId}/photos/download-urls`
Request body (model `PhotoIDsBody`):
```json
{ "photoIDs": ["uuid1", "uuid2"] }
```
Response `200`:
```json
{
  "downloadUrls": [
    { "photoID": "uuid1", "downloadUrl": "https://...presigned-get-url..." }
  ]
}
```
(Note: this mints direct presigned GET URLs per photo — different from the `download` Lambda's server-side ZIP flow below.)

#### `DELETE /events/{eventId}/photos/{photoId}`
No body. Caller must be the photo's uploader or the event's organizer, and the event must be `ACTIVE` (archived events are permanently read-only). Fires `CascadeDelete` async.

Response `200`:
```json
{ "deleted": true }
```

#### `POST /events/{eventId}/photos/bulk-delete`
Request body (model `PhotoIDsBody`):
```json
{ "photoIDs": ["uuid1", "uuid2"] }
```
Silently filters to only photos the caller is authorized to delete (uploader or organizer) — doesn't error on unauthorized IDs, just excludes them.

Response `200`:
```json
{ "deletedPhotoIDs": ["uuid1"] }
```

---

### `download` — Lambda: `glimpses-download`

Server-side ZIP building (for bulk download of a whole event/selection, as opposed to `gallery`'s per-photo presigned URLs above).

#### `POST /events/{eventId}/photos/download`
Request body (model `DownloadKickoffBody`, optional):
```json
{ "photoIds": ["uuid1", "uuid2"] }
```
Omit `photoIds` (or send `null`) to download every photo in the event. Kicks off async ZIP building (self-invokes the same Lambda), returns immediately.

Response `200`:
```json
{ "downloadId": "uuid" }
```

#### `GET /events/{eventId}/downloads/{downloadId}/status`
Response `200`, while building:
```json
{ "status": "PENDING" }
```
Response `200`, once ready:
```json
{ "status": "READY", "downloadUrl": "https://...presigned-get-url-for-the-zip..." }
```
(`status` can also be `FAILED`, with no `downloadUrl`.)

---

### Not exposed via API Gateway (internal-only, no frontend-facing routes)

- **`db_api`** — internal action-dispatch Lambda other Lambdas/the state machine call directly, not via HTTP.
- **`ingestion`** — Step Functions state machine steps (`Extract`/`IndexOnePhoto`/`Finalize`/`ListAttendees`/`MatchAttendees`), plus the `MatchOneAttendee` DynamoDB Stream entry point. No HTTP surface.
- **`heic_converter`** — invoked internally during `Extract`, converts HEIC to JPEG. No HTTP surface.
- **`CascadeDelete`** — invoked async by `events`/`gallery` for event/photo teardown, plus its own DynamoDB Stream TTL-delete entry point. No HTTP surface.
