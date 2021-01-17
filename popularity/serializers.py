from rest_framework import serializers

from popularity.models import Repo


class RepoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repo
        fields = ['id', 'name', 'url']


class RepoSerializerDetail(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repo
        fields = ['id', 'created', 'name', 'github_url', 'url']
