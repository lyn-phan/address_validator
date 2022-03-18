from flask import Flask, request, redirect, render_template, flash
import sqlalchemy
import os
from model import db, Address, connect_to_db
from dotenv import load_dotenv
import requests
import crud
import jsonify

app = Flask(__name__)
app.secret_key = os.getenv("app.secret_key")
# app.jinja_env.undefined = StrictUndefined

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
    print("This is before the data")

    results = {"address_line": check_db_for_address[0],
               "city": check_db_for_address[1],
               "state": check_db_for_address[2],
               "zip_code": check_db_for_address[3],
               "latitude": check_db_for_address[4],
               "longitude": check_db_for_address[5]}
    print("This is after the data")

    return render_template("geocode.html", results=results)


@app.route("/", methods=['POST'])
def geocode():
    """takes user input, makes a request to mapbox API and it returns long/lat coordinates"""

    address_line = request.form.get("address-line")
    add = address_line.replace(" ", "%20")  # replace spaces with "%20"
    city = request.form.get("city-name")
    city_name = city.replace(" ", "%20")  # replace spaces with "%20"
    state = request.form.get("state-name")
    zipcode = request.form.get("zipcode")

    # check the db with the user input
    try:
        # run the check_db function
        check_db()
        if

    except:
        # if not found, run a look up in mapbox API. If successful, add address + long / lat in db
        full_encoded_address = "".join(
            add + "%20" + city_name + "%20" + state + "%20" + zipcode)

        mapbox_token = API_KEY
        query = full_encoded_address
        payload = {"query": full_encoded_address, "mapbox_token": mapbox_token}

        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={mapbox_token}"
        req = requests.get(url, params=payload)
        res = req.json()
        # this is the lat long resturned from API
        results = list(res["features"][0]["center"])

        if results:
            # add found address to db
            added_address = crud.add_address(
                address_line=address_line, city=city, state=state, zipcode=zipcode, longitude=results[0], latitude=results[1])

            data = {"address_line": address_line,
                    "city": city,
                    "state": state,
                    "zip_code": zipcode,
                    "longitude": results[0],
                    "latitude": results[1]}

            return render_template("geocode.html", results=data)

        else:
            flash("Sorry, your address isn't valid. Redirecting back home")
            return redirect('/')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")
