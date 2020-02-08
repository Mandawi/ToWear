'''
! ONLY LOOK AT THIS IF YOU WANT TO DEVELOP ON THE COMMAND LINE, THIS IS NOT USED ANYWHERE ON THE APP! 
Get or generate user data which includes outfit_tried, temp_global, and feeling
representing the clothes worn list, the weather outside, how the user felt with their outfit in that weather.
This is used for training the ML model.
'''

# Import the libraries
from random import randint
from sklearn.linear_model import LinearRegression
import statistics as tats
from points_to_english import Wardrobe, translate_outfit

# TESTING
my_closet = Wardrobe()
my_closet.generic_clothes_generator()
# TESTING


def user_happy(outfit_tried, temp_outfit, temp_global, *secrets):
    """check user feeling of this outfit in this temperature

    Arguments:
        outfit_tried {list} -- outfit used
        temp_outfit {int} -- warmth of the outfit
        temp_global {int} -- temperature outside
        *secrets {list} -- [temp_desired, temp_coefficients]

    Returns:
        Boolean -- whether the user felt good in this outfit or not

    Suggestion:
        Returns:
            int -- (-10 to 10) integer of how the user felt from freezing to melting
    """
    if secrets[0] is not None and secrets[1] is not None:
        temp_desired = secrets[0]
        temp_coefficients = secrets[1]
        temp_deviation = (temp_outfit+temp_global) - temp_desired
        if temp_deviation > 2 or temp_deviation < -2:
            return False
        else:
            for index, element in enumerate(outfit_tried):
                if element == 0:
                    element_significance = 0
                else:
                    element_significance = element/temp_outfit
                if element_significance > 0.2 + temp_coefficients[index] or element_significance < temp_coefficients[index]-0.2:
                    return False
        return True
    else:
        user = input(
            f"Did your outfit {outfit_tried} = {translate_outfit(my_closet,outfit_tried)} feel appropriate in temperature of {temp_global} (t or f)? ").lower()
        if user == "f":
            return False
        elif user == "t":
            return True
        else:
            raise ValueError(
                'Expected either t or f but got something else!')


def generate_data(data_amount, *secrets):
    """create train set data for machine learning; note that only the omniscient user knows the secret numbers

    Arguments:
        data_amount {int} -- how much data?
        temp_desired {int} -- a secret number
        temp_coefficients {[type]} -- a secret list of percentages that affect the user's temperature
    """
    estimated_desired_temp = list()
    estimated_coefficients = []
    weather_input = list()
    # make the range arbitrary equal to how many parts of clothing there are
    outfit_output = [[] for _ in range(0, 4)]
    if secrets:
        temp_desired = secrets[0]
        temp_desired_scaled = (40/134) * temp_desired
        temp_coefficients = secrets[1]
    else:
        temp_desired_scaled = temp_coefficients = None
    for _ in range(data_amount):
        # make the range arbitrary in the future
        temp_global_original = randint(0, 134)
        # global temperature in the same terms as the temperature of the outfit
        if secrets:
            temp_global_scaled = (40/134) * temp_global_original
        else:
            temp_global_scaled = temp_global_original
        # make the ranges arbitrary in the future
        outfit_tried = [randint(0, 10) for _ in range(0, 4)]
        temp_outfit = sum(outfit_tried)
        if user_happy(outfit_tried, temp_outfit, temp_global_scaled,
                      temp_desired_scaled, temp_coefficients):
            # May test what the algorithm tried and liked with this
            # print(f"Tried and liked {outfit_tried} for weather {temp_global_original}")
            estimated_desired_temp.append(temp_outfit+temp_global_scaled)
            estimated_coefficients.append(
                [element/temp_outfit for element in outfit_tried])
            weather_input.append([int(temp_global_original)])
            for index, output in enumerate(outfit_output):
                output.append(int(outfit_tried[index]))
    if not secrets:
        temp_desired = sum(estimated_desired_temp)/len(estimated_desired_temp)
        temp_coefficients = [[] for _ in range(0, 4)]
        for outfit in estimated_coefficients:
            for i in range(0, 4):
                temp_coefficients[i].append(outfit[i])
        temp_coefficients = [
            sum(temp_coefficients[i])/(len(temp_coefficients)-1) for i in range(0, 4)]
        print(
            f"Estimated that the desired body temperature is {temp_desired} degrees fahrenheit \
            \nEstimated that importance of elements is {[round(element, 2) for element in temp_coefficients]}")
    return weather_input, outfit_output


def suggest_outfit(weather_input, outfit_output, weather_given):
    # Create linear regression objects for the four clothing slots (make arbitrary)
    predictors = [LinearRegression(n_jobs=-1) for _ in range(0, 4)]
    # fit the linear model (approximate a target function)
    for index, predictor in enumerate(predictors):
        predictor.fit(X=weather_input, y=outfit_output[index])

    X_TEST = [[int(weather_given)]]
    # Predict the ouput of the test data using the linear model
    outfit = [predictor.predict(X=X_TEST) for predictor in predictors]
    for i in range(len(outfit)):
        if outfit[i] < 0:
            outfit[i] = 0
        elif outfit[i] > 10:
            outfit[i] = 10
    return outfit


def main():
    print("TIME FOR TESTING!")
    secrets = input("Do you know the secrets? (t or f) ")
    training_amount = int(input("Training amount: "))
    secret_coefficients = []
    if secrets == "t":
        print("Enter 4 coefficients for head, top, bottom, and shoes accordingly:")
        for _ in range(0, 4):
            coef = float(input(""))
            secret_coefficients.append(coef)
        secret_temp_desired = int(input("Secret temperature desired: "))
        weather = int(input("Weather in Fahrenheit: "))
        while weather:
            weather_input, outfit_output = generate_data(
                training_amount, secret_temp_desired, secret_coefficients)
            suggested_outift = [int(element) for element in suggest_outfit(
                weather_input, outfit_output, weather)]
            print(
                f"Suggested outfit: {suggested_outift} = {translate_outfit(my_closet, suggested_outift)}")
            weather = int(input("Weather in Fahrenheit: "))
    elif secrets == "f":
        weather_input, outfit_output = generate_data(training_amount)
        weather = int(input("Weather in Fahrenheit: "))
        while weather:
            suggested_outift = [int(element) for element in suggest_outfit(
                weather_input, outfit_output, weather)]
            print(
                f"Suggested outfit: {suggested_outift} = {translate_outfit(my_closet, suggested_outift)}")
            weather = int(input("Weather in Fahrenheit: "))


if __name__ == "__main__":
    main()
