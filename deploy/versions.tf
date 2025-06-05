terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.17.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.37.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.99.1"
    }
  }
  required_version = ">= 1.12"
}