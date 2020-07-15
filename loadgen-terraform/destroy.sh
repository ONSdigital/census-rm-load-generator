#!/bin/bash
set -e

if [ -z "$ENV" ]; then
  echo "Missing ENV variable"
  exit 1
fi

if [ "$WFH_IP" ]; then
    echo "Using $WFH_IP as WFH IP"
fi

if [ "$DEV_PUBSUB" ]; then
    echo "Dev pubsub resources set to [$DEV_PUBSUB]"
fi

if [ "$DEV_SCALE_DOWN" ]; then
    echo "Dev scale down resources set to [$DEV_SCALE_DOWN]"
fi

if [ "$RH_PEER_PROJECT" ]; then
    echo "Peering with RH project [$RH_PEER_PROJECT]"
fi

GCP_PROJECT=census-rm-$ENV
GCP_BUCKET=$GCP_PROJECT-tfstate
GCP_REGION=europe-west2

rm -rf .terraform

cat > terraform.tfvars << EOS
environment_name = "$ENV"
region = "$GCP_REGION"
gcp_project = "$GCP_PROJECT"
db_user_password = "password"
EOS

if [ "$RH_PEER_PROJECT" ]; then
    cat >> terraform.tfvars << EOS
rh_peer_project = "$RH_PEER_PROJECT"
EOS
fi

if [ "$DEV_PUBSUB" ]; then
    cat >> terraform.tfvars << EOS
dev_pubsub_enabled = "$DEV_PUBSUB"
EOS
fi

if [ "$DEV_SCALE_DOWN" ]; then
    cat >> terraform.tfvars << EOS
dev_scale_down_enabled = "$DEV_SCALE_DOWN"
EOS
fi

if [ "$DEV_SCALE_DOWN_CRON" ]; then
    cat >> terraform.tfvars << EOS
dev_scale_down_cron = "$DEV_SCALE_DOWN_CRON"
EOS
fi

if [ "$DISABLE_CI_BINDING" ]; then
    cat >> terraform.tfvars << EOS
disable_ci_binding = "$DISABLE_CI_BINDING"
EOS
fi

if [ "$WFH_IP" ]; then
    cat >> terraform.tfvars << EOS
wfh_allowed_cidrs = ["$WFH_IP"]
k8s_master_whitelist_cidrs = [
	{
		display_name = "Newport Wifi"
		cidr_block   = "89.248.28.81/32"
	},
	{
		display_name = "Titchfield Wifi"
		cidr_block   = "62.253.69.130/32"
	},
	{
		display_name = "CI NAT"
		cidr_block   = "35.242.166.25/32"
	},
	{
		display_name = "Home"
		cidr_block   = "$WFH_IP"
	},
]
EOS
fi

tfenv install

gcloud config set project $GCP_PROJECT
gsutil mb -p $GCP_PROJECT -c regional -l $GCP_REGION gs://$GCP_BUCKET/ || true


terraform init \
    -backend-config="bucket=$GCP_BUCKET" \
    -backend-config="prefix=rm"
if [ "$WORKSPACE" ]; then
	terraform workspace new $WORKSPACE || terraform workspace select $WORKSPACE
else
	terraform workspace select default
fi

if [ "$AUTO_APPLY" ]; then
    AUTO_APPLY="-auto-approve"
    QUIET="--quiet"
fi
terraform destroy $AUTO_APPLY -var "gcp_project=$GCP_PROJECT"
