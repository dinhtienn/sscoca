from mongoengine import *

class Feedback(Document):
    time = DateTimeField()
    content = StringField()