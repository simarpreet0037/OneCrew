# registration/models.py
from django.db import models

class UserCredentials(models.Model):
    name = models.CharField(max_length=100)
    username = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name