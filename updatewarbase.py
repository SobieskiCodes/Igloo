import requests
import json
import time
import sys
import os

header = {'X-Api-Key': os.environ.get('api_header_key')}
torn_key = os.environ.get('torn_api_key')


def main(facid):
    logging.info('/warbase starting war update')
    try:
        members = {}
        faction_url = f"https://api.torn.com/faction/{facid}?selections=&key={torn_key}"
        test = requests.get(faction_url)
        if test.status_code == 200:
            members = test.json()
        if test.status_code != 200:
                logging.info(f'/warbase torn status {test.status_code}')
                return

        the_dict = {}
        for member in members['members']:
            logging.info(f'/warbase {member}')
            tes = requests.get(f'https://api.torn.com/user/{member}?selections=profile,personalstats&key={torn_key}')
            if tes.status_code != 200:
                the_json = tes.json()
                the_dict[member] = the_json
                time.sleep(5)
            if tes.status_code != 200:
                logging.info(f'/warbase torn status {tes.status_code}')
                return

        testing = json.dumps(the_dict)
        logging.info('/warbase sending dict')
        requests.put("https://probsjust.in/api/warbase", data=testing, headers=header)
        logging.info(f'/warbase sending dict')
    except Exception as e:
        logging.error(f'/warbase {e}')


class Log:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def info(self, message: str):
        self._write(f':INFO: {message}')

    def error(self, message: str):
        self._write(f':ERROR: {message}')

    def warning(self, message: str):
        self._write(f':WARNING: {message}')

    def critical(self, message: str):
        self._write(f':CRITICAL: {message}')

    def _write(self, message: str):
        with open(self.file_name, 'a') as file:
            file.write(f'logging {message} \n')


logging = Log('./test.log')

main(sys.argv[1])
