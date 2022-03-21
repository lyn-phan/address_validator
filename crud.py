"""CRUD Operation"""

from flask import Flask
from model import db, Address, connect_to_db


def add_address(address_line_one, city, state, zip_code, latitude, longitude):
    """ if search is successful, the entry is added to the database """

    log_address = Address(address_line_one=address_line_one, city=city, state=state,
                          zip_code=zip_code, latitude=latitude, longitude=longitude)

    db.session.add(log_address)
    db.session.commit()

    return log_address


def find_address(address_line_one, city, state, zip_code):
    """check address of user input. If address is already in database, return address + Lat/Long,
    and don't add duplicate in database."""

    try:
        valid_address = Address.query.filter_by(address_line_one=address_line_one, city=city, state=state,
                                                zip_code=zip_code).first()
        if valid_address is not None:
            target_address = valid_address.address_line_one, valid_address.city, valid_address.state, valid_address.zip_code, valid_address.latitude, valid_address.longitude
            return target_address

        else:
            return None
    except:
        return None


if __name__ == '__main__':
    from backend_server import app
    connect_to_db(app)
