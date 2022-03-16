from flask import Flask, request, redirect, render_template, flash
import sqlalchemy
import os
from model import *
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = os.getenv("app.secret_key")
# app.jinja_env.undefined = StrictUndefined

load_dotenv()
API_KEY = os.getenv("API_KEY")


@app.route("/")
def homepage():
    """view homepage"""

    return render_template("homepage.html")


@app.route("/", methods=['POST'])
def geocode():
    """takes user input, makes a request to mapbox API and it returns long/lat coordinates"""

    add = request.form.get("address-line")
    address_line = add.replace(" ", "%20")  # replace spaces with "%20"
    city = request.form.get("city-name")
    city_name = city.replace(" ", "%20")  # replace spaces with "%20"
    state_name = request.form.get("state-name")
    zipcode = request.form.get("zip-code")

    full_encoded_address = "".join(
        address_line + "%20" + city_name + "%20" + state_name + "%20" + zipcode)

    mapbox_token = API_KEY
    query = full_encoded_address
    payload = {"query": full_encoded_address, "mapbox_token": mapbox_token}

    if payload:
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={mapbox_token}"

        req = requests.get(url, params=payload)
        res = req.json()
        results = str(res["features"][0]["center"])
        return render_template("geocode.html", results=results)
    else:
        flash("Sorry, there were no results found. Redirecting back home")
        return redirect('/')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")
