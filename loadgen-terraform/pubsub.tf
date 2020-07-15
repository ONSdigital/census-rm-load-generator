locals {
  receipting_topic_name           = "receipting-topic-${var.environment_name}"
  receipting_subscription_name    = "receipting-subscription-${var.environment_name}"
  eq_fulfilment_topic_name        = "eq-fulfilment-topic-${var.environment_name}"
  eq_fulfilment_subscription_name = "eq-fulfilment-subscription-${var.environment_name}"

}

resource "kubernetes_config_map" "pubsub-config" {

  metadata {
    name = "pubsub-config"
  }

  data = {
    receipt-topic-name              = local.receipting_topic_name
    receipt-topic-project-id        = var.gcp_project
    subscription-name               = local.receipting_subscription_name
    subscription-project-id         = var.gcp_project
    eq-fulfilment-topic-name        = local.eq_fulfilment_topic_name
    eq-fulfilment-subscription-name = local.eq_fulfilment_subscription_name
    eq-fulfilment-project-id        = var.gcp_project
  }
}

// PUBSUB SERVICE ACCOUNT AND ROLES
resource "google_service_account" "pubsub-loadgen" {
  account_id   = "pubsub-loadgen"
  display_name = "RM Pub/Sub loadgen service account"
}

resource "kubernetes_service_account" "pubsub-loadgen" {
  automount_service_account_token = false
  metadata {
    name = "pubsub-loadgen"
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.pubsub-loadgen.email
    }
  }
}

resource "google_service_account_iam_binding" "pubsub-loadgen-workload-identity" {
  service_account_id = google_service_account.pubsub-loadgen.name
  role               = "roles/iam.workloadIdentityUser"
  members            = ["serviceAccount:${var.gcp_project}.svc.id.goog[default/pubsub-loadgen]"]
  depends_on         = [google_container_cluster.response-management]
}
