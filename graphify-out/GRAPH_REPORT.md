# Graph Report - Glimpses  (2026-08-29)

## Corpus Check
- 373 files · ~271,906 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1540 nodes · 2839 edges · 169 communities (128 shown, 41 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 62 edges (avg confidence: 0.8)
- Token cost: 110,428 input · 0 output

## Community Hubs (Navigation)
- api_gateway Terraform
- cascadeDelete DAO
- events DAO
- Frontend Dependencies
- ingestion Infra
- download DAO
- gallery Manager
- state_machine Terraform
- Frontend src
- membership DAO
- profile DAO
- cascadeDelete Infra
- Infrastructure imports
- membership Tests
- events Infra
- download Infra
- gallery Tests
- ingestion Tests
- dynamodb Terraform
- upload_status DAO
- Frontend src
- Frontend src
- heic_converter Tests
- membership Tests
- db_api DAO
- buckets Terraform
- Frontend src
- Frontend src
- gallery Tests
- gallery Infra
- upload_status Tests
- Frontend frontend
- Frontend src
- Docs: INFRASTRUCTURE
- events Tests
- events Tests
- ingestion DAO
- Frontend src
- ingestion Tests
- Frontend README.md
- profile Tests
- cloudfront Terraform
- Frontend src
- Frontend src
- events requirements
- upload_status Tests
- events Infra
- gallery Infra
- ingestion Tests
- membership Infra
- Frontend public
- download Tests
- ingestion DAO
- ingestion DAO
- ingestion Handler
- upload_status Infra
- cognito Terraform
- alarms Terraform
- ingestion Tests
- profile Infra
- Frontend .oxlintrc.json
- Frontend src
- ingestion Tests
- membership Infra
- profile Infra
- upload_status Infra
- db_api Infra
- ingestion Tests
- Docs: BACKEND
- Docs: FRONTEND
- Frontend frontend
- cascadeDelete Tests
- heic_converter Infra
- Docs: FRONTEND
- Docs: INFRASTRUCTURE
- cascadeDelete Infra
- db_api Infra
- download Infra
- events Infra
- gallery Infra
- heic_converter Infra
- ingestion Infra
- membership Infra
- profile Infra
- upload_status Infra
- Frontend frontend
- cascadeDelete Infra
- cascadeDelete Infra
- db_api Infra
- db_api Infra
- db_api Infra
- download Infra
- download Infra
- events Infra
- events Infra
- gallery Infra
- gallery Infra
- heic_converter Infra
- heic_converter Infra
- heic_converter Infra
- ingestion Infra
- ingestion Infra
- membership Infra
- membership Infra
- profile Infra
- profile Infra
- upload_status Infra
- upload_status Infra
- cascadeDelete Infra
- db_api Infra
- gallery Infra
- heic_converter Infra
- membership Infra
- membership Infra
- profile Infra
- upload_status Infra
- dynamodb Terraform
- Frontend frontend
- Frontend index.html
- Infrastructure .terraform.lock
- Docs: FRONTEND
- Docs: FRONTEND
- Docs: FRONTEND
- Docs: FRONTEND
- Docs: INFRASTRUCTURE

## God Nodes (most connected - your core abstractions)
1. `aws_api_gateway_rest_api.this` - 57 edges
2. `react` - 23 edges
3. `handle_process_one_photo()` - 18 edges
4. `useAuth()` - 17 edges
5. `delete_event_cascade()` - 15 edges
6. `_event()` - 14 edges
7. `aws_api_gateway_resource.event_id` - 14 edges
8. `_attendee()` - 13 edges
9. `module.buckets` - 13 edges
10. `aws_api_gateway_deployment.this` - 13 edges

## Surprising Connections (you probably didn't know these)
- `cascadeDelete requirements.txt` --shares_data_with--> `CascadeDelete Lambda`  [INFERRED]
  Backend/cascadeDelete/requirements.txt → Miscellaneous/BACKEND.md
- `gallery requirements.txt` --shares_data_with--> `gallery Lambda (glimpses-gallery)`  [INFERRED]
  Backend/gallery/requirements.txt → Miscellaneous/BACKEND.md
- `download requirements.txt` --shares_data_with--> `download Lambda (glimpses-download)`  [INFERRED]
  Backend/download/requirements.txt → Miscellaneous/BACKEND.md
- `events requirements.txt` --shares_data_with--> `events Lambda (glimpses-events)`  [INFERRED]
  Backend/events/requirements.txt → Miscellaneous/BACKEND.md
- `ingestion requirements.txt` --shares_data_with--> `ingestion Lambda (Step Functions steps)`  [INFERRED]
  Backend/ingestion/requirements.txt → Miscellaneous/BACKEND.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **API Gateway routes uniformly requiring Cognito authorizer across 6 frontend-facing Lambdas** — miscellaneous_infrastructure_api_gateway_module, miscellaneous_backend_profile_lambda, miscellaneous_backend_events_lambda, miscellaneous_backend_membership_lambda, miscellaneous_backend_upload_status_lambda, miscellaneous_backend_gallery_lambda, miscellaneous_backend_download_lambda [EXTRACTED 1.00]
- **Step Functions ingestion pipeline: db_api status writes, ingestion steps, Jobs table** — miscellaneous_infrastructure_state_machine, miscellaneous_backend_ingestion_lambda, miscellaneous_backend_db_api_lambda, miscellaneous_infrastructure_jobs_table, miscellaneous_backend_jobs_status_enum [EXTRACTED 1.00]
- **DynamoDB-stream-driven CascadeDelete teardown and MatchOneAttendee matching, both fed by table status transitions** — miscellaneous_infrastructure_events_table, miscellaneous_infrastructure_eventattendees_table, miscellaneous_backend_cascadedelete_lambda, miscellaneous_backend_ingestion_lambda, miscellaneous_backend_eventattendees_status_enum [EXTRACTED 1.00]

## Communities (169 total, 41 thin omitted)

### Community 0 - "api_gateway Terraform"
Cohesion: 0.06
Nodes (82): aws_api_gateway_authorizer.cognito, aws_api_gateway_deployment.this, aws_api_gateway_gateway_response.default_4xx, aws_api_gateway_gateway_response.default_5xx, aws_api_gateway_integration.options, aws_api_gateway_integration_response.options, aws_api_gateway_integration.route, aws_api_gateway_method.options (+74 more)

### Community 1 - "cascadeDelete DAO"
Cohesion: 0.10
Nodes (40): batch_delete_attendees(), batch_delete_faces(), batch_delete_photos(), decrement_event_counters(), delete_collection(), delete_event_row(), delete_faces_from_collection(), delete_photo_row() (+32 more)

### Community 2 - "events DAO"
Cohesion: 0.10
Nodes (49): access_code_exists(), batch_get_events(), count_attendees(), create_collection(), delete_collection(), _dynamodb(), _event_attendees_table(), _events_table() (+41 more)

### Community 3 - "Frontend Dependencies"
Cohesion: 0.04
Nodes (47): amazon-cognito-identity-js, axios, dependencies, amazon-cognito-identity-js, axios, jsqr, jszip, motion (+39 more)

### Community 4 - "ingestion Infra"
Cohesion: 0.06
Nodes (36): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access (+28 more)

### Community 5 - "download DAO"
Cohesion: 0.11
Nodes (34): abort_multipart_upload(), _batch_get_photo_keys(), complete_multipart_upload(), create_download(), create_multipart_upload(), _downloads_table(), generate_presigned_url(), get_download() (+26 more)

### Community 6 - "gallery Manager"
Cohesion: 0.12
Nodes (34): batch_get_photos(), _event_attendees_table(), _events_table(), generate_presigned_url(), get_attendee(), get_event(), get_photo_by_id(), invoke_cascade_delete() (+26 more)

### Community 7 - "state_machine Terraform"
Cohesion: 0.12
Nodes (32): aws_cloudwatch_event_rule.upload_complete, aws_cloudwatch_event_target.start_ingestion, aws_iam_role.eventbridge_start_execution, aws_iam_role_policy.distributed_map_self_execution, aws_iam_role_policy.eventbridge_start_execution, aws_iam_role_policy.invoke_db_api, aws_iam_role_policy.invoke_ingestion, aws_iam_role_policy.read_manifest (+24 more)

### Community 8 - "Frontend src"
Cohesion: 0.12
Nodes (21): App(), AuthShell(), RequireAuth(), Header(), MarketingLayout(), AuthContext, useAuth(), userFromSession() (+13 more)

### Community 9 - "membership DAO"
Cohesion: 0.16
Nodes (32): _dynamodb(), _event_attendees_table(), _events_table(), get_attendee(), get_event(), get_event_by_access_code(), get_users(), list_attendees_by_status() (+24 more)

### Community 10 - "profile DAO"
Cohesion: 0.14
Nodes (29): create_user(), delete_object(), detect_face_count(), _dynamodb(), generate_presigned_get_url(), generate_presigned_put_url(), get_user(), _rekognition() (+21 more)

### Community 11 - "cascadeDelete Infra"
Cohesion: 0.08
Nodes (27): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access (+19 more)

### Community 12 - "Infrastructure imports"
Cohesion: 0.20
Nodes (24): module.alarms, module.api_gateway, module.buckets, module.cascade_delete, module.cloudfront, module.cognito, module.db_api, module.download (+16 more)

### Community 13 - "membership Tests"
Cohesion: 0.19
Nodes (21): _attendee(), _event(), _full_event(), test_admit_attendee_rejects_non_pending(), test_admit_attendee_transitions_pending_to_attendee(), test_deny_attendee_transitions_pending_to_blocked(), test_eject_attendee_rejects_non_attendee(), test_eject_attendee_transitions_attendee_to_blocked() (+13 more)

### Community 14 - "events Infra"
Cohesion: 0.10
Nodes (20): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+12 more)

### Community 15 - "download Infra"
Cohesion: 0.11
Nodes (18): aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.photos_access, data.aws_iam_policy_document.photos_bucket_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn (+10 more)

### Community 16 - "gallery Tests"
Cohesion: 0.45
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_photos_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 17 - "ingestion Tests"
Cohesion: 0.18
Nodes (15): compute_content_hash(), make_thumbnail(), normalize_to_jpeg(), handle_process_one_photo(), test_computes_sha256_hash(), test_different_bytes_produce_different_hash(), test_same_bytes_produce_same_hash(), test_process_one_photo_converts_heic_via_invoke() (+7 more)

### Community 18 - "dynamodb Terraform"
Cohesion: 0.17
Nodes (12): aws_dynamodb_table.downloads, aws_dynamodb_table.event_attendees, aws_dynamodb_table.events, aws_dynamodb_table.faces, aws_dynamodb_table.jobs, aws_dynamodb_table.photos, aws_dynamodb_table.users, output.event_attendees_stream_arn (+4 more)

### Community 19 - "upload_status DAO"
Cohesion: 0.21
Nodes (17): _events_table(), generate_presigned_put_url(), get_event(), get_job(), _jobs_table(), query_latest_job(), _s3(), get_job_status() (+9 more)

### Community 20 - "Frontend src"
Cohesion: 0.24
Nodes (13): ConfirmDialog(), EventMenu(), Gallery(), formatDate(), PhotoViewer(), api, getDownloadStatus(), requestDownload() (+5 more)

### Community 21 - "Frontend src"
Cohesion: 0.19
Nodes (15): QRScanner(), scanLoop(), startCamera(), CameraCapture(), startCamera(), cameraErrorMessage(), BARE_CODE_RE, decodeQRFromFile() (+7 more)

### Community 22 - "heic_converter Tests"
Cohesion: 0.16
Nodes (12): heic_to_jpeg(), get_object(), put_object(), handle(), convert_and_store(), lambda_handler(), inject_lambda_context, _FakeLambdaContext (+4 more)

### Community 23 - "membership Tests"
Cohesion: 0.43
Nodes (17): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_users_table(), _FakeLambdaContext, _put_event() (+9 more)

### Community 24 - "db_api DAO"
Cohesion: 0.18
Nodes (13): create_job(), _table(), update_job_status(), handle(), _create(), handle_action(), _update_status(), lambda_handler() (+5 more)

### Community 25 - "buckets Terraform"
Cohesion: 0.18
Nodes (14): aws_s3_bucket_cors_configuration.photos, aws_s3_bucket.deploy_artifacts, aws_s3_bucket_lifecycle_configuration.photos, aws_s3_bucket_notification.photos_eventbridge, aws_s3_bucket.photos, aws_s3_bucket_public_access_block.deploy_artifacts, aws_s3_bucket_public_access_block.photos, output.deploy_artifacts_bucket_arn (+6 more)

### Community 26 - "Frontend src"
Cohesion: 0.26
Nodes (12): DEFAULT_MESSAGES, LoadingSpinner(), getOrganizedEvents(), admitAttendee(), denyAttendee(), ejectAttendee(), getAttendees(), getEventInfo() (+4 more)

### Community 27 - "Frontend src"
Cohesion: 0.22
Nodes (12): SelfieOptionsSheet(), SelfieToast(), getMyEvents(), deleteSelfie(), getProfile(), updateProfile(), uploadSelfie(), EventCard() (+4 more)

### Community 28 - "gallery Tests"
Cohesion: 0.21
Nodes (11): _photo(), test_bulk_delete_photos_drops_unauthorized_and_reuses_single_events_lookup(), test_bulk_delete_photos_skips_invoke_when_nothing_authorized(), test_delete_photo_authorizes_organizer(), test_delete_photo_authorizes_uploader(), test_delete_photo_rejects_unauthorized_caller(), test_delete_photo_rejects_when_event_archived(), test_get_download_urls_filters_to_own_event() (+3 more)

### Community 29 - "gallery Infra"
Cohesion: 0.13
Nodes (14): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+6 more)

### Community 30 - "upload_status Tests"
Cohesion: 0.42
Nodes (13): lambda_handler(), inject_lambda_context, _api_event(), _create_events_table(), _create_jobs_table(), _FakeLambdaContext, mock_aws, test_job_status_reflects_row_written_by_db_api() (+5 more)

### Community 31 - "Frontend frontend"
Cohesion: 0.23
Nodes (11): aws_cloudfront_distribution.hosting, aws_cloudfront_origin_access_control.hosting, aws_s3_bucket.hosting, aws_s3_bucket_policy.hosting_oac_access, aws_s3_bucket_public_access_block.hosting, data.aws_iam_policy_document.hosting_oac_access, output.bucket_arn, output.bucket_name (+3 more)

### Community 32 - "Frontend src"
Cohesion: 0.16
Nodes (11): ImageSlot(), About(), audiences, pairs, HowItWorks(), pipeline, properties, stackGroups (+3 more)

### Community 33 - "Docs: INFRASTRUCTURE"
Cohesion: 0.20
Nodes (15): CascadeDelete Lambda, download Lambda (glimpses-download), events Lambda (glimpses-events), gallery Lambda (glimpses-gallery), motion (Framer Motion successor) drag-to-dismiss decision, Phase 9 Deletion build (Danger zone), Phase 8 Download flow build (popup-blocker fix), Phase 6 Gallery & PhotoViewer build (+7 more)

### Community 34 - "events Tests"
Cohesion: 0.36
Nodes (12): handle_internal_action(), lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _FakeLambdaContext, mock_aws (+4 more)

### Community 35 - "events Tests"
Cohesion: 0.25
Nodes (11): _event(), test_archive_event_deletes_collection_and_marks_archived(), test_archive_event_is_a_no_op_when_already_archived(), test_delete_event_invokes_cascade_delete(), test_get_event_detail_raises_for_non_owner(), test_get_stats_returns_photo_count_storage_and_attendee_count(), test_list_events_returns_public_shape(), test_list_my_events_returns_only_pending_and_attendee_rows() (+3 more)

### Community 36 - "ingestion DAO"
Cohesion: 0.25
Nodes (13): delete_object(), _dynamodb(), _event_attendees_table(), _events_table(), _faces_table(), increment_event_counters(), invoke_heic_converter(), is_duplicate() (+5 more)

### Community 37 - "Frontend src"
Cohesion: 0.21
Nodes (8): AppHeader(), getEventStats(), formatBytes(), EventAnalytics(), Privacy(), PRIVACY_ITEMS, CONSENT_POINTS, SelfieInfo()

### Community 38 - "ingestion Tests"
Cohesion: 0.28
Nodes (8): list_admitted_attendees(), put_object(), handle_build_photos_manifest(), handle_list_attendees(), test_build_photos_manifest_handles_no_results(), test_build_photos_manifest_keeps_only_succeeded_photos(), test_list_attendees_empty_event(), test_list_attendees_writes_manifest_of_admitted_userids()

### Community 39 - "Frontend README.md"
Cohesion: 0.15
Nodes (13): profile requirements.txt, Oxlint, React Compiler, React + Vite starter template, Flat 502 error-shape gap (no Powertools exception handler), COGNITO_USER_POOLS authorizer (every route), profile Lambda (glimpses-profile), Phased frontend build plan (Phase 0-12) (+5 more)

### Community 40 - "profile Tests"
Cohesion: 0.45
Nodes (11): lambda_handler(), inject_lambda_context, _api_event(), _create_users_table(), _FakeLambdaContext, mock_aws, test_confirm_selfie_rejects_and_deletes_when_not_exactly_one_face(), test_delete_selfie_removes_object() (+3 more)

### Community 41 - "cloudfront Terraform"
Cohesion: 0.24
Nodes (10): aws_cloudfront_distribution.photos, aws_cloudfront_origin_access_control.photos, aws_s3_bucket_policy.photos_oac_access, data.aws_iam_policy_document.photos_oac_access, output.distribution_domain_name, output.distribution_id, var.name_prefix, var.photos_bucket_arn (+2 more)

### Community 42 - "Frontend src"
Cohesion: 0.27
Nodes (11): AuthProvider(), confirmPassword(), confirmSignUp(), forgotPassword(), getCurrentSession(), login(), refreshCurrentSession(), resendConfirmationCode() (+3 more)

### Community 43 - "Frontend src"
Cohesion: 0.28
Nodes (9): archiveEvent(), createEvent(), deleteEvent(), getEventDetail(), updateEventDetail(), CreateEvent(), CONTRIBUTION_POLICIES, EventSettings() (+1 more)

### Community 44 - "events requirements"
Cohesion: 0.20
Nodes (12): cascadeDelete requirements.txt, download requirements.txt, events requirements.txt, gallery requirements.txt, heic_converter requirements.txt, ingestion requirements.txt, aws-lambda-powertools (library), Pillow (library) (+4 more)

### Community 45 - "upload_status Tests"
Cohesion: 0.26
Nodes (8): _event(), _job(), test_get_job_status_rejects_job_belonging_to_another_uploader(), test_get_job_status_returns_job_owned_by_caller(), test_get_latest_job_returns_most_recent_via_dao(), test_mint_upload_url_allows_organizer_when_organizer_only(), test_mint_upload_url_builds_key_from_event_and_user_and_generated_job_id(), test_mint_upload_url_rejects_attendee_when_organizer_only()

### Community 46 - "events Infra"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 47 - "gallery Infra"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 48 - "ingestion Tests"
Cohesion: 0.35
Nodes (8): extract_entries(), get_object(), get_user(), handle_stage(), _parse_upload_key(), test_stage_copies_each_entry_raw_and_writes_manifest(), test_stage_does_no_format_sniffing_or_decoding(), _zip_bytes()

### Community 49 - "membership Infra"
Cohesion: 0.18
Nodes (10): var.alarm_sns_topic_arn, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.name_prefix (+2 more)

### Community 50 - "Frontend public"
Cohesion: 0.27
Nodes (10): db_api requirements.txt, About.jsx audience card images, HowItWorks.jsx tech stack logos, ImageSlot fallback-to-placeholder pattern, Landing.jsx hero collage images, db_api Lambda (internal action-dispatch), Jobs status enum (CREATED..SUCCESS/FAILED), Marketing site imagery side-quest (+2 more)

### Community 52 - "ingestion DAO"
Cohesion: 0.36
Nodes (8): add_matched_photo_ids(), get_faces(), search_faces_by_image(), selfie_exists(), handle_match_attendees(), resolve_and_store_matches(), test_matches_and_stores_photo_ids(), test_skips_attendee_with_no_selfie()

### Community 53 - "ingestion DAO"
Cohesion: 0.33
Nodes (8): get_event(), index_faces(), put_face(), _rekognition(), handle_index_one_photo(), test_handles_photo_with_no_faces(), test_indexes_faces_and_stores_each_one(), test_indexing_error_is_caught_and_counted_as_failed()

### Community 54 - "ingestion Handler"
Cohesion: 0.31
Nodes (6): handle(), handle_step(), handle_stream_records(), lambda_handler(), inject_lambda_context, test_resolves_each_stream_record()

### Community 56 - "upload_status Infra"
Cohesion: 0.20
Nodes (9): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.events_table_arn, var.events_table_name, var.jobs_table_arn, var.jobs_table_name, var.name_prefix, var.photos_bucket_arn (+1 more)

### Community 57 - "cognito Terraform"
Cohesion: 0.33
Nodes (6): aws_cognito_user_pool_client.this, aws_cognito_user_pool.this, output.user_pool_arn, output.user_pool_client_id, output.user_pool_id, var.name_prefix

### Community 58 - "alarms Terraform"
Cohesion: 0.32
Nodes (5): aws_sns_topic.alerts, aws_sns_topic_subscription.alerts_email, output.alarm_sns_topic_arn, var.alarm_email, var.name_prefix

### Community 59 - "ingestion Tests"
Cohesion: 0.46
Nodes (6): _create_tables(), _FakeLambdaContext, mock_aws, test_event_attendees_stream_record_triggers_match_attendees(), test_stage_then_process_then_index_then_finalize_full_round_trip(), _zip_bytes()

### Community 60 - "profile Infra"
Cohesion: 0.25
Nodes (7): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn, var.photos_bucket_name, var.users_table_arn, var.users_table_name

### Community 61 - "Frontend .oxlintrc.json"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

### Community 62 - "Frontend src"
Cohesion: 0.43
Nodes (6): getJobStatus(), getUploadUrl(), fibonacciPollDelay(), STAGE_LABEL, STAGE_PCT, UploadFlow()

### Community 63 - "ingestion Tests"
Cohesion: 0.48
Nodes (5): sniff_format(), test_returns_none_for_unrecognized_format(), test_sniffs_heic(), test_sniffs_jpeg(), test_sniffs_png()

### Community 64 - "membership Infra"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.users_access

### Community 65 - "profile Infra"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.photos_bucket_access, data.aws_iam_policy_document.rekognition_access, data.aws_iam_policy_document.users_access

### Community 66 - "upload_status Infra"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.events_access, aws_iam_role_policy.jobs_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.jobs_access, data.aws_iam_policy_document.photos_bucket_access

### Community 67 - "db_api Infra"
Cohesion: 0.33
Nodes (5): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.jobs_table_arn, var.jobs_table_name, var.name_prefix

### Community 69 - "ingestion Tests"
Cohesion: 0.53
Nodes (4): handle_finalize(), test_all_succeeded(), test_some_photos_failed_but_others_succeeded(), test_total_failure_when_nothing_succeeded()

### Community 70 - "Docs: BACKEND"
Cohesion: 0.47
Nodes (6): membership requirements.txt, EventAttendees status enum (PENDING/ATTENDEE/LEFT/BLOCKED), ingestion Lambda (Step Functions steps), membership Lambda (glimpses-membership), Events TTL / EventAttendees stream-driven CascadeDelete + MatchOneAttendee flow, EventAttendees DynamoDB table

### Community 71 - "Docs: FRONTEND"
Cohesion: 0.33
Nodes (6): upload_status requirements.txt, upload_status Lambda (glimpses-upload_status), JSZip client-side zip decision, Phase 7 Upload flow build (real progress bar), Upload flow spec (single original.zip PUT, 500-photo client-zip cap), Jobs DynamoDB table

### Community 72 - "Frontend frontend"
Cohesion: 0.47
Nodes (4): module.hosting, output.bucket_name, output.distribution_domain_name, output.distribution_id

### Community 73 - "cascadeDelete Tests"
Cohesion: 0.60
Nodes (3): _event(), test_delete_event_cascade_deletes_collection_faces_photos_s3_and_attendees(), test_delete_event_cascade_skips_batch_calls_when_nothing_to_delete()

### Community 74 - "heic_converter Infra"
Cohesion: 0.40
Nodes (4): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn

### Community 75 - "Docs: FRONTEND"
Cohesion: 0.40
Nodes (5): axios + Cognito ID token interceptor decision, amazon-cognito-identity-js custom-screen auth decision, Auth live-pass bugs (VerifyCode, AddSelfiePrompt, keypad input), localStorage token storage (not httpOnly cookie) decision, cognito Terraform module (User Pool + App Client)

### Community 76 - "Docs: INFRASTRUCTURE"
Cohesion: 0.40
Nodes (5): Frontend hosting infra (private S3 + independent CloudFront + OAC), frontend / frontend-app Jenkins jobs, buckets Terraform module (photos, deploy-artifacts), cloudfront Terraform module (photos distribution), 17-job local Jenkins CI/CD (per-module Jenkinsfile)

### Community 77 - "cascadeDelete Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 79 - "db_api Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 80 - "download Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 81 - "events Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 82 - "gallery Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 83 - "heic_converter Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 84 - "ingestion Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 85 - "membership Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 86 - "profile Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 87 - "upload_status Infra"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

## Knowledge Gaps
- **212 isolated node(s):** `aws_cloudwatch_log_group.this`, `aws_cloudwatch_metric_alarm.errors`, `var.name_prefix`, `var.deploy_artifacts_bucket`, `var.events_table_name` (+207 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Frontend src` to `Frontend src`, `Frontend src`, `Frontend src`, `Frontend src`, `Frontend src`, `Frontend src`, `Frontend .oxlintrc.json`, `Frontend src`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **What connects `aws_cloudwatch_log_group.this`, `aws_cloudwatch_metric_alarm.errors`, `var.name_prefix` to the rest of the system?**
  _212 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `api_gateway Terraform` be split into smaller, more focused modules?**
  _Cohesion score 0.05833905284831846 - nodes in this community are weakly interconnected._
- **Should `cascadeDelete DAO` be split into smaller, more focused modules?**
  _Cohesion score 0.10105580693815988 - nodes in this community are weakly interconnected._
- **Should `events DAO` be split into smaller, more focused modules?**
  _Cohesion score 0.09879336349924585 - nodes in this community are weakly interconnected._
- **Should `Frontend Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._
- **Should `ingestion Infra` be split into smaller, more focused modules?**
  _Cohesion score 0.06153846153846154 - nodes in this community are weakly interconnected._