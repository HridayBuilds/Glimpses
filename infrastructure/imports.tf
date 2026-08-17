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
