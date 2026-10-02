# Graph Report - Glimpses  (2026-10-02)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1776 nodes · 3205 edges · 225 communities (138 shown, 87 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 61 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d2455536`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- API Gateway Configuration
- Cascade Delete Logic
- Events Data Access
- Frontend Dependencies
- Download Management Service
- User Profile Service
- Gallery Data Access
- Ingestion IAM Policies
- EventBridge and State Machine
- Membership Data Access
- Cascade Delete IAM Policies
- React Auth Components
- Infrastructure Module Imports
- Face Matching Ingestion
- Photo Processing Logic
- Notification Service
- Membership Unit Tests
- Notification Infrastructure
- Download IAM Policies
- Event Membership UI
- DynamoDB Table Definitions
- QR and Camera Components
- Events Infrastructure Inputs
- Gallery Route Handler
- Membership Route Handler
- Profile IAM Policies
- Upload Status Service
- Gallery UI Components
- Gallery Infrastructure Inputs
- HEIC Image Converter
- Ingestion Result Mapping
- Selfie Dispatcher Infrastructure
- CloudFront Photo Distribution
- Event Management UI
- Ingestion Lambda
- db_api/src/Manager/manager.py
- ingestion/test/integration/test_route_handler.py
- aws_s3_bucket.photos
- Profile.jsx
- Gallery Unit Tests
- Upload Status Handler
- Events Route Handler
- Events Unit Tests
- Zip Extraction Logic
- Selfie Match Dispatcher
- Frontend Hosting Infrastructure
- Marketing Landing Pages
- Cognito Auth Service
- Profile Route Handler
- Upload Status Tests
- System Architecture Diagram
- events/infra/iam_policies.tf
- gallery/infra/iam_policies.tf
- membership/infra/input.tf
- download/test/unit/test_manager.py
- upload_status/infra/input.tf
- Cognito User Pool
- SES Email Identity
- SNS Alerting Infrastructure
- Linting Configuration
- Upload Flow UI
- Finalization Unit Tests
- Membership IAM Policies
- Upload Status IAM
- DB API Inputs
- File Deduplication Utility
- Frontend Infrastructure Outputs
- Delete Event Tests
- HEIC Converter Inputs
- Manifest Building Tests
- AWS Service Icons
- Frontend README
- cascadeDelete/infra/iam_role.tf
- db_api/infra/iam_role.tf
- download/infra/iam_role.tf
- events/infra/iam_role.tf
- gallery/infra/iam_role.tf
- heic_converter/infra/iam_role.tf
- ingestion/infra/iam_role.tf
- membership/infra/iam_role.tf
- notifications/infra/iam_role.tf
- test_delivery.py
- profile/infra/iam_role.tf
- selfie_match_dispatcher/infra/iam_role.tf
- upload_status/infra/iam_role.tf
- provider.aws
- System Architecture Overview
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
- notifications/infra/cloudwatch.tf
- notifications/infra/output.tf
- profile/infra/cloudwatch.tf
- profile/infra/output.tf
- selfie_match_dispatcher/infra/cloudwatch.tf
- selfie_match_dispatcher/infra/output.tf
- upload_status/infra/cloudwatch.tf
- upload_status/infra/output.tf
- Infrastructure/.terraform.lock.hcl
- Amazon DynamoDB Stream
- Amazon S3 Logo
- AWS Lambda Architecture Icon
- AWS WAF Architecture Icon
- Boto3 Logo
- Event Lobby Admission UI
- Personalized Photo Gallery
- cascadeDelete/infra/event_source_mapping.tf
- db_api/infra/lambda.tf
- events/infra/lambda.tf
- heic_converter/infra/lambda.tf
- ingestion/infra/event_source_mapping.tf
- membership/infra/lambda.tf
- infra/.terraform.lock.hcl
- Upload Status Lambda
- upload_status/infra/lambda.tf
- provider.registry.terraform.io/hashicorp/aws
- frontend/.terraform.lock.hcl
- state_machine/.terraform.lock.hcl
- AWS Lambda Powertools logo (large)
- Amazon API Gateway Architecture Icon
- Amazon CloudFront Architecture Icon
- Amazon DynamoDB Architecture Icon
- Amazon EventBridge Architecture Icon
- AWS Step Functions Architecture Icon
- Terraform Logo
- Knowledge Graph Visualization
- Glimpses Hero Section
- Download ZIP UI
- Event Analytics Dashboard
- My Events Dashboard
- Photo Gallery View
- Join Event UI
- Login Screen
- Upload Completion UI
- Privacy Policy Page
- Share Event QR UI
- Sign Up Screen
- Upload Progress UI
- Amazon API Gateway
- Amazon CloudFront
- Amazon EventBridge
- AWS WAF
- Download Lambda
- Membership Lambda
- Wide marketing image showing people at a dinner event using phones to scan a QR code
- Marketing image of a diverse group of friends hugging and smiling outdoors
- Marketing image of people networking at a professional conference or event
- Marketing image of a large family reunion group posing outdoors
- Marketing image of a bride and groom laughing during a wedding ceremony
- Hero image of friends laughing together at an outdoor sunset event
- Hero image of a woman laughing while others take photos of her with smartphones
- Hero image of a couple laughing at an event, seen through a smartphone camera lens
- Hero image of people toasting with wine glasses, with a smartphone capturing the moment
- Boto3 (AWS SDK for Python) icon
- DynamoDB Streams Stack Logo
- Jenkins Stack Logo
- Python Stack Logo

## God Nodes (most connected - your core abstractions)
1. `aws_api_gateway_rest_api.this` - 60 edges
2. `react` - 23 edges
3. `_event()` - 19 edges
4. `useAuth()` - 17 edges
5. `handle_process_one_photo()` - 17 edges
6. `delete_event_cascade()` - 16 edges
7. `module.buckets` - 15 edges
8. `resolve_and_store_matches()` - 14 edges
9. `_attendee()` - 14 edges
10. `aws_api_gateway_resource.event_id` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Ingestion Lambda` --calls--> `Amazon Rekognition`  [EXTRACTED]
  Backend/ingestion/requirements.txt → assets/architecture/icon-sources/Arch_Amazon-Rekognition_64.svg
- `Step Functions Icon` --references--> `Ingestion Pipeline`  [EXTRACTED]
  Frontend/public/images/marketing/stack-aws-step-functions.png → README.md
- `DynamoDB Icon` --references--> `DynamoDB Tables`  [EXTRACTED]
  Frontend/public/images/marketing/stack-amazon-dynamodb.png → README.md
- `S3 Icon` --references--> `S3 Storage`  [EXTRACTED]
  Frontend/public/images/marketing/stack-amazon-s3.png → README.md
- `Jenkins Pipeline Registry` --references--> `Jenkins`  [EXTRACTED]
  Infrastructure/cicd/jenkinsfiles.txt → assets/architecture/icon-sources/jenkins-svgrepo-com.png

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI/CD and IaC Stack** — jenkins, terraform, infrastructure_cicd_jenkinsfiles [EXTRACTED 0.90]
- **Face Matching Pipeline** — assets_product_profile, assets_step_function_pipeline_graph, assets_product_photos_of_me [EXTRACTED 0.95]
- **Event Deletion & Cleanup** — backend_events, backend_cascadedelete, backend_notifications, s3_bucket, aws_rekognition [EXTRACTED 1.00]
- **Photo Ingestion Flow** — aws_step_functions_ingestion, backend_ingestion, backend_heic_converter, backend_db_api, aws_rekognition [EXTRACTED 1.00]
- **Selfie Matching & Dispatch** — backend_profile, backend_selfie_match_dispatcher, backend_ingestion, aws_rekognition [EXTRACTED 1.00]
- **Event Lifecycle** — assets_product_events_dashboard, assets_product_event_settings, assets_product_share_event [INFERRED 0.80]
- **AWS Serverless Infrastructure** — aws_lambda, aws_api_gateway, aws_step_functions, aws_dynamodb, aws_eventbridge [INFERRED 0.85]

## Communities (225 total, 87 thin omitted)

### Community 0 - "API Gateway Configuration"
Cohesion: 0.06
Nodes (85): aws_api_gateway_authorizer.cognito, aws_api_gateway_deployment.this, aws_api_gateway_gateway_response.default_4xx, aws_api_gateway_gateway_response.default_5xx, aws_api_gateway_integration.options, aws_api_gateway_integration_response.options, aws_api_gateway_integration.route, aws_api_gateway_method.options (+77 more)

### Community 1 - "Cascade Delete Logic"
Cohesion: 0.10
Nodes (41): batch_delete_attendees(), batch_delete_faces(), batch_delete_photos(), decrement_event_counters(), delete_collection(), delete_event_row(), delete_faces_from_collection(), delete_photo_row() (+33 more)

### Community 2 - "Events Data Access"
Cohesion: 0.10
Nodes (50): access_code_exists(), batch_get_events(), count_attendees(), create_collection(), delete_collection(), _dynamodb(), _event_attendees_table(), _events_table() (+42 more)

### Community 3 - "Frontend Dependencies"
Cohesion: 0.04
Nodes (47): amazon-cognito-identity-js, axios, dependencies, amazon-cognito-identity-js, axios, jsqr, jszip, motion (+39 more)

### Community 4 - "Download Management Service"
Cohesion: 0.11
Nodes (38): abort_multipart_upload(), _batch_get_photo_keys(), complete_multipart_upload(), create_download(), create_multipart_upload(), _downloads_table(), _event_attendees_table(), generate_presigned_url() (+30 more)

### Community 5 - "User Profile Service"
Cohesion: 0.13
Nodes (38): clear_current_selfie(), copy_object(), create_user(), delete_object(), detect_face_count(), _dynamodb(), generate_presigned_get_url(), generate_presigned_put_url() (+30 more)

### Community 6 - "Gallery Data Access"
Cohesion: 0.11
Nodes (35): batch_get_photos(), _event_attendees_table(), _events_table(), generate_presigned_url(), get_attendee(), get_event(), get_photo_by_id(), invoke_cascade_delete() (+27 more)

### Community 7 - "Ingestion IAM Policies"
Cohesion: 0.06
Nodes (36): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access (+28 more)

### Community 8 - "EventBridge and State Machine"
Cohesion: 0.12
Nodes (32): aws_cloudwatch_event_rule.upload_complete, aws_cloudwatch_event_target.start_ingestion, aws_iam_role.eventbridge_start_execution, aws_iam_role_policy.distributed_map_self_execution, aws_iam_role_policy.eventbridge_start_execution, aws_iam_role_policy.invoke_db_api, aws_iam_role_policy.invoke_ingestion, aws_iam_role_policy.manifest_access (+24 more)

### Community 9 - "Membership Data Access"
Cohesion: 0.16
Nodes (32): _dynamodb(), _event_attendees_table(), _events_table(), get_attendee(), get_event(), get_event_by_access_code(), get_users(), list_attendees_by_status() (+24 more)

### Community 10 - "Cascade Delete IAM Policies"
Cohesion: 0.07
Nodes (31): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access (+23 more)

### Community 11 - "React Auth Components"
Cohesion: 0.13
Nodes (19): App(), AuthShell(), RequireAuth(), Header(), MarketingLayout(), AuthContext, useAuth(), userFromSession() (+11 more)

### Community 12 - "Infrastructure Module Imports"
Cohesion: 0.18
Nodes (29): module.alarms, module.api_gateway, module.buckets, module.cascade_delete, module.cloudfront, module.cognito, module.db_api, module.download (+21 more)

### Community 13 - "Face Matching Ingestion"
Cohesion: 0.14
Nodes (26): add_matched_photo_ids(), _dynamodb(), _event_attendees_table(), _events_table(), _faces_table(), get_event(), get_faces(), increment_event_counters() (+18 more)

### Community 14 - "Photo Processing Logic"
Cohesion: 0.13
Nodes (22): sniff_format(), make_thumbnail(), normalize_to_jpeg(), delete_object(), invoke_heic_converter(), _lambda_client(), handle_process_one_photo(), test_returns_none_for_unrecognized_format() (+14 more)

### Community 15 - "Notification Service"
Cohesion: 0.17
Nodes (22): claim_notification(), get_event(), get_user(), list_admitted_user_ids(), mark_sent(), release_notification(), send_email(), _table() (+14 more)

### Community 16 - "Membership Unit Tests"
Cohesion: 0.18
Nodes (25): _attendee(), _event(), _full_event(), test_admit_attendee_rejects_non_pending(), test_admit_attendee_transitions_pending_to_attendee(), test_deny_attendee_transitions_pending_to_blocked(), test_eject_attendee_rejects_non_attendee(), test_eject_attendee_transitions_attendee_to_blocked() (+17 more)

### Community 17 - "Notification Infrastructure"
Cohesion: 0.09
Nodes (23): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.event_attendees_stream_arn, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_stream_arn, var.events_table_arn, var.events_table_name (+15 more)

### Community 18 - "Download IAM Policies"
Cohesion: 0.10
Nodes (22): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.photos_access, data.aws_iam_policy_document.photos_bucket_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket (+14 more)

### Community 19 - "Event Membership UI"
Cohesion: 0.16
Nodes (17): AppHeader(), DEFAULT_MESSAGES, LoadingSpinner(), getOrganizedEvents(), admitAttendee(), denyAttendee(), ejectAttendee(), getAttendees() (+9 more)

### Community 20 - "DynamoDB Table Definitions"
Cohesion: 0.15
Nodes (14): aws_dynamodb_table.downloads, aws_dynamodb_table.event_attendees, aws_dynamodb_table.events, aws_dynamodb_table.faces, aws_dynamodb_table.jobs, aws_dynamodb_table.notifications, aws_dynamodb_table.photos, aws_dynamodb_table.users (+6 more)

### Community 21 - "QR and Camera Components"
Cohesion: 0.17
Nodes (17): QRScanner(), scanLoop(), startCamera(), CameraCapture(), startCamera(), cameraErrorMessage(), joinEvent(), BARE_CODE_RE (+9 more)

### Community 22 - "Events Infrastructure Inputs"
Cohesion: 0.11
Nodes (19): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+11 more)

### Community 23 - "Gallery Route Handler"
Cohesion: 0.45
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_photos_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 24 - "Membership Route Handler"
Cohesion: 0.43
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_users_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 25 - "Profile IAM Policies"
Cohesion: 0.11
Nodes (18): aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.photos_bucket_access, data.aws_iam_policy_document.rekognition_access, data.aws_iam_policy_document.users_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket (+10 more)

### Community 26 - "Upload Status Service"
Cohesion: 0.21
Nodes (17): _events_table(), generate_presigned_put_url(), get_event(), get_job(), _jobs_table(), query_latest_job(), _s3(), get_job_status() (+9 more)

### Community 27 - "Gallery UI Components"
Cohesion: 0.24
Nodes (13): ConfirmDialog(), EventMenu(), Gallery(), formatDate(), PhotoViewer(), getDownloadStatus(), requestDownload(), bulkDeletePhotos() (+5 more)

### Community 28 - "Gallery Infrastructure Inputs"
Cohesion: 0.11
Nodes (17): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+9 more)

### Community 29 - "HEIC Image Converter"
Cohesion: 0.16
Nodes (12): heic_to_jpeg(), get_object(), put_object(), handle(), convert_and_store(), lambda_handler(), inject_lambda_context, _FakeLambdaContext (+4 more)

### Community 30 - "Ingestion Result Mapping"
Cohesion: 0.27
Nodes (13): count_result_items(), parse_result_file(), parse_result_manifest(), get_object(), list_admitted_attendees(), put_object(), _s3(), handle_build_photos_manifest() (+5 more)

### Community 31 - "Selfie Dispatcher Infrastructure"
Cohesion: 0.12
Nodes (16): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.name_prefix, var.users_table_arn, var.users_table_name, aws_lambda_function.this (+8 more)

### Community 32 - "CloudFront Photo Distribution"
Cohesion: 0.18
Nodes (15): aws_cloudfront_distribution.photos, aws_cloudfront_key_group.photos_signing, aws_cloudfront_origin_access_control.photos, aws_cloudfront_public_key.photos_signing, aws_s3_bucket_policy.photos_oac_access, data.aws_iam_policy_document.photos_oac_access, output.distribution_domain_name, output.distribution_id (+7 more)

### Community 33 - "Event Management UI"
Cohesion: 0.19
Nodes (12): archiveEvent(), createEvent(), deleteEvent(), getEventDetail(), getEventStats(), updateEventDetail(), formatBytes(), CreateEvent() (+4 more)

### Community 34 - "Ingestion Lambda"
Cohesion: 0.11
Nodes (18): Amazon Rekognition Logo, Amazon Rekognition, Ingestion Pipeline, Cascade Delete Lambda, DB API Lambda, Events Lambda, Gallery Lambda, HEIC Converter Lambda (+10 more)

### Community 35 - "db_api/src/Manager/manager.py"
Cohesion: 0.18
Nodes (13): create_job(), _table(), update_job_status(), handle(), _create(), handle_action(), _update_status(), lambda_handler() (+5 more)

### Community 36 - "ingestion/test/integration/test_route_handler.py"
Cohesion: 0.20
Nodes (12): handle(), handle_stream_records(), lambda_handler(), inject_lambda_context, _create_tables(), _FakeLambdaContext, mock_aws, test_event_attendees_stream_record_triggers_match_attendees() (+4 more)

### Community 37 - "aws_s3_bucket.photos"
Cohesion: 0.18
Nodes (14): aws_s3_bucket_cors_configuration.photos, aws_s3_bucket.deploy_artifacts, aws_s3_bucket_lifecycle_configuration.photos, aws_s3_bucket_notification.photos_eventbridge, aws_s3_bucket.photos, aws_s3_bucket_public_access_block.deploy_artifacts, aws_s3_bucket_public_access_block.photos, output.deploy_artifacts_bucket_arn (+6 more)

### Community 38 - "Profile.jsx"
Cohesion: 0.22
Nodes (13): SelfieOptionsSheet(), SelfieToast(), getMyEvents(), deleteSelfie(), getProfile(), updateEmailNotifications(), updateProfile(), uploadSelfie() (+5 more)

### Community 39 - "Gallery Unit Tests"
Cohesion: 0.23
Nodes (15): _photo(), _stub_signing(), test_bulk_delete_photos_drops_unauthorized_and_reuses_single_events_lookup(), test_bulk_delete_photos_skips_invoke_when_nothing_authorized(), test_delete_photo_authorizes_organizer(), test_delete_photo_authorizes_uploader(), test_delete_photo_rejects_unauthorized_caller(), test_delete_photo_rejects_when_event_archived() (+7 more)

### Community 40 - "Upload Status Handler"
Cohesion: 0.42
Nodes (14): lambda_handler(), inject_lambda_context, _api_event(), _create_events_table(), _create_jobs_table(), _FakeLambdaContext, mock_aws, test_job_status_reflects_row_written_by_db_api() (+6 more)

### Community 41 - "Events Route Handler"
Cohesion: 0.38
Nodes (13): handle_internal_action(), lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _FakeLambdaContext, mock_aws (+5 more)

### Community 42 - "Events Unit Tests"
Cohesion: 0.24
Nodes (12): _event(), test_archive_event_deletes_collection_and_marks_archived(), test_archive_event_is_a_no_op_when_already_archived(), test_delete_event_invokes_cascade_delete(), test_get_event_detail_raises_for_non_owner(), test_get_stats_returns_photo_count_storage_and_attendee_count(), test_list_events_returns_public_shape(), test_list_my_events_excludes_self_organized_events() (+4 more)

### Community 43 - "Zip Extraction Logic"
Cohesion: 0.26
Nodes (11): extract_entries(), _is_junk_entry(), get_user(), handle_stage(), _parse_upload_key(), test_stage_copies_each_entry_raw_and_writes_manifest(), test_stage_does_no_format_sniffing_or_decoding(), _zip_bytes() (+3 more)

### Community 44 - "Selfie Match Dispatcher"
Cohesion: 0.21
Nodes (10): get_user(), invoke_ingestion(), list_attendee_rows_for_user(), handle(), dispatch(), lambda_handler(), inject_lambda_context, _FakeContext (+2 more)

### Community 45 - "Frontend Hosting Infrastructure"
Cohesion: 0.23
Nodes (11): aws_cloudfront_distribution.hosting, aws_cloudfront_origin_access_control.hosting, aws_s3_bucket.hosting, aws_s3_bucket_policy.hosting_oac_access, aws_s3_bucket_public_access_block.hosting, data.aws_iam_policy_document.hosting_oac_access, output.bucket_arn, output.bucket_name (+3 more)

### Community 46 - "Marketing Landing Pages"
Cohesion: 0.16
Nodes (11): ImageSlot(), About(), audiences, pairs, HowItWorks(), pipeline, properties, stackGroups (+3 more)

### Community 47 - "Cognito Auth Service"
Cohesion: 0.24
Nodes (12): AuthProvider(), api, confirmPassword(), confirmSignUp(), forgotPassword(), getCurrentSession(), login(), refreshCurrentSession() (+4 more)

### Community 48 - "Profile Route Handler"
Cohesion: 0.45
Nodes (11): lambda_handler(), inject_lambda_context, _api_event(), _create_users_table(), _FakeLambdaContext, mock_aws, test_confirm_selfie_rejects_and_deletes_when_not_exactly_one_face(), test_delete_selfie_removes_object() (+3 more)

### Community 49 - "Upload Status Tests"
Cohesion: 0.24
Nodes (9): _event(), _job(), test_get_job_status_rejects_job_belonging_to_another_uploader(), test_get_job_status_returns_job_owned_by_caller(), test_get_latest_job_returns_most_recent_via_dao(), test_mint_upload_url_allows_organizer_when_organizer_only(), test_mint_upload_url_builds_key_from_event_and_user_and_generated_job_id(), test_mint_upload_url_rejects_archived_event() (+1 more)

### Community 50 - "System Architecture Diagram"
Cohesion: 0.17
Nodes (12): Jenkins Logo, Python Logo, Terraform Logo, System Architecture Diagram, Amazon DynamoDB, AWS Lambda, AWS Step Functions, DynamoDB Streams (+4 more)

### Community 51 - "events/infra/iam_policies.tf"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 52 - "gallery/infra/iam_policies.tf"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 53 - "membership/infra/input.tf"
Cohesion: 0.18
Nodes (10): var.alarm_sns_topic_arn, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.name_prefix (+2 more)

### Community 56 - "upload_status/infra/input.tf"
Cohesion: 0.20
Nodes (9): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.events_table_arn, var.events_table_name, var.jobs_table_arn, var.jobs_table_name, var.name_prefix, var.photos_bucket_arn (+1 more)

### Community 57 - "Cognito User Pool"
Cohesion: 0.33
Nodes (6): aws_cognito_user_pool_client.this, aws_cognito_user_pool.this, output.user_pool_arn, output.user_pool_client_id, output.user_pool_id, var.name_prefix

### Community 58 - "SES Email Identity"
Cohesion: 0.31
Nodes (6): aws_sesv2_email_identity_feedback_attributes.sender, aws_sesv2_email_identity.sender, output.sender_email, output.sender_identity_arn, output.sender_verification_status, var.sender_email

### Community 59 - "SNS Alerting Infrastructure"
Cohesion: 0.32
Nodes (5): aws_sns_topic.alerts, aws_sns_topic_subscription.alerts_email, output.alarm_sns_topic_arn, var.alarm_email, var.name_prefix

### Community 60 - "Linting Configuration"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

### Community 61 - "Upload Flow UI"
Cohesion: 0.43
Nodes (6): getJobStatus(), getUploadUrl(), fibonacciPollDelay(), STAGE_LABEL, STAGE_PCT, UploadFlow()

### Community 62 - "Finalization Unit Tests"
Cohesion: 0.62
Nodes (6): _manifest_bytes(), _result_file_bytes(), test_all_succeeded(), test_counts_task_level_index_failures(), test_some_photos_failed_but_others_succeeded(), test_total_failure_when_nothing_succeeded()

### Community 63 - "Membership IAM Policies"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.users_access

### Community 64 - "Upload Status IAM"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.events_access, aws_iam_role_policy.jobs_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.jobs_access, data.aws_iam_policy_document.photos_bucket_access

### Community 65 - "DB API Inputs"
Cohesion: 0.33
Nodes (5): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.jobs_table_arn, var.jobs_table_name, var.name_prefix

### Community 67 - "File Deduplication Utility"
Cohesion: 0.53
Nodes (4): compute_content_hash(), test_computes_sha256_hash(), test_different_bytes_produce_different_hash(), test_same_bytes_produce_same_hash()

### Community 68 - "Frontend Infrastructure Outputs"
Cohesion: 0.47
Nodes (4): module.hosting, output.bucket_name, output.distribution_domain_name, output.distribution_id

### Community 69 - "Delete Event Tests"
Cohesion: 0.60
Nodes (3): _event(), test_delete_event_cascade_deletes_collection_faces_photos_s3_and_attendees(), test_delete_event_cascade_skips_batch_calls_when_nothing_to_delete()

### Community 70 - "HEIC Converter Inputs"
Cohesion: 0.40
Nodes (4): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn

### Community 71 - "Manifest Building Tests"
Cohesion: 0.70
Nodes (4): _manifest_bytes(), _result_file_bytes(), test_build_photos_manifest_counts_task_level_failures(), test_build_photos_manifest_keeps_only_succeeded_photos()

### Community 72 - "AWS Service Icons"
Cohesion: 0.40
Nodes (5): API Gateway Icon, CloudFront Icon, EventBridge Icon, Lambda Icon, Glimpses README

### Community 73 - "Frontend README"
Cohesion: 0.40
Nodes (5): Frontend README, Oxc, SWC, @vitejs/plugin-react, @vitejs/plugin-react-swc

### Community 74 - "cascadeDelete/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 76 - "db_api/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 77 - "download/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 78 - "events/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 79 - "gallery/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 80 - "heic_converter/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 81 - "ingestion/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 82 - "membership/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 83 - "notifications/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 84 - "test_delivery.py"
Cohesion: 0.67
Nodes (3): mock_aws, test_delivery_is_deduplicated_and_respects_preference(), test_failed_send_releases_claim_for_retry()

### Community 85 - "profile/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 86 - "selfie_match_dispatcher/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 87 - "upload_status/infra/iam_role.tf"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 89 - "System Architecture Overview"
Cohesion: 0.67
Nodes (3): System Architecture Overview, AWS Step Function Workflow, Glimpses Platform

## Knowledge Gaps
- **316 isolated node(s):** `var.alarm_sns_topic_arn`, `var.deploy_artifacts_bucket`, `var.event_attendees_table_arn`, `var.event_attendees_table_name`, `var.events_stream_arn` (+311 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `handle_internal_action()` connect `Events Route Handler` to `Events Data Access`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Why does `test_list_my_events_returns_only_pending_and_attendee_rows()` connect `Events Route Handler` to `Membership Unit Tests`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **What connects `var.alarm_sns_topic_arn`, `var.deploy_artifacts_bucket`, `var.event_attendees_table_arn` to the rest of the system?**
  _316 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API Gateway Configuration` be split into smaller, more focused modules?**
  _Cohesion score 0.056915807560137456 - nodes in this community are weakly interconnected._
- **Should `Cascade Delete Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.09941944847605225 - nodes in this community are weakly interconnected._
- **Should `Events Data Access` be split into smaller, more focused modules?**
  _Cohesion score 0.09796806966618288 - nodes in this community are weakly interconnected._
- **Should `Frontend Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._