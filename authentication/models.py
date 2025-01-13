from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    CONTRIBUTOR ='CONTRIBUTOR'
    VISITOR = 'VISITOR'

    ROLE_CHOICES = (
        (CONTRIBUTOR, 'Contributor'),
        (VISITOR, 'Visitor'),
        )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='Rôle')
