# Glimpses — Environment Setup Steps

**What this file is:** a running log of the one-time, human-run setup steps needed to get from "nothing exists" to "Terraform can deploy Glimpses" — IAM, local tooling, and the Terraform state backend bootstrap. Written as we did each step, in order, so it's reproducible later (including by `Sam`, self-deploying the repo from Terraform, per the recurring cast in `LOCKED_PRODUCT.md`).

**What this file is not:** infrastructure-as-code. Nothing here is run by Terraform or CI — these are the steps that have to happen *before* either can do anything, done once, by hand, outside all 10 `T-06` CI jobs.

**Region:** `ap-south-1` (Mumbai) — ruled `P-95`/`D-124`.

---

## 1. IAM user for Terraform

**Why:** Terraform needs AWS credentials to create/modify resources. Using AWS root account keys for this is a real risk — root has no ceiling (billing, account closure, everything), so leaked root keys are catastrophic, while a scoped IAM user's leaked keys are contained. AWS itself discourages root access keys for anything programmatic.

**Steps taken:**
1. Signed in to the AWS Console as root (one of the few things root still does).
2. IAM → Users → Create user → named `glimpses-terraform`. No console access granted — programmatic only.
3. Attached AWS-managed policies directly (broad-but-scoped-to-services, tightenable later once the full resource set is known):
   - `AmazonDynamoDBFullAccess`
   - `AWSLambda_FullAccess`
   - `IAMFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonAPIGatewayAdministrator`
   - `AWSStepFunctionsFullAccess`
   - `AmazonRekognitionFullAccess`
   - `CloudWatchFullAccess`
4. Created an access key for CLI use (Security credentials tab → Create access key → "Command Line Interface (CLI)"). Key id and secret saved outside the repo (password manager), never pasted into chat or committed anywhere.

**Result:** IAM user `arn:aws:iam::921274142861:user/glimpses-terraform`.

---

## 2. Local AWS CLI configuration

**Why:** the IAM user's keys need to live somewhere Terraform (and the CLI) can read them, outside the repo so `gitleaks` (`T-07`) never has anything to catch here.

**Steps taken:**
```
aws configure --profile glimpses
```
Prompted for and entered:
- Access Key ID (from step 1)
- Secret Access Key (from step 1)
- Default region: `ap-south-1`
- Default output format: `json`

This writes to `~/.aws/credentials` and `~/.aws/config` — both outside this repo.

**Verified with:**
```
aws sts get-caller-identity --profile glimpses
```
Returned:
```json
{
    "UserId": "AIDA5NABX2CGRUFI2Y6ED",
    "Account": "921274142861",
    "Arn": "arn:aws:iam::921274142861:user/glimpses-terraform"
}
```

---

## 3. Terraform version

**Why:** `T-06` requires native S3 state locking (`use_lockfile = true`), which needs **Terraform ≥1.10**.

**Steps taken:**
```
terraform version    # was 1.15.6 — already satisfies ≥1.10, updated anyway
brew update
brew upgrade terraform
terraform version    # now 1.15.8
```

---

## 4. Terraform state bucket (manual bootstrap)

**Why:** `T-06` — S3 bucket backend with native locking, versioning on, no DynamoDB lock table. This bucket has to exist *before* any `terraform apply`, so it can't be created by Terraform itself (an apply can't depend on the state store it's about to write to). Created once, by hand, outside all 10 CI jobs.

**Steps taken, using the `glimpses` CLI profile (not root):**

```
aws s3api create-bucket \
  --bucket glimpses-terraform-state \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1 \
  --profile glimpses
```
```
aws s3api put-bucket-versioning \
  --bucket glimpses-terraform-state \
  --versioning-configuration Status=Enabled \
  --profile glimpses
```
```
aws s3api put-public-access-block \
  --bucket glimpses-terraform-state \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true \
  --profile glimpses
```

**Result:** bucket `glimpses-terraform-state` in `ap-south-1`, versioned, fully blocked from public access, default SSE-S3 encryption (on by default for new buckets, no separate step needed).

---

## 5. Rekognition service quota check (`ap-south-1`)

**Why:** `P-95`/`D-124` flagged Rekognition availability in `ap-south-1` as an unverified obligation. `T-02` separately requires `MaxConcurrency` (the Distributed Map's fan-out concurrency for `IndexFaces`/`SearchFacesByImage`) to be set to the deploying account's **actual** TPS Service Quota for each operation, not the published default of 50 — new/lightly-used accounts commonly start lower.

**Checked:** Rekognition is available in `ap-south-1`. Account's actual `IndexFaces` TPS quota is **5**, not the published default of 50. **`SearchFacesByImage`'s TPS quota was measured separately, 2026-08-17** (`aws service-quotas list-service-quotas --service-code rekognition --query "Quotas[?contains(QuotaName, 'SearchFaces')]"`, after finding the quota under Service Quotas → Amazon Rekognition, not inside the Rekognition console itself) — also **5**, same as `IndexFaces`, confirmed rather than assumed.

**Consequence:** the Terraform variables `rekognition_index_max_concurrency` and `rekognition_search_max_concurrency` (`T-02`, on the `state_machines` module) are both set to **5**, not 50. This throttles ingestion/matching throughput (batches process slower than the 50-TPS case) but changes nothing about correctness — the Distributed Maps' retry/backoff and tolerated-failure-% handle this regardless of the concurrency ceiling. A quota increase can be requested later via the Service Quotas console if throughput becomes a real bottleneck at scale; not needed now.

---

## 6. `infrastructure/providers.tf` and `infrastructure/variables.tf`

**Why:** the composition root (`T-06`) needs a `terraform {}` block (required Terraform/provider versions, the S3 backend pointing at `glimpses-terraform-state` with `use_lockfile = true`) and a `provider "aws" {}` block. Region is a Terraform variable (`aws_region`, default `ap-south-1`) rather than hardcoded, per the "keep Terraform parameterised by region" obligation on `P-95`/`D-124`.

**Note:** the `backend "s3" {}` block's own values (`bucket`, `region`) must be literal strings — Terraform reads backend config before any variables are resolved, so it can't reference `var.*` there. Only the `provider "aws"` block's region is a variable.

## 7. `terraform init` — first run, credential error and fix

> **⚠ If any Terraform command fails with:**
> ```
> Error: validating provider credentials: retrieving caller identity from STS: ...
> api error InvalidClientTokenId: The security token included in the request is invalid.
> ```
> **you're almost certainly missing `AWS_PROFILE=glimpses` in this terminal session. Run:**
> ```
> export AWS_PROFILE=glimpses
> ```
> **then retry. Full explanation below.**

**Error hit:**
```
Error: validating provider credentials: retrieving caller identity from STS: ...
api error InvalidClientTokenId: The security token included in the request is invalid.
```

**Cause:** the AWS SDK's default credential chain resolves to a profile named literally `"default"` when neither `AWS_PROFILE` nor a `profile` argument is set — and no `[default]` section (or a stale one) exists in `~/.aws/credentials`, only `[glimpses]` (written by `aws configure --profile glimpses` in step 2). Terraform's provider proactively calls `sts:GetCallerIdentity` on init to validate whatever credentials it resolved, which is where this surfaced immediately.

**Fix — set the profile via environment variable, not hardcoded in `providers.tf`** (keeps the Terraform code credential-agnostic for Jenkins/`Sam` later, who won't have a profile named `glimpses`):
```
export AWS_PROFILE=glimpses
terraform init
```

**Result:** succeeded — S3 backend configured against `glimpses-terraform-state`, `hashicorp/aws` provider v5.100.0 installed, `.terraform.lock.hcl` created (commit this file — it pins the exact provider version for reproducible runs).

**Standing note — this recurs, it's not a one-time fix:** `AWS_PROFILE=glimpses` must be exported in **every new terminal session** before running any Terraform command locally, since the cross-module apply stays manual forever (`T-06` — never automated via Jenkins). Forgetting to export it after opening a fresh terminal tab is the most likely way to hit this same error again later in the build.

---

## Next up

- `infrastructure/modules/dynamodb/` — all 6 tables, per `T-04`'s fully-ruled schema.
