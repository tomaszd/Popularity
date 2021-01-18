from django.db import models

from popularity.utils import get_github_api_response


class Repo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    # Name of github repo should be in github format to identify  github_user/repo_name e.g. facebook/react
    name = models.CharField(max_length=200, blank=True, default='', unique=True)

    class Meta:
        ordering = ['created']

    @property
    def popular_status(self):
        return get_github_api_response(repo_name=self.name)

    @property
    def github_url(self):
        return f"https://github.com/{self.name}/"

    def save(self, *args, **kwargs):
        self.name = self.name.replace("https://github.com", ''). \
            replace("http://github.com", ''). \
            rstrip("/").lstrip("/")
        super(Repo, self).save(*args, **kwargs)
