from unittest.mock import patch

from django.test import TestCase
# Create your tests here.
from django.urls import resolve, reverse
from djoser.urls.base import User
from rest_framework import status

from popularity import views
from popularity.models import Repo
from popularity.utils import calculate_popularity, POPULAR_REPO_RESULT, NOT_POPULAR_REPO_RESULT

WRONG_TOKEN_VALUE_GOOD_FORMAT = "657e8d9bae9a642fb24503ff2dffb70c5e904401"


class MockRequestsToGithubPopularRepo:
    def __init__(self):
        self.status_code = 200

    @staticmethod
    def json():
        return {
            "stargazers_count": 500,
            "forks": 200
        }


class MockRequestsToGithubNotPopularRepo:
    def __init__(self):
        self.status_code = 200

    @staticmethod
    def json():
        return {
            "stargazers_count": 499,
            "forks": 0
        }


class MockRequestsToGithubNotExistingRepo:
    def __init__(self):
        self.status_code = 404
        self.reason = "not existing"


class SmokeTests(TestCase):
    """Test Repo models, urls smoke test"""

    def setUp(self):
        self.repo1 = Repo.objects.create(name='user/repo1_name')
        self.repo2 = Repo.objects.create(name='user2/repo2_name')

    def test_check_if_view_repos_have_good_class(self):
        found = resolve(reverse('repo-list'))
        self.assertEquals(found.func.cls, views.RepoViewSet)

    def test_check_if_view_single_repo_has_good_class(self):
        found = resolve(reverse('repo-detail', kwargs={'pk': 1}))
        self.assertEquals(found.func.cls, views.RepoViewSet)
        found = resolve(reverse('repo-detail', kwargs={'pk': 2}))
        self.assertEquals(found.func.cls, views.RepoViewSet)

    def test_repos_not_available_for_anonymous(self):
        response = self.client.get(reverse('repo-list'), follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_single_repo_not_available_for_anonymous(self):
        response = self.client.get(reverse('repo-detail', kwargs={'pk': 1}), follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SingleRepoTest(TestCase):
    """Test Addition of new repos, details about single repo"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_check_addition_of_new_repo(self):
        initial_count = Repo.objects.count()
        repo_name = "facebook/react"
        self.assertFalse(Repo.objects.filter(name=repo_name))
        response = self.client.post(reverse('repo-list'), data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Repo.objects.count(), initial_count + 1)
        self.assertTrue(Repo.objects.get(name=repo_name))

    def test_check_uniqueness_of_repo_name(self):
        repo_name = "test_user/test_name"
        response = self.client.post(reverse('repo-list'), data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('repo-list'), data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_single_repo_fields(self):
        repo_name = "test_user/test_name"
        response = self.client.post(reverse('repo-list'), data={"name": repo_name})
        test_id = response.json()['id']
        response = self.client.get(reverse('repo-detail', kwargs={'pk': test_id}))
        response_json = response.json()
        test_id = response_json.get('id')
        self.assertEquals(response_json.get('name'), repo_name)
        self.assertEquals(response_json.get('github_url'), f'https://github.com/{repo_name}/')
        self.assertEquals(response_json.get('url'),
                          ''.join(['http://testserver', reverse('repo-detail', kwargs={'pk': test_id})]))
        self.assertIn('created', response_json)
        self.assertNotEquals(response_json.get('created'), '')

    @patch("os.environ.get", return_value=WRONG_TOKEN_VALUE_GOOD_FORMAT)
    def test_single_repo_popularity_wrong_token_value(self, mocked_env):
        """Test popularity when token granted with not working value."""
        response = self.call_github_rest_api_for_popularity()
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("os.environ.get", return_value=None)
    def test_single_repo_popularity_no_token(self, mocked_env):
        """Test popularity when no token on server."""
        response = self.call_github_rest_api_for_popularity()
        self.assertEquals(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("os.environ.get", return_value="test_personal_access_token_in_env")
    @patch("requests.get", return_value=MockRequestsToGithubPopularRepo())
    def test_single_repo_popularity_valid_response_from_github_popular(self, mocked_env, mocked_requests):
        """Test popularity when token granted on server and github api responsible. Check popular repo."""
        response = self.call_github_rest_api_for_popularity()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), 'popular')

    @patch("os.environ.get", return_value="test_personal_access_token_in_env")
    @patch("requests.get", return_value=MockRequestsToGithubNotPopularRepo())
    def test_single_repo_popularity_valid_response_from_github_not_popular(self, mocked_env, mocked_requests):
        """Test popularity when token granted on server and github api responsible. Check not popular repo."""
        response = self.call_github_rest_api_for_popularity()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json(), 'not popular')

    def call_github_rest_api_for_popularity(self):
        repo_name = "test_user/test_name2"
        response = self.client.post(reverse('repo-list'), data={"name": repo_name})
        test_id = response.json()['id']
        response = self.client.get(f'/api/v1/repos/{test_id}/popular/')
        return response


class RepoListTest(TestCase):
    """Test Addition of new repos, details about single repo"""
    repo_list_url = reverse('repo-list')

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_pagination_visible(self):
        repo_name = "test_user/test_name"
        initial_count = Repo.objects.count()
        amount_of_new_repo = 100

        for i in range(amount_of_new_repo):
            self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}{i}"})
        actual_count = initial_count + amount_of_new_repo
        self.assertEquals(actual_count, initial_count + amount_of_new_repo)
        response_json = self.client.get(self.repo_list_url).json()
        self.assertEquals(response_json.get('count'), actual_count)
        self.assertEquals(response_json.get('next'), f'http://testserver{self.repo_list_url}?page=2')
        self.assertEquals(response_json.get('previous'), None)
        response_next_page_json = self.client.get(f'http://testserver{self.repo_list_url}?page=2').json()
        self.assertEquals(response_next_page_json.get('count'), actual_count)
        self.assertEquals(response_next_page_json.get('previous'), f'http://testserver{self.repo_list_url}')
        self.assertEquals(response_next_page_json.get('next'), f'http://testserver{self.repo_list_url}?page=3')

    def test_check_name_addition(self):
        repo_name = "test_user/test_name"
        response = self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}"}).json()
        self.assertEquals(response.get('name'), repo_name)

    def test_check_name_addition_lstrip(self):
        repo_name = "/user/name"
        response = self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}"}).json()
        self.assertEquals(response.get('name'), repo_name.lstrip('/'))

    def test_check_name_addition_lstrip_multiple(self):
        repo_name = "/////user/name"
        response = self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}"}).json()
        self.assertEquals(response.get('name'), repo_name.lstrip('/'))

    def test_check_name_addition_github_https_replace(self):
        repo_name = "https://github.com/user/name"
        response = self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}"}).json()
        self.assertEquals(response.get('name'), repo_name.replace('https://github.com/', ''))

    def test_check_name_addition_github_http_replace(self):
        repo_name = "http://github.com/user/name"
        response = self.client.post(f'{self.repo_list_url}', data={"name": f"{repo_name}"}).json()
        self.assertEquals(response.get('name'), repo_name.replace('http://github.com/', ''))


class AuthorizationSmokeTest(TestCase):
    """Smoke test if only auth users could use repos urls"""

    def setUp(self):
        self.test_id = 3
        not_existing_repo_name = 'repo_user/repo_name'
        self.repo3 = Repo.objects.create(name=not_existing_repo_name, id=self.test_id)
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_repos_available_for_authenticated(self):
        response = self.client.get(reverse('repo-list'), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_repo_available_for_authenticated(self):
        response = self.client.get(reverse('repo-detail', kwargs={'pk': self.test_id}), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("os.environ.get", return_value="proper_and_working_personal_access_token_value")
    @patch("requests.get", return_value=MockRequestsToGithubNotExistingRepo())
    def test_single_repo_nonexisting_in_github(self, mocked, mocked_requests):
        response = self.client.get(f'/api/v1/repos/{self.test_id}/popular/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("os.environ.get", return_value="proper_and_working_personal_access_token_value")
    @patch("requests.get", return_value=MockRequestsToGithubNotExistingRepo())
    def test_single_repo_popular_nonexisting_in_github(self, mocked, mocked_requests):
        response = self.client.get(f'/api/v1/repos/{self.test_id}/popular/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("os.environ.get", return_value="proper_and_working_personal_access_token_value")
    @patch("requests.get", return_value=MockRequestsToGithubPopularRepo())
    def test_single_repo_popular_existing_in_github(self, mocked, mocked_requests):
        response = self.client.get(f'/api/v1/repos/{self.test_id}/popular/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentationTest(TestCase):
    """Check availability of Doc pages """

    def test_schema_json_available(self):
        response = self.client.get(reverse('schema-json', kwargs={'format': '.json'}), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_yaml_available(self):
        response = self.client.get(reverse('schema-json', kwargs={'format': '.yaml'}), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_swagger_ui_available(self):
        response = self.client.get(reverse('schema-swagger-ui'), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_redoc_available(self):
        response = self.client.get(reverse('schema-redoc'), follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PopularityCheckerTest(TestCase):
    """Check if calculate popularity function returns proper results for different amount of stars, forks"""

    def test_check_score_positive_cases(self):
        self.assertEquals(calculate_popularity(num_stars=500, num_forks=0), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=0, num_forks=250), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=498, num_forks=1), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=100, num_forks=200), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=400, num_forks=50), POPULAR_REPO_RESULT)

    def test_check_score_negative_cases(self):
        self.assertEquals(calculate_popularity(num_stars=499, num_forks=0), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=0, num_forks=249), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=497, num_forks=1), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=99, num_forks=200), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(num_stars=0, num_forks=0), NOT_POPULAR_REPO_RESULT)


class HealthCheckTest(TestCase):
    """Check if health-check pages are present and properly serviced"""

    def test_health_check_url(self):
        found = resolve('/health_check/')
        self.assertEquals(found.func.view_class, views.HealthCheckView)

    @patch("os.environ.get", return_value=None)
    def test_health_check_without_token(self, mocked):
        response = self.client.get('/health_check/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("os.environ.get", return_value="proper_and_working_personal_access_token_value")
    @patch("requests.get", return_value=MockRequestsToGithubPopularRepo())
    def test_health_check_connection_to_github_ok_token_ok(self, mocked_env, mocked_requests):
        response = self.client.get('/health_check/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("os.environ.get", return_value="wrong_format_value")
    def test_health_check_connection_to_github_ok_token_format_wrong(self, mocked_env):
        response = self.client.get('/health_check/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("os.environ.get", return_value=WRONG_TOKEN_VALUE_GOOD_FORMAT)
    def test_health_check_connection_to_github_token_value_wrong(self, mocked_env):
        response = self.client.get('/health_check/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
