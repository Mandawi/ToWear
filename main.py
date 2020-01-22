from flask import Flask, render_template, url_for, request
from try_towear import generate_data, suggest_outfit, my_closet
from points_to_english import translate_outfit, Garment
import pyowm

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/try")
def try_page():
    return render_template('try.html')


@app.route("/closet")
def closet():
    return render_template('my_closet.html', closet=my_closet.content_display())


def get_weather():
    owm = pyowm.OWM('07a7c137a54f5238063fbcd575974072')
    observation = owm.weather_at_place('Worcester, US')
    w = observation.get_weather()
    weather = w.get_temperature('fahrenheit')['temp']
    return weather


@app.route("/closet", methods=['POST'])
def closet_add():
    if "name" in request.form:
        name = request.form['name']
        warmth = list(
            map(int, str(request.form['warmth']).split()))
        w1 = warmth[0]
        w2 = warmth[1]
        w3 = warmth[2]
        w4 = warmth[3]
        stackable = int(request.form['stackable'])
        new_item = Garment(name, w1, w2, w3, w4, stackable)
        my_closet.add_item(new_item)
        return render_template('my_closet.html', closet=my_closet.content_display())
    elif "name2" in request.form:
        name2 = request.form['name2']
        my_closet.delete_by_name(name2)
        return render_template('my_closet.html', closet=my_closet.content_display())
    else:
        return render_template('my_closet.html', closet=my_closet.content_display())


@app.route('/try', methods=['POST'])
def form_post():
    training_amount = int(request.form['training_amount'])
    secret_coefficients = list(
        map(float, str(request.form['secret_coefficients']).split()))  # MUST BE DECIMAL! e.g. .2 .4 .4 .2
    secret_temp_desired = float(request.form['secret_temp_desired'])
    weather = get_weather()
    print(f"ta: {training_amount}, sc: {secret_coefficients}, std: {secret_temp_desired}, weather: {weather}")
    weather_input, outfit_output = generate_data(
        training_amount, secret_temp_desired, secret_coefficients)
    print(f"wi: {weather_input}, oo: {outfit_output}")
    suggested_outfit = [int(element) for element in suggest_outfit(
        weather_input, outfit_output, weather)]
    suggested_outfit_translated = translate_outfit(my_closet, suggested_outfit)

    return render_template('try.html', w=weather, souin=suggested_outfit, head=suggested_outfit_translated[0], upper_body=suggested_outfit_translated[1], lower_body=suggested_outfit_translated[2], feet=suggested_outfit_translated[3])
    # return render_template('try.html', ta=training_amount, sc=secret_coefficients, st=secret_temp_desired, w=weather)


if __name__ == "__main__":
    app.run(debug=True)
