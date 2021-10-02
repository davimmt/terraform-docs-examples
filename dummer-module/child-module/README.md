<!-- BEGIN_TF_EXAMPLES -->
module "child"
  source = ./dummer-module/child-module
  environment        = string
  instance_number    = number
  root_block_device  = object({
  security_group_ids = list
  tags               = map
}
<!-- END_TF_EXAMPLES -->