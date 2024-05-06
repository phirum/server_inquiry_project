from pymongo import MongoClient
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient(current_app.config['MONGO_URI'])
db = client.get_default_database()

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def save(self):
        db.users.insert_one(self.to_dict())

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role
        }

    @staticmethod
    def find_by_username(username):
        return db.users.find_one({'username': username})

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Additional models for Course, Enroll, and Quiz can be created similarly.
