# census-rm-load-generator
Performance testing simulated load generator

## How to run (locally)
Run: `PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run python app.py`

## How to run (in GCP)
Run:

1. `make apply-deployment`
2. `connect-to-pod`
3. `python app.py`
