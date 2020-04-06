from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        unique_together = (('username', 'email'),)
