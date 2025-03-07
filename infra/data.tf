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

data "aws_internet_gateway" "gw" {
  filter {
    name = "attachment.vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Data source to retrieve available availability zones
data "aws_availability_zones" "available" {}