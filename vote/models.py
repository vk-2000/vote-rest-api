from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Poll(models.Model):
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="polls")
    name = models.CharField(max_length=100)
    result_public = models.BooleanField(default=True)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.name) + "___" + str(self.id)


class Question(models.Model):
    desc = models.CharField(max_length=200)
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="questions")

    def __str__(self) -> str:
        return str(self.desc) + "  " + str(self.id)


class Choice(models.Model):
    text = models.CharField(max_length=100)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices")

    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.text)


class IpAddress(models.Model):
    ip_address = models.GenericIPAddressField()
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="voted_ip_addresses")
