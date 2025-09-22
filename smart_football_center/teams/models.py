from django.db import models
from smart_football_center.accounts.models import User


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="coached_teams")
    players = models.ManyToManyField(User, related_name="teams", blank=True)

    def __str__(self):
        return self.name
