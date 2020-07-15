// create a network with no initial subnets
resource "google_compute_network" "k8s-subnet" {
  name                    = "loadgen-subnet"
  auto_create_subnetworks = "false"
  routing_mode            = "REGIONAL"
  description             = "Private Kubernetes cluster network"
}

// create a large subnet for kubernetes worker nodes
resource "google_compute_subnetwork" "nodes" {
  name                     = "nodes"
  ip_cidr_range            = var.k8s_subnetwork_nodes_cidr
  region                   = var.region
  network                  = google_compute_network.k8s-subnet.self_link
  private_ip_google_access = "true"

  secondary_ip_range {
    range_name    = "response-management-loadgen-pods"
    ip_cidr_range = var.k8s_subnetwork_pods_alias_cidr
  }

  secondary_ip_range {
    range_name    = "response-management-loadgen-services"
    ip_cidr_range = var.k8s_subnetwork_services_alias_cidr
  }
}

// static address to be used by Google Cloud NAT
resource "google_compute_address" "k8s-nat-address" {
  name = "nat"
}

resource "google_compute_router" "k8s-router" {
  name    = "rtr-rm-${var.environment_name}"
  project = var.gcp_project
  region  = google_compute_subnetwork.nodes.region
  network = google_compute_network.k8s-subnet.self_link
}

resource "google_compute_router_nat" "k8s-nat" {
  name                               = "nat-rm-${var.environment_name}"
  project                            = var.gcp_project
  router                             = google_compute_router.k8s-router.name
  region                             = "europe-west2"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                            = [google_compute_address.k8s-nat-address.self_link]
}

resource "google_compute_network_peering" "loadgen-rm" {
  count = var.load-gen_peer_project != "" ? 1 : 0

  name         = "loadgen-rm"
  network      = google_compute_network.k8s-subnet.self_link
  peer_network = "projects/${var.load-gen_peer_project}/global/networks/k8s-subnet"
}