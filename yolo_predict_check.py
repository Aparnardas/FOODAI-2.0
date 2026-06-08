import os
from ultralytics import YOLO

# Paths
MODEL_PATH = "/home/mnasa/FoodAI2.0/model/food_yolo_best.pt"
INPUT_FOLDER = "/home/mnasa/Pictures/Gphotos/check"
OUTPUT_ROOT = "/home/mnasa/FoodAI2.0/logs"
OUTPUT_NAME = "yolo_predictions"  # subfolder name inside logs/

def main():
    # Make sure output folder exists
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    print(f"✅ Loading model from: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)

    print(f"✅ Reading images from: {INPUT_FOLDER}")
    if not os.path.isdir(INPUT_FOLDER):
        print("❌ Input folder not found!")
        return

    # Run YOLO on all images in the folder
    results = model.predict(
        source=INPUT_FOLDER,
        conf=0.3,
        save=True,
        project=OUTPUT_ROOT,
        name=OUTPUT_NAME,
        exist_ok=True,  # reuse folder if it already exists
    )

    print("\n✅ YOLO prediction finished!")
    print("📁 Output images saved in:")
    print(f"   {os.path.join(OUTPUT_ROOT, OUTPUT_NAME)}")

if __name__ == "__main__":
    main()

