install:
	pipenv install --dev

package_vulnerability:
	# TODO reinstate this once https://github.com/pypa/pipenv/issues/4188 is resolved
	#pipenv check

flake:
	pipenv run flake8 .
