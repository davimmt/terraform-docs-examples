locals { 
  helper = []

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

  output = slice(local.instance_subnet, 0, var.instance_number)
}

variable "project_name" {
  description = "Project Name"
  type        = string
}

variable "caller" {
  description = "User account ID calling the Terraform"
}

variable "environment" {
  description = "Environment type"

  validation {
    condition     = contains(["Development", "Homologation", "Production"], var.environment)
    error_message = "Valid values include Development, Homologation, Production."
  }
}

variable "public" {
  description = "Whether the instance is public or not"
  type        = bool
}

resource "aws_iam_group" "group" {
  name = var.name
  path = "/${var.path}/"
}

resource "aws_iam_group_policy_attachment" "iam_group_policy_attachment" {
  count      = length(var.policies_arn)
  policy_arn = var.policies_arn[count.index]
  group      = aws_iam_group.group.name
}


variable "instance_number" {
  default     = 1
  description = "Number of instances"
  type        = number
}

variable "name" {
  description = "Launch template and instances sufix name"
  type        = string
}

output "id" {
  value = aws_instance.ec2.*.id
}

output "public_ip" {
  value = aws_instance.ec2.*.public_ip
}

output "private_ip" {
  value = aws_instance.ec2.*.public_ip
}


