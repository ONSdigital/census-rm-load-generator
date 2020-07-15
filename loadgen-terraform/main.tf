terraform {
  backend "gcs" {
    prefix = "rm"
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.region
  version = "~> 2.1"
}

provider "null" {
  version = "~> 2.1.2"
}

provider "template" {
  version = "~> 2.1.2"
}

data "google_client_config" "current" {
}

provider "kubernetes" {
  version = "1.10"
  host    = "https://${google_container_cluster.response-management.endpoint}"
  token   = data.google_client_config.current.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.response-management.master_auth[0].cluster_ca_certificate,
  )
  load_config_file = false
}

