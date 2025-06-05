resource "helm_release" "fast-api" {
  name             = "fast-api"
  chart            = "./helm-charts/fast-api"
  create_namespace = true
  namespace        = "dev"

  values = [
    file("${path.module}/helm-charts/fast-api/values.yaml")
  ]
  set {
    name  = "image.tag"
    value = var.image_tag
  }
}