from django.db import models
from smart_football_center.teams.models import Team


class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date.date()}"
