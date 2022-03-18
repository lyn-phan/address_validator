"""CRUD Operation"""

from flask import Flask
from model import db, Address, connect_to_db


def add_address(address_line, city, state, zipcode, latitude, longitude):
    """ if search is successful, the entry is added to the database """

    log_address = Address(address_line=address_line, city=city, state=state,
                          zip_code=zipcode, latitude=latitude, longitude=longitude)

    db.session.add(log_address)
    db.session.commit()

    return log_address


def find_address(address_line, city, state, zipcode):
    """check address of user input. If address is already in database, return address + Lat/Long,
    and don't add duplicate in database."""

    valid_address = Address.query.filter_by(address_line=address_line, city=city, state=state,
                                            zip_code=zipcode).first()
    target_address = valid_address.address_line, valid_address.city, valid_address.state, valid_address.zip_code, valid_address.latitude, valid_address.longitude

    return target_address


# delete and address ?


if __name__ == '__main__':
    from server import app
    connect_to_db(app)
