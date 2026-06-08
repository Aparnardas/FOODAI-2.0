import numpy as np
import tensorflow as tf
import os

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image


# Load pretrained feature extractor
backbone = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

MODEL_PATH = "model/food_gate.npz"


# Load logistic regression weights
if os.path.exists(MODEL_PATH):

    data = np.load(MODEL_PATH, allow_pickle=True)

    clf = data["clf"].item()

else:

    # fallback classifier
    from sklearn.linear_model import LogisticRegression

    clf = LogisticRegression()

    clf.coef_ = np.zeros((1, 1280))

    clf.intercept_ = np.zeros(1)

    clf.classes_ = np.array([0, 1])  # 0 = nonfood, 1 = food


def extract_features(img_path):

    img = image.load_img(img_path, target_size=(224, 224))

    x = image.img_to_array(img)

    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x.astype(np.float32))

    features = backbone.predict(x, verbose=0)

    return features


def is_food(img_path, threshold=0.45):

    """
    Returns
    -------
    is_food : bool
    probability : float
    """

    f = extract_features(img_path)

    z = f @ clf.coef_.T + clf.intercept_

    p = 1 / (1 + np.exp(-z))

    p = float(p[0][0])

    return p >= threshold, p
