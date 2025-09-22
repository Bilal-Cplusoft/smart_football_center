from django.db import models
from smart_football_center.accounts.models import User


class FieldReservation(models.Model):
    field_name = models.CharField(max_length=100)
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.field_name} reserved by {self.reserved_by} from {self.start_time}"
