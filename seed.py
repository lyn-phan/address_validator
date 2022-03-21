import backend_server
import crud
import os
from model import *

os.system('dropdb addresses')
os.system('createdb addresses')

connect_to_db(backend_server.app)
db.create_all()


def get_addresses(db):
    return db.session.execute("""
    SELECT address_line_one, city, state, zipcode, latitude, longitude FROM addresses""").fetchall()


def seed_database(db):
    address1 = Address(address_line_one='415 Mission Street',
                       city="San Francisco", state="CA", zip_code="94105", longitude="-122.39695", latitude="37.789895")

    db.session.add(address1)
    db.session.commit()

    return address1


seed_database(db)
