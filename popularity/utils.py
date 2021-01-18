import os
import requests
from rest_framework import status

POPULAR_REPO_RESULT = "popular"
NOT_POPULAR_REPO_RESULT = "not popular"


def get_github_api_response(repo_name):
    personal_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
    if personal_token is None:
        return status.HTTP_503_SERVICE_UNAVAILABLE, "PERSONAL ACCESS TOKEN not granted on server"
    try:
        response = requests.get(f'https://api.github.com/repos/{repo_name}',
                                headers={'Authorization': f'Token {personal_token}'})
    except OSError:
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "not proper value for PERSONAL ACCESS TOKEN"
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return status.HTTP_503_SERVICE_UNAVAILABLE, "PERSONAL ACCESS TOKEN not authorizing with Github Rest Api"
    if response.status_code not in [status.HTTP_200_OK]:
        return response.status_code, response.reason
    resp_json = response.json()
    _num_stars = resp_json['stargazers_count']
    _num_forks = resp_json['forks']
    return response.status_code, calculate_popularity(num_stars=_num_stars, num_forks=_num_forks)


def calculate_popularity(num_stars, num_forks):
    """Calculate if GitHub repository is popular or not.
     "popular" means the repo for which score >= 500 where score = num_stars * 1 + num_forks * 2."""
    _popularity = NOT_POPULAR_REPO_RESULT
    popularity_limit = 500
    if (num_stars + num_forks * 2) >= popularity_limit:
        _popularity = POPULAR_REPO_RESULT
    return _popularity
