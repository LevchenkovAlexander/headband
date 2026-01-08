from tortoise.models import Model
from tortoise import fields

class Master(Model):
    id = fields.IntField(pk=True)
    