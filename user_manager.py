import json
import os

# -----------------------------------
# Data path
# -----------------------------------

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)


# -----------------------------------
# Load user profile
# -----------------------------------

def load_user():

    if not os.path.exists(DATA_PATH):
        return {}

    try:

        with open(DATA_PATH, "r") as f:
            return json.load(f)

    except Exception:

        return {}


# -----------------------------------
# Save user profile
# -----------------------------------

def save_user(user_data):

    try:

        with open(DATA_PATH, "w") as f:
            json.dump(user_data, f, indent=2)

    except Exception as e:

        print("User save failed:", e)


# -----------------------------------
# Default user values
# -----------------------------------

def default_user():

    return {

        "name": "User",
        "age": 25,
        "gender": "male",
        "weight": 60,     # kg
        "height": 170,    # cm
        "activity": "sedentary"

    }


# -----------------------------------
# Calculate BMR
# -----------------------------------

def calculate_bmr(user):

    if not user:
        user = default_user()

    weight = float(user.get("weight", 60))
    height = float(user.get("height", 170))
    age = float(user.get("age", 25))
    gender = user.get("gender", "male").lower()

    # Mifflin-St Jeor Equation

    if gender == "male":

        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    else:

        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    return round(bmr, 2)


# -----------------------------------
# Daily calorie limit
# -----------------------------------

def daily_calorie_limit(user):

    if not user:
        return 2000

    bmr = calculate_bmr(user)

    activity_levels = {

        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9

    }

    activity = user.get("activity", "sedentary")

    multiplier = activity_levels.get(activity, 1.2)

    calories = bmr * multiplier

    return round(calories, 2)


# -----------------------------------
# User summary (for dashboard)
# -----------------------------------

def user_summary():

    user = load_user()

    if not user:
        user = default_user()

    return {

        "name": user.get("name", "User"),
        "age": user.get("age", 25),
        "weight": user.get("weight", 60),
        "height": user.get("height", 170),
        "bmr": calculate_bmr(user),
        "daily_limit": daily_calorie_limit(user)

    }
