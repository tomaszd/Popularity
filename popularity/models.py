import time
from django.db import models



class Repo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.TextField()

    @property
    def popular(self):
        return f"Here would be info about repo popularity  {self.get_github_api_response()}"

    def get_github_api_response(self):
        # @Todo add proper obtaining of repo popularity. use Github Rest api
        # This would be a time consuming function
        time.sleep(1)
        return "todo Popular/ not popular"

    class Meta:
        ordering = ['created']
