//allow access from home
resource "google_compute_firewall" "main-allow-wfh" {
  count = length(var.wfh_allowed_cidrs) > 0 ? 1 : 0

  name    = "k8s-override-allow-wfh"
  network = google_compute_network.k8s-subnet.name

  priority  = 750
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = var.wfh_allowed_cidrs
}

resource "google_compute_firewall" "main-allow-network-ips" {
  name    = "k8s-override-internal-traffic"
  network = google_compute_network.k8s-subnet.name

  priority  = 750
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = [var.k8s_master_cidr, var.k8s_subnetwork_nodes_cidr, var.k8s_subnetwork_pods_alias_cidr, var.k8s_subnetwork_services_alias_cidr]
}

