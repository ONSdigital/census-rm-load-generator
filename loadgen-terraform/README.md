# Load gen env
This terraform can be used to creat an environment/k8s cluster from which we can run a large scale load gen activity from

##  RabbitMQ Access

- To access the RabbitMQ cluster the target project will need to be peered with the load-gen project
- A k8s secret "rabbitmq" is expected by the load-gen deployment so this will need to be created, note: the host needs
to be the interal IP of rabbit as the k8s internal DNS is nt visible (so using "rabbitmq" as the host wont work)


##  Postgres Access
- To get to the postgres we have to use the public IP along with the correct SSL certs, you will need to create the
following secrets: cloud-sql-certs,cloud-sql-jdbc-certs, db-credentials and the db-config configmap
- the load-gen NAT gateway IP will need to whitelisted in the postgres instance
