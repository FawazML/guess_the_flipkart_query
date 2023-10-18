from dc import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):

    _id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(200))
    created_by = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_by = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"'User('{self.name}', '{self.email}')'"

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)



class FlipkartQuery(db.Model):

    _id = db.Column('id', db.Integer, primary_key=True)
    features = db.Column(db.String(200))
    labels = db.Column(db.String(200))

    def __init__(self, feature, label):
        self.features = feature
        self.labels = label

    def __repr__(self):
        return f"'FlipkartQuery('{self.features}', '{self.labels}')'"