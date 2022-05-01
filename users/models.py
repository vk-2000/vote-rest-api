from django.db import models

# Create your models here.
from django.contrib.auth.models import User, UserManager


class CustomUser(User):

    age = models.IntegerField(blank=False)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()
