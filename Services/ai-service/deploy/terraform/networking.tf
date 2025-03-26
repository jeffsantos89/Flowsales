# ========================== #
#    VARIÁVEIS UTILIZÁVEIS   #
# ========================== #
variable "region" {
    description = "The AWS region to deploy resources in"
    default     = "us-east-1"
}

variable "vpc_cidr" {
    description = "The CIDR block for the VPC"
    default     = "10.0.0.0/16"
}

variable "public_subnets" {
    description = "A list of public subnet CIDR blocks"
    type        = list(string)
    default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
    description = "A list of private subnet CIDR blocks"
    type        = list(string)
    default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "enable_nat_gateway" {
    description = "Enable NAT Gateway for private subnets"
    type        = bool
    default     = true
}

provider "aws" {
    region = var.region
}

data "aws_availability_zones" "available" {}

# ========================== #
#        CRIAÇÃO DA VPC      #
# ========================== #
resource "aws_vpc" "main" {
    cidr_block           = var.vpc_cidr
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {
        Name = "ai-service-vpc"
    }
}

# ========================== #
#    INTERNET GATEWAY        #
# ========================== #
resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "main-igw"
    }
}

# ========================== #
#  SUBNETS PÚBLICAS & PRIVADAS #
# ========================== #
resource "aws_subnet" "public" {
    count                   = length(var.public_subnets)
    vpc_id                  = aws_vpc.main.id
    cidr_block              = var.public_subnets[count.index]
    map_public_ip_on_launch = true
    availability_zone       = data.aws_availability_zones.available.names[count.index]
    tags = {
        Name = "public-subnet-${count.index + 1}"
        Type = "Public"
    }
}

resource "aws_subnet" "private" {
    count                   = length(var.private_subnets)
    vpc_id                  = aws_vpc.main.id
    cidr_block              = var.private_subnets[count.index]
    map_public_ip_on_launch = false
    availability_zone       = data.aws_availability_zones.available.names[count.index]
    tags = {
        Name = "private-subnet-${count.index + 1}"
        Type = "Private"
    }
}

# ========================== #
#   TABELAS DE ROTEAMENTO    #
# ========================== #
resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "public-route-table"
    }
}

resource "aws_route" "public_internet_access" {
    route_table_id         = aws_route_table.public.id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public" {
    count          = length(var.public_subnets)
    subnet_id      = aws_subnet.public[count.index].id
    route_table_id = aws_route_table.public.id
}

# ========================== #
#    NAT GATEWAY (Privadas)  #
# ========================== #
resource "aws_eip" "nat" {
    count  = var.enable_nat_gateway ? 1 : 0
    domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
    count         = var.enable_nat_gateway ? 1 : 0
    allocation_id = aws_eip.nat[0].id
    subnet_id     = aws_subnet.public[0].id
    tags = {
        Name = "ai-service-nat"
    }
}

resource "aws_route_table" "private" {
    count  = var.enable_nat_gateway ? 1 : 0
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "private-route-table"
    }
}

resource "aws_route" "private_nat_access" {
    count                  = var.enable_nat_gateway ? 1 : 0
    route_table_id         = aws_route_table.private[0].id
    destination_cidr_block = "0.0.0.0/0"
    nat_gateway_id         = aws_nat_gateway.nat[0].id
}

resource "aws_route_table_association" "private" {
    count          = length(var.private_subnets)
    subnet_id      = aws_subnet.private[count.index].id
    route_table_id = var.enable_nat_gateway ? aws_route_table.private[0].id : aws_route_table.public.id
}

# ========================== #
#   SECURITY GROUP BÁSICO    #
# ========================== #
resource "aws_security_group" "default" {
    name        = "default-security-group"
    description = "Security group padrão para acesso restrito"
    vpc_id      = aws_vpc.main.id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "default-security-group"
    }
}

# ========================== #
#          OUTPUTS           #
# ========================== #
output "vpc_id" {
    value = aws_vpc.main.id
}

output "public_subnet_ids" {
    value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
    value = aws_subnet.private[*].id
}

output "internet_gateway_id" {
    value = aws_internet_gateway.igw.id
}

output "nat_gateway_id" {
    value = var.enable_nat_gateway ? aws_nat_gateway.nat[0].id : "NAT Gateway disabled"
}
