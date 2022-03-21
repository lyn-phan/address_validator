
from flask import Flask, request, redirect, render_template, flash
from flask_caching import Cache
import sqlalchemy
import os
from model import db, Address, connect_to_db
from dotenv import load_dotenv
import requests
import crud
from urllib.parse import quote

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


@app.route("/")
def homepage():
    """view homepage"""
    return render_template("homepage.html")


def check_db():
    """grabs user input and checks database for records"""
    address_line = request.form.get("address-line")
    city = request.form.get("city-name")
    state = request.form.get("state-name")
    zipcode = request.form.get("zipcode")

    check_db_for_address = crud.find_address(address_line=address_line,
                                             city=city, state=state, zipcode=zipcode)

    data = {"address_line": check_db_for_address[0],
            "city": check_db_for_address[1],
            "state": check_db_for_address[2],
            "zip_code": check_db_for_address[3],
            "latitude": check_db_for_address[4],
            "longitude": check_db_for_address[5]}

    return data


def parse_addresses():
    """grabs user input from form and returns it as a list"""

    address_line = request.form.get("address-line")
    city = request.form.get("city-name")
    state = request.form.get("state-name")
    zipcode = request.form.get("zipcode")

    return [address_line, city, state, zipcode]


@app.route("/", methods=['POST'])
# @cache.cached(timeout=10)
def geocode():
    """takes user input, makes a request to mapbox API and it returns long/lat coordinates"""

    parsed_address = parse_addresses()
    join_add = " ".join(parsed_address)
    encoded_address = quote(join_add)

    # check the db with the user input
    try:
        # check cache, if not in cache, run API
        data = cache.get(encoded_address)
        if data is not None:
            print("this is the cache result")
            return data

        data = check_db()
        if data is not None:
            print("this is a db hit!")
            return data

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
            added_address = crud.add_address(
                address_line=parsed_address[0], city=parsed_address[1], state=parsed_address[2], zipcode=parsed_address[3], longitude=results[0], latitude=results[1])

            data = {"address_line": parsed_address[0],
                    "city": parsed_address[1],
                    "state": parsed_address[2],
                    "zip_code": parsed_address[3],
                    "longitude": results[0],
                    "latitude": results[1]}
            cache.set(encoded_address, data)

            return data
        else:
            return "We couldn't find an address. Please try again."

    except:
        flash("Sorry, your address isn't valid. Redirecting back home")

        return redirect('/')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")
