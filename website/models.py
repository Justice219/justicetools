from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    title = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    notes = db.relationship('Note')

class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    title = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    clicks = db.Column(db.Integer)
    original_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))