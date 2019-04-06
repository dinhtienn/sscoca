from mongoengine import *

class Count(Document):
    time = DateTimeField()
    amount = IntField()
