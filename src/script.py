import requests
import datetime
r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
date_time = datetime.datetime.now()
print(f"{date_time} > CRON HIT, RESPONSE CODE = {r.status_code}")