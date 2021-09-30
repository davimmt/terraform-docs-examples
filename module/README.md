
<!-- BEGIN_TF_EXAMPLES -->
## Example
```hcl
module "module" {
  source               = ./module
  root_block_device    = string [{]
  block_devices        = list(object({
    encrypted   = bool
    device_name = string
    volume_size = number
    volume_type = string
  })) [[]]
  security_group_ids   = list [[]]
  new_hosted_zone_bool = bool [__required__]
  tags                 = map [{}]
}
```
<!-- END_TF_EXAMPLES -->