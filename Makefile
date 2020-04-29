install:
	pipenv install --dev

package_vulnerability:
	pipenv check

flake:
	pipenv run flake8 .
