#!/bin/bash
set -e

if [ "$ENV_CONFIG" ]; then
  source $ENV_CONFIG
fi

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

if [ "$RM_PEER_ENV" ]; then
    cat >> terraform.tfvars << EOS
load-gen_peer_project = "census-rm-$RM_PEER_ENV"
peer_environment = "$RM_PEER_ENV"
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

gcloud container clusters get-credentials rm-k8s-cluster \
    --region $GCP_REGION \
    --project $GCP_PROJECT

kubectl config set-context $(kubectl config current-context)

if [ "$RABBIT_HOST" ]; then
  kubectl create secret generic rabbitmq-host --from-literal=rabbitmq-host=$RABBIT_HOST --from-literal=rabbitmq-port=5672
fi

if [ "$RABBIT_PASS" ]; then
  kubectl create secret generic rabbitmq-cred --from-literal=rabbit_password=$RABBIT_PASS --from-literal=rabbit_username=rmquser
fi

if [ "$DB_HOST" ]; then
  kubectl create secret generic db-config --from-literal=db-host=$DB_HOST --from-literal=db-name=rm --from-literal=db-port=5432
fi
