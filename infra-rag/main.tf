terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.56"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # Backend remoto — descomentar após criar bucket de state dedicado ao RAG HML
  # backend "s3" {
  #   bucket         = "marh-agent-terraform-state"
  #   key            = "rag-hml/terraform.tfstate"
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
      Component   = "rag-hml"
      ManagedBy   = "terraform"
    }
  }
}
