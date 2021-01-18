# Create your views here.
from django.http import HttpResponse
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from popularity.models import Repo
from popularity.serializers import RepoSerializer, RepoSerializerDetail
from popularity.utils import get_github_api_response


class RepoViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    list:
    Post a github repo url as name to save repo.
    name could be sth like  https://github.com/facebook/create-react-app or facebook/create-react-app
    """
    queryset = Repo.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=True)
    def popular(self, request, *args, **kwargs):
        """
        GET endpoint for Api to score popularity of saved github repo.
        Repo is popular if 1 * num_stars + 2 * num_forks >= 500.  Returns:  "popular" or "not popular"
        """
        repo = self.get_object()
        _status, info = repo.popular_status
        return Response(info, _status)

    def get_serializer_class(self):
        if self.action == 'list':
            return RepoSerializer
        else:
            return RepoSerializerDetail


class HealthCheckView(View):
    """
    Checks to see if the service is healthy. Check if communication with Api Github Api is working.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        """
        Create a request to Github Rest Api to check if it is working.
        Assumption test_repo = "facebook/react" is available on Github.
        """
        test_repo = "facebook/react"
        _status, _ = get_github_api_response(test_repo)
        if _status == status.HTTP_200_OK:
            return HttpResponse("ok")
        return HttpResponse("Not ok", status=_status)
