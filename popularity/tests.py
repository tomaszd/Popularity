from django.test import TestCase
# Create your tests here.
from django.urls import resolve, reverse
from djoser.urls.base import User

from popularity import views
from popularity.models import Repo
from rest_framework import status

from popularity.utils import calculate_popularity, POPULAR_REPO_RESULT, NOT_POPULAR_REPO_RESULT


class SmokeTests(TestCase):
    """Test repo models  """

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


class AuthorizationSmokeTest(TestCase):
    """Smoke test if only auth users could use repos urls """

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
    """Check if calculate popularity fuinction returns proper results for different amount of stars, forks"""

    def test_check_score_positive_cases(self):
        self.assertEquals(calculate_popularity(stars=500, forks=0), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=0, forks=250), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=498, forks=1), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=100, forks=200), POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=400, forks=50), POPULAR_REPO_RESULT)

    def test_check_score_negative_cases(self):
        self.assertEquals(calculate_popularity(stars=499, forks=0), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=0, forks=249), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=497, forks=1), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=99, forks=200), NOT_POPULAR_REPO_RESULT)
        self.assertEquals(calculate_popularity(stars=0, forks=0), NOT_POPULAR_REPO_RESULT)
