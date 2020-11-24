import requests
header = {'X-Api-Key': 'xxxxxxxx'}
verify = requests.get('http://probsjust.in/api/test', headers=header).json()
if verify['message'] == "OK":
    clean = 'http://probsjust.in/api/members/clean'
    reset = 'http://probsjust.in/api/members/reset'
    send = requests.post(clean, headers=header).json()
    print(send['message'])
