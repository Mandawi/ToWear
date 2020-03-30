"""Web APPlication creation and web page direction (basically, glues the whole program together)."""


from flask import Flask, render_template, request, redirect, url_for

import pyowm

from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

import pymysql.cursors  # database

from try_towear import generate_data, suggest_outfit
from points_to_english import translate_outfit
from clothes_manager import Garment, Wardrobe


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'donttellanyonethis'
APP.config['TEMPLATES_AUTO_RELOAD'] = True

MY_CLOSET = Wardrobe()
MY_CLOSET.generic_clothes_generator()

conn = pymysql.connect(host="sql9.freemysqlhosting.net", user="sql9330153",
                       password="Q8RVqW38bq", db="sql9330153")
cursor = conn.cursor()
cursor.execute(
    f"CREATE TABLE IF NOT EXISTS login_info (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,name VARCHAR(20),password VARCHAR(80),email VARCHAR(50));")
conn.commit()


@APP.after_request
def add_header(made_request):
    """
    source: https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """
    made_request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    made_request.headers["Pragma"] = "no-cache"
    made_request.headers["Expires"] = "0"
    made_request.headers['Cache-Control'] = 'public, max-age=0'
    return made_request


class LoginForm(FlaskForm):
    """Login form setup

    Arguments:
        FlaskForm -- Flask-specific subclass of WTForms ~wtforms.form.Form.
    """
    username = StringField("Username", validators=[
        InputRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[
        InputRequired(), Length(8, 80)])
    remember = BooleanField("Remember me")


class RegisterForm(FlaskForm):
    """Registeration form setup

    Arguments:
        FlaskForm - - Flask-specific subclass of WTForms ~wtforms.form.Form.
    """
    username = StringField("Username", validators=[
        InputRequired(), Length(min=5, max=20)])
    email = StringField("Email", validators=[
        InputRequired(), Email(message="This is an invalid email!"), Length(max=50)])
    password = PasswordField("Password", validators=[
        InputRequired(), Length(8, 80)])


@APP.route("/home")
@APP.route("/")
def home():
    """Home page."""
    return render_template('index.html')


@APP.route("/register", methods=['GET', 'POST'])
def register():
    """Registration page."""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        cursor.execute(
            "INSERT INTO login_info (name,password,email)VALUES(%s,%s,%s)", (username, password, email))
        conn.commit()
        return redirect(url_for('register'))
    return render_template('register.html', form=form)


@APP.route("/login", methods=['GET', 'POST'])
def login():
    """Login page."""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        cursor.execute(
            "SELECT name FROM login_info WHERE name ='"+username+"'")
        user = cursor.fetchone()
        if len(user) is 1:
            return redirect(url_for('closet'))
        return "failed"
    return render_template('login.html', form=form)


@APP.route("/about")
def about():
    """About page."""
    return render_template('about.html')


@APP.route("/try")
def try_page():
    """Developer demo page."""
    return render_template('try.html')


@APP.route("/closet")
def closet():
    """User closet page."""
    return render_template('my_closet.html', closet=MY_CLOSET)


def get_temp(zipcode):
    """function to get weather using zipcode through pyOWM

    Arguments:
        zipcode {str} - - given by the user

    Returns:
        int - - temperature in fahrenheit returned by pyOWM
                for the current zipcode at the current time
    """
    owm = pyowm.OWM('07a7c137a54f5238063fbcd575974072')  # API key
    observation = owm.weather_at_zip_code(zipcode, "us")
    current_weather = observation.get_weather()
    temperature = current_weather.get_temperature('fahrenheit')['temp']
    return temperature


@APP.route("/closet", methods=['POST'])
def closet_modify():
    """Page direction after modification of closet."""
    if "name" in request.form:
        name = request.form['name']
        warmth = list(
            map(int, str(request.form['warmth']).split()))
        new_item = Garment(name, warmth)
        MY_CLOSET.add_item(new_item)
        return render_template('my_closet.html', closet=MY_CLOSET)
    if "check" in request.form:
        selected_items = request.form.getlist('check')
        for item in selected_items:
            MY_CLOSET.delete_by_name(item)
        return render_template('my_closet.html', closet=MY_CLOSET)
    if "name3" in request.form:
        name3 = request.form['name3']
        warmth3 = list(
            map(int, str(request.form['warmth3']).split()))
        MY_CLOSET.change_warmth(name3, warmth3)
        return render_template('my_closet.html', closet=MY_CLOSET)
    if "repopulate" in request.form:
        MY_CLOSET.contents = []
        MY_CLOSET.generic_clothes_generator()
        return render_template('my_closet.html', closet=MY_CLOSET)
    return render_template('my_closet.html', closet=MY_CLOSET)


@APP.route('/try', methods=['POST'])
def form_post():
    """Page direction after submitting request for outfit suggestion."""
    secret_coefficients = list(
        map(float, str(request.form['weather_conditions']).split()))
    secret_temp_desired = float(request.form['temperature_tolerance'])
    zipcode = str(request.form['zipcode'])
    temp = get_temp(zipcode)
    # using what we know, generate training set of different
    # temperature (temp_input) to outfit (outfit_input) combinations
    # (e.g. 20, [1 6 5 4])
    temp_input, outfit_output = generate_data(
        secret_temp_desired, secret_coefficients)
    # using the training set, predict an outfit given the temperature
    suggested_outfit = [int(element) for element in suggest_outfit(
        temp_input, outfit_output, temp)]
    # translate the outfit from an array of integers to clothes using the given closet
    suggested_outfit_translated = translate_outfit(MY_CLOSET, suggested_outfit)

    return render_template(
        'try.html', temperature=temp, suggested_outfit_warmths=suggested_outfit,
        suggested_outfit_garments=suggested_outfit_translated)


if __name__ == "__main__":
    BSTRAP = Bootstrap(APP)
    APP.run(debug=True)
