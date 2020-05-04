install:
	pipenv install --dev

package_vulnerability:
# uncomment this when the api key bug is fixed
# 	pipenv check

flake:
	pipenv run flake8 .

build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-load-generator .

delete-pod:
	kubectl delete deploy load-generator

apply-deployment:
	kubectl apply -f load-generator-deployment.yml

connect-to-pod:
	kubectl exec -it `kubectl get pods -o name | grep -m1 load-generator | cut -d'/' -f 2` -- /bin/bash