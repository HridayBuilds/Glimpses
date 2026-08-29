variable "name_prefix" {
  description = "Prefix applied to every resource's AWS-visible name (T-06)"
  type        = string
  default     = "glimpses"
}

variable "ingestion_function_arn" {
  description = "ARN of the ingestion Lambda every Task state invokes (Stage/ProcessOnePhoto/BuildPhotosManifest/IndexOnePhoto/Finalize/ListAttendees/MatchAttendees)"
  type        = string
}

variable "db_api_function_arn" {
  description = "ARN of the db_api Lambda, invoked by UpdateJobStatus after Finalize to flip the Jobs row out of PENDING (jobId/status/succeededCount/failedCount, matching Finalize's own output)"
  type        = string
}

variable "photos_bucket_name" {
  description = "Name of the glimpses-photos bucket (T-09), matched by the upload-complete EventBridge rule"
  type        = string
}

variable "photos_bucket_arn" {
  description = "ARN of the glimpses-photos bucket, for IAM scoping IndexPhotos' manifest read (uploads/ prefix, T-09)"
  type        = string
}

variable "rekognition_index_max_concurrency" {
  description = "IndexPhotos Distributed Map's MaxConcurrency. This account's measured IndexFaces TPS quota is 5, not the published default of 50 (SETUP_STEPS.md #5)."
  type        = number
  default     = 5
}

variable "rekognition_search_max_concurrency" {
  description = "MatchAttendees Distributed Map's MaxConcurrency, for SearchFacesByImage. Measured 2026-08-17 via `aws service-quotas list-service-quotas --service-code rekognition` — this account's real TPS quota is 5, same value IndexFaces measured at (SETUP_STEPS.md #5), confirmed independently rather than assumed."
  type        = number
  default     = 5
}

variable "photo_processing_max_concurrency" {
  description = "ProcessPhotos Distributed Map's MaxConcurrency"
  type        = number
  default     = 4
}
