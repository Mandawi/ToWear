from flask import Flask, render_template, url_for, request
from try_towear import generate_data, suggest_outfit, my_closet
from points_to_english import translate_outfit
from clothes_manager import Garment
import pyowm
# debugging purposes
import sys

app = Flask(__name__)


@app.after_request
def add_header(r):
    """
    source: https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# main page
@app.route("/")
def home():
    return render_template('index.html')

# about page
@app.route("/about")
def about():
    return render_template('about.html')

# try page
@app.route("/try")
def try_page():
    return render_template('try.html')

# closet page
@app.route("/closet")
def closet():
    return render_template('my_closet.html', closet=my_closet)


def get_temp(zipcode):
    """function to get weather using zipcode through pyOWM

    Arguments:
        zipcode {str} -- given by the user

    Returns:
        int -- temperature in fahrenheit returned by pyOWM for the current zipcode at the current time
    """
    owm = pyowm.OWM('07a7c137a54f5238063fbcd575974072')  # API key
    observation = owm.weather_at_zip_code(zipcode, "us")
    w = observation.get_weather()
    weather = w.get_temperature('fahrenheit')['temp']
    return weather

# closet page after submission of garment addition (or deletion) request
@app.route("/closet", methods=['POST'])
def closet_modify():
    if "name" in request.form:
        name = request.form['name']
        warmth = list(
            map(int, str(request.form['warmth']).split()))
        w1 = warmth[0]
        w2 = warmth[1]
        w3 = warmth[2]
        w4 = warmth[3]
        new_item = Garment(name, w1, w2, w3, w4)
        my_closet.add_item(new_item)
        return render_template('my_closet.html', closet=my_closet)
    elif "check" in request.form:
        selected_items = request.form.getlist('check')
        print(selected_items, file=sys.stderr)
        for item in selected_items:
            print(item, file=sys.stderr)
            my_closet.delete_by_name(item)
        return render_template('my_closet.html', closet=my_closet)
    elif "name3" in request.form:
        name3 = request.form['name3']
        warmth3 = list(
            map(int, str(request.form['warmth3']).split()))
        my_closet.change_warmth(name3, warmth3)
        return render_template('my_closet.html', closet=my_closet)
    elif "repopulate" in request.form:
        my_closet.contents = []
        my_closet.generic_clothes_generator()
        return render_template('my_closet.html', closet=my_closet)
    else:
        return render_template('my_closet.html', closet=my_closet)

# try page after suggestion request
@app.route('/try', methods=['POST'])
def form_post():
    training_amount = int(request.form['training_amount'])
    secret_coefficients = list(
        map(float, str(request.form['secret_coefficients']).split()))  # MUST BE DECIMAL! e.g. .2 .4 .4 .2
    secret_temp_desired = float(request.form['secret_temp_desired'])
    zipcode = str(request.form['zipcode'])
    temp = get_temp(zipcode)
    # using what we know, generate training set of different
    # temperature (temp_input) to outfit (outfit_input) combinations
    # (e.g. 20, [1 6 5 4])
    temp_input, outfit_output = generate_data(
        training_amount, secret_temp_desired, secret_coefficients)
    # using the training set, predict an outfit given the temperature
    suggested_outfit = [int(element) for element in suggest_outfit(
        temp_input, outfit_output, temp)]
    # translate the outfit from an array of integers to clothes using the given closet
    suggested_outfit_translated = translate_outfit(my_closet, suggested_outfit)

    return render_template('try.html', w=temp, souin=suggested_outfit, outfit=suggested_outfit_translated)


if __name__ == "__main__":
    app.run(debug=True)
