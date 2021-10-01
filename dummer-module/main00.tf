locals { 
  loop = {
    for i in range(0, ceil(var.instance_number/length(var.subnet_ids))): i => {
      instance_subnet = concat(local.helper, var.subnet_ids)
    }
  }

  instance_subnet = flatten([
    for loop_key, loop_value in local.loop : [
      for subnet_key, id in loop_value.instance_subnet : id
    ]
  ])
}

variable "environment" {
  description = "Environment type"

  validation {
    condition     = contains(["Development", "Homologation", "Production"], var.environment)
    error_message = "Valid values include Development, Homologation, Production."
  }
}

resource "aws_iam_group" "group" {
  name = var.name
  path = "/${var.path}/"
}

variable "instance_number" {
  default     = 1
  description = "Number of instances"
  type        = number
}

output "id" {
  value = aws_instance.ec2.*.id
}
