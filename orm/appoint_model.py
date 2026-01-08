from tortoise.models import Model
from tortoise import fields

class Appoint(Model):
    id = fields.IntField(pk= True)
    user_id = fields.IntField()
    master_id = fields.IntField()
    date_time = fields.DateTimeField(null=False)