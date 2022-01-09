from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField()
    location = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    reputation_score = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}|{self.username}"
