"""Web APPlication creation and web page direction (basically, glues the whole program together)."""


import json
import pickle
import requests

from flask import Flask, render_template, request, redirect, url_for, session

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

import pymysql.cursors  # database

from passlib.hash import sha256_crypt  # password encryption

from try_towear import generate_data, suggest_outfit
from points_to_english import translate_outfit
from clothes_manager import Garment, Wardrobe


APP = Flask(__name__)
Bootstrap(APP)
APP.config["SECRET_KEY"] = "donttellanyonethis"
APP.config["TEMPLATES_AUTO_RELOAD"] = True

DB = pymysql.connect(
    host="oamandawi.mysql.pythonanywhere-services.com",
    user="oamandawi",
    password="FrFZpH^gq5",
    db="oamandawi$towear",
)
CURSOR = DB.cursor()
CURSOR.execute(
    "CREATE TABLE IF NOT EXISTS login_info"
    "(id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,"
    "name VARCHAR(20),password VARCHAR(80),email VARCHAR(50));"
)
DB.commit()
CURSOR.execute(
    "CREATE TABLE IF NOT EXISTS users_closets"
    "(id INT(11) NOT NULL PRIMARY KEY,"
    "closet VARCHAR(4096));"
)
DB.commit()

CURSOR.execute("SELECT id,name,password FROM login_info")
USERS = CURSOR.fetchall()
print(USERS)


class User:
    """a user class to keep track of the users without having to keep making sql queries
    Notes:
          this is an optimization
    """

    def __init__(self, my_id, username, password):
        self.my_id = my_id
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User: {self.username}>"


towear_users = [
    User(my_id=user[0], username=user[1], password=user[2]) for user in USERS
]


@APP.after_request
def add_header(made_request):
    """
    source: https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """
    made_request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    made_request.headers["Pragma"] = "no-cache"
    made_request.headers["Expires"] = "0"
    made_request.headers["Cache-Control"] = "public, max-age=0"
    return made_request


class LoginForm(FlaskForm):
    """Login form setup

    Arguments:
        FlaskForm -- Flask-specific subclass of WTForms ~wtforms.form.Form.
    """

    username = StringField(
        "Username", validators=[InputRequired(), Length(min=5, max=20)]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(8, 80)])
    remember = BooleanField("Remember me")


class RegisterForm(FlaskForm):
    """Registeration form setup

    Arguments:
        FlaskForm - - Flask-specific subclass of WTForms ~wtforms.form.Form.
    """

    username = StringField(
        "Username", validators=[InputRequired(), Length(min=5, max=20)]
    )
    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email(message="This is an invalid email!"),
            Length(max=50),
        ],
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(8, 80)])


@APP.route("/home")
@APP.route("/")
def home():
    """Home page."""
    return render_template("index.html")


@APP.route("/register", methods=["GET", "POST"])
def register():
    """Registration page."""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        secure_password = sha256_crypt.encrypt(str(password))  # encrypted password
        CURSOR.execute(
            "INSERT INTO login_info (name,password,email)VALUES(%s,%s,%s)",
            (username, secure_password, email),
        )
        DB.commit()
        CURSOR.execute(
            "SELECT id,name,password FROM login_info WHERE name = %s", (username),
        )
        new_user = CURSOR.fetchone()
        towear_users.append(
            User(my_id=new_user[0], username=new_user[1], password=new_user[2])
        )
        my_closet = Wardrobe()
        my_closet.generic_clothes_generator()
        curr_user = [user for user in towear_users if user.username == username][0]
        CURSOR.execute(
            "INSERT INTO users_closets (id,closet)VALUES(%s,%s)",
            (curr_user.my_id, pickle.dumps(my_closet, 0)),
        )
        DB.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@APP.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    form = LoginForm()
    if form.validate_on_submit():
        session.pop("user_id", None)
        username = form.username.data
        password = form.password.data
        CURSOR.execute(
            "SELECT name FROM login_info WHERE name = %s", (username),
        )
        namedata = CURSOR.fetchone()
        CURSOR.execute(
            "SELECT password FROM login_info WHERE name = %s", (username),
        )
        passdata = CURSOR.fetchone()
        if namedata is None:
            return render_template("login.html", form=form)
        curr_user = [user for user in towear_users if user.username == username][0]
        for passdata_block in passdata:
            if sha256_crypt.verify(password, passdata_block):
                session["user_id"] = curr_user.my_id
                session["log"] = True
                return redirect(url_for("closet"))
    return render_template("login.html", form=form)


@APP.route("/logout")  # LOGIN REQUIRED!
def logout():
    """Log user out."""
    session.clear()
    return redirect(url_for("login"))


@APP.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@APP.route("/try")
def try_page():
    """Developer demo page."""
    if "log" not in session:
        return redirect(url_for("login"))
    print(session["user_id"])
    return render_template("try.html")


@APP.route("/closet")
def closet():  # LOGIN REQUIRED!
    """User closet page."""
    if "log" not in session:
        return redirect(url_for("login"))
    CURSOR.execute(
        "SELECT closet FROM users_closets WHERE id = %s", (session["user_id"]),
    )
    closet_pickled = CURSOR.fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    print(session["user_id"])
    return render_template("my_closet.html", closet=user_closet)


def get_temp(zipcode):
    """function to get weather using zipcode through pyOWM

    Arguments:
        zipcode {str} - - given by the user

    Returns:
        int - - temperature in fahrenheit returned by pyOWM
                for the current zipcode at the current time
    """
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?zip={zipcode},us&units=imperial&appid=a1f5a7e05ed9d8a645dc1651d089e671"
    )
    response_dict = json.loads(response.text)
    temp = response_dict["main"]["temp"]
    print(f"{'*'*20}\nTHE TEMPERATURE is {temp}\n{'*'*20}")
    return temp


def closet_modify():
    """Page direction after modification of closet."""
    if "log" not in session:
        return redirect(url_for("login"))
    CURSOR.execute(
        "SELECT closet FROM users_closets WHERE id = %s", (session["user_id"]),
    )
    closet_pickled = CURSOR.fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    if "name" in request.form:
        name = request.form["name"]
        warmth = list(map(int, str(request.form["warmth"]).split()))
        new_item = Garment(name, warmth)
        user_closet.add_item(new_item)
        CURSOR.execute(
            "UPDATE users_closets SET closet = %s WHERE id = %s",
            (pickle.dumps(user_closet, 0), session["user_id"]),
        )
        return render_template("my_closet.html", closet=user_closet)
    if "check" in request.form:
        selected_items = request.form.getlist("check")
        for item in selected_items:
            user_closet.delete_by_name(item)
        CURSOR.execute(
            "UPDATE users_closets SET closet = %s WHERE id = %s",
            (pickle.dumps(user_closet, 0), session["user_id"]),
        )
        return render_template("my_closet.html", closet=user_closet)
    if "name3" in request.form:
        name3 = request.form["name3"]
        warmth3 = list(map(int, str(request.form["warmth3"]).split()))
        user_closet.change_warmth(name3, warmth3)
        CURSOR.execute(
            "UPDATE users_closets SET closet = %s WHERE id = %s",
            (pickle.dumps(user_closet, 0), session["user_id"]),
        )
        return render_template("my_closet.html", closet=user_closet)
    if "repopulate" in request.form:
        user_closet.contents = []
        user_closet.generic_clothes_generator()
        CURSOR.execute(
            "UPDATE users_closets SET closet = %s WHERE id = %s",
            (pickle.dumps(user_closet, 0), session["user_id"]),
        )
        return render_template("my_closet.html", closet=user_closet)
    return render_template("my_closet.html", closet=user_closet)


@APP.route("/try", methods=["POST"])  # LOGIN REQUIRED!
def form_post():
    """Page direction after submitting request for outfit suggestion."""
    if "log" not in session:
        return redirect(url_for("login"))
    secret_coefficients = list(
        map(float, str(request.form["weather_conditions"]).split())
    )
    secret_temp_desired = float(request.form["temperature_tolerance"])
    zipcode = str(request.form["zipcode"])
    temp = get_temp(zipcode)
    # using what we know, generate training set of different
    # temperature (temp_input) to outfit (outfit_input) combinations
    # (e.g. 20, [1 6 5 4])
    temp_input, outfit_output = generate_data(secret_temp_desired, secret_coefficients)
    # using the training set, predict an outfit given the temperature
    suggested_outfit = [
        int(element) for element in suggest_outfit(temp_input, outfit_output, temp)
    ]
    # translate the outfit from an array of integers to clothes using the given closet
    CURSOR.execute(
        "SELECT closet FROM users_closets WHERE id = %s", (session["user_id"]),
    )
    closet_pickled = CURSOR.fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    suggested_outfit_translated = translate_outfit(user_closet, suggested_outfit)

    return render_template(
        "try.html",
        temperature=temp,
        suggested_outfit_warmths=suggested_outfit,
        suggested_outfit_garments=suggested_outfit_translated,
    )


if __name__ == "__main__":
    APP.run()
