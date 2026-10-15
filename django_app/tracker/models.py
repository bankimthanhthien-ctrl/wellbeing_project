from django.db import models
from django.contrib.auth.models import User


class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    mood = models.CharField(max_length=50)
    sleep_hours = models.FloatField()
    journal = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'date')


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)


class HabitRecord(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)


class AIWeeklyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()
    summary = models.TextField()
    negative_patterns = models.JSONField(default=list)
    small_goals = models.JSONField(default=list)
    safe_actions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)