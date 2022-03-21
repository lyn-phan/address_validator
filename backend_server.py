from flask import Flask
from flask_caching import Cache
import os
from model import db, Address, connect_to_db
from dotenv import load_dotenv
import requests
import crud
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv("app.secret_key")
cache = Cache()
config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
}
app.config.from_mapping(config)
cache.init_app(app)


# load the API key
load_dotenv()
API_KEY = os.getenv("API_KEY")


def format_user_input(query_address):
    """helper function to take query address and add to a list for access"""
    address_arr = []

    address_line_one = str(query_address["address_line_one"])
    city = str(query_address["city"])
    state = str(query_address["state"])
    zip_code = str(query_address["zip_code"])

    address_arr.append(address_line_one)
    address_arr.append(city)
    address_arr.append(state)
    address_arr.append(zip_code)

    return address_arr


def check_db(query_address):
    """grabs user input and checks database for records"""

    address_arr = format_user_input(query_address)
    check_db_for_address = crud.find_address(
        address_line_one=address_arr[0], city=address_arr[1], state=address_arr[2], zip_code=address_arr[3])

    if check_db_for_address:
        data = {"address_line_one": check_db_for_address[0],
                "city": check_db_for_address[1],
                "state": check_db_for_address[2],
                "zip_code": check_db_for_address[3],
                "latitude": check_db_for_address[4],
                "longitude": check_db_for_address[5]}

        return data
    else:
        return None


def query_address_data(query_address):
    """encode the queried address, then checks cache or db to see if address exists. If it does, we return it"""
    # encodes the address by adding a '%20' where there is a space

    target_address = []
    for k, v in query_address.items():
        target_address.append(v)

    join_add = " ".join(target_address)
    encoded_address = quote(join_add)

    # check cache, if it is cached, we return the results
    data = cache.get(encoded_address)
    if data is not None:
        return data

    # if not cached, we then check the database. If it is in db, we return it
    data = check_db(query_address)
    if data is not None:
        print(data)
        return data
    else:
        return call_API_to_get_lat_long(encoded_address, query_address)


def add_data_to_db(query_address, results):
    """helper function to add data to db"""

    address_arr = format_user_input(query_address)

    added_address = crud.add_address(
        address_line_one=address_arr[0], city=address_arr[1], state=address_arr[2], zip_code=address_arr[3], longitude=results[0], latitude=results[1])

    return added_address


def cache_data(encoded_address, data):
    """helper function to cache data"""

    cache.set(encoded_address, data)


def call_API_to_get_lat_long(encoded_address, query_address):
    """makes an API call if address isn't cached or in db"""

    mapbox_token = API_KEY
    query = encoded_address
    payload = {"query": encoded_address,
               "mapbox_token": mapbox_token}

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={mapbox_token}"
    req = requests.get(url, params=payload)
    res = req.json()

    # lat & long returned from API
    results = list(res["features"][0]["center"])

    if results:
        # we add results from API to db
        current_address = format_user_input(query_address)

        data = {"address_line_one": current_address[0],
                "city": current_address[1],
                "state": current_address[2],
                "zip_code": current_address[3],
                "longitude": results[0]}

        add_results_to_db = add_data_to_db(query_address, results)
        add_data_to_cache = cache_data(encoded_address, data)

        return data
    else:
        return "We couldn't find an address. Please try again."


def validate_user_input(item):
    # check if user input is a string and it's valid

    for v in item.values():
        if isinstance(v, str) is True:
            return True
        elif isinstance(v, int) is True:
            raise TypeError(
                "Sorry, you entered an invalid type. Please be sure it is a string.")
        else:
            return False


def verify_and_return_address_array(query_address):

    address_arr = []

    if query_address == []:
        raise ValueError("Your parameters are empty.")

    for item in query_address:
        # try:
        if validate_user_input(item) is True:
            queried_address = query_address_data(item)
            if queried_address is not None:
                address_arr.append(queried_address)
            else:
                return "Your address is invalid. Let's check your input"
    # if user_input is not a string, we append None
        # elif validate_user_input(item) is False:
        #     address_arr.append(None)
        #     continue
        else:
            raise TypeError(
                "Sorry, you entered an invalid type. Please be sure it is a string.")

    return address_arr


if __name__ == "__main__":
    connect_to_db(app)

    # query_address = [{"address_line_one": "900 Lombard Street",
#                   "city": "San Francisco", "state": "CA", "zip_code": "94133"},
#                  {"address_line_one": "1 La Avanzada Street",
#                  "city": "San Francisco", "state": "CA", "zip_code": "94131"},
#                  {"address_line_one": "20 W 34th Street",
#                  "city": "New York", "state": "NY", "zip_code": "10001"}]
# query_address = []  # returns false --> Value Error
# query_address = [{}]  # returns an empty list
# query_address = ""  # returns an empty list
# query_address = [1234]
    query_address = [{"address_line_one": "900 E 11th Street",
                      "city": "Austin", "state": "TX", "zip_code": "78702"},
                     {"address_line_one": "1375 E Buena Vista Drive",
                     "city": "Orlando", "state": "FL", "zip_code": "32836"}]

    print("\n")
    print("\n")
    print(verify_and_return_address_array(query_address))
    print("\n")


# app.run(debug=True, host="0.0.0.0")
