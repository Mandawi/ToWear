![freepik-logo.ico](static/freepik-logo.ico?raw=true "Logo")

# ToWear

### ToWear is an application that suggests outfits to users from their closets based on the weather. We aim to use linear regression to personalize the results to each user. [Check out the current state of the app here](http://oamandawi.pythonanywhere.com/).

# Table of contents
1. [Main Ideas](#ideas)
    1. [For Users](#ideas_user)
    2. [For Developers](#ideas_developer)
3. [Slideshow](#slideshow)
4. [In the works](#new)


## The main ideas of the app -- for users and for developers: <a name="ideas"></a>

### 1. For Users <a name="ideas_user"></a>
We want our users to provide as little inputs as possible because we believe that will give them a better experience using the app.
    
You only have to create your closet based on the clothes you have. Each garment has a score from 1 to 10 to
specify the warmth. Each garment warms one of four parts of the body: (1) head, (2) top, (3) bottom, (4) feet.

You can then ask for a suggestion and you will be given a suggested outfit based on the current weather
outside.

If desired, you can give the app information every day about what you wore and how you felt. This will be compared to the weather outside for that given day; the next time you ask for a suggestion, you will get more personalized outfits.

### 2. For Developers <a name="ideas_developer"></a>
Make sure to download all dependencies using "pip install -r requirements.txt" without quotes in your cmd.

In [main.py](https://github.com/Mandawi/ToWear/blob/master/main.py) you will find the Flask code. MUST see first for anyone who wants to understand the code.

In [try_towear.py](https://github.com/Mandawi/ToWear/blob/master/try_towear.py) you will find most of the backend code for predicting body coefficients and desired temperature, which are used to suggest outfits.

In [points_to_english.py](https://github.com/Mandawi/ToWear/blob/master/points_to_english.py) you will find code relating to the representation of garments and clothes, as well as how the array outfit generated by the machine learning algorithm is translated into clothes.

*Note that you can use ***user_data.py*** and ***points_to_english.py*** alone to develop features using the cmd and without the flask front-end. Simply download these two files and run "python user_data.py" to see a text-based version of the app.*
### 3. Slideshow explaining the app <a name="slideshow"></a>
[embed]https://github.com/Mandawi/ToWear/blob/master/ToWear.pdf[/embed]

### 4. Features in the works <a name="new"></a>
        
        
