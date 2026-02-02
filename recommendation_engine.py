import json

with open("hindi_diseases.json", encoding="utf-8") as f:
    HINDI_DB = json.load(f)

with open("marathi_diseases.json", encoding="utf-8") as f:
    MARATHI_DB = json.load(f)


def normalize_disease_name(disease):
    return disease.lower().replace("wheat_", "").replace("rice_", "")

def is_unidentified(disease, confidence, threshold=0.6):
    if disease is None:
        return True
    if disease.lower() in ["unknown", "unidentified"]:
        return True
    if confidence < threshold:
        return True
    return False

def unidentified_response(language="hindi"):
    if language == "marathi":
        return {
            "Message": "रोग स्पष्ट ओळखता आला नाही.",
            "Advice": [
                "सध्या औषध फवारणी करू नका",
                "पिकावर लक्ष ठेवा",
                "स्वच्छ फोटो पुन्हा काढा"
            ]
        }

    return {
        "Message": "रोग की स्पष्ट पहचान नहीं हो पाई है।",
        "Advice": [
            "अभी दवा का छिड़काव न करें",
            "फसल की निगरानी करें",
            "स्पष्ट फोटो दोबारा लें"
        ]
    }


def get_farmer_recommendation(crop, disease, confidence, language="hindi"):
    if is_unidentified(disease, confidence):
        return unidentified_response(language)

    crop = crop.lower()
    disease_key = normalize_disease_name(disease)

    db = HINDI_DB if language == "hindi" else MARATHI_DB

    crop_data = db.get(crop)
    if not crop_data:
        return unidentified_response(language)

    disease_data = crop_data.get(disease_key)
    if not disease_data:
        return unidentified_response(language)

    response = {
        "Crop": disease_data.get("crop"),
        "Disease": disease_data.get("disease_name"),
        "Identification": disease_data.get("identification", []),
        "Treatment": disease_data.get("treatment", [])
    }

    if language == "hindi" and "causes" in disease_data:
        response["Causes"] = disease_data["causes"]

    return response
