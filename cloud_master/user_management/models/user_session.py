from mongoengine import Document, ObjectIdField, StringField


class UserSession(Document):
    user_id = ObjectIdField()
    session_key = StringField()
