"""
calorie_estimator.py
--------------------
Estimate calories and nutrients from food name and volume.
Used by FoodAI detection pipeline.
"""

# -------------------------------------------------
# Food density (g/cm³) and nutrition values
# -------------------------------------------------

FOODS = {

    "chappathi": {
        "density": 0.85,
        "kcal_g": 2.6,
        "nutrients": {"protein": 9, "fat": 3, "carbs": 45}
    },

    "dosa": {
        "density": 0.95,
        "kcal_g": 1.4,
        "nutrients": {"protein": 5, "fat": 3, "carbs": 25}
    },

    "idli": {
        "density": 0.95,
        "kcal_g": 1.1,
        "nutrients": {"protein": 3, "fat": 1, "carbs": 20}
    },

    "puttu": {
        "density": 0.95,
        "kcal_g": 1.2,
        "nutrients": {"protein": 3, "fat": 1, "carbs": 20}
    },

    "chutney": {
        "density": 1.0,
        "kcal_g": 1.8,
        "nutrients": {"protein": 2, "fat": 12, "carbs": 6}
    },

    "sambar": {
        "density": 1.0,
        "kcal_g": 0.8,
        "nutrients": {"protein": 2.5, "fat": 3, "carbs": 8}
    },

    "chicken_curry": {
        "density": 1.05,
        "kcal_g": 2.4,
        "nutrients": {"protein": 27, "fat": 14, "carbs": 3}
    },

    "gulabjamun": {
        "density": 1.1,
        "kcal_g": 3.3,
        "nutrients": {"protein": 4, "fat": 12, "carbs": 40}
    }
}


# -------------------------------------------------
# Get food info
# -------------------------------------------------

def get_food_info(food_name):
    """
    Return food information from database
    """

    if not food_name:
        return None

    return FOODS.get(food_name.lower())


# -------------------------------------------------
# Estimate calories
# -------------------------------------------------

def estimate_calories(food_name, volume_cm3):
    """
    Estimate calories and nutrients from food volume

    Parameters
    ----------
    food_name : str
    volume_cm3 : float

    Returns
    -------
    calories : float
    nutrients : dict
    """

    food = get_food_info(food_name)

    if food is None:
        return 0.0, {"protein": 0, "fat": 0, "carbs": 0}

    # Volume → mass
    mass_g = volume_cm3 * food["density"]

    # Mass → calories
    calories = mass_g * food["kcal_g"]

    # Nutrient estimation
    nutrients = {

        nutrient: round((mass_g / 100) * value, 2)
        for nutrient, value in food["nutrients"].items()

    }

    return round(calories, 2), nutrients


# -------------------------------------------------
# Optional test
# -------------------------------------------------

if __name__ == "__main__":

    food = "dosa"
    volume = 150

    calories, nutrients = estimate_calories(food, volume)

    print("Food:", food)
    print("Volume:", volume, "cm³")
    print("Calories:", calories, "kcal")
    print("Nutrients:", nutrients)
