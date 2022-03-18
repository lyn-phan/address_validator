from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


class Address(db.Model):
    """an address"""

    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    address_line = db.Column(db.String(45), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.String(40))
    longitude = db.Column(db.String(40))

    def __repr__(self):
        return f'<Address address_id={self.address_id} has been added.>'


def connect_to_db(app, db_uri='postgresql:///addresses', echo=True):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = echo
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)

    print('Connected to the database!')


if __name__ == '__main__':
    """If the model is run or imported..."""
    from server import app
    connect_to_db(app)

    db.create_all()
