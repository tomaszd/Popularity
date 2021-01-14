# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from popularity.models import Repo
from popularity.serializers import RepoSerializer


class RepoViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    permission_classes = (IsAuthenticated,)

    #?def perform_create(self, serializer):
    #?    serializer.save(owner=self.request.user)
