terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend remoto (S3) — descomentar após criar o bucket
  # backend "s3" {
  #   bucket         = "marh-agent-terraform-state"
  #   key            = "hml/terraform.tfstate"
  #   region         = "sa-east-1"
  #   encrypt        = true
  #   dynamodb_table = "marh-agent-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "marh-agent"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
