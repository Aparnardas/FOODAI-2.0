import os
import uuid
import json
import cv2
import base64
from datetime import datetime
from collections import defaultdict

from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from reportlab.pdfgen import canvas


# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = "foodai_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")
RESULTS_DIR = os.path.join(STATIC_DIR, "results")

DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
USER_FILE = os.path.join(DATA_DIR, "user.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------
# Load Model
# -----------------------------
MODEL_PATH = os.path.join(BASE_DIR, "model", "food_yolo_best.pt")
model = YOLO(MODEL_PATH)


# -----------------------------
# Food DB
# -----------------------------
FOODS = {
    "chappathi":{"density":0.95,"kcal_g":2.7,"nutrients":{"protein":9,"fat":3,"carbs":45}},
    "dosa":{"density":0.95,"kcal_g":2.5,"nutrients":{"protein":6,"fat":4,"carbs":40}},
    "idli":{"density":0.95,"kcal_g":1.5,"nutrients":{"protein":4,"fat":1,"carbs":28}},
    "puttu":{"density":0.95,"kcal_g":1.9,"nutrients":{"protein":4,"fat":2,"carbs":35}},
    "chutney":{"density":1.0,"kcal_g":1.2,"nutrients":{"protein":2,"fat":5,"carbs":8}},
    "sambar":{"density":1.0,"kcal_g":0.9,"nutrients":{"protein":3,"fat":2,"carbs":10}},
    "chicken_curry":{"density":1.1,"kcal_g":2.4,"nutrients":{"protein":20,"fat":15,"carbs":5}},
    "gulabjamun":{"density":1.0,"kcal_g":3.5,"nutrients":{"protein":4,"fat":10,"carbs":55}}
}


# -----------------------------
# UTIL FUNCTIONS
# -----------------------------
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return {}
    return {} if "user" in file else []


def save_history(data):
    history = load_json(HISTORY_FILE)

    history.append({
        "food": data["food"],
        "volume": float(data["volume"]),
        "calories": float(data["calories"]),
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# -----------------------------
# Volume
# -----------------------------
def estimate_volume(image_path, bbox):
    image = cv2.imread(image_path)
    if image is None:
        return 50

    x1, y1, x2, y2 = map(int, bbox)
    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        crop = image

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 50

    area = max(cv2.contourArea(c) for c in contours)
    image_area = image.shape[0] * image.shape[1]

    plate_area = 490  # approx cm²
    return round((area / image_area) * plate_area * 2, 2)


# -----------------------------
# Calories
# -----------------------------
def estimate_calories(food, volume):
    if food not in FOODS:
        return None, None

    f = FOODS[food]
    mass = volume * f["density"]
    calories = mass * f["kcal_g"]

    nutrients = {
        k: round((mass / 100) * v, 2)
        for k, v in f["nutrients"].items()
    }

    return round(calories, 2), nutrients

# -----------------------------
# BMI CALCULATION
# -----------------------------
def calculate_bmi(weight, height_cm):
    try:
        height = float(height_cm) / 100
        weight = float(weight)

        if height <= 0:
            return None, None

        bmi = round(weight / (height * height), 1)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return bmi, category

    except:
        return None, None
# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/capture")
def capture():
    return render_template("capture.html")


# -----------------------------
# DETECT
# -----------------------------
@app.route("/detect", methods=["POST"])
def detect():
    upload_path = None
    captured = request.form.get("captured_image")

    if captured:
        img_data = base64.b64decode(captured.split(",")[1])
        filename = f"{uuid.uuid4().hex}.png"
        upload_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(upload_path, "wb") as f:
            f.write(img_data)

    elif "image" in request.files:
        file = request.files["image"]

        if file.filename == "":
            flash("No file selected")
            return redirect(url_for("capture"))

        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{filename}")
        file.save(upload_path)

    else:
        flash("No input provided")
        return redirect(url_for("capture"))

    try:
        results = model.predict(upload_path, conf=0.55)[0]

        foods = []
        total = 0

        if results.boxes:
            for box in results.boxes:

                name = model.names[int(box.cls[0])].lower()
                conf = float(box.conf[0])

                # 🚨 FIX WRONG DETECTION
                if conf < 0.55 or name not in FOODS:
                    continue
                if name not in FOODS:
                    name = "unknown_food"

                bbox = box.xyxy[0].tolist()
                vol = estimate_volume(upload_path, bbox)
                cal, nut = estimate_calories(name, vol)

                if cal:
                    total += cal

                    foods.append({
                        "food": name,
                        "volume": vol,
                        "calories": cal,
                        "nutrients": nut,
                        "confidence": round(conf, 2)
                    })

                    save_history({
                        "food": name,
                        "volume": vol,
                        "calories": cal
                    })

        # ❗ IF NOTHING DETECTED
        if not foods:
            foods.append({
                "food": "Unknown",
                "volume": "-",
                "calories": "Not Available",
                "nutrients": None
            })

        img = cv2.cvtColor(results.plot(), cv2.COLOR_RGB2BGR)

        result_file = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(RESULTS_DIR, result_file)
        cv2.imwrite(result_path, img)

        return render_template(
            "detect_result.html",
            result_image=url_for("static", filename=f"results/{result_file}"),
            foods=foods,
            total_calories=round(total, 2)
        )

    except Exception as e:
        flash(str(e))
        return redirect(url_for("capture"))


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    history = load_json(HISTORY_FILE)
    user = load_json(USER_FILE)

    data = defaultdict(float)

    # 📊 Group calories by date
    for h in history:
        try:
            data[h["date"]] += float(h["calories"])
        except:
            continue

    sorted_data = dict(sorted(data.items()))
    labels = list(sorted_data.keys())
    values = list(sorted_data.values())

    # 🔥 TODAY CALORIES
    today_date = datetime.now().strftime("%Y-%m-%d")
    today = sum(
        float(h["calories"])
        for h in history
        if h["date"] == today_date
    )

    daily_limit = int(user.get("goal", 2000))

    # =============================
    # 🔥 ADD THIS (BMI CONNECTION)
    # =============================

    bmi, bmi_category = calculate_bmi(
        user.get("weight"),
        user.get("height")
    )

    # =============================
    # 💡 SMART HEALTH TIPS
    # =============================

    tips = []

    if today == 0:
        tips.append("Start your day with a healthy meal 🍽️")

    if today > daily_limit:
        tips.append("You exceeded your calorie limit ⚠️")

    if bmi:
        if bmi < 18.5:
            tips.append("You are underweight — eat more nutritious food 🥗")
        elif bmi > 25:
            tips.append("Try regular exercise and balanced meals 🏃")

    if not tips:
        tips = [
            "Drink more water 💧",
            "Eat fruits daily 🍎",
            "Sleep well 😴"
        ]

    return render_template(
        "dashboard.html",
        labels=labels,
        values=values,
        today=round(today, 2),
        daily_limit=daily_limit,
        bmi=bmi,                    # ✅ NEW
        bmi_category=bmi_category, # ✅ NEW
        tips=tips
    )
# -----------------------------
# HISTORY
# -----------------------------
@app.route("/history")
def history():
    return render_template("history.html", history=load_json(HISTORY_FILE))


# -----------------------------
# REPORT
# -----------------------------
@app.route("/report")
def report():
    history = load_json(HISTORY_FILE)

    data = defaultdict(float)
    for h in history:
        try:
            data[h["date"]] += float(h["calories"])
        except:
            continue

    labels = list(data.keys())
    values = list(data.values())

    total = sum(values)
    avg = round(total / len(values), 2) if values else 0

    return render_template(
        "report.html",
        labels=labels,
        values=values,
        total_foods=len(history),
        total_calories=round(total, 2),
        avg_calories=avg
    )


# -----------------------------
# PDF
# -----------------------------
@app.route("/download_report")
def download_report():
    history = load_json(HISTORY_FILE)

    file_path = os.path.join(DATA_DIR, "report.pdf")
    c = canvas.Canvas(file_path)

    y = 800
    c.drawString(200, 820, "FoodAI Report")

    for h in history:
        c.drawString(100, y, f"{h['date']} - {h['food']} - {h['calories']} kcal")
        y -= 20

    c.save()

    return send_file(file_path, as_attachment=True)


# -----------------------------
# PROFILE
# -----------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = load_json(USER_FILE)

    bmi = None
    bmi_category = None
    bmr = None
    daily_limit = None

    if request.method == "POST":
        user = dict(request.form)

        # 🔥 CALCULATE BMI
        weight = user.get("weight")
        height = user.get("height")

        bmi, bmi_category = calculate_bmi(weight, height)

        # 🔥 BMR CALCULATION (Mifflin-St Jeor)
        try:
            age = int(user.get("age", 25))
            weight = float(weight)
            height = float(height)

            if user.get("gender") == "male":
                bmr = 10*weight + 6.25*height - 5*age + 5
            else:
                bmr = 10*weight + 6.25*height - 5*age - 161

            # 🔥 ACTIVITY MULTIPLIER
            activity_map = {
                "sedentary": 1.2,
                "light": 1.375,
                "moderate": 1.55,
                "active": 1.725,
                "very_active": 1.9
            }

            multiplier = activity_map.get(user.get("activity"), 1.2)
            daily_limit = int(bmr * multiplier)

            user["goal"] = daily_limit  # auto update goal

        except:
            bmr = None
            daily_limit = None

        # SAVE USER
        with open(USER_FILE, "w") as f:
            json.dump(user, f, indent=2)

        flash("Profile updated with BMI & calorie goal 🎯")
        return redirect(url_for("profile"))

    # 🔥 LOAD BMI IF USER EXISTS
    if user:
        bmi, bmi_category = calculate_bmi(
            user.get("weight"),
            user.get("height")
        )

        # Recalculate BMR for display
        try:
            age = int(user.get("age", 25))
            weight = float(user.get("weight", 60))
            height = float(user.get("height", 165))

            if user.get("gender") == "male":
                bmr = 10*weight + 6.25*height - 5*age + 5
            else:
                bmr = 10*weight + 6.25*height - 5*age - 161

            activity_map = {
                "sedentary": 1.2,
                "light": 1.375,
                "moderate": 1.55,
                "active": 1.725,
                "very_active": 1.9
            }

            multiplier = activity_map.get(user.get("activity"), 1.2)
            daily_limit = int(bmr * multiplier)

        except:
            pass

    return render_template(
        "profile.html",
        user=user,
        bmi=bmi,
        bmi_category=bmi_category,
        bmr=round(bmr, 2) if bmr else None,
        daily_limit=daily_limit
    )
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
