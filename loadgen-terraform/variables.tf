variable "gcp_project" {
}

variable "gcp_folder_id" {
  description = "The folder the project will live in, defaults to the RM development folder"
  default     = "684515858784"
}

variable "gcp_billing_account" {
  description = "The billing account the project will use, defaults to the Census CTS account"
  default     = "010C5C-D2E6F2-FA1F92"
}

variable "region" {
  default = "europe-west2"
}

variable "zones" {
  type    = list(string)
  default = ["europe-west2-a", "europe-west2-b", "europe-west2-c"]
}

variable "environment_name" {
  description = "the name of the environment"
  default     = "response-management"
}

variable "machine_type" {
  default = "n1-standard-4"
}

variable "initial_node_count" {
  description = "The initial number of nodes per node pool, the value 1 in a 3 AZ regional cluster will actually result in 3 nodes"
  default     = 1
}

variable "min_node_count" {
  description = "The min number of nodes per node pool, the value 1 in a 3 AZ regional cluster will actually result in 3 nodes"
  default     = 1
}

variable "max_node_count" {
  description = "The max number of nodes per node pool, the value 1 in a 3 AZ regional cluster will actually result in 3 nodes"
  default     = 1
}

variable "max_pods_per_node" {
  description = "The max number of pods per node"
  default     = 110
}

variable "k8s_min_master_version" {
  description = "The minimum version of the master"
  default     = "1.14.10-gke.36"
}

variable "k8s_subnetwork_nodes_cidr" {
  description = "The Kubernetes nodes subnetwork CIDR"
  default     = "10.60.0.0/16"
}

variable "k8s_subnetwork_pods_alias_cidr" {
  description = "The Kubernetes pods subnetwork alias CIDR"
  default     = "10.70.0.0/16"
}

variable "k8s_subnetwork_services_alias_cidr" {
  description = "The Kubernetes services subnetwork alias CIDR"
  default     = "10.80.0.0/16"
}

variable "k8s_master_cidr" {
  description = "The Kubernetes master CIDR"
  default     = "10.90.0.0/28"
}

variable "k8s_master_whitelist_cidrs" {
  type = list

  default = [
    {
      display_name = "CI NAT"
      cidr_block   = "35.242.166.25/32"
    },
  ]
}

variable "wfh_allowed_cidrs" {
  type    = list(string)
  default = []
}

variable "disable_ci_binding" {
  description = "A boolean toggle for creating ci project viewer role binding"
  default     = "false"
}

variable "load-gen_peer_project" {
  description = "A RM project to peer to"
  default     = ""
}

variable "peer_environment" {
  description = "The peered project environment name"
  default     = ""
}
