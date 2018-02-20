from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from datetime import datetime


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_developer = models.BooleanField(default=False)

class Game(models.Model):
    name = models.CharField(max_length = 100, unique=True)
    developer = models.ForeignKey(User, on_delete=models.CASCADE,
            related_name='games')
    url = models.URLField()
    price = models.DecimalField(max_digits=5, decimal_places=2)


# key to owner, key to game, json for saves
class GameOwnerships(models.Model):
    gameOwner = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    data = models.CharField(max_length = 500, null=True)
    high_score = models.DecimalField(max_digits=5, decimal_places=0, null=True)

class Purchase(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    time = models.DateTimeField()
