import requests
import json
import time
from datetime import datetime
from configparser import ConfigParser
parser = ConfigParser()
parser.read('config.ini')
header = {'X-Api-Key': parser.get('secrets', 'api_header_key')}
torn_key = parser.get('secrets', 'torn_api_key')



def get_the_date():
    today = datetime.today()
    day = today.strftime("%d")
    return day

def main():
    print('starting mem update')
    if get_the_date() == '01':
        requests.post("http://probsjust.in/api/members/reset", headers=header)
    facs = {'igloo': 18569, 'op': 27312}
    for f in facs.values():
        the_dict = {'members': {}}
        faction_url = f"https://api.torn.com/faction/{f}?selections=&key={torn_key}"
        faction_json = requests.get(faction_url).json()
        the_dict['ID'] = f
        for member in faction_json['members']:
            member_url = f"https://api.torn.com/user/{member}?selections=profile,personalstats&key={torn_key}"
            get_member = requests.get(member_url).json()
            the_dict['members'][member] = get_member
            time.sleep(7)
        test = json.dumps(the_dict)
        print(test)
        print('sending mems to server')
        try:
            requests.put("http://probsjust.in/api/members", headers=header, data=test)
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to update mems {e}\n{exc}')


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