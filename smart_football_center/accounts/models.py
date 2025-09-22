from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('player', 'Player'),
        ('parent', 'Parent'),
        ('child', 'Child'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
