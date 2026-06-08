# FOODAI 2.0 🍽️

A Flask-based intelligent web application that detects Kerala regional food items from images and provides real-time calorie estimation, nutritional tracking, and personalized health insights.

##  Features

- **Kerala Food Detection** — Recognizes 8 regional food classes using a custom-trained YOLO model
- **Real-time Calorie Estimation** — Estimates calorie content of multiple food items from a single 2D image
- **Custom Dataset** — Dataset built specifically for Kerala regional food, labelled using MakeSense AI
- **History & Reports** — Stores meal history and generates personalized nutritional reports
- **BMI Calculator** — Built-in BMI calculator for personalized health tracking
- **Personalized Data** — Tracks and stores user-specific dietary data over time

# Supported Food Classes

| Food Item | Category |
|-----------|----------|
| Dosa | Breakfast |
| Idli | Breakfast |
| Sambar | Side Dish |
| Chutney | Side Dish |
| Puttu | Breakfast |
| Chappathi | Main Course |
| Chicken Curry | Main Course |
| Gulab Jamun | Dessert |

##  Technologies Used

- **Backend:** Python, Flask
- **ML Model:** YOLOv8 (custom trained — `best.pt`)
- **Dataset:** Custom Kerala food dataset (8 classes, labelled with MakeSense AI)
- **Image Processing:** OpenCV
- **Frontend:** HTML, CSS
- **Environment:** Python Virtual Environment (foodenv)

##  How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Or use the package script
bash package.sh

# Run the app
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Note

The trained YOLO model file (`best.pt`) is not included in this repo due to file size.  
The model was trained on a custom Kerala regional food dataset using YOLOv8.

##  Developed By

Aparna R Das — B.Tech Computer Science, MG College of Engineering
