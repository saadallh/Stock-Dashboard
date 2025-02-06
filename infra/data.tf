# Data source to retrieve the default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source to retrieve the default subnets
data "aws_subnets" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

# Data source to retrieve available availability zones
data "aws_availability_zones" "available" {
  state = "available"
}