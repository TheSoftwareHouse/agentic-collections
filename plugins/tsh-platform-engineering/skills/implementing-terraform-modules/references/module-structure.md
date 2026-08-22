# Terraform module structure

## Repository layout

For a shared module library, group by provider then by component:

```text
terraform-modules/
├── aws/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── s3/
├── azure/
│   ├── vnet/
│   ├── aks/
│   └── storage/
└── gcp/
    ├── vpc/
    ├── gke/
    └── cloud-sql/
```

## Standard module layout

Every module, without exception:

```text
module-name/
├── main.tf          # resources
├── variables.tf     # inputs
├── outputs.tf       # outputs
├── versions.tf      # terraform and provider constraints
├── README.md        # what it makes, and how to call it
├── examples/
│   └── complete/    # a runnable root module — also the test fixture
│       ├── main.tf
│       └── variables.tf
└── tests/
    └── module_test.go
```

A module missing `versions.tf` inherits whatever the consumer happens to have, which
is how a module that worked last month breaks on a new machine.

## Worked example — AWS VPC

### main.tf

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.name
    },
    var.tags
  )
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.name}-private-${count.index + 1}"
      Tier = "private"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  count  = var.create_internet_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.name}-igw"
    },
    var.tags
  )
}
```

Three conventions to carry into every module: `merge()` so consumers can add tags
without losing the module's own, `count` for optional resources rather than a
separate module, and interpolated names derived from a single `var.name`.

### variables.tf

```hcl
variable "name" {
  description = "Name of the VPC"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  validation {
    condition     = can(cidrnetmask(var.cidr_block))
    error_message = "CIDR block must be valid IPv4 CIDR notation."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = []
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

variable "create_internet_gateway" {
  description = "Whether to create an Internet Gateway"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

The `validation` block on `cidr_block` is the pattern worth copying: catch a bad value
at plan time, with a message that says what a good value looks like, rather than
letting the provider fail mid-apply.

### outputs.tf

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr_block" {
  description = "CIDR block of VPC"
  value       = aws_vpc.main.cidr_block
}
```

Export anything a consumer might compose against. Adding an output later is harmless;
discovering it is missing while wiring a dependent module is not.

## Practices

1. Semantic versioning on published modules.
2. Provider versions pinned in `versions.tf`.
3. `description` on every variable and output.
4. A runnable example in `examples/`.
5. `validation` blocks where a wrong value fails late.
6. Outputs for every attribute a consumer could need.
7. `locals` for computed values.
8. `count` or `for_each` for conditional and repeated resources.
9. Tests with Terratest — see [testing modules](./testing-modules.md).
10. Consistent tagging, merged with consumer tags.
