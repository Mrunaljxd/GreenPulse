from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()


class User(UserMixin, db.Model):
__tablename__ = 'user'
id = db.Column(db.Integer, primary_key=True)
username = db.Column(db.String(80), unique=True, nullable=False)
email = db.Column(db.String(120), unique=True, nullable=False)
password_hash = db.Column(db.String(200), nullable=False)
points = db.Column(db.Integer, default=0)
is_admin = db.Column(db.Boolean, default=False)
created_at = db.Column(db.DateTime, default=datetime.utcnow)
plants = db.relationship('UserPlant', backref='owner', lazy=True)


class Plant(db.Model):
__tablename__ = 'plant'
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(120), nullable=False)
scientific = db.Column(db.String(200))
description = db.Column(db.Text)
difficulty = db.Column(db.String(50))
base_points = db.Column(db.Integer, default=10)
userplants = db.relationship('UserPlant', backref='plant', lazy=True)


class UserPlant(db.Model):
__tablename__ = 'user_plant'
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
planted_at = db.Column(db.DateTime, default=datetime.utcnow)
photos = db.relationship('Upload', backref='userplant', lazy=True)


class Upload(db.Model):
__tablename__ = 'upload'
id = db.Column(db.Integer, primary_key=True)
userplant_id = db.Column(db.Integer, db.ForeignKey('user_plant.id'), nullable=False)
filename = db.Column(db.String(300), nullable=False)
task = db.Column(db.String(80)) # 'planting', 'watering', 'manure', etc.
points_awarded = db.Column(db.Integer, default=0)
verified = db.Column(db.Boolean, default=False)
uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)