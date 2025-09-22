from django.db import models
from smart_football_center.accounts.models import User
from smart_football_center.teams.models import Team


class TrainingSession(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateTimeField()
    focus_area = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.team.name} training on {self.date}"


class Attendance(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.username} - {self.session.date}"
