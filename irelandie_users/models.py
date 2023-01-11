# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    password_reset = models.DateTimeField(null=True)
    reset_lock = models.BooleanField(default=False)
