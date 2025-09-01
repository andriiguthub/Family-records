from flask_sqlalchemy import SQLAlchemy, Model

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(120), nullable=False)

class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    lastname = db.Column(db.String)
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String)
    death_date = db.Column(db.Date)
    death_place = db.Column(db.String)
    sex = db.Column(db.String)

class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    father_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    mother_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)

class Spouse(db.Model):
    __tablename__ = 'spouse'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    spouse_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    marriage_date = db.Column(db.Date)
    divorce_date = db.Column(db.Date)
