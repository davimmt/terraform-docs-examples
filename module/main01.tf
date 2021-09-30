variable "root_block_device" {

  default = {
    "encrypted"   = true
    "volume_size" = 10
    "volume_type" = "gp3"
  }

  description = "Root block devices"

  type = object({
    encrypted   = bool
    volume_size = number
    volume_type = string
  })

  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2", "sc1", "st1"], var.root_block_device.volume_type)
    error_message = "Valid values include standard, gp2, gp3, io1, io2, sc1, or st1. Defaults to gp2."
  }
}

variable "block_devices" {
  default     = []
  description = "Block devices"

  type = list(object({
    encrypted   = bool
    device_name = string
    volume_size = number
    volume_type = string
  }))

  validation {

    condition = alltrue([
      for i in var.block_devices : contains(["gp2", "gp3", "io1", "io2", "sc1", "st1"], i.volume_type)
    ])

    error_message = "Valid values include standard, gp2, gp3, io1, io2, sc1, or st1. Defaults to gp2."
  }
}

variable "security_group_ids" {
  default     = []
  description = "Secutiry group ids"
  type        = list
}

resource "random_id" "id" {
  byte_length = 2

  keepers = {
    bucket = var.bucket_name
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket = "${random_id.id.hex}-${var.bucket_name}"
  acl    = "private"
  policy = var.s3_policy == "" ? "" : file("${var.s3_policy}")

  lifecycle_rule {
    enabled = var.lifecycle_rule

    transition {
      days          = 0
      storage_class = var.storage_class
    }
  }

  force_destroy = true

  versioning {
    enabled = var.versioning
  }

  server_side_encryption_configuration {

    rule {

      apply_server_side_encryption_by_default {
        kms_master_key_id = module.s3_kms.key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }

  tags = merge(var.tags, {
    Name        = lower("s3-${replace(var.project_name, " ", "_")}-${replace(regex(".{3}", var.environment), "ro", "rd")}-${random_id.id.hex}-${var.bucket_name}")
    Project     = var.project_name
    Environment = title(lower(var.environment))
    Terraform   = true
    Caller      = var.caller
  })
}

resource "aws_s3_bucket_public_access_block" "s3_block" {
  depends_on          = [aws_s3_bucket.bucket]
  bucket              = aws_s3_bucket.bucket.id
  block_public_acls   = true
  block_public_policy = true
}

module "s3_kms" {
  source          = "../kms-module"
  project_name    = var.project_name
  environment     = var.environment
  caller          = var.caller
  kms_alias_name  = var.bucket_name
  kms_description = var.s3_kms_description
  kms_policy      = var.kms_policy == "" ? "" : file("${var.kms_policy}")
  tags            = var.tags
}

variable "new_hosted_zone_bool" {
  description = "Whether to create a new Hosted Zone (true) or get an existing one (false)"
  type        = bool
}

variable "tags" {
  default     = {}
  description = "Resource's Tags"
  type        = map
}
