module "dynamodb" {
  source = "./modules/dynamodb"
}

module "buckets" {
  source = "./modules/buckets"
}

module "alarms" {
  source = "./modules/alarms"

  alarm_email = var.alarm_email
}

module "cloudfront" {
  source = "./modules/cloudfront"

  photos_bucket_name                 = module.buckets.photos_bucket_name
  photos_bucket_arn                  = module.buckets.photos_bucket_arn
  photos_bucket_regional_domain_name = module.buckets.photos_bucket_regional_domain_name
}

module "heic_converter" {
  source = "../Backend/heic_converter/infra"

  deploy_artifacts_bucket = module.buckets.deploy_artifacts_bucket_name
  photos_bucket_arn       = module.buckets.photos_bucket_arn
  alarm_sns_topic_arn     = module.alarms.alarm_sns_topic_arn
}

module "db_api" {
  source = "../Backend/db_api/infra"

  deploy_artifacts_bucket = module.buckets.deploy_artifacts_bucket_name
  jobs_table_name         = module.dynamodb.table_names["jobs"]
  jobs_table_arn          = module.dynamodb.table_arns["jobs"]
  alarm_sns_topic_arn     = module.alarms.alarm_sns_topic_arn
}

module "download" {
  source = "../Backend/download/infra"

  deploy_artifacts_bucket = module.buckets.deploy_artifacts_bucket_name
  downloads_table_name    = module.dynamodb.table_names["downloads"]
  downloads_table_arn     = module.dynamodb.table_arns["downloads"]
  photos_table_name       = module.dynamodb.table_names["photos"]
  photos_table_arn        = module.dynamodb.table_arns["photos"]
  photos_bucket_name      = module.buckets.photos_bucket_name
  photos_bucket_arn       = module.buckets.photos_bucket_arn
  alarm_sns_topic_arn     = module.alarms.alarm_sns_topic_arn
}

module "ingestion" {
  source = "../Backend/ingestion/infra"

  deploy_artifacts_bucket      = module.buckets.deploy_artifacts_bucket_name
  photos_table_name            = module.dynamodb.table_names["photos"]
  photos_table_arn             = module.dynamodb.table_arns["photos"]
  events_table_name            = module.dynamodb.table_names["events"]
  events_table_arn             = module.dynamodb.table_arns["events"]
  faces_table_name             = module.dynamodb.table_names["faces"]
  faces_table_arn              = module.dynamodb.table_arns["faces"]
  event_attendees_table_name   = module.dynamodb.table_names["event_attendees"]
  event_attendees_table_arn    = module.dynamodb.table_arns["event_attendees"]
  event_attendees_stream_arn   = module.dynamodb.event_attendees_stream_arn
  users_table_name             = module.dynamodb.table_names["users"]
  users_table_arn              = module.dynamodb.table_arns["users"]
  photos_bucket_name           = module.buckets.photos_bucket_name
  photos_bucket_arn            = module.buckets.photos_bucket_arn
  heic_converter_function_name = module.heic_converter.function_name
  heic_converter_function_arn  = module.heic_converter.function_arn
  alarm_sns_topic_arn          = module.alarms.alarm_sns_topic_arn
}

module "profile" {
  source = "../Backend/profile/infra"

  deploy_artifacts_bucket = module.buckets.deploy_artifacts_bucket_name
  users_table_name        = module.dynamodb.table_names["users"]
  users_table_arn         = module.dynamodb.table_arns["users"]
  photos_bucket_name      = module.buckets.photos_bucket_name
  photos_bucket_arn       = module.buckets.photos_bucket_arn
  alarm_sns_topic_arn     = module.alarms.alarm_sns_topic_arn
}

module "upload_status" {
  source = "../Backend/upload_status/infra"

  deploy_artifacts_bucket = module.buckets.deploy_artifacts_bucket_name
  jobs_table_name         = module.dynamodb.table_names["jobs"]
  jobs_table_arn          = module.dynamodb.table_arns["jobs"]
  events_table_name       = module.dynamodb.table_names["events"]
  events_table_arn        = module.dynamodb.table_arns["events"]
  photos_bucket_name      = module.buckets.photos_bucket_name
  photos_bucket_arn       = module.buckets.photos_bucket_arn
  alarm_sns_topic_arn     = module.alarms.alarm_sns_topic_arn
}

module "events" {
  source = "../Backend/events/infra"

  deploy_artifacts_bucket    = module.buckets.deploy_artifacts_bucket_name
  events_table_name          = module.dynamodb.table_names["events"]
  events_table_arn           = module.dynamodb.table_arns["events"]
  event_attendees_table_name = module.dynamodb.table_names["event_attendees"]
  event_attendees_table_arn  = module.dynamodb.table_arns["event_attendees"]
  photos_bucket_name         = module.buckets.photos_bucket_name
  photos_bucket_arn          = module.buckets.photos_bucket_arn
  cloudfront_domain_name     = module.cloudfront.distribution_domain_name
  frontend_domain_name       = var.frontend_domain_name
  alarm_sns_topic_arn        = module.alarms.alarm_sns_topic_arn

  cascade_delete_function_name = module.cascade_delete.function_name
  cascade_delete_function_arn  = module.cascade_delete.function_arn
}

module "membership" {
  source = "../Backend/membership/infra"

  deploy_artifacts_bucket    = module.buckets.deploy_artifacts_bucket_name
  event_attendees_table_name = module.dynamodb.table_names["event_attendees"]
  event_attendees_table_arn  = module.dynamodb.table_arns["event_attendees"]
  events_table_name          = module.dynamodb.table_names["events"]
  events_table_arn           = module.dynamodb.table_arns["events"]
  users_table_name           = module.dynamodb.table_names["users"]
  users_table_arn            = module.dynamodb.table_arns["users"]
  cloudfront_domain_name     = module.cloudfront.distribution_domain_name
  alarm_sns_topic_arn        = module.alarms.alarm_sns_topic_arn
}

module "gallery" {
  source = "../Backend/gallery/infra"

  deploy_artifacts_bucket    = module.buckets.deploy_artifacts_bucket_name
  photos_table_name          = module.dynamodb.table_names["photos"]
  photos_table_arn           = module.dynamodb.table_arns["photos"]
  events_table_name          = module.dynamodb.table_names["events"]
  events_table_arn           = module.dynamodb.table_arns["events"]
  event_attendees_table_name = module.dynamodb.table_names["event_attendees"]
  event_attendees_table_arn  = module.dynamodb.table_arns["event_attendees"]
  photos_bucket_name         = module.buckets.photos_bucket_name
  photos_bucket_arn          = module.buckets.photos_bucket_arn
  cloudfront_domain_name     = module.cloudfront.distribution_domain_name
  alarm_sns_topic_arn        = module.alarms.alarm_sns_topic_arn

  cloudfront_signing_key_pair_id     = module.cloudfront.signing_key_pair_id
  cloudfront_signing_private_key_pem = module.cloudfront.signing_private_key_pem

  cascade_delete_function_name = module.cascade_delete.function_name
  cascade_delete_function_arn  = module.cascade_delete.function_arn
}

module "cascade_delete" {
  source = "../Backend/cascadeDelete/infra"

  deploy_artifacts_bucket    = module.buckets.deploy_artifacts_bucket_name
  events_table_name          = module.dynamodb.table_names["events"]
  events_table_arn           = module.dynamodb.table_arns["events"]
  events_stream_arn          = module.dynamodb.events_stream_arn
  photos_table_name          = module.dynamodb.table_names["photos"]
  photos_table_arn           = module.dynamodb.table_arns["photos"]
  faces_table_name           = module.dynamodb.table_names["faces"]
  faces_table_arn            = module.dynamodb.table_arns["faces"]
  event_attendees_table_name = module.dynamodb.table_names["event_attendees"]
  event_attendees_table_arn  = module.dynamodb.table_arns["event_attendees"]
  photos_bucket_name         = module.buckets.photos_bucket_name
  photos_bucket_arn          = module.buckets.photos_bucket_arn
  alarm_sns_topic_arn        = module.alarms.alarm_sns_topic_arn
}

module "state_machine" {
  source = "./modules/state_machine"

  ingestion_function_arn = module.ingestion.function_arn
  db_api_function_arn    = module.db_api.function_arn
  photos_bucket_name     = module.buckets.photos_bucket_name
  photos_bucket_arn      = module.buckets.photos_bucket_arn
}

module "cognito" {
  source = "./modules/cognito"
}

module "api_gateway" {
  source = "./modules/api_gateway"

  cognito_user_pool_arn = module.cognito.user_pool_arn

  profile_function_name = module.profile.function_name
  profile_function_arn  = module.profile.function_arn

  events_function_name = module.events.function_name
  events_function_arn  = module.events.function_arn

  membership_function_name = module.membership.function_name
  membership_function_arn  = module.membership.function_arn

  upload_status_function_name = module.upload_status.function_name
  upload_status_function_arn  = module.upload_status.function_arn

  gallery_function_name = module.gallery.function_name
  gallery_function_arn  = module.gallery.function_arn

  download_function_name = module.download.function_name
  download_function_arn  = module.download.function_arn
}
