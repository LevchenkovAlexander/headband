from tortoise.models import models
from tortoise import fields
from tortoise.contrib.pyndantic import pyndantic
from datetime import datetime

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.charField(max_length=50, unique=True)
    

    class Meta:
        table = "users"

    def __str__(self):
        return self.username

    def __int__(self):
        return self.id

    