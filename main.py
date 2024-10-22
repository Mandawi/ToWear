"""Web APPlication creation and web page direction (basically, glues the whole program together)."""

import pickle
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

from passlib.hash import sha256_crypt  # password encryption

from try_towear import generate_data, suggest_outfit
from points_to_english import translate_outfit
from clothes_manager import Garment, Wardrobe

APP = Flask(__name__)
APP.config["SECRET_KEY"] = "donttellanyonethis"
APP.config["TEMPLATES_AUTO_RELOAD"] = True
APP.config["DEBUG"] = True
BOOTSTRAP = Bootstrap(APP)

if __name__ == "__main__":
    import sshtunnel

    sshtunnel.SSH_TIMEOUT = sshtunnel.TUNNEL_TIMEOUT = 5.0

    TUNNEL = sshtunnel.open_tunnel(
        ("ssh.pythonanywhere.com"),
        ssh_username="oamandawi",
        ssh_password="ToWearwego?",
        remote_bind_address=("oamandawi.mysql.pythonanywhere-services.com", 3306),
        debug_level="TRACE",
    )

    TUNNEL.start()

    APP.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+pymysql://{username}:{password}@{hostname}:{tunnel}/{databasename}".format(
        username="oamandawi",
        password="FrFZpH^gq5",
        hostname="127.0.0.1",
        tunnel=TUNNEL.local_bind_port,
        databasename="oamandawi$towear",
    )

else:
    APP.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
        username="oamandawi",
        password="FrFZpH^gq5",
        hostname="oamandawi.mysql.pythonanywhere-services.com",
        databasename="oamandawi$towear",
    )

APP.config["SQLALCHEMY_POOL_RECYCLE"] = 299
APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB = SQLAlchemy(APP)

DB.engine.execute(
    "CREATE TABLE IF NOT EXISTS login_info"
    "(id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,"
    "name VARCHAR(20),password VARCHAR(80),email VARCHAR(50));"
)

DB.engine.execute(
    "CREATE TABLE IF NOT EXISTS users_closets"
    "(id INT(11) NOT NULL PRIMARY KEY,"
    "closet VARCHAR(4096));"
)

USERS = DB.engine.execute("SELECT id,name,password FROM login_info;").fetchall()

APP.logger.info("Successfully created DB and connected")


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
        return ("<User: %s>", self.username)


TOWEAR_USERS = [
    User(my_id=user[0], username=user[1], password=user[2]) for user in USERS
]


# @APP.after_request
# def add_header(made_request):
#     """
#     source: https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
#     """
#     made_request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     made_request.headers["Pragma"] = "no-cache"
#     made_request.headers["Expires"] = "0"
#     made_request.headers["Cache-Control"] = "public, max-age=0"
#     return made_request


class LoginForm(FlaskForm):
    """Login form setup

    Arguments:
        FlaskForm -- Flask-specific subclass of WTForms ~wtforms.form.Form.
    """

    username = StringField("", validators=[InputRequired(), Length(min=5, max=20)])
    password = PasswordField("", validators=[InputRequired(), Length(8, 80)])
    remember = BooleanField("")


class RegisterForm(FlaskForm):
    """Registeration form setup

    Arguments:
        FlaskForm - - Flask-specific subclass of WTForms ~wtforms.form.Form.
    """

    username = StringField("", validators=[InputRequired(), Length(min=5, max=20)])
    email = StringField(
        "",
        validators=[
            InputRequired(),
            Email(message="This is an invalid email!"),
            Length(max=50),
        ],
    )
    password = PasswordField("", validators=[InputRequired(), Length(8, 80)])


@APP.route("/register", methods=["GET", "POST"])
def register():
    """Registration page."""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        secure_password = sha256_crypt.encrypt(str(password))  # encrypted password
        DB.engine.execute(
            "INSERT INTO login_info (name,password,email)VALUES(%s,%s,%s);",
            (username, secure_password, email),
        )
        new_user = DB.engine.execute(
            "SELECT id,name,password FROM login_info WHERE name = %s;", (username),
        ).fetchone()
        TOWEAR_USERS.append(
            User(my_id=new_user[0], username=new_user[1], password=new_user[2])
        )
        my_closet = Wardrobe()
        my_closet.generic_clothes_generator()
        curr_user = [user for user in TOWEAR_USERS if user.username == username][0]
        DB.engine.execute(
            "INSERT INTO users_closets (id,closet)VALUES(%s,%s);",
            (curr_user.my_id, pickle.dumps(my_closet, 0)),
        )
        APP.logger.info("Successfully registered")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@APP.route("/home")
@APP.route("/")
@APP.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    APP.logger.info("Arrived at login page")
    form = LoginForm()
    APP.logger.info("Form validated")
    if form.validate_on_submit():
        APP.logger.info("Fetching form data")
        session.pop("user_id", None)
        username = form.username.data
        password = form.password.data
        APP.logger.info("Form data has been successfully fetched")
        namedata = DB.engine.execute(
            "SELECT name FROM login_info WHERE name = %s;", (username)
        ).fetchone()
        APP.logger.info("Name data is %s", (namedata))
        passdata = DB.engine.execute(
            "SELECT password FROM login_info WHERE name = %s;", (username)
        ).fetchone()
        if namedata is None or passdata is None:
            return render_template("login.html", form=form)
        APP.logger.info("Searching for current user")
        curr_user = [user for user in TOWEAR_USERS if user.username == username][0]
        APP.logger.info("Current user is %s", (curr_user.my_id))
        for passdata_block in passdata:
            APP.logger.info("Decrypting password")
            if sha256_crypt.verify(password, passdata_block):
                session["user_id"] = curr_user.my_id
                session["user_name"] = curr_user.username
                session["log"] = True
                APP.logger.info("Successfully logged in")
                return redirect(url_for("closet"))
        APP.logger.info(
            "Login authentication complete.\nNo such user.\nRedirecting to login page..."
        )
    return render_template("login.html", form=form)


@APP.route("/logout")  # LOGIN REQUIRED!
def logout():
    """Log user out."""
    session.clear()
    APP.logger.info("Successfully logged out")
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
    return render_template("try.html")


@APP.route("/closet")
def closet():  # LOGIN REQUIRED!
    """User closet page."""
    if "log" not in session:
        return redirect(url_for("login"))
    closet_pickled = DB.engine.execute(
        "SELECT closet FROM users_closets WHERE id = %s;", (session["user_id"]),
    ).fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    return render_template(
        "my_closet.html", closet=user_closet, user=session["user_name"]
    )


def get_temp(zipcode):
    """function to get weather using zipcode through pyOWM

    Arguments:
        zipcode {str} - - given by the user

    Returns:
        int - - temperature in fahrenheit returned by pyOWM
                for the current zipcode at the current time
    """
    print(zipcode)
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?zip={zipcode},"
        "us&units=imperial&appid=a1f5a7e05ed9d8a645dc1651d089e671"
    ).json()
    if response["cod"] == "404":
        temp = 50
    else:
        temp = response["main"]["temp"]
    print(f"{'*'*20}\nWRONG ZIPCODE, 01602 ZIPCODE SENT{temp}\n{'*'*20}")
    return temp


@APP.route("/closet", methods=["GET", "POST"])
def closet_modify():
    """Page direction after modification of closet."""
    if "log" not in session:
        return redirect(url_for("login"))
    closet_pickled = DB.engine.execute(
        "SELECT closet FROM users_closets WHERE id = %s;", (session["user_id"]),
    ).fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    if "name" in request.form:
        name = request.form["name"]
        warmth = list(map(int, str(request.form["warmth"]).split()))
        new_item = Garment(name, warmth)
        user_closet.add_item(new_item)
    if "check" in request.form:
        selected_items = request.form.getlist("check")
        for item in selected_items:
            user_closet.delete_by_name(item)
    if "name3" in request.form:
        name3 = request.form["name3"]
        warmth3 = list(map(int, str(request.form["warmth3"]).split()))
        user_closet.change_warmth(name3, warmth3)
    if "repopulate" in request.form:
        user_closet.contents = []
        user_closet.generic_clothes_generator()
    DB.engine.execute(
        "UPDATE users_closets SET closet = %s WHERE id = %s;",
        (pickle.dumps(user_closet, 0), session["user_id"]),
    )
    APP.logger.info("Successfully modified closet for user %s", (session["user_id"]))
    return render_template(
        "my_closet.html", closet=user_closet, user=session["user_name"]
    )


@APP.route("/try", methods=["GET", "POST"])  # LOGIN REQUIRED!
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
    closet_pickled = DB.engine.execute(
        "SELECT closet FROM users_closets WHERE id = %s;", (session["user_id"]),
    ).fetchone()
    user_closet = pickle.loads(str.encode(closet_pickled[0]))
    suggested_outfit_translated = translate_outfit(user_closet, suggested_outfit)
    APP.logger.info("%s sucessfully tried clothes", (session["user_id"]))
    APP.logger.info("%s is the suggested outfit", (suggested_outfit_translated))
    return render_template(
        "try.html",
        temperature=temp,
        suggested_outfit_warmths=suggested_outfit,
        suggested_outfit_garments=suggested_outfit_translated,
    )


if __name__ == "__main__":
    APP.run(debug=True)
