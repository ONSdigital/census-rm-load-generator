import random
import time
from datetime import datetime

import requests

from config import Config
from utilities.db_helper import execute_sql_query

api_call_rate = int(Config.API_CALL_RATE)  # Per second
test_cases = []
total_api_calls = int(Config.TOTAL_API_CALLS)


def get_cases_from_db(num_of_cases_to_fetch=int(Config.CASES_TO_FETCH)):
    sql_query = f'''
    SELECT c.case_id, c.case_ref, c.case_type, c.address_level, c.region, c.treatment_code, u.uac, u.qid
    FROM casev2.cases c, casev2.uac_qid_link u
    WHERE u.caze_case_id = c.case_id
    LIMIT {num_of_cases_to_fetch};'''

    db_result = execute_sql_query(sql_query)

    for row in db_result:
        case = {
            "case_id": row[0],
            "case_ref": row[1],
            "case_type": row[2],
            "address_level": row[3],
            "region": row[4],
            "treatment_code": row[5],
            "uac": row[6],
            "qid": row[7]
        }

        test_cases.append(case)


def call_the_api():
    with open(f'case-api-results-{time.strftime("%Y%m%d-%H%M%S")}.csv', 'w') as results_file:
        for _ in range(total_api_calls):
            random_delay = random.random() / api_call_rate  # In seconds
            random_case = test_cases[random.randint(0, len(test_cases) - 1)]

            time.sleep(random_delay)

            try:
                start_time = time.time()
                response = requests.get(
                    f"{Config.CASE_API_URL}/cases/{random_case['case_id']}")
                total_time = int(round((time.time() - start_time) * 1000))  # In milliseconds

                response.raise_for_status()
                results_file.write(f'{datetime.now().isoformat()},{total_time},\n')
            except requests.exceptions.HTTPError as errh:
                total_time = int(round((time.time() - start_time) * 1000))  # In milliseconds
                results_file.write(f'{datetime.now().isoformat()},{total_time},"Http Error: {errh}"\n')
            except requests.exceptions.ConnectionError as errc:
                total_time = int(round((time.time() - start_time) * 1000))  # In milliseconds
                results_file.write(f'{datetime.now().isoformat()},{total_time},"Error Connecting: {errc}"\n')
            except requests.exceptions.Timeout as errt:
                total_time = int(round((time.time() - start_time) * 1000))  # In milliseconds
                results_file.write(f'{datetime.now().isoformat()},{total_time},"Timeout Error: {errt}"\n')
            except requests.exceptions.RequestException as err:
                total_time = int(round((time.time() - start_time) * 1000))  # In milliseconds
                results_file.write(f'{datetime.now().isoformat()},{total_time},"Other Error: {err}"\n')


def main():
    print("Preparing the data...")

    # Load a bunch of cases from the DB
    get_cases_from_db()

    # Call Case API
    print('Running test...')
    call_the_api()

    # Done!
    print('Finished test.')


if __name__ == "__main__":
    main()
