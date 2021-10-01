<!-- BEGIN_TF_EXAMPLES -->
module "dummy" {
  source = ./dummy-module
  environment = string [__required__]
  instance_number = number [1]
  root_block_device = {
    encrypted   = bool
    volume_size = number
    volume_type = string
  } [{
    "encrypted"   = true
    "volume_size" = 10
    "volume_type" = "gp3"
  }]
  security_group_ids = list [[]]
  tags = map [{}]
}
<!-- END_TF_EXAMPLES -->
