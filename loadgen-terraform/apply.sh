#!/bin/bash
set -e

if [ -z "$ENV" ]; then
  echo "Missing ENV variable"
  exit 1
fi

if [ "$WFH_IP" ]; then
    echo "Using $WFH_IP as WFH IP"
fi

GCP_PROJECT=census-rm-$ENV
GCP_BUCKET=$GCP_PROJECT-tfstate
GCP_REGION=europe-west2

rm -rf .terraform

tfenv install

cat > terraform.tfvars << EOS
environment_name = "$ENV"
region = "$GCP_REGION"
gcp_project = "$GCP_PROJECT"
EOS

if [ "$RM_PEER_PROJECT" ]; then
    cat >> terraform.tfvars << EOS
load-gen_peer_project = "$RM_PEER_PROJECT"
EOS
fi

if [ "$WFH_IP" ]; then
    cat >> terraform.tfvars << EOS
wfh_allowed_cidrs = ["$WFH_IP"]
k8s_master_whitelist_cidrs = [
	{
		display_name = "Home"
		cidr_block   = "$WFH_IP"
	},
]
EOS
fi


gcloud config set project $GCP_PROJECT
gsutil mb -p $GCP_PROJECT -c regional -l $GCP_REGION gs://$GCP_BUCKET/ || true
gsutil versioning set on gs://$GCP_BUCKET
gcloud services enable servicenetworking.googleapis.com \
                       container.googleapis.com \
                       compute.googleapis.com \
                       --project $GCP_PROJECT  --quiet

terraform init \
    -backend-config="bucket=$GCP_BUCKET" \
    -backend-config="prefix=rm"
if [ "$WORKSPACE" ]; then
	terraform workspace new $WORKSPACE || terraform workspace select $WORKSPACE
else
	terraform workspace select default
fi

terraform apply -var "gcp_project=$GCP_PROJECT"