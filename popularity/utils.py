import os
import requests
from rest_framework import status

POPULAR_REPO_RESULT = "popular"
NOT_POPULAR_REPO_RESULT = "not popular"


def get_github_api_response(repo_name):
    personal_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
    if not personal_token:
        return status.HTTP_503_SERVICE_UNAVAILABLE, "PERSONAL TOKEN NOT GRANTED ON SERVER"
    response = requests.get(f'https://api.github.com/repos/{repo_name}',
                            headers={'Authorization': f'Token {personal_token}'})
    if response.status_code not in [status.HTTP_200_OK]:
        return response.status_code, response.reason
    resp_json = response.json()
    _stars = resp_json['stargazers_count']
    _forks = resp_json['forks']
    return response.status_code, calculate_popularity(stars=_stars, forks=_forks)


def calculate_popularity(stars, forks):
    _popularity = NOT_POPULAR_REPO_RESULT
    popularity_limit = 500
    if (stars + forks * 2) >= popularity_limit:
        _popularity = POPULAR_REPO_RESULT
    return _popularity
