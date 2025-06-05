provider "aws" {
  region = var.aws_region
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
    # host                   = data.aws_eks_cluster.eneco.endpoint
    # cluster_ca_certificate = base64decode(data.aws_eks_cluster.eneco.certificate_authority.0.data)
    # exec {
    #   api_version = "client.authentication.k8s.io/v1beta1"
    #   args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.eneco.name]
    #   command     = "aws"
    # }
  }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.eneco.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.eneco.certificate_authority.0.data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.eneco.name]
    command     = "aws"
  }
}
