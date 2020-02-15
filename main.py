"""Web application creation and web page direction (basically, glues the whole program together)."""

from flask import Flask, render_template, request
import pyowm  # for temperature
from try_towear import generate_data, suggest_outfit
from points_to_english import translate_outfit
from clothes_manager import Garment, Wardrobe


APP = Flask(__name__)
MY_CLOSET = Wardrobe()
MY_CLOSET.generic_clothes_generator()

# disable css caching
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

# main page
@APP.route("/")
def home():
    """Home page."""
    return render_template('index.html')

# about page
@APP.route("/about")
def about():
    """About page."""
    return render_template('about.html')

# try page
@APP.route("/try")
def try_page():
    """Developer demo page."""
    return render_template('try.html')

# closet page
@APP.route("/closet")
def closet():
    """User closet page."""
    return render_template('my_closet.html', closet=MY_CLOSET)


def get_temp(zipcode):
    """function to get weather using zipcode through pyOWM

    Arguments:
        zipcode {str} -- given by the user

    Returns:
        int -- temperature in fahrenheit returned by pyOWM
                for the current zipcode at the current time
    """
    owm = pyowm.OWM('07a7c137a54f5238063fbcd575974072')  # API key
    observation = owm.weather_at_zip_code(zipcode, "us")
    current_weather = observation.get_weather()
    temperature = current_weather.get_temperature('fahrenheit')['temp']
    return temperature

# closet page after submission of garment addition (or deletion) request
@APP.route("/closet", methods=['POST'])
def closet_modify():
    """Page direction after modification of closet."""
    if "name" in request.form:
        name = request.form['name']
        warmth = list(
            map(int, str(request.form['warmth']).split()))
        w_1 = warmth[0]
        w_2 = warmth[1]
        w_3 = warmth[2]
        w_4 = warmth[3]
        new_item = Garment(name, [w_1, w_2, w_3, w_4])
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

# try page after suggestion request
@APP.route('/try', methods=['POST'])
def form_post():
    """Page direction after submitting request for outfit suggestion."""
    secret_coefficients = list(
        map(float, str(request.form['secret_coefficients']).split()))
    secret_temp_desired = float(request.form['secret_temp_desired'])
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
    APP.run(debug=True)
