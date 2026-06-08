import json
import os
from datetime import datetime


HISTORY_FILE = "data/history.json"

os.makedirs("data", exist_ok=True)


def load_history():

    if not os.path.exists(HISTORY_FILE):

        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

    with open(HISTORY_FILE, "r") as f:

        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_history(history):

    with open(HISTORY_FILE, "w") as f:

        json.dump(history, f, indent=4)


def add_to_history(food, calories, image_path=None):

    history = load_history()

    entry = {

        "food": food,
        "calories": calories,
        "image": image_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d")

    }

    history.append(entry)

    save_history(history)

    print(f"Added to history: {food} ({calories} kcal)")


def get_chart_data():

    history = load_history()

    labels = [item["food"] for item in history[-10:]]

    values = [item["calories"] for item in history[-10:]]

    return labels, values
