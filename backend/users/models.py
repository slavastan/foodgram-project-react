from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(("email address"), blank=False, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="is_subscribed"
    )

    class Meta:
        unique_together = ["user", "follower"]

    def __str__(self):
        return f"{self.user} -> {self.follower}"
