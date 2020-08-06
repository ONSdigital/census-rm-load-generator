locals {
  receipting_topic_name           = "receipting-topic-${var.peer_environment}"
  receipting_subscription_name    = "receipting-subscription-${var.peer_environment}"
  eq_fulfilment_topic_name        = "eq-fulfilment-topic-${var.peer_environment}"
  eq_fulfilment_subscription_name = "eq-fulfilment-subscription-${var.peer_environment}"
  fulfilment_confirmed_topic_name = "fulfilment-confirmed-topic"
  qm_undelivered_topic_name       = "qm-undelivered-topic"
}

resource "kubernetes_config_map" "pubsub-config" {

  metadata {
    name = "pubsub-config"
  }

  data = {
    receipt-topic-name              = local.receipting_topic_name
    receipt-topic-project-id        = var.load-gen_peer_project
    subscription-name               = local.receipting_subscription_name
    subscription-project-id         = var.load-gen_peer_project
    eq-fulfilment-topic-name        = local.eq_fulfilment_topic_name
    eq-fulfilment-subscription-name = local.eq_fulfilment_subscription_name
    eq-fulfilment-project-id        = var.load-gen_peer_project
    fulfilment-confirmed-project    = var.load-gen_peer_project
    fulfilment-confirmed-topic-name = local.fulfilment_confirmed_topic_name
    offline-receipt-topic-project   = var.load-gen_peer_project
    qm-undelivered-project-id       = var.load-gen_peer_project
    qm-undelivered-topic-name       = local.qm_undelivered_topic_name
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
