import requests
import json
import time
from configparser import ConfigParser
parser = ConfigParser()
parser.read('config.ini')
header = {'X-Api-Key': parser.get('secrets', 'api_header_key')}
torn_key = parser.get('secrets', 'torn_api_key')

def main():
    logging.info('starting rackets')
    try:
        racket_url = f"https://api.torn.com/torn/?selections=territory,rackets&key={torn_key}"
        racket_json = requests.get(racket_url).json()
        the_dict = {}
        for racket in racket_json['rackets']:
            if racket in racket_json['territory']:
                faction_url = f"http://api.torn.com/faction/{racket_json['rackets'][racket]['faction']}?selections=&key={torn_key}"
                faction_json = requests.get(faction_url).json()
                the_dict[racket] = racket_json['rackets'][racket]
                faction_name = faction_json['name']
                the_dict[racket].update({"factionname": faction_name})
                the_dict[racket]['sector'] = racket_json['territory'][racket]['sector']
                time.sleep(7)
        test = json.dumps(the_dict)
        print(test)
        try:
            resp = requests.put("http://probsjust.in/api/rackets", headers=header, data=test)
        except Exception as e:
            logging.error(f'rackets {e}')
    except Exception as e:
        logging.error(f'rackets {e}')


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

main()
