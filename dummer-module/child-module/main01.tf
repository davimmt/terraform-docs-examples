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

variable "tags" {
  default     = {}
  description = "Resource's Tags"
  type        = map
}
