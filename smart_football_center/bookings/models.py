from django.db import models
from smart_football_center.accounts.models import User


class Session(models.Model):
    SESSION_TYPES = (
        ('group', 'Group Session'),
        ('1on1', '1-on-1 Session'),
        ('event', 'Event'),
        ('recovery', 'Recovery Session'),
    )
    name = models.CharField(max_length=100)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField()
    spots_left = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.date})"


class Booking(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="confirmed")

    def __str__(self):
        return f"{self.player} booked {self.session}"


class Bundle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    sessions_included = models.PositiveIntegerField()
    sessions_used = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()

    def credits_left(self):
        return self.sessions_included - self.sessions_used


class Membership(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    plan_name = models.CharField(max_length=100)
    renewal_date = models.DateField()
    freeze_count = models.PositiveIntegerField(default=0)


class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    percentage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.percentage}%)"
