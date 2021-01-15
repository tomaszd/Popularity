from rest_framework import serializers

from popularity.models import Repo


class RepoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repo
        fields = ['created', 'name', 'github_url', 'url']


class RepoSerializerDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repo
        fields = ['created', 'name', 'github_url', 'url']
