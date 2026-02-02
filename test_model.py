import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.preprocessing import image

IMG_SIZE = (224, 224)
CROP_CONF_THRESHOLD = 0.75
DISEASE_CONF_THRESHOLD = 0.6

# =========================
# LOAD MODELS
# =========================
crop_model = tf.keras.models.load_model("crop_classifier.h5")
rice_model = tf.keras.models.load_model("rice_disease_model.h5")
wheat_model = tf.keras.models.load_model("wheat_disease_model.h5")

# =========================
# LOAD CLASS MAPS
# =========================
def load_map(path):
    with open(path) as f:
        data = json.load(f)
    return {int(v): k.capitalize() for k, v in data.items()}

crop_map = load_map("crop_classes.json")
rice_map = load_map("rice_classes.json")
wheat_map = load_map("wheat_classes.json")

# =========================
# IMAGE PREPROCESS
# =========================
def preprocess(img_path):
    img = image.load_img(img_path, target_size=IMG_SIZE)
    arr = image.img_to_array(img) / 255.0
    return np.expand_dims(arr, axis=0)

# =========================
# PREDICTION PIPELINE
# =========================
def predict(img_path):
    img = preprocess(img_path)

    crop_preds = crop_model.predict(img)
    crop_conf = float(np.max(crop_preds))
    crop_idx = int(np.argmax(crop_preds))
    crop = crop_map[crop_idx]

    if crop_conf < CROP_CONF_THRESHOLD:
        return {
            "Status": "Crop Uncertain",
            "Suggestions": {
                crop_map[i]: round(float(crop_preds[0][i]), 2)
                for i in range(len(crop_preds[0]))
            }
        }

    disease_model = rice_model if crop == "Rice" else wheat_model
    class_map = rice_map if crop == "Rice" else wheat_map

    disease_preds = disease_model.predict(img)
    disease_conf = float(np.max(disease_preds))
    disease_idx = int(np.argmax(disease_preds))

    if disease_conf < DISEASE_CONF_THRESHOLD:
        return {
            "Crop": crop,
            "Status": "Disease Uncertain",
            "Confidence": round(disease_conf, 2)
        }

    return {
        "Crop": crop,
        "Disease": class_map[disease_idx],
        "Confidence": round(disease_conf, 2)
    }


