install:
	pipenv install --dev

package_vulnerability:
	PIPENV_PYUP_API_KEY="" pipenv check

flake:
	pipenv run flake8 .

build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-load-generator .

delete-pod:
	kubectl delete deploy load-generator

apply-deployment:
	kubectl apply -f load-generator-deployment.yml

connect-to-pod:
	kubectl exec -it $(kubectl get pods --selector=app=load-generator -o jsonpath='{.items[*].metadata.name}') -- /bin/bash
