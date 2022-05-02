from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Blog(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
