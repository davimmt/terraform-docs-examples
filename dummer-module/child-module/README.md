<!-- BEGIN_TF_EXAMPLES -->
module "child"
  source = ./dummer-module/child-module
  variable "environment" {
  description = "Environment type"
  validation {
  condition = contains(["Development", "Homologation", "Production"], var.environment)
  error_message = "Valid values include Development, Homologation, Production."
  }
  }
  variable "instance_number" {
  default = 1
  description = "Number of instances"
  type = number
  }
  variable "root_block_device" {
  default = {
  "encrypted" = true
  "volume_size" = 10
  "volume_type" = "gp3"
  }
  description = "Root block devices"
  type = object({
  encrypted = bool
  volume_size = number
  volume_type = string
  })
  validation {
  condition = contains(["gp2", "gp3", "io1", "io2", "sc1", "st1"], var.root_block_device.volume_type)
  error_message = "Valid values include standard, gp2, gp3, io1, io2, sc1, or st1. Defaults to gp2."
  }
  }
  variable "security_group_ids" {
  default = []
  description = "Secutiry group ids"
  type = list
  }
  variable "tags" {
  default = {}
  description = "Resource's Tags"
  type = map
}
<!-- END_TF_EXAMPLES -->