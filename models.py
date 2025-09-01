from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model  

udb = SQLAlchemy()

class User(udb.Model):
    __tablename__ = 'users'
    id = udb.Column(udb.Integer, primary_key=True)
    username = udb.Column(udb.String(80), unique=True, nullable=False)
    hash = udb.Column(udb.String(120), nullable=False)

class Person(udb.Model):
    __tablename__ = 'person'
    id = udb.Column(udb.Integer, primary_key=True)
    name = udb.Column(udb.String)
    lastname = udb.Column(udb.String)
    birth_date = udb.Column(udb.Date)
    birth_place = udb.Column(udb.String)
    death_date = udb.Column(udb.Date)
    death_place = udb.Column(udb.String)
    sex = udb.Column(udb.String)

class Parent(udb.Model):
    __tablename__ = 'parent'
    id = udb.Column(udb.Integer, primary_key=True)
    person_id = udb.Column(udb.Integer, udb.ForeignKey('person.id'), nullable=False)
    father_id = udb.Column(udb.Integer, udb.ForeignKey('person.id'), nullable=True)
    mother_id = udb.Column(udb.Integer, udb.ForeignKey('person.id'), nullable=True)

class Spouse(udb.Model):
    __tablename__ = 'spouse'
    id = udb.Column(udb.Integer, primary_key=True)
    person_id = udb.Column(udb.Integer, udb.ForeignKey('person.id'), nullable=False)
    spouse_id = udb.Column(udb.Integer, udb.ForeignKey('person.id'), nullable=False)
    marriage_date = udb.Column(udb.Date)
    divorce_date = udb.Column(udb.Date)
