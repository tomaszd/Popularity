# Project Summary
Popularity API for getting the popularity of github repo.
Popular GitHub repository means one with many forks and stars.
To use Github Rest Api the Github Personal Access Token is needed.

# Project Assumptions
+ App is using PERSONAL_ACCESS_TOKEN from github.
+ PERSONAL_ACCESS_TOKEN is valid and working . Be sure it is available in env in env where the app is running.
+ Rest Github Api GitHub's official REST API https://docs.github.com/en/rest is not changed
+ Service is only for authenticated users. There is TokenAuthentication and SessionAuthentication
+ Speed of obtaining responses from Github Api is changing during day. It is about 0.5s - 1s.
+ Maximum amount of api hits for github api  is 5000/h for 1 token. Service would not work after the limit is reached.
+ Requests library with PERSONAL_ACCESS_TOKEN in Header is used for communicating with Github.
+ The api is communicating live with Github Api. No caching for common calls.
+ Name of Saved github repo should be in github format to identify  github_user/repo_name e.g. facebook/react

# Project Technologies
+ Python 3.7
+ Django 3
+ Django Rest Framework
+ Github Rest Api
+ Django openapi swagger
+ Docker
+ Docker Compose
+ Requests

   1. build the service
      1. run automatic tests
      1. run the service locally

# How to use Service

## 1. build the service locally

+ used Python 3.7
+ pip install -r requirements.txt
+ python manage.py makemigrations
+ python manage.py migrate
+ export PERSONAL_ACCESS_TOKEN=<your token>
+ python manage.py runserver 8000
+ python manage.py createsuperuser
+ login in /admin
+ check http://127.0.0.1:8000/health_check/ if service is working. If not - probably no valid token was granted.
+ navigate to /doc in browser to use swagger
+ navigate to /api/v1/ in browser to use Django Rest Framework UI
+ create new valid repo by POST in /api/v1/repos/  e.g. name="facebook/react"
+ Get /api/v1/repos/<created_model_id>/popular/ to get popularity score


## 1. build the service in local docker

+ based on python:3.7 image
+ add valid PERSONAL ACCESS TOKEN to ".env_file" environment file
+ docker-compose up #this would download python:3.7 if there is no image yet
+ docker-compose run web python manage.py createsuperuser
+ login as superuser in /admin
+ navigate to /doc/ to use swagger
+ navigate to /api/v1/ in browser to use Django Rest Framework UI
+ create new valid repo by POST in /api/v1/repos/  e.g. name="facebook/react"
+ Get /api/v1/repos/<created_model_id>/popular/ to get popularity score

## Automatic tests
### local
+ python manage.py test
### docker
+ docker-compose run web python manage.py test


## Info about  Personal Access Token
+ https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
+ Follow the instructions to obtain Personal Access Token to fasten up the development
+ export PERSONAL_ACCESS_TOKEN=<your_personal_access_token> for local service
+ add valid PERSONAL ACCESS TOKEN to ".env_file" environment file for docker.
+ *Github Api gives 5000 hits/h limit for accessing the GitHubApi*


#### Basic auth checks:
##### Register a new user:
+ $ curl -X POST http://127.0.0.1:8000/auth/users/ --data 'username=djoser&password=alpine12'
{"email": "", "username": "djoser", "id":1}
##### Create token
+ python manage.py drf_create_token djoser
+ >>>>>>>Generated token 62c20951d9f30234719a6a3e117ece3b4ff57df6 for user djoser
{"auth_token": "e80988aed847782fcca766cfdd220ea82fae0649"}
+ #for docker: docker-compose run web python manage.py drf_create_token djoser

##### Use token auth for Api:
+ $ curl -LX GET http://127.0.0.1:8000/api/v1/repos/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'
curl -LX GET http://127.0.0.1:8000/api/v1/repos/ -H 'Authorization: Token e80988aed847782fcca766cfdd220ea82fae0649'

#### Use swagger to traverse UI:
+ login in /admin as earlier prepared user
+ navigate to /doc/
+ use the swagger UI to play with api.

#### Simple usage of popularity Api:
Be sure the PERSONAL_ACCESS_TOKEN is available as an env variable on running machine
+ export PERSONAL_ACCESS_TOKEN=<your token>  - for local development
+ add <your token>  to .env_file             - for docker development
+ Login as an admin
+ check /health_check/ if service is working
+ navigate to http://127.0.0.1:8000/api/v1/repos/ post new repo name :
e.g. https://github.com/facebook/react/ has millions of stars and forks
+ go to http://127.0.0.1:8000/api/v1/repos/<id>/
+ utilize extra action "Popular" to obtain the result of repo popularity
+ you can also navigate to http://127.0.0.1:8000/api/v1/repos/<id>/popular/ to obtain repo popularity instantly
+ observe if repo is "popular" or "not popular"


# Future Improvements
+ PyGithub Library could be used for Rest Github Api (not used due to project restrictions to use REST Github Api)
https://pygithub.readthedocs.io/en/latest/apis.html
+ Communication with Github Api done in faster service. As for now only 0.5s -> 2s speed is reached.
+ Caching/Storing the most common requests to Github Api. As for now the api is live. As for speed of change of
+ Users could send their github tokens. Not only 1 global instance used.
+ Possible another endpoint to save new personal token for users.
+ Users could use api by sending repo links and their personal tokens.
+ Add new paths for 'accounts/* urls to be compatible with Swagger Docs buttons.
+ Use faster db. As for now sqlite is used.
+ Better documentation for swagger
+ As for now App is DEBUG=True mode. It is in development. Remove DEBUG=True to fasten up speed of service.
