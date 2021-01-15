import time

from django.db import models


class Repo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, blank=True, default='', unique=True)

    class Meta:
        ordering = ['created']

    @property
    def popular_status(self):
        return f"Here would be info about repo popularity  {self.get_github_api_response()}"

    @property
    def github_url(self):
        return f"https://github.com/{self.name}/"

    def get_github_api_response(self):
        # @Todo add proper obtaining of repo popularity. use Github Rest api
        # This would be a time consuming function
        time.sleep(1)
        return "todo Popular/ not popular"

    def save(self, *args, **kwargs):
        self.name = self.name.lstrip("https://github.com").lstrip("http://github.com").rstrip("/")
        super(Repo, self).save(*args, **kwargs)
