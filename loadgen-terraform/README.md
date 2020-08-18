# Load gen env
This terraform can be used to creat an environment/k8s cluster from which we can run a large scale load gen activity from

## Creating the env

- Get the relevant details (host IPs etc) from the environment you want to generate the load on, and put these details in `env_config.txt`
- Run the script using `ENV=<<your-loadgen-env-name>> WFH_IP=<<your-ip>> ENV_CONFIG=env_config.txt ./apply.sh`
- Once built, in the target project navigate to `VPC Network Peering` and create a new peering connection. Link this up to the project you've created and the k8s-subnet.
- Whitelist your loadgen project NAT IP on the database and the k8s cluster on the target project
- Add the pod address range of the load generating cluster to the LoadBalancerSourceRanges of the rabbitmq service in the target k8s cluster
- Use the instructions from https://github.com/ONSdigital/census-rm-kubernetes#ssl-connections to set up certificates (does not require jdbc secret)
- In the target env, give the pubsub service account from your loadgen project the pubsub publisher permissions on all the pubsub topics (apart from the data export topic)
- Apply the load-generator-deployment.yml to the new cluster you've set up and see if it works



If you decide not to follow those steps, the following is info for what rabbitmq and postgres require
###  RabbitMQ Access

- To access the RabbitMQ cluster the target project will need to be peered with the load-gen project
- A k8s secret "rabbitmq" is expected by the load-gen deployment so this will need to be created, note: the host needs
to be the internal IP of rabbit as the k8s internal DNS is not visible (so using "rabbitmq" as the host wont work)
- The Pod address range of the load generating cluster needs to be added to the LoadBalancerSourceRanges of the rabbitmq service in the target k8s cluster


###  Postgres Access
- To get to the postgres we have to use the public IP along with the correct SSL certs, you will need to create the
following secrets: cloud-sql-certs, db-credentials and the db-config configmap
- the load-gen NAT gateway IP will need to whitelisted in the postgres instance
