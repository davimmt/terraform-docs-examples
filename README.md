# terraform-examples

Provides you a almost-ready-to-copy-and-paste example on how to call a module using Terraform style.

If you have a file regex-named *var*.tf anywhere from the root where you execute the script (it searches recursivly), it will take it's variables content and write it to a README.md.

Example of file and it's output:

`variable.tf`
``` 
...

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "ami" {
  default     = "ami-0f8243a5175208e08"
  description = "The AMI to use, default is AL2"
  type        = string
}

variable "public" {
  description = "Whether the instance is public or not"
  type        = bool
}

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
}

...
```
`README.md`
```
<!-- BEGIN_TF_EXAMPLES -->
## Example
```hcl
module "ec2" {
  ...
  vpc_id            = string [__required__]
  ami               = string ["ami-0f8243a5175208e08"]
  public            = bool [__required__]
  shutdown_behavior = string ["terminate"]
  root_block_device = object({
    encrypted   = bool
    volume_size = number
    volume_type = string
  }) [{
    "encrypted"   = true
    "volume_size" = 10
    "volume_type" = "gp3"
  }]
  block_devices     = list(object({
    encrypted   = bool
    device_name = string
    volume_size = number
    volume_type = string
  })) [[]]
  ...
}
<!-- END_TF_EXAMPLES -->
```
