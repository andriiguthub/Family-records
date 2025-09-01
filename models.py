from app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    lastname = db.Column(db.String)
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String)
    death_date = db.Column(db.Date)
    death_place = db.Column(db.String)
    sex = db.Column(db.String)

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, nullable=False)
    father_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    mother_id = db.Column(db.Integer, db.ForeignKey('person.id'))

class Spouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    spouse_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    marriage_date = db.Column(db.Date)
    divorce_date = db.Column(db.Date)
