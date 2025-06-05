data "aws_eks_cluster" "eneco" {
  name = "eneco"
}

data "kubernetes_service" "fast-api" {
  depends_on = [helm_release.fast-api]
  metadata {
    name = "fast-api"
  }
}
