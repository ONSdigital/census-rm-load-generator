resource "google_container_cluster" "response-management" {
  provider                 = google-beta
  name                     = "rm-k8s-cluster"
  description              = "Private Kubernetes Cluster - ${var.environment_name} environment"
  location                 = var.region                 // NB: impacts node versions available if missing zone
  min_master_version       = var.k8s_min_master_version // OPTIONAL and likely to be volatile
  network                  = google_compute_network.k8s-subnet.self_link
  subnetwork               = google_compute_subnetwork.nodes.self_link
  initial_node_count       = var.initial_node_count
  remove_default_node_pool = true
  enable_shielded_nodes    = true
  project                  = var.gcp_project

  private_cluster_config {
    enable_private_nodes   = true
    master_ipv4_cidr_block = var.k8s_master_cidr
    enable_private_endpoint = false
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "response-management-loadgen-pods"
    services_secondary_range_name = "response-management-loadgen-services"
  }

  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.k8s_master_whitelist_cidrs
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = lookup(cidr_blocks.value, "display_name", null)
      }
    }
  }

  // this turns off cluster basic auth
  master_auth {
    username = ""
    password = ""

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      // GMT
      start_time = "03:00"
    }
  }

  workload_identity_config {
    identity_namespace = "${var.gcp_project}.svc.id.goog"
  }

  # Use non-legacy monitoring and logging
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
}

resource "google_container_node_pool" "default-node-pool" {
  provider          = google-beta
  name              = "default-node-pool"
  location          = var.region
  cluster           = google_container_cluster.response-management.name
  max_pods_per_node = var.max_pods_per_node
  node_count        = var.initial_node_count
  project           = var.gcp_project

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  node_config {
    machine_type = var.machine_type
    disk_size_gb = 100

    oauth_scopes = [
      "compute-rw",
      "storage-rw",
      "logging-write",
      "monitoring",
    ]

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    // Enables workload identity on the node. This also replaces the need for metadata concealment
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }

    service_account = google_service_account.compute.email
    tags            = ["k8s-node", "default-node-pool"]

  }

  management {
    auto_repair  = "true"
    auto_upgrade = "false"
  }
}

// COMPUTE SERVICE ACCOUNT AND ROLES
resource "google_service_account" "compute" {
  account_id   = "compute"
  display_name = "Compute Engine service account"
}

// Storage Object Viewer permissions to allow kubernetes to pull rm images from the private GCR in census-rm-ci
resource "google_project_iam_member" "ci-storage-object-view" {
  count   = var.disable_ci_binding ? 0 : 1
  project = "census-rm-ci"
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.compute.email}"
}

output "gcloud-k8-login" {
  value = "gcloud container clusters get-credentials ${google_container_cluster.response-management.name} --region ${var.region} --project ${var.gcp_project}"
}

resource "kubernetes_config_map" "project-config" {
  metadata {
    name = "project-config"
  }

  data = {
    project-name = var.gcp_project
  }
}
