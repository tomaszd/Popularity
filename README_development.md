# Development tricks
### local development
Python 3.7.2
+ pip install -r requirements.txt
+ python manage.py makemigrations
+ python manage.py migrate
+ python manage.py runserver 8000
+ tests: python manage.py test
to utilize the github token please do : export PERSONAL_ACCESS_TOKEN=<your token> before python manage.py runserver 8000

### local docker development
///to use PERSONAL ACCES TOKEN please put it into .env_file
+ docker-compose up
+ docker-compose run web python manage.py createsuperuser
+ docker-compose run web python manage.py test


### Basic auth checks:
##### Register a new user:
+ $ curl -X POST http://127.0.0.1:8000/auth/users/ --data 'username=djoser&password=alpine12'
{"email": "", "username": "djoser", "id":1}
##### Get access token
+ curl -X POST http://127.0.0.1:8000/auth/token/login/ --data 'username=djoser&password=alpine12'
{"auth_token": "b704c9fc3655635646356ac2950269f352ea1139"}
##### Use token for api:
+ $ curl -LX GET http://127.0.0.1:8000/auth/users/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'
{"email": "", "username": "djoser", "id": 1}

#### Use swagger:
+ login in /admin as earlier prepared admin
+ navigate to /doc/
+ use the swagger UI

#### Personal Access Token
+ https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
+ Follow the instructions to obtain Personal Access Token to fasten up the development
+ export PERSONAL_ACCESS_TOKEN=<your_personal_access_token>
+ *Github Api gives 5000/h limit for accesing the GitHubApi*

#### Simple usage of popularity Api:
Be sure the PERSONAL_ACCESS_TOKEN is available as an env variable on running machine
export PERSONAL_ACCESS_TOKEN=<your token>  - for local development
add <your token>  to .env_file             - for docker development
+ Login as an admin
+ navigate to http://127.0.0.1:8000/api/v1/repos/ post new repo name :
e.g. https://github.com/facebook/react/ has millions of stars and forks
+ go to http://127.0.0.1:8000/api/v1/repos/<id>/  detail view
+ utilize extra action "Popular" to obtain the result of repo popularity
+ you can also navigate to http://127.0.0.1:8000/api/v1/repos/<id>/popular to obtain repo popularity instantly

