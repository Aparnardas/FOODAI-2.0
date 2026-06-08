import json
import os
from collections import defaultdict


PATH = "data/history.json"


def get_chart_data():

    """
    Returns chart labels and calorie values grouped by date
    """

    if not os.path.exists(PATH):

        return [], []

    with open(PATH, "r") as f:

        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return [], []

    totals = defaultdict(float)

    for item in data:

        date = item.get("date") or item.get("timestamp", "")[:10]

        calories = item.get("calories", 0)

        totals[date] += calories

    dates = sorted(totals.keys())

    calories = [round(totals[d], 2) for d in dates]

    return dates, calories
