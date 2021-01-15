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
    """
    queryset = Repo.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=True)
    def popular(self, request, *args, **kwargs):
        repo = self.get_object()
        return Response(repo.popular_status)

    def get_serializer_class(self):
        if self.action == 'list':
            return RepoSerializer
        else:
            return RepoSerializerDetail
