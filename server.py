from flask import Flask, request, redirect, render_template
import sqlalchemy
import os
from model import *
from dotenv import load_dotenv

app = Flask(__name__)


@app.route("/")
def homepage():
    """view homepage"""

    return render_template("home.html")
