
from base64 import encode
from flask import Flask
from flask_caching import Cache
import os
from model import db, Address, connect_to_db
from dotenv import load_dotenv
import requests
import crud
from urllib.parse import quote, unquote

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


def check_db(query_address):
    """grabs user input and checks database for records"""

    address_line_one = str(query_address["address_line_one"])
    city = str(query_address["city"])
    state = str(query_address["state"])
    zip_code = str(query_address["zip_code"])

    check_db_for_address = crud.find_address(
        address_line_one=address_line_one, city=city, state=state, zip_code=zip_code)
    print(check_db_for_address)

    if check_db_for_address:
        data = {"address_line_one": check_db_for_address[0],
                "city": check_db_for_address[1],
                "state": check_db_for_address[2],
                "zip_code": check_db_for_address[3],
                "latitude": check_db_for_address[4],
                "longitude": check_db_for_address[5]}
        print(data)
        return data
    else:
        return None


# query_address = {"address_line_one": "600 Montgomery Street",
#                  "city": "San Francisco", "state": "CA", "zip_code": "94111"}
# print(check_db(query_address))

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
        return data
    else:
        call_API_to_get_lat_long(encoded_address, query_address)


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
        address_line_one = str(query_address["address_line_one"])
        city = str(query_address["city"])
        state = str(query_address["state"])
        zip_code = str(query_address["zip_code"])

        added_address = crud.add_address(
            address_line_one=address_line_one, city=city, state=state, zip_code=zip_code, longitude=results[0], latitude=results[1])

        data = {"address_line_one": address_line_one,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "longitude": results[0],
                "latitude": results[1]}
        cache.set(encoded_address, data)

        return data
    else:
        return "We couldn't find an address. Please try again."


def verify_and_return_address_array(query_address):
    address_arr = []

    if query_address == []:
        return None

    for item in range(len(query_address)):
        if query_address_data(query_address[item]):
            address_arr.append(query_address[item])
        print(address_arr)

    return address_arr


if __name__ == "__main__":
    connect_to_db(app)
    query_address = [{"address_line_one": "600 Montgomery Street",
                      "city": "San Francisco", "state": "CA", "zip_code": "94111"}, {"address_line_one": "1 La Avanzada Street",
                                                                                     "city": "San Francisco", "state": "CA", "zip_code": "94131"}
                     ]
    verify_and_return_address_array(query_address)

# app.run(debug=True, host="0.0.0.0")
