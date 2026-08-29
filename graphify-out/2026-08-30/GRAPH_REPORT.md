# Graph Report - Glimpses  (2026-08-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1549 nodes · 2912 edges · 160 communities (123 shown, 37 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b414e5e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- aws_api_gateway_rest_api.this
- cascadeDelete/src/DAO/dao.py
- events/src/Manager/manager.py
- dependencies
- ingestion/infra/input.tf
- download/src/DAO/dao.py
- gallery/src/Manager/manager.py
- iam.tf
- App.jsx
- membership/src/Manager/manager.py
- profile/src/Manager/manager.py
- cascadeDelete/infra/input.tf
- Infrastructure/imports.tf
- membership/test/unit/test_manager.py
- events/infra/input.tf
- download/infra/input.tf
- gallery/test/integration/test_route_handler.py
- handle_process_one_photo
- output.table_arns
- upload_status/src/Manager/manager.py
- Gallery.jsx
- JoinEvent.jsx
- convert_and_store
- membership/test/integration/test_route_handler.py
- db_api/src/Manager/manager.py
- aws_s3_bucket.photos
- react
- Profile.jsx
- gallery/test/unit/test_manager.py
- gallery/infra/input.tf
- upload_status/test/integration/test_route_handler.py
- aws_s3_bucket.hosting
- HowItWorks.jsx
- README.md
- events/test/integration/test_route_handler.py
- events/test/unit/test_manager.py
- ingestion/src/DAO/dao.py
- EventAnalytics.jsx
- put_object
- React + Vite starter template
- profile/test/integration/test_route_handler.py
- aws_cloudfront_distribution.photos
- cognito.js
- eventsApi.js
- aws-lambda-powertools (library)
- upload_status/test/unit/test_manager.py
- events/infra/iam_policies.tf
- gallery/infra/iam_policies.tf
- handle_stage
- membership/infra/input.tf
- match_attendees.py
- download/test/unit/test_manager.py
- membershipApi.js
- state_machine/.terraform.lock.hcl
- Header.jsx
- upload_status/infra/input.tf
- aws_cognito_user_pool.this
- aws_sns_topic.alerts
- ingestion/test/integration/test_route_handler.py
- profile/infra/input.tf
- .oxlintrc.json
- UploadFlow.jsx
- sniff_format
- membership/infra/iam_policies.tf
- profile/infra/iam_policies.tf
- upload_status/infra/iam_policies.tf
- db_api/infra/input.tf
- ingestion/src/Manager/manager.py
- test_build_photos_manifest.py
- module.hosting
- test_delete_event.py
- heic_converter/infra/input.tf
- cascadeDelete/infra/iam_role.tf
- db_api/infra/iam_role.tf
- download/infra/iam_role.tf
- events/infra/iam_role.tf
- gallery/infra/iam_role.tf
- heic_converter/infra/iam_role.tf
- ingestion/infra/iam_role.tf
- membership/infra/iam_role.tf
- profile/infra/iam_role.tf
- upload_status/infra/iam_role.tf
- provider.aws
- cascadeDelete/infra/cloudwatch.tf
- cascadeDelete/infra/output.tf
- db_api/infra/cloudwatch.tf
- db_api/infra/iam_policies.tf
- db_api/infra/output.tf
- download/infra/cloudwatch.tf
- download/infra/output.tf
- events/infra/cloudwatch.tf
- events/infra/output.tf
- gallery/infra/cloudwatch.tf
- gallery/infra/output.tf
- heic_converter/infra/cloudwatch.tf
- heic_converter/infra/iam_policies.tf
- heic_converter/infra/output.tf
- ingestion/infra/cloudwatch.tf
- ingestion/infra/output.tf
- membership/infra/cloudwatch.tf
- membership/infra/output.tf
- profile/infra/cloudwatch.tf
- profile/infra/output.tf
- upload_status/infra/cloudwatch.tf
- upload_status/infra/output.tf
- cascadeDelete/infra/lambda.tf
- db_api/infra/lambda.tf
- heic_converter/infra/lambda.tf
- membership/infra/lambda.tf
- infra/.terraform.lock.hcl
- profile/infra/lambda.tf
- upload_status/infra/lambda.tf
- provider.registry.terraform.io/hashicorp/aws
- frontend/.terraform.lock.hcl
- Frontend index.html entry point
- Infrastructure/.terraform.lock.hcl

## God Nodes (most connected - your core abstractions)
1. `aws_api_gateway_rest_api.this` - 57 edges
2. `react` - 23 edges
3. `_event()` - 19 edges
4. `handle_process_one_photo()` - 17 edges
5. `useAuth()` - 17 edges
6. `delete_event_cascade()` - 15 edges
7. `_attendee()` - 14 edges
8. `aws_api_gateway_resource.event_id` - 14 edges
9. `aws_api_gateway_deployment.this` - 13 edges
10. `module.buckets` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_list_my_events_returns_only_pending_and_attendee_rows()` --calls--> `_full_event()`  [INFERRED]
  Backend/events/test/integration/test_route_handler.py → Backend/membership/test/unit/test_manager.py
- `Home()` --indirect_call--> `getProfile()`  [INFERRED]
  Frontend/src/pages/app/Home.jsx → Frontend/src/lib/profileApi.js
- `test_delete_event_cascades_photos_faces_attendees_and_row()` --calls--> `lambda_handler()`  [INFERRED]
  Backend/cascadeDelete/test/integration/test_route_handler.py → Backend/cascadeDelete/src/routeHandler.py
- `test_delete_event_is_a_no_op_when_already_gone()` --calls--> `lambda_handler()`  [INFERRED]
  Backend/cascadeDelete/test/integration/test_route_handler.py → Backend/cascadeDelete/src/routeHandler.py
- `test_delete_photos_cascades_faces_row_s3_and_decrements_counters()` --calls--> `lambda_handler()`  [INFERRED]
  Backend/cascadeDelete/test/integration/test_route_handler.py → Backend/cascadeDelete/src/routeHandler.py

## Import Cycles
- None detected.

## Communities (160 total, 37 thin omitted)

### Community 0 - "aws_api_gateway_rest_api.this"
Cohesion: 0.06
Nodes (82): aws_api_gateway_authorizer.cognito, aws_api_gateway_deployment.this, aws_api_gateway_gateway_response.default_4xx, aws_api_gateway_gateway_response.default_5xx, aws_api_gateway_integration.options, aws_api_gateway_integration_response.options, aws_api_gateway_integration.route, aws_api_gateway_method.options (+74 more)

### Community 1 - "cascadeDelete/src/DAO/dao.py"
Cohesion: 0.10
Nodes (40): batch_delete_attendees(), batch_delete_faces(), batch_delete_photos(), decrement_event_counters(), delete_collection(), delete_event_row(), delete_faces_from_collection(), delete_photo_row() (+32 more)

### Community 2 - "events/src/Manager/manager.py"
Cohesion: 0.10
Nodes (50): access_code_exists(), batch_get_events(), count_attendees(), create_collection(), delete_collection(), _dynamodb(), _event_attendees_table(), _events_table() (+42 more)

### Community 3 - "dependencies"
Cohesion: 0.04
Nodes (47): amazon-cognito-identity-js, axios, dependencies, amazon-cognito-identity-js, axios, jsqr, jszip, motion (+39 more)

### Community 4 - "ingestion/infra/input.tf"
Cohesion: 0.06
Nodes (37): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access (+29 more)

### Community 5 - "download/src/DAO/dao.py"
Cohesion: 0.11
Nodes (34): abort_multipart_upload(), _batch_get_photo_keys(), complete_multipart_upload(), create_download(), create_multipart_upload(), _downloads_table(), generate_presigned_url(), get_download() (+26 more)

### Community 6 - "gallery/src/Manager/manager.py"
Cohesion: 0.11
Nodes (35): batch_get_photos(), _event_attendees_table(), _events_table(), generate_presigned_url(), get_attendee(), get_event(), get_photo_by_id(), invoke_cascade_delete() (+27 more)

### Community 7 - "iam.tf"
Cohesion: 0.12
Nodes (32): aws_cloudwatch_event_rule.upload_complete, aws_cloudwatch_event_target.start_ingestion, aws_iam_role.eventbridge_start_execution, aws_iam_role_policy.distributed_map_self_execution, aws_iam_role_policy.eventbridge_start_execution, aws_iam_role_policy.invoke_db_api, aws_iam_role_policy.invoke_ingestion, aws_iam_role_policy.manifest_access (+24 more)

### Community 8 - "App.jsx"
Cohesion: 0.16
Nodes (16): App(), AuthShell(), RequireAuth(), AuthContext, useAuth(), userFromSession(), queryClient, ForgotPassword() (+8 more)

### Community 9 - "membership/src/Manager/manager.py"
Cohesion: 0.16
Nodes (32): _dynamodb(), _event_attendees_table(), _events_table(), get_attendee(), get_event(), get_event_by_access_code(), get_users(), list_attendees_by_status() (+24 more)

### Community 10 - "profile/src/Manager/manager.py"
Cohesion: 0.14
Nodes (29): create_user(), delete_object(), detect_face_count(), _dynamodb(), generate_presigned_get_url(), generate_presigned_put_url(), get_user(), _rekognition() (+21 more)

### Community 11 - "cascadeDelete/infra/input.tf"
Cohesion: 0.08
Nodes (27): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access (+19 more)

### Community 12 - "Infrastructure/imports.tf"
Cohesion: 0.20
Nodes (24): module.alarms, module.api_gateway, module.buckets, module.cascade_delete, module.cloudfront, module.cognito, module.db_api, module.download (+16 more)

### Community 13 - "membership/test/unit/test_manager.py"
Cohesion: 0.18
Nodes (25): _attendee(), _event(), _full_event(), test_admit_attendee_rejects_non_pending(), test_admit_attendee_transitions_pending_to_attendee(), test_deny_attendee_transitions_pending_to_blocked(), test_eject_attendee_rejects_non_attendee(), test_eject_attendee_transitions_attendee_to_blocked() (+17 more)

### Community 14 - "events/infra/input.tf"
Cohesion: 0.10
Nodes (20): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+12 more)

### Community 15 - "download/infra/input.tf"
Cohesion: 0.11
Nodes (18): aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.photos_access, data.aws_iam_policy_document.photos_bucket_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn (+10 more)

### Community 16 - "gallery/test/integration/test_route_handler.py"
Cohesion: 0.45
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_photos_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 17 - "handle_process_one_photo"
Cohesion: 0.16
Nodes (18): compute_content_hash(), make_thumbnail(), normalize_to_jpeg(), handle_process_one_photo(), test_computes_sha256_hash(), test_different_bytes_produce_different_hash(), test_same_bytes_produce_same_hash(), test_process_one_photo_converts_heic_via_invoke() (+10 more)

### Community 18 - "output.table_arns"
Cohesion: 0.17
Nodes (12): aws_dynamodb_table.downloads, aws_dynamodb_table.event_attendees, aws_dynamodb_table.events, aws_dynamodb_table.faces, aws_dynamodb_table.jobs, aws_dynamodb_table.photos, aws_dynamodb_table.users, output.event_attendees_stream_arn (+4 more)

### Community 19 - "upload_status/src/Manager/manager.py"
Cohesion: 0.21
Nodes (17): _events_table(), generate_presigned_put_url(), get_event(), get_job(), _jobs_table(), query_latest_job(), _s3(), get_job_status() (+9 more)

### Community 20 - "Gallery.jsx"
Cohesion: 0.23
Nodes (14): ConfirmDialog(), EventMenu(), Gallery(), formatDate(), PhotoViewer(), api, getDownloadStatus(), requestDownload() (+6 more)

### Community 21 - "JoinEvent.jsx"
Cohesion: 0.19
Nodes (15): QRScanner(), scanLoop(), startCamera(), CameraCapture(), startCamera(), cameraErrorMessage(), BARE_CODE_RE, decodeQRFromFile() (+7 more)

### Community 22 - "convert_and_store"
Cohesion: 0.16
Nodes (12): heic_to_jpeg(), get_object(), put_object(), handle(), convert_and_store(), lambda_handler(), inject_lambda_context, _FakeLambdaContext (+4 more)

### Community 23 - "membership/test/integration/test_route_handler.py"
Cohesion: 0.43
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_users_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 24 - "db_api/src/Manager/manager.py"
Cohesion: 0.18
Nodes (13): create_job(), _table(), update_job_status(), handle(), _create(), handle_action(), _update_status(), lambda_handler() (+5 more)

### Community 25 - "aws_s3_bucket.photos"
Cohesion: 0.18
Nodes (14): aws_s3_bucket_cors_configuration.photos, aws_s3_bucket.deploy_artifacts, aws_s3_bucket_lifecycle_configuration.photos, aws_s3_bucket_notification.photos_eventbridge, aws_s3_bucket.photos, aws_s3_bucket_public_access_block.deploy_artifacts, aws_s3_bucket_public_access_block.photos, output.deploy_artifacts_bucket_arn (+6 more)

### Community 26 - "react"
Cohesion: 0.17
Nodes (16): plugins, DEFAULT_MESSAGES, LoadingSpinner(), SelfieToast(), getMyEvents(), getOrganizedEvents(), getEventInfo(), EventEntry() (+8 more)

### Community 27 - "Profile.jsx"
Cohesion: 0.47
Nodes (6): SelfieOptionsSheet(), deleteSelfie(), getProfile(), updateProfile(), uploadSelfie(), Profile()

### Community 28 - "gallery/test/unit/test_manager.py"
Cohesion: 0.23
Nodes (15): _photo(), _stub_signing(), test_bulk_delete_photos_drops_unauthorized_and_reuses_single_events_lookup(), test_bulk_delete_photos_skips_invoke_when_nothing_authorized(), test_delete_photo_authorizes_organizer(), test_delete_photo_authorizes_uploader(), test_delete_photo_rejects_unauthorized_caller(), test_delete_photo_rejects_when_event_archived() (+7 more)

### Community 29 - "gallery/infra/input.tf"
Cohesion: 0.11
Nodes (17): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+9 more)

### Community 30 - "upload_status/test/integration/test_route_handler.py"
Cohesion: 0.42
Nodes (14): lambda_handler(), inject_lambda_context, _api_event(), _create_events_table(), _create_jobs_table(), _FakeLambdaContext, mock_aws, test_job_status_reflects_row_written_by_db_api() (+6 more)

### Community 31 - "aws_s3_bucket.hosting"
Cohesion: 0.23
Nodes (11): aws_cloudfront_distribution.hosting, aws_cloudfront_origin_access_control.hosting, aws_s3_bucket.hosting, aws_s3_bucket_policy.hosting_oac_access, aws_s3_bucket_public_access_block.hosting, data.aws_iam_policy_document.hosting_oac_access, output.bucket_arn, output.bucket_name (+3 more)

### Community 32 - "HowItWorks.jsx"
Cohesion: 0.16
Nodes (11): ImageSlot(), About(), audiences, pairs, HowItWorks(), pipeline, properties, stackGroups (+3 more)

### Community 33 - "README.md"
Cohesion: 0.07
Nodes (26): 1. AWS account and IAM, 2. Local AWS CLI profile, 3. Terraform 1.10 or newer, 4. Bootstrap the Terraform state bucket by hand, once, 5. Check your account's real Rekognition quota, 6. Variables to change for your own deployment, 7. Deploy, Architecture (+18 more)

### Community 34 - "events/test/integration/test_route_handler.py"
Cohesion: 0.38
Nodes (13): handle_internal_action(), lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _FakeLambdaContext, mock_aws (+5 more)

### Community 35 - "events/test/unit/test_manager.py"
Cohesion: 0.24
Nodes (12): _event(), test_archive_event_deletes_collection_and_marks_archived(), test_archive_event_is_a_no_op_when_already_archived(), test_delete_event_invokes_cascade_delete(), test_get_event_detail_raises_for_non_owner(), test_get_stats_returns_photo_count_storage_and_attendee_count(), test_list_events_returns_public_shape(), test_list_my_events_excludes_self_organized_events() (+4 more)

### Community 36 - "ingestion/src/DAO/dao.py"
Cohesion: 0.19
Nodes (18): _dynamodb(), _event_attendees_table(), _events_table(), _faces_table(), get_event(), increment_event_counters(), index_faces(), invoke_heic_converter() (+10 more)

### Community 37 - "EventAnalytics.jsx"
Cohesion: 0.21
Nodes (8): AppHeader(), getEventStats(), formatBytes(), EventAnalytics(), Privacy(), PRIVACY_ITEMS, CONSENT_POINTS, SelfieInfo()

### Community 38 - "put_object"
Cohesion: 0.33
Nodes (7): delete_object(), list_admitted_attendees(), put_object(), _s3(), handle_list_attendees(), test_list_attendees_empty_event(), test_list_attendees_writes_manifest_of_admitted_userids()

### Community 39 - "React + Vite starter template"
Cohesion: 0.67
Nodes (3): Oxlint, React Compiler, React + Vite starter template

### Community 40 - "profile/test/integration/test_route_handler.py"
Cohesion: 0.45
Nodes (11): lambda_handler(), inject_lambda_context, _api_event(), _create_users_table(), _FakeLambdaContext, mock_aws, test_confirm_selfie_rejects_and_deletes_when_not_exactly_one_face(), test_delete_selfie_removes_object() (+3 more)

### Community 41 - "aws_cloudfront_distribution.photos"
Cohesion: 0.18
Nodes (15): aws_cloudfront_distribution.photos, aws_cloudfront_key_group.photos_signing, aws_cloudfront_origin_access_control.photos, aws_cloudfront_public_key.photos_signing, aws_s3_bucket_policy.photos_oac_access, data.aws_iam_policy_document.photos_oac_access, output.distribution_domain_name, output.distribution_id (+7 more)

### Community 42 - "cognito.js"
Cohesion: 0.27
Nodes (11): AuthProvider(), confirmPassword(), confirmSignUp(), forgotPassword(), getCurrentSession(), login(), refreshCurrentSession(), resendConfirmationCode() (+3 more)

### Community 43 - "eventsApi.js"
Cohesion: 0.28
Nodes (9): archiveEvent(), createEvent(), deleteEvent(), getEventDetail(), updateEventDetail(), CreateEvent(), CONTRIBUTION_POLICIES, EventSettings() (+1 more)

### Community 44 - "aws-lambda-powertools (library)"
Cohesion: 0.15
Nodes (15): cascadeDelete requirements.txt, db_api requirements.txt, download requirements.txt, events requirements.txt, gallery requirements.txt, heic_converter requirements.txt, ingestion requirements.txt, membership requirements.txt (+7 more)

### Community 45 - "upload_status/test/unit/test_manager.py"
Cohesion: 0.24
Nodes (9): _event(), _job(), test_get_job_status_rejects_job_belonging_to_another_uploader(), test_get_job_status_returns_job_owned_by_caller(), test_get_latest_job_returns_most_recent_via_dao(), test_mint_upload_url_allows_organizer_when_organizer_only(), test_mint_upload_url_builds_key_from_event_and_user_and_generated_job_id(), test_mint_upload_url_rejects_archived_event() (+1 more)

### Community 46 - "events/infra/iam_policies.tf"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 47 - "gallery/infra/iam_policies.tf"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 48 - "handle_stage"
Cohesion: 0.26
Nodes (10): extract_entries(), _is_junk_entry(), get_user(), handle_stage(), _parse_upload_key(), test_stage_copies_each_entry_raw_and_writes_manifest(), test_stage_does_no_format_sniffing_or_decoding(), _zip_bytes() (+2 more)

### Community 49 - "membership/infra/input.tf"
Cohesion: 0.18
Nodes (10): var.alarm_sns_topic_arn, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.name_prefix (+2 more)

### Community 50 - "match_attendees.py"
Cohesion: 0.20
Nodes (12): add_matched_photo_ids(), get_faces(), search_faces_by_image(), selfie_exists(), handle(), handle_step(), handle_match_attendees(), resolve_and_store_matches() (+4 more)

### Community 52 - "membershipApi.js"
Cohesion: 0.42
Nodes (7): admitAttendee(), denyAttendee(), ejectAttendee(), getAttendees(), joinEvent(), JoinLink(), Roster()

### Community 56 - "upload_status/infra/input.tf"
Cohesion: 0.20
Nodes (9): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.events_table_arn, var.events_table_name, var.jobs_table_arn, var.jobs_table_name, var.name_prefix, var.photos_bucket_arn (+1 more)

### Community 57 - "aws_cognito_user_pool.this"
Cohesion: 0.33
Nodes (6): aws_cognito_user_pool_client.this, aws_cognito_user_pool.this, output.user_pool_arn, output.user_pool_client_id, output.user_pool_id, var.name_prefix

### Community 58 - "aws_sns_topic.alerts"
Cohesion: 0.32
Nodes (5): aws_sns_topic.alerts, aws_sns_topic_subscription.alerts_email, output.alarm_sns_topic_arn, var.alarm_email, var.name_prefix

### Community 59 - "ingestion/test/integration/test_route_handler.py"
Cohesion: 0.36
Nodes (8): lambda_handler(), inject_lambda_context, _create_tables(), _FakeLambdaContext, mock_aws, test_event_attendees_stream_record_triggers_match_attendees(), test_stage_then_process_then_index_then_finalize_full_round_trip(), _zip_bytes()

### Community 60 - "profile/infra/input.tf"
Cohesion: 0.25
Nodes (7): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn, var.photos_bucket_name, var.users_table_arn, var.users_table_name

### Community 61 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): rules, react/only-export-components, react/rules-of-hooks, $schema, warn

### Community 62 - "UploadFlow.jsx"
Cohesion: 0.43
Nodes (6): getJobStatus(), getUploadUrl(), fibonacciPollDelay(), STAGE_LABEL, STAGE_PCT, UploadFlow()

### Community 63 - "sniff_format"
Cohesion: 0.48
Nodes (5): sniff_format(), test_returns_none_for_unrecognized_format(), test_sniffs_heic(), test_sniffs_jpeg(), test_sniffs_png()

### Community 64 - "membership/infra/iam_policies.tf"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.users_access

### Community 65 - "profile/infra/iam_policies.tf"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.photos_bucket_access, data.aws_iam_policy_document.rekognition_access, data.aws_iam_policy_document.users_access

### Community 66 - "upload_status/infra/iam_policies.tf"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.events_access, aws_iam_role_policy.jobs_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.jobs_access, data.aws_iam_policy_document.photos_bucket_access

### Community 67 - "db_api/infra/input.tf"
Cohesion: 0.33
Nodes (5): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.jobs_table_arn, var.jobs_table_name, var.name_prefix

### Community 69 - "ingestion/src/Manager/manager.py"
Cohesion: 0.33
Nodes (12): count_result_items(), parse_result_file(), parse_result_manifest(), get_object(), handle_build_photos_manifest(), handle_finalize(), _manifest_bytes(), _result_file_bytes() (+4 more)

### Community 70 - "test_build_photos_manifest.py"
Cohesion: 0.70
Nodes (4): _manifest_bytes(), _result_file_bytes(), test_build_photos_manifest_counts_task_level_failures(), test_build_photos_manifest_keeps_only_succeeded_photos()

### Community 72 - "module.hosting"
Cohesion: 0.47
Nodes (4): module.hosting, output.bucket_name, output.distribution_domain_name, output.distribution_id

### Community 73 - "test_delete_event.py"
Cohesion: 0.60
Nodes (3): _event(), test_delete_event_cascade_deletes_collection_faces_photos_s3_and_attendees(), test_delete_event_cascade_skips_batch_calls_when_nothing_to_delete()

### Community 74 - "heic_converter/infra/input.tf"
Cohesion: 0.40
Nodes (4): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn

### Community 77 - "cascadeDelete/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 79 - "db_api/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 80 - "download/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 81 - "events/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 82 - "gallery/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 83 - "heic_converter/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 84 - "ingestion/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 85 - "membership/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 86 - "profile/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 87 - "upload_status/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

## Knowledge Gaps
- **240 isolated node(s):** `aws_cloudwatch_log_group.this`, `aws_cloudwatch_metric_alarm.errors`, `output.function_arn`, `output.function_name`, `aws_cloudwatch_log_group.this` (+235 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `handle_internal_action()` connect `events/test/integration/test_route_handler.py` to `events/src/Manager/manager.py`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Why does `test_list_my_events_returns_only_pending_and_attendee_rows()` connect `events/test/integration/test_route_handler.py` to `membership/test/unit/test_manager.py`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **What connects `aws_cloudwatch_log_group.this`, `aws_cloudwatch_metric_alarm.errors`, `output.function_arn` to the rest of the system?**
  _240 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `aws_api_gateway_rest_api.this` be split into smaller, more focused modules?**
  _Cohesion score 0.05833905284831846 - nodes in this community are weakly interconnected._
- **Should `cascadeDelete/src/DAO/dao.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10105580693815988 - nodes in this community are weakly interconnected._
- **Should `events/src/Manager/manager.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09796806966618288 - nodes in this community are weakly interconnected._
- **Should `dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._