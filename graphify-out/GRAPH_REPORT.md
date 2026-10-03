# Graph Report - Glimpses  (2026-10-04)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1816 nodes · 3228 edges · 248 communities (132 shown, 116 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.85)
- Token cost: 10,373 input · 2,660 output

## Graph Freshness
- Built from commit: `d0558696`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- API Gateway Configuration
- Events Data Access
- Drive Import Infrastructure
- Cascade Delete Logic
- Database Integration Tests
- Frontend Dependencies
- Download Management Service
- Google Drive Manager
- Gallery Data Access
- User Profile Service
- Membership Data Access
- EventBridge Workflow Orchestration
- Photo Ingestion Service
- Infrastructure Root Modules
- Photo Processing Pipeline
- Membership Unit Tests
- React Auth Context
- Download IAM Policies
- QR and Camera Components
- Events Infrastructure Inputs
- Gallery Route Handler
- Profile IAM Policies
- DynamoDB Table Definitions
- Gallery UI Components
- Ingestion Infrastructure Inputs
- Upload Status Service
- Gallery Infrastructure Inputs
- HEIC Image Converter
- Ingestion Result Mapping
- CloudFront Photo Distribution
- Ingestion Stream Handler
- S3 Bucket Infrastructure
- Gallery Manager Tests
- Membership UI Components
- Profile UI Components
- Ingestion IAM Policies
- Upload Status Routes
- Event Manager Tests
- Zip Extraction Logic
- Selfie Match Dispatcher
- Frontend Hosting Infrastructure
- Marketing Landing Pages
- Upload Flow Components
- Cascade Delete Policies
- Cascade Delete Inputs
- Database API Service
- Upload Status Tests
- App Analytics UI
- Cognito Auth Provider
- Event Management UI
- Tech Stack Documentation
- Events IAM Policies
- Gallery IAM Policies
- Membership Infrastructure Inputs
- Download Manager Tests
- Drive Import DAO
- Upload Status Inputs
- Lambda IAM Roles
- Google Drive Client
- Cognito User Pool
- SNS Alerting Infrastructure
- Linting Configuration
- Finalization Task Tests
- Membership IAM Policies
- Upload Status Policies
- Database API Inputs
- Content Deduplication Utility
- Frontend Infrastructure Outputs
- Event Deletion Tests
- HEIC Converter Inputs
- Manifest Building Tests
- Frontend Tooling Docs
- Marketing Layout Components
- Cascade Delete Roles
- Database API Roles
- Download Service Roles
- Events Service Roles
- Gallery Service Roles
- HEIC Converter Roles
- Ingestion Service Roles
- Membership Service Roles
- Profile Service Roles
- Selfie Dispatcher Roles
- Upload Status Roles
- Frontend Provider Config
- System Architecture Docs
- Cascade Delete Monitoring
- Cascade Delete Outputs
- Database API Monitoring
- Database API Policies
- Database API Outputs
- Download Service Monitoring
- Download Service Outputs
- Drive Import Monitoring
- Drive Import Outputs
- Drive Import Handler
- Events Service Monitoring
- Events Function Outputs
- Gallery Monitoring
- Gallery Function Outputs
- HEIC Converter Monitoring
- HEIC Converter Permissions
- HEIC Converter Outputs
- Ingestion Monitoring
- Ingestion Function Outputs
- Membership Monitoring
- Membership Function Outputs
- Membership Route Handler
- Profile Monitoring
- Profile Function Outputs
- Profile Route Handler
- Selfie Match Monitoring
- Selfie Match Outputs
- Upload Status Monitoring
- Upload Status Outputs
- Infrastructure Terraform Lock
- DynamoDB Stream Integration
- Rekognition Image Analysis
- S3 Storage Service
- Lambda Powertools Utilities
- WAF Security Configuration
- Codebase Documentation Overview
- Event Management UI
- User Profile UI
- Cascade Delete Trigger
- DB API Function
- Events Lambda Function
- HEIC Converter Function
- Ingestion Stream Mapping
- Membership Lambda Function
- Core Infrastructure Providers
- Upload Status Function
- DynamoDB Provider Config
- Frontend Infrastructure Providers
- State Machine Providers
- Lambda Powertools Branding
- API Gateway Architecture
- CloudFront Architecture
- DynamoDB Architecture
- EventBridge Architecture
- Step Functions Architecture
- Terraform Tooling
- Landing Page Hero
- Download Interface
- Event Analytics UI
- Events Dashboard
- Photo Gallery Interface
- Event Registration UI
- User Login Interface
- Upload Success UI
- Legal Privacy Page
- Event Sharing UI
- User Registration Interface
- Upload Progress Interface
- Drive Import Logic
- API Gateway Service
- CloudFront CDN Service
- EventBridge Messaging Service
- WAF Security Service
- Cascade Delete Service
- Database API Service
- Download Service Lambda
- Events Service Lambda
- Gallery Service Lambda
- HEIC Converter Service
- Ingestion Service Lambda
- Membership Service Lambda
- Profile Lambda
- Selfie Match Dispatcher
- Upload Status Lambda
- Downloads Table
- Event Attendees Table
- Events Table
- Faces Table
- Jobs Table
- Photos Table
- Users Table
- Marketing Dinner Image
- Marketing Friends Image
- Marketing Networking Image
- Marketing Family Image
- Marketing image of a bride and groom laughing during a wedding ceremony
- Hero image of friends laughing together at an outdoor sunset event
- Hero image of a woman laughing while others take photos of her with smartphones
- Hero image of a couple laughing at an event, seen through a smartphone camera lens
- Hero image of people toasting with wine glasses, with a smartphone capturing the moment
- API Gateway Icon
- CloudFront Icon
- DynamoDB Icon
- EventBridge Icon
- Rekognition Icon
- S3 Icon
- Lambda Icon
- Step Functions Icon
- Boto3 (AWS SDK for Python) icon
- DynamoDB Streams Stack Logo
- Jenkins Stack Logo
- Python Stack Logo
- Frontend React App

## God Nodes (most connected - your core abstractions)
1. `aws_api_gateway_rest_api.this` - 61 edges
2. `lambda_handler()` - 25 edges
3. `react` - 24 edges
4. `aws_iam_role.this` - 20 edges
5. `_event()` - 19 edges
6. `handle_process_one_photo()` - 17 edges
7. `useAuth()` - 17 edges
8. `delete_event_cascade()` - 15 edges
9. `aws_api_gateway_resource.event_id` - 15 edges
10. `module.buckets` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Jenkins Pipeline Registry` --references--> `Jenkins`  [EXTRACTED]
  Infrastructure/cicd/jenkinsfiles.txt → assets/architecture/icon-sources/jenkins-svgrepo-com.png
- `Codebase Knowledge Graph Overview` --references--> `Glimpses`  [EXTRACTED]
  assets/graphify/graph-overview.png → README.md
- `test_api_returns_accepted_job_and_rejects_bad_links()` --calls--> `lambda_handler()`  [INFERRED]
  Backend/drive_import/test/unit/test_import.py → Backend/drive_import/src/routeHandler.py
- `AWS Lambda Powertools for Python logo` --conceptually_related_to--> `AWS Lambda Architecture Icon`  [INFERRED]
  Frontend/public/images/marketing/stack-aws-lambda-powertools.png → assets/architecture/icon-sources/Arch_AWS-Lambda_64.png
- `AWS WAF (Web Application Firewall) icon` --conceptually_related_to--> `AWS WAF Architecture Icon`  [INFERRED]
  Frontend/public/images/marketing/stack-aws-waf.png → assets/architecture/icon-sources/Arch_AWS-WAF_64.png

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI/CD and IaC Stack** — jenkins, terraform, infrastructure_cicd_jenkinsfiles [EXTRACTED 0.90]
- **Face Matching Pipeline** — assets_product_profile, assets_step_function_pipeline_graph, assets_product_photos_of_me [EXTRACTED 0.95]
- **DynamoDB Schema** — dynamodb_users, dynamodb_events, dynamodb_jobs, dynamodb_photos, dynamodb_faces, dynamodb_eventattendees, dynamodb_downloads [EXTRACTED 1.00]
- **Event Lifecycle** — assets_product_events_dashboard, assets_product_event_settings, assets_product_share_event [INFERRED 0.80]
- **AWS Serverless Infrastructure** — aws_lambda, aws_api_gateway, aws_step_functions, aws_dynamodb, aws_eventbridge [INFERRED 0.85]

## Communities (248 total, 116 thin omitted)

### Community 0 - "API Gateway Configuration"
Cohesion: 0.05
Nodes (89): aws_api_gateway_authorizer.cognito, aws_api_gateway_deployment.this, aws_api_gateway_gateway_response.default_4xx, aws_api_gateway_gateway_response.default_5xx, aws_api_gateway_integration.options, aws_api_gateway_integration_response.options, aws_api_gateway_integration.route, aws_api_gateway_method.options (+81 more)

### Community 1 - "Events Data Access"
Cohesion: 0.07
Nodes (55): access_code_exists(), batch_get_events(), count_attendees(), create_collection(), delete_collection(), _dynamodb(), _event_attendees_table(), _events_table() (+47 more)

### Community 2 - "Drive Import Infrastructure"
Cohesion: 0.06
Nodes (49): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.jobs_table_arn, var.jobs_table_name (+41 more)

### Community 3 - "Cascade Delete Logic"
Cohesion: 0.10
Nodes (40): batch_delete_attendees(), batch_delete_faces(), batch_delete_photos(), decrement_event_counters(), delete_collection(), delete_event_row(), delete_faces_from_collection(), delete_photo_row() (+32 more)

### Community 4 - "Database Integration Tests"
Cohesion: 0.15
Nodes (45): Boto3 Logo, _create_jobs_table(), _FakeLambdaContext, mock_aws, test_create_then_mark_success_round_trip(), test_drive_create_retry_preserves_progress_and_counts(), lambda_handler(), _api_event() (+37 more)

### Community 5 - "Frontend Dependencies"
Cohesion: 0.04
Nodes (47): amazon-cognito-identity-js, axios, dependencies, amazon-cognito-identity-js, axios, jsqr, jszip, motion (+39 more)

### Community 6 - "Download Management Service"
Cohesion: 0.11
Nodes (38): abort_multipart_upload(), _batch_get_photo_keys(), complete_multipart_upload(), create_download(), create_multipart_upload(), _downloads_table(), _event_attendees_table(), generate_presigned_url() (+30 more)

### Community 7 - "Google Drive Manager"
Cohesion: 0.08
Nodes (27): parse_folder_link(), _authorize(), collect_page(), combine_results(), download_file(), fail(), handle_step(), initialize() (+19 more)

### Community 8 - "Gallery Data Access"
Cohesion: 0.11
Nodes (35): batch_get_photos(), _event_attendees_table(), _events_table(), generate_presigned_url(), get_attendee(), get_event(), get_photo_by_id(), invoke_cascade_delete() (+27 more)

### Community 9 - "User Profile Service"
Cohesion: 0.13
Nodes (35): clear_current_selfie(), copy_object(), create_user(), delete_object(), detect_face_count(), _dynamodb(), generate_presigned_get_url(), generate_presigned_put_url() (+27 more)

### Community 10 - "Membership Data Access"
Cohesion: 0.14
Nodes (34): _dynamodb(), _event_attendees_table(), _events_table(), get_attendee(), get_event(), get_event_by_access_code(), get_users(), list_attendees_by_status() (+26 more)

### Community 11 - "EventBridge Workflow Orchestration"
Cohesion: 0.12
Nodes (32): aws_cloudwatch_event_rule.upload_complete, aws_cloudwatch_event_target.start_ingestion, aws_iam_role.eventbridge_start_execution, aws_iam_role_policy.distributed_map_self_execution, aws_iam_role_policy.eventbridge_start_execution, aws_iam_role_policy.invoke_db_api, aws_iam_role_policy.invoke_ingestion, aws_iam_role_policy.manifest_access (+24 more)

### Community 12 - "Photo Ingestion Service"
Cohesion: 0.14
Nodes (26): add_matched_photo_ids(), _dynamodb(), _event_attendees_table(), _events_table(), _faces_table(), get_event(), get_faces(), increment_event_counters() (+18 more)

### Community 13 - "Infrastructure Root Modules"
Cohesion: 0.20
Nodes (26): module.alarms, module.api_gateway, module.buckets, module.cascade_delete, module.cloudfront, module.cognito, module.db_api, module.download (+18 more)

### Community 14 - "Photo Processing Pipeline"
Cohesion: 0.13
Nodes (22): sniff_format(), make_thumbnail(), normalize_to_jpeg(), delete_object(), invoke_heic_converter(), _lambda_client(), handle_process_one_photo(), test_returns_none_for_unrecognized_format() (+14 more)

### Community 15 - "Membership Unit Tests"
Cohesion: 0.18
Nodes (25): _attendee(), _event(), _full_event(), test_admit_attendee_rejects_non_pending(), test_admit_attendee_transitions_pending_to_attendee(), test_deny_attendee_transitions_pending_to_blocked(), test_eject_attendee_rejects_non_attendee(), test_eject_attendee_transitions_attendee_to_blocked() (+17 more)

### Community 16 - "React Auth Context"
Cohesion: 0.16
Nodes (15): App(), AuthShell(), RequireAuth(), AuthContext, useAuth(), queryClient, ForgotPassword(), Login() (+7 more)

### Community 17 - "Download IAM Policies"
Cohesion: 0.10
Nodes (22): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.photos_access, data.aws_iam_policy_document.photos_bucket_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket (+14 more)

### Community 18 - "QR and Camera Components"
Cohesion: 0.17
Nodes (17): QRScanner(), scanLoop(), startCamera(), CameraCapture(), startCamera(), cameraErrorMessage(), joinEvent(), BARE_CODE_RE (+9 more)

### Community 19 - "Events Infrastructure Inputs"
Cohesion: 0.11
Nodes (19): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+11 more)

### Community 20 - "Gallery Route Handler"
Cohesion: 0.45
Nodes (19): lambda_handler(), inject_lambda_context, _api_event(), _create_event_attendees_table(), _create_events_table(), _create_photos_table(), _FakeLambdaContext, _put_event() (+11 more)

### Community 21 - "Profile IAM Policies"
Cohesion: 0.11
Nodes (18): aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.photos_bucket_access, data.aws_iam_policy_document.rekognition_access, data.aws_iam_policy_document.users_access, var.alarm_sns_topic_arn, var.deploy_artifacts_bucket (+10 more)

### Community 22 - "DynamoDB Table Definitions"
Cohesion: 0.17
Nodes (12): aws_dynamodb_table.downloads, aws_dynamodb_table.event_attendees, aws_dynamodb_table.events, aws_dynamodb_table.faces, aws_dynamodb_table.jobs, aws_dynamodb_table.photos, aws_dynamodb_table.users, output.event_attendees_stream_arn (+4 more)

### Community 23 - "Gallery UI Components"
Cohesion: 0.23
Nodes (14): ConfirmDialog(), EventMenu(), Gallery(), formatDate(), PhotoViewer(), api, getDownloadStatus(), requestDownload() (+6 more)

### Community 24 - "Ingestion Infrastructure Inputs"
Cohesion: 0.11
Nodes (18): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.faces_table_arn, var.faces_table_name (+10 more)

### Community 25 - "Upload Status Service"
Cohesion: 0.17
Nodes (17): _events_table(), generate_presigned_put_url(), get_event(), get_job(), _jobs_table(), query_latest_job(), _s3(), get_job_status() (+9 more)

### Community 26 - "Gallery Infrastructure Inputs"
Cohesion: 0.11
Nodes (17): var.alarm_sns_topic_arn, var.cascade_delete_function_arn, var.cascade_delete_function_name, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn (+9 more)

### Community 27 - "HEIC Image Converter"
Cohesion: 0.16
Nodes (12): heic_to_jpeg(), get_object(), put_object(), handle(), convert_and_store(), lambda_handler(), inject_lambda_context, _FakeLambdaContext (+4 more)

### Community 28 - "Ingestion Result Mapping"
Cohesion: 0.27
Nodes (13): count_result_items(), parse_result_file(), parse_result_manifest(), get_object(), list_admitted_attendees(), put_object(), _s3(), handle_build_photos_manifest() (+5 more)

### Community 29 - "CloudFront Photo Distribution"
Cohesion: 0.18
Nodes (15): aws_cloudfront_distribution.photos, aws_cloudfront_key_group.photos_signing, aws_cloudfront_origin_access_control.photos, aws_cloudfront_public_key.photos_signing, aws_s3_bucket_policy.photos_oac_access, data.aws_iam_policy_document.photos_oac_access, output.distribution_domain_name, output.distribution_id (+7 more)

### Community 30 - "Ingestion Stream Handler"
Cohesion: 0.20
Nodes (12): handle(), handle_stream_records(), lambda_handler(), inject_lambda_context, _create_tables(), _FakeLambdaContext, mock_aws, test_event_attendees_stream_record_triggers_match_attendees() (+4 more)

### Community 31 - "S3 Bucket Infrastructure"
Cohesion: 0.18
Nodes (14): aws_s3_bucket_cors_configuration.photos, aws_s3_bucket.deploy_artifacts, aws_s3_bucket_lifecycle_configuration.photos, aws_s3_bucket_notification.photos_eventbridge, aws_s3_bucket.photos, aws_s3_bucket_public_access_block.deploy_artifacts, aws_s3_bucket_public_access_block.photos, output.deploy_artifacts_bucket_arn (+6 more)

### Community 32 - "Gallery Manager Tests"
Cohesion: 0.23
Nodes (15): _photo(), _stub_signing(), test_bulk_delete_photos_drops_unauthorized_and_reuses_single_events_lookup(), test_bulk_delete_photos_skips_invoke_when_nothing_authorized(), test_delete_photo_authorizes_organizer(), test_delete_photo_authorizes_uploader(), test_delete_photo_rejects_unauthorized_caller(), test_delete_photo_rejects_when_event_archived() (+7 more)

### Community 33 - "Membership UI Components"
Cohesion: 0.25
Nodes (12): DEFAULT_MESSAGES, LoadingSpinner(), getOrganizedEvents(), admitAttendee(), denyAttendee(), ejectAttendee(), getAttendees(), getEventInfo() (+4 more)

### Community 34 - "Profile UI Components"
Cohesion: 0.21
Nodes (11): SelfieToast(), getMyEvents(), deleteSelfie(), getProfile(), updateProfile(), uploadSelfie(), EventCard(), eventCardState() (+3 more)

### Community 35 - "Ingestion IAM Policies"
Cohesion: 0.18
Nodes (15): aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.faces_access, data.aws_iam_policy_document.photos_access (+7 more)

### Community 36 - "Upload Status Routes"
Cohesion: 0.42
Nodes (14): lambda_handler(), inject_lambda_context, _api_event(), _create_events_table(), _create_jobs_table(), _FakeLambdaContext, mock_aws, test_job_status_reflects_row_written_by_db_api() (+6 more)

### Community 37 - "Event Manager Tests"
Cohesion: 0.24
Nodes (12): _event(), test_archive_event_deletes_collection_and_marks_archived(), test_archive_event_is_a_no_op_when_already_archived(), test_delete_event_invokes_cascade_delete(), test_get_event_detail_raises_for_non_owner(), test_get_stats_returns_photo_count_storage_and_attendee_count(), test_list_events_returns_public_shape(), test_list_my_events_excludes_self_organized_events() (+4 more)

### Community 38 - "Zip Extraction Logic"
Cohesion: 0.26
Nodes (11): extract_entries(), _is_junk_entry(), get_user(), handle_stage(), _parse_upload_key(), test_stage_copies_each_entry_raw_and_writes_manifest(), test_stage_does_no_format_sniffing_or_decoding(), _zip_bytes() (+3 more)

### Community 39 - "Selfie Match Dispatcher"
Cohesion: 0.21
Nodes (10): get_user(), invoke_ingestion(), list_attendee_rows_for_user(), handle(), dispatch(), lambda_handler(), inject_lambda_context, _FakeContext (+2 more)

### Community 40 - "Frontend Hosting Infrastructure"
Cohesion: 0.23
Nodes (11): aws_cloudfront_distribution.hosting, aws_cloudfront_origin_access_control.hosting, aws_s3_bucket.hosting, aws_s3_bucket_policy.hosting_oac_access, aws_s3_bucket_public_access_block.hosting, data.aws_iam_policy_document.hosting_oac_access, output.bucket_arn, output.bucket_name (+3 more)

### Community 41 - "Marketing Landing Pages"
Cohesion: 0.16
Nodes (8): ImageSlot(), audiences, pairs, pipeline, properties, stackGroups, heroPhotos, steps

### Community 42 - "Upload Flow Components"
Cohesion: 0.22
Nodes (12): getJobStatus(), getUploadUrl(), importDriveFolder(), DriveImport(), start(), LABELS, STAGE_INDEX, STAGES (+4 more)

### Community 43 - "Cascade Delete Policies"
Cohesion: 0.21
Nodes (13): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.faces_access, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access (+5 more)

### Community 44 - "Cascade Delete Inputs"
Cohesion: 0.14
Nodes (13): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.faces_table_arn, var.faces_table_name (+5 more)

### Community 45 - "Database API Service"
Cohesion: 0.29
Nodes (10): create_drive_job(), create_job(), _table(), update_job_status(), handle(), _create(), handle_action(), _update_status() (+2 more)

### Community 46 - "Upload Status Tests"
Cohesion: 0.23
Nodes (10): _event(), _job(), test_drive_status_exposes_progress_and_access_error(), test_get_job_status_rejects_job_belonging_to_another_uploader(), test_get_job_status_returns_job_owned_by_caller(), test_get_latest_job_returns_most_recent_via_dao(), test_mint_upload_url_allows_organizer_when_organizer_only(), test_mint_upload_url_builds_key_from_event_and_user_and_generated_job_id() (+2 more)

### Community 47 - "App Analytics UI"
Cohesion: 0.21
Nodes (6): AppHeader(), getEventStats(), formatBytes(), EventAnalytics(), PRIVACY_ITEMS, CONSENT_POINTS

### Community 48 - "Cognito Auth Provider"
Cohesion: 0.24
Nodes (12): AuthProvider(), userFromSession(), confirmPassword(), confirmSignUp(), forgotPassword(), getCurrentSession(), login(), refreshCurrentSession() (+4 more)

### Community 49 - "Event Management UI"
Cohesion: 0.28
Nodes (9): archiveEvent(), createEvent(), deleteEvent(), getEventDetail(), updateEventDetail(), CreateEvent(), CONTRIBUTION_POLICIES, EventSettings() (+1 more)

### Community 50 - "Tech Stack Documentation"
Cohesion: 0.17
Nodes (12): Jenkins Logo, Python Logo, Terraform Logo, System Architecture Diagram, Amazon DynamoDB, AWS Lambda, AWS Step Functions, DynamoDB Streams (+4 more)

### Community 51 - "Events IAM Policies"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_bucket_access, aws_iam_role_policy.rekognition_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 52 - "Gallery IAM Policies"
Cohesion: 0.27
Nodes (10): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.invoke_cascade_delete, aws_iam_role_policy.photos_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.invoke_cascade_delete (+2 more)

### Community 53 - "Membership Infrastructure Inputs"
Cohesion: 0.18
Nodes (10): var.alarm_sns_topic_arn, var.cloudfront_domain_name, var.deploy_artifacts_bucket, var.event_attendees_table_arn, var.event_attendees_table_name, var.events_table_arn, var.events_table_name, var.name_prefix (+2 more)

### Community 55 - "Drive Import DAO"
Cohesion: 0.27
Nodes (5): create_job(), get_item(), _invoke_db(), table(), update_job()

### Community 57 - "Upload Status Inputs"
Cohesion: 0.20
Nodes (9): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.events_table_arn, var.events_table_name, var.jobs_table_arn, var.jobs_table_name, var.name_prefix, var.photos_bucket_arn (+1 more)

### Community 58 - "Lambda IAM Roles"
Cohesion: 0.28
Nodes (7): aws_lambda_function.this, aws_iam_role_policy.event_attendees_access, data.aws_iam_policy_document.event_attendees_access, aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role, var.event_attendees_stream_arn

### Community 59 - "Google Drive Client"
Cohesion: 0.44
Nodes (8): _api_key(), download(), DriveAccessError, DriveTransientError, folder_metadata(), list_page(), _request(), Exception

### Community 60 - "Cognito User Pool"
Cohesion: 0.33
Nodes (6): aws_cognito_user_pool_client.this, aws_cognito_user_pool.this, output.user_pool_arn, output.user_pool_client_id, output.user_pool_id, var.name_prefix

### Community 61 - "SNS Alerting Infrastructure"
Cohesion: 0.32
Nodes (5): aws_sns_topic.alerts, aws_sns_topic_subscription.alerts_email, output.alarm_sns_topic_arn, var.alarm_email, var.name_prefix

### Community 63 - "Linting Configuration"
Cohesion: 0.25
Nodes (7): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, warn

### Community 64 - "Finalization Task Tests"
Cohesion: 0.62
Nodes (6): _manifest_bytes(), _result_file_bytes(), test_all_succeeded(), test_counts_task_level_index_failures(), test_some_photos_failed_but_others_succeeded(), test_total_failure_when_nothing_succeeded()

### Community 65 - "Membership IAM Policies"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.event_attendees_access, aws_iam_role_policy.events_access, aws_iam_role_policy.users_access, data.aws_iam_policy_document.event_attendees_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.users_access

### Community 66 - "Upload Status Policies"
Cohesion: 0.43
Nodes (6): aws_iam_role_policy.events_access, aws_iam_role_policy.jobs_access, aws_iam_role_policy.photos_bucket_access, data.aws_iam_policy_document.events_access, data.aws_iam_policy_document.jobs_access, data.aws_iam_policy_document.photos_bucket_access

### Community 67 - "Database API Inputs"
Cohesion: 0.33
Nodes (5): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.jobs_table_arn, var.jobs_table_name, var.name_prefix

### Community 68 - "Content Deduplication Utility"
Cohesion: 0.53
Nodes (4): compute_content_hash(), test_computes_sha256_hash(), test_different_bytes_produce_different_hash(), test_same_bytes_produce_same_hash()

### Community 69 - "Frontend Infrastructure Outputs"
Cohesion: 0.47
Nodes (4): module.hosting, output.bucket_name, output.distribution_domain_name, output.distribution_id

### Community 70 - "Event Deletion Tests"
Cohesion: 0.60
Nodes (3): _event(), test_delete_event_cascade_deletes_collection_faces_photos_s3_and_attendees(), test_delete_event_cascade_skips_batch_calls_when_nothing_to_delete()

### Community 71 - "HEIC Converter Inputs"
Cohesion: 0.40
Nodes (4): var.alarm_sns_topic_arn, var.deploy_artifacts_bucket, var.name_prefix, var.photos_bucket_arn

### Community 72 - "Manifest Building Tests"
Cohesion: 0.70
Nodes (4): _manifest_bytes(), _result_file_bytes(), test_build_photos_manifest_counts_task_level_failures(), test_build_photos_manifest_keeps_only_succeeded_photos()

### Community 73 - "Frontend Tooling Docs"
Cohesion: 0.40
Nodes (5): Frontend README, Oxc, SWC, @vitejs/plugin-react, @vitejs/plugin-react-swc

### Community 75 - "Cascade Delete Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 77 - "Database API Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 78 - "Download Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 79 - "Events Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 80 - "Gallery Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 81 - "HEIC Converter Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 82 - "Ingestion Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 83 - "Membership Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 84 - "Profile Service Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 85 - "Selfie Dispatcher Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 86 - "Upload Status Roles"
Cohesion: 0.83
Nodes (3): aws_iam_role_policy_attachment.basic_execution, aws_iam_role.this, data.aws_iam_policy_document.assume_role

### Community 88 - "System Architecture Docs"
Cohesion: 0.67
Nodes (3): System Architecture Overview, AWS Step Function Workflow, Glimpses Platform

## Knowledge Gaps
- **328 isolated node(s):** `output.function_arn`, `output.function_name`, `aws_cloudwatch_log_group.this`, `aws_cloudwatch_metric_alarm.errors`, `output.function_arn` (+323 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **116 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Boto3` connect `Database Integration Tests` to `Cascade Delete Logic`, `User Profile Service`, `Database API Service`, `Drive Import DAO`, `Google Drive Client`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `get_event()` connect `Cascade Delete Logic` to `Events Data Access`, `Membership Data Access`, `Upload Status Service`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `lambda_handler()` connect `Database Integration Tests` to `Google Drive Manager`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `lambda_handler()` (e.g. with `test_create_then_mark_success_round_trip()` and `test_drive_create_retry_preserves_progress_and_counts()`) actually correct?**
  _`lambda_handler()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `output.function_arn`, `output.function_name`, `aws_cloudwatch_log_group.this` to the rest of the system?**
  _328 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API Gateway Configuration` be split into smaller, more focused modules?**
  _Cohesion score 0.05319355464958261 - nodes in this community are weakly interconnected._
- **Should `Events Data Access` be split into smaller, more focused modules?**
  _Cohesion score 0.07364114552893045 - nodes in this community are weakly interconnected._