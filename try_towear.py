# needed for generating test data
from random import randint
# needed for predicting using training sets
from sklearn.linear_model import LinearRegression
# needed for translating the outfit suggestion into human-readable format
from points_to_english import translate_outfit
from clothes_manager import Wardrobe

# generate a closet with some pre-defined wardrobe
my_closet = Wardrobe()
my_closet.generic_clothes_generator()


def user_happy(outfit_tried: list, temp_outfit: int, temp_global: int, *secrets: list) -> bool:
    """simulates user's feeling in this outfit with this temperature based on the user's desired temperature and coefficients

    Arguments:
        outfit_tried {list} -- outfit used
        temp_outfit {int} -- warmth of the outfit
        temp_global {int} -- temperature outside
        *secrets {list} -- [temp_desired {int} -- a secret number,
                            temp_coefficients {[type]} -- a secret list of percentages that affect the user's temperature]

    Returns:
        bool -- whether the user felt good in this outfit or not
    """
    if secrets[0] != None and secrets[1] != None:
        # the serets are known so, we can just take them
        temp_desired = secrets[0]
        temp_coefficients = secrets[1]
        # deviation of what is an accepted outfit and what is not
        temp_deviation = (temp_outfit+temp_global) - temp_desired
        if temp_deviation > 1 or temp_deviation < -1:
            # too much deviation from the desired temperature (remember all temperatures are scaled from 0 to 40)
            # user should be unhappy since the temperature does not match the desired temperature
            return False
        else:
            for index, element in enumerate(outfit_tried):
                if temp_outfit == 0:
                    # this may seem redundant but it's necessary to avoid division by zero exception
                    element_significance = 0
                else:
                    # the effect of any garment on the temperature of the outfit
                    # is equal to the temperature of the garment divided by the temperature of the outfit
                    element_significance = element/temp_outfit
                if element_significance > 0.1 + temp_coefficients[index] or element_significance < temp_coefficients[index]-0.1:
                    # user should be unhappy since the coefficient does not match the desired temperature
                    return False
        return True
    else:
        # TODO: Allow users to modify desired temperature and coefficients with real inputs
        raise ValueError('Expected known secrets')


def generate_data(data_amount: int, *secrets: list) -> tuple:
    """create train set data for machine learning; note that only the omniscient user knows the secret numbers
    although the secrets are known, we'll let the AI figure them out on its own

    Arguments:
        data_amount {int} -- how much training data?
        *secrets {list} -- [temp_desired {int} -- a secret number,
                            temp_coefficients {[type]} -- a secret list of percentages that affect the user's temperature]

    Returns:
        tuple -- pairs of weathers and corresponding appropriate outfits
    """
    # list for predicting the desired temperature of the user
    estimated_desired_temp = list()
    # list for predicting the warmth coefficients of the user
    estimated_coefficients = []
    # list of weather data
    weather_input = list()
    # list of outfits corresponding to the weather data
    outfit_output = [[] for _ in range(0, 4)]
    if secrets:
        # the serets are known so, we can just take them
        temp_desired = secrets[0]
        temp_coefficients = secrets[1]
        # scale the desired temperature to a number between 0 and 40
        temp_desired_scaled = (40/134) * temp_desired
    else:
        # if we don't know the desired temperatures, we should estimate them later
        temp_desired_scaled = temp_coefficients = None
    # generate data_amount of items for the training sets of weather_input and outfit_output
    while len(weather_input) != data_amount:
        # random weather value between 0 and 40
        temp_global_original = randint(0, 134)
        # global temperature in the same terms as the temperature of the outfit
        temp_global_scaled = (40/134) * temp_global_original
        # generate a random tried outfit with garment warmths between 0 and 10 for all 4 parts
        outfit_tried = [randint(0, 10) for _ in range(0, 4)]
        # the temperature of the outfit generated between 0 and 40 for the temperature which is between 0 and 40
        temp_outfit = sum(outfit_tried)
        if user_happy(outfit_tried, temp_outfit, temp_global_scaled,
                      temp_desired_scaled, temp_coefficients):
            # if the user, knowing their desired temperature and coefficients are happy with the result,
            # we should include the weather_input and outfit_output pair in the training set
            estimated_desired_temp.append(temp_outfit+temp_global_scaled)
            estimated_coefficients.append(
                [element/temp_outfit for element in outfit_tried])
            weather_input.append([int(temp_global_original)])
            for index, output in enumerate(outfit_output):
                output.append(int(outfit_tried[index]))
    return weather_input, outfit_output


def suggest_outfit(weather_input: list, outfit_output: list, weather_given: int) -> list:
    """suggest an outfit to the user using the training sets of weather and outfit pairs

    Arguments:
        weather_input {list} -- weather inputs to use as training sets
        outfit_output {list} -- outfits appropriate for each weather input
        weather_given {int} -- the given weather in this case

    Returns:
        list -- [int,int,int,int] of the perfect outfit for the weather for this user
    """
    # create linear regression objects for the four clothing slots
    predictors = [LinearRegression(n_jobs=-1) for _ in range(0, 4)]
    # fit the linear model (approximate a target function)
    for index, predictor in enumerate(predictors):
        predictor.fit(X=weather_input, y=outfit_output[index])
    # use the current weather as input
    X_TEST = [[int(weather_given)]]
    # Predict the ouput of the input X_Test using the linear model
    outfit = [predictor.predict(X=X_TEST) for predictor in predictors]
    # get rid of any below 0 inaccuracies
    for i in range(len(outfit)):
        if outfit[i] < 0:
            outfit[i] = 0
        elif outfit[i] > 10:
            outfit[i] = 10
    return outfit
