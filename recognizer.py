import tensorflow as tf
import numpy as np
import os

from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input,
    decode_predictions,
    MobileNetV2
)

from tensorflow.keras.preprocessing import image


# -------------------------------------------------
# Model Paths
# -------------------------------------------------

TFLITE_INT8 = "model/mobilenet_food_int8.tflite"
TFLITE_FP32 = "model/mobilenet_food.tflite"


USE_TFLITE = False
interpreter = None
model = None


# -------------------------------------------------
# Load Model
# -------------------------------------------------

try:

    if os.path.exists(TFLITE_INT8):

        interpreter = tf.lite.Interpreter(model_path=TFLITE_INT8)
        interpreter.allocate_tensors()

        print("✅ Using TFLite INT8 model")

        USE_TFLITE = True

    elif os.path.exists(TFLITE_FP32):

        interpreter = tf.lite.Interpreter(model_path=TFLITE_FP32)
        interpreter.allocate_tensors()

        print("✅ Using TFLite FP32 model")

        USE_TFLITE = True

    else:

        print("⚠️ TFLite model not found, using MobileNetV2")

        model = MobileNetV2(weights="imagenet")

except Exception as e:

    print("⚠️ Model load failed, using MobileNetV2 fallback")

    model = MobileNetV2(weights="imagenet")


# -------------------------------------------------
# Food Mapping
# -------------------------------------------------

FOOD_MAP = {

    "granny_smith": "apple",
    "orange": "orange",
    "banana": "banana",
    "strawberry": "strawberry",

    "pizza": "pizza",
    "cheeseburger": "burger",
    "hotdog": "hotdog",
    "burrito": "burrito",
    "sandwich": "sandwich",

    "bagel": "bread",
    "mushroom": "mushroom",
    "broccoli": "broccoli",
    "cauliflower": "cauliflower",
    "carrot": "carrot",

    "spaghetti": "pasta",
    "rice": "rice",
    "cup": "drink",

    # Kerala foods
    "idli": "idli",
    "dosa": "dosa",
    "puttu": "puttu",
    "appam": "appam",
    "idiyappam": "idiyappam",
    "porotta": "porotta",
    "chappathi": "chappathi",

    "fish_curry": "meen curry",
    "chicken_curry": "chicken curry",
    "sambar": "sambar",
    "avial": "avial",
    "thoran": "thoran",
    "payasam": "payasam",
    "banana_fritters": "pazham pori"

}


# -------------------------------------------------
# Calorie Database
# -------------------------------------------------

CALORIE_DB = {

    "apple": 52,
    "orange": 47,
    "banana": 89,
    "strawberry": 32,

    "burger": 295,
    "pizza": 266,
    "hotdog": 290,
    "burrito": 300,
    "sandwich": 250,

    "bread": 265,
    "mushroom": 22,
    "broccoli": 34,
    "carrot": 41,
    "pasta": 131,
    "rice": 130,
    "drink": 40,

    # Kerala foods
    "idli": 39,
    "dosa": 133,
    "puttu": 180,
    "appam": 120,
    "idiyappam": 100,
    "porotta": 320,
    "chappathi": 120,
    "meen curry": 210,
    "chicken curry": 260,
    "sambar": 90,
    "avial": 150,
    "thoran": 170,
    "payasam": 300,
    "pazham pori": 250,

    "unknown": 100
}


# -------------------------------------------------
# Non-food detection
# -------------------------------------------------

NON_FOOD_KEYWORDS = [

    "dog", "cat", "car", "bus", "truck",
    "person", "chair", "table", "laptop",
    "keyboard", "book", "bottle", "television",
    "clock", "building", "motorcycle"

]


# -------------------------------------------------
# Regional Food Matching
# -------------------------------------------------

def match_regional_food(label):

    regional_keywords = {

        "puttu": ["steamed rice cake"],
        "appam": ["pancake", "hopper"],
        "idiyappam": ["string hoppers", "rice noodles"],
        "porotta": ["flatbread", "paratha"],
        "sambar": ["lentil", "curry"],
        "avial": ["vegetable curry"],
        "thoran": ["stir fry"],
        "payasam": ["pudding", "dessert"],
        "pazham pori": ["banana fritters"]

    }

    for food, hints in regional_keywords.items():

        for h in hints:

            if h in label:

                return food

    return None


# -------------------------------------------------
# Image Preprocessing
# -------------------------------------------------

def preprocess_image(img_path):

    img = image.load_img(img_path, target_size=(224, 224))

    x = image.img_to_array(img)

    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x)

    return x


# -------------------------------------------------
# Prediction
# -------------------------------------------------

def predict_food(img_path):

    if not os.path.exists(img_path):

        return {
            "label": "unknown",
            "calories": 0,
            "confidence": 0,
            "nutrients": {},
            "non_food": True
        }

    try:

        x = preprocess_image(img_path)

        if USE_TFLITE:

            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            interpreter.set_tensor(input_details[0]["index"], x)

            interpreter.invoke()

            preds = interpreter.get_tensor(output_details[0]["index"])

        else:

            preds = model.predict(x)

        decoded = decode_predictions(preds, top=1)[0][0]

        label = decoded[1].lower()

        confidence = float(decoded[2])

        # --------------------------------
        # Non food filtering
        # --------------------------------

        for kw in NON_FOOD_KEYWORDS:

            if kw in label:

                return {

                    "label": label,
                    "calories": 0,
                    "confidence": round(confidence, 2),
                    "nutrients": {},
                    "non_food": True
                }

        # --------------------------------
        # Regional match
        # --------------------------------

        regional = match_regional_food(label)

        if regional:

            label = regional

        mapped = FOOD_MAP.get(label, label)

        calories = CALORIE_DB.get(mapped, 100)

        nutrients = {

            "Protein (g)": round(calories * 0.04, 1),
            "Fat (g)": round(calories * 0.03, 1),
            "Carbs (g)": round(calories * 0.12, 1),
            "Fiber (g)": round(calories * 0.02, 1)

        }

        return {

            "label": mapped,
            "calories": calories,
            "confidence": round(confidence, 2),
            "nutrients": nutrients,
            "non_food": False

        }

    except Exception as e:

        print("Prediction error:", e)

        return {

            "label": "unknown",
            "calories": 0,
            "confidence": 0,
            "nutrients": {},
            "non_food": True
        }
