from django.test import TestCase
# Create your tests here.
from django.urls import resolve, reverse
from djoser.urls.base import User
from rest_framework import status

from popularity import views
from popularity.models import Repo
from popularity.utils import calculate_popularity, POPULAR_REPO_RESULT, NOT_POPULAR_REPO_RESULT


class SmokeTests(TestCase):
    """Test Repo models , urls smoke test"""

    def setUp(self):
        self.repo1 = Repo.objects.create(name='repo1_name')
        self.repo2 = Repo.objects.create(name='repo2_name')

    def test_check_if_view_repos_have_good_class(self):
        found = resolve('/api/v1/repos/')
        self.assertEquals(found.func.cls, views.RepoViewSet)

    def test_check_if_view_single_repo_has_good_class(self):
        found = resolve('/api/v1/repos/1/')
        self.assertEquals(found.func.cls, views.RepoViewSet)
        found = resolve('/api/v1/repos/2/')
        self.assertEquals(found.func.cls, views.RepoViewSet)

    def test_repos_not_available_for_anonymous(self):
        response = self.client.get('/api/v1/repos/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_single_repo_not_available_for_anonymous(self):
        response = self.client.get('/api/v1/repos/1/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_single_repo_popular_status_for_non_authenticated(self):
        response = self.client.get(f'/api/v1/repos/1/popular/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SingleRepoTest(TestCase):
    """Test Addition of new repos , details about single repo"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_check_addition_of_new_repo(self):
        initial_count = Repo.objects.count()
        repo_name = "facebook/react"
        self.assertFalse(Repo.objects.filter(name=repo_name))
        response = self.client.post('/api/v1/repos/', data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Repo.objects.count(), initial_count + 1)
        self.assertTrue(Repo.objects.get(name=repo_name))

    def test_check_uniqueness_of_repo_name(self):
        repo_name = "test_user/test_name"
        response = self.client.post('/api/v1/repos/', data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/api/v1/repos/', data={"name": repo_name})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_single_repo_fields(self):
        repo_name = "test_user/test_name"
        response = self.client.post('/api/v1/repos/', data={"name": repo_name})
        test_id = response.json()['id']
        response = self.client.get(f'/api/v1/repos/{test_id}/')
        response_json = response.json()
        test_id = response_json.get('id')
        self.assertEquals(response_json.get('name'), repo_name)
        self.assertEquals(response_json.get('github_url'), f'https://github.com/{repo_name}/')
        self.assertEquals(response_json.get('url'), f'http://testserver/api/v1/repos/{test_id}/')
        self.assertIn('created', response_json)

    def test_single_repo_popularity(self):
        """Test popularity when token not granted on server"""
        repo_name = "test_user/test_name"
        response = self.client.post('/api/v1/repos/', data={"name": repo_name})
        test_id = response.json()['id']
        response = self.client.get(f'/api/v1/repos/{test_id}/popular/')
        self.assertEquals(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class RepoListTest(TestCase):
    """Test Addition of new repos , details about single repo"""

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_check_pagination(self):
        repo_name = "test_user/test_name"
        initial_count = Repo.objects.count()
        amount_of_new_repo = 100
        repo_list_url = '/api/v1/repos/'
        for i in range(amount_of_new_repo):
            self.client.post(f'{repo_list_url}', data={"name": f"{repo_name}{i}"})
        actual_count = initial_count + amount_of_new_repo
        self.assertEquals(actual_count, initial_count + amount_of_new_repo)
        response_json = self.client.get(repo_list_url).json()
        self.assertEquals(response_json.get('count'), actual_count)
        self.assertEquals(response_json.get('next'), f'http://testserver{repo_list_url}?page=2')
        self.assertEquals(response_json.get('previous'), None)
        response_next_page_json = self.client.get(f'http://testserver{repo_list_url}?page=2').json()
        self.assertEquals(response_next_page_json.get('count'), actual_count)
        self.assertEquals(response_next_page_json.get('previous'), f'http://testserver{repo_list_url}')
        self.assertEquals(response_next_page_json.get('next'), f'http://testserver{repo_list_url}?page=3')


class AuthorizationSmokeTest(TestCase):
    """Smoke test if only auth users could use repos urls"""

    def setUp(self):
        self.test_id = 3
        self.repo3 = Repo.objects.create(name='repo3_name', id=self.test_id)
        self.user = User.objects.create_user('test', 'test@email.com', 'testtest')
        self.client.force_login(self.user)

    def test_repos_available_for_authenticated(self):
        response = self.client.get('/api/v1/repos/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_repo_available_for_authenticated(self):
        response = self.client.get(f'/api/v1/repos/{self.test_id}/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_repo_popular_status_available_for_authenticated(self):
        response = self.client.get(f'/api/v1/repos/{self.test_id}/popular/', follow=True)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_health_check_without_token(self):
        response = self.client.get('/health_check/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
