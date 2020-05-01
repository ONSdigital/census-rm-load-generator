install:
	pipenv install --dev

package_vulnerability:
	pipenv check

flake:
	pipenv run flake8 .

build:
	docker build -t eu.gcr.io/census-rm-ci/rm/census-rm-load-generator .