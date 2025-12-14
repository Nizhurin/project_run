from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    RUN_STATUS_CHOICES = [
        ("init", "init"),
        ("in_progress", "in_progress"),
        ("finished", "finished"),
    ]
    status = models.CharField(
        max_length=20,
        choices=RUN_STATUS_CHOICES,
        default="init",
    )
