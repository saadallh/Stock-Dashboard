# Fetch available Availability Zones in the region specified by the provider
data "aws_availability_zones" "available" {}

# Fetch the default VPC (if you want to use the default VPC)
data "aws_vpc" "default" {
  default = true
}
