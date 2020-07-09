# census-rm-load-generator
Performance testing simulated load generator

This app loads a configured (Config.CASES_TO_FETCH) number of cases from the database and a configured 
(Config.UNADDRESSED_QIDS_TO_FETCH) number of unlinked qids from the database.

It will prepare a fixed number of msgs (Config.TOTAL_MESSAGES_TO_SEND), then send those msgs with small delays based on
a random time / Config.MESSAGE_RATE.

The messages it sends are set in the list 'message_weightings', this has the types and weighting which should add up to 100.

In order to run this you will need a good sized sample and unaddressed qids in the database.

## Chaos Monkey
Each message type can be configured to have a random amount of chaos, as controlled by a P-value.

In order to turn off the chaos, set the chaos value to zero for all the message types in the `message_settings` block, in `app.py`.

## How to run (locally)
Run: `PUBSUB_EMULATOR_HOST=localhost:8538 pipenv run python app.py`

## How to run (in GCP)
Run:

1. `make apply-deployment`
2. `make connect-to-pod`
3. `python app.py`
