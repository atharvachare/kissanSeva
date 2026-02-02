from test_model import predict
from recommendation_engine import get_farmer_recommendation


def pretty_print_recommendation(data):
    print("\n FARMER RECOMMENDATION")
    print("=" * 40)

    # Case: Unidentified / uncertain disease
    if "Message" in data:
        print(data["Message"])
        for tip in data.get("Advice", []):
            print(f"• {tip}")
        return

    # Crop & Disease
    print(f"\nफसल : {data.get('Crop')}")
    print(f"रोग  : {data.get('Disease')}\n")

    # Identification
    if "Identification" in data:
        print(" रोग की पहचान:")
        for item in data["Identification"]:
            print(f"• {item}")
        print()

    # Causes (Hindi only – optional)
    if "Causes" in data:
        print(" रोग के कारण:")
        for item in data["Causes"]:
            print(f"• {item}")
        print()

    # Treatment
    if "Treatment" in data:
        print(" उपचार:")
        for item in data["Treatment"]:
            print(f"• {item}")
        print()


result = predict("test_images/000022.jpg")

print("\nMODEL OUTPUT:")
print(result)

advice = get_farmer_recommendation(
    crop=result["Crop"],
    disease=result["Disease"],
    confidence=result["Confidence"],
    language="hindi"   # change to "marathi" if needed
)

pretty_print_recommendation(advice)
