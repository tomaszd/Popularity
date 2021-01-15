# Development tricks
Python 3.7.2
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8000
```
### Basic auth checks:
##### Register a new user:
$ curl -X POST http://127.0.0.1:8000/auth/users/ --data 'username=djoser&password=alpine12'
{"email": "", "username": "djoser", "id":1}
##### Get access token
curl -X POST http://127.0.0.1:8000/auth/token/login/ --data 'username=djoser&password=alpine12'
{"auth_token": "b704c9fc3655635646356ac2950269f352ea1139"}
##### Use token for api:
$ curl -LX GET http://127.0.0.1:8000/auth/users/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'
{"email": "", "username": "djoser", "id": 1}

##### use swagger Api:
navigate to /doc/
use django login button
login as an admin
use the swagger UI api


