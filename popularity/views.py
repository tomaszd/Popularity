# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from popularity.models import Repo
from popularity.serializers import RepoSerializer, RepoSerializerDetail


class RepoViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    list:
    Post a github repo url as name to save repo.
    name could be sth like  https://github.com/facebook/create-react-app or   facebook/create-react-app
    """
    queryset = Repo.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=True)
    def popular(self, request, *args, **kwargs):
        """
        Api to score popularity of saved github repo.
        Repo is popular if #stars + 2 * #forks >= 500
        Returns:  "popular" or "not popular"
        Throws 503 Error if PERSONAL_ACCESS_TOKEN is not granted on server"""
        repo = self.get_object()
        status, info = repo.popular_status
        return Response(info, status)

    def get_serializer_class(self):
        if self.action == 'list':
            return RepoSerializer
        else:
            return RepoSerializerDetail
