#!/usr/bin/env python3
"""
Inspect and test the pickled model `food_demand_model.pkl`.

Run:
    python scripts\inspect_and_predict.py
"""
import os
import joblib
import pandas as pd


def main():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "food_demand_model.pkl"))
    print("Loading model from:", model_path)
    model = joblib.load(model_path)

    print("sklearn version stored in model:", getattr(model, "_sklearn_version", "unknown"))
    features = list(getattr(model, "feature_names_in_", []))
    print("feature_names_in_:", features)
    print("coef_ shape:", getattr(model, "coef_", None).shape if hasattr(model, "coef_") else None)
    print("intercept_:", getattr(model, "intercept_", None))

    if not features:
        print("No feature names found; cannot build example input.")
        return

    # Build an example input row using the model's feature names.
    row = {f: 0 for f in features}
    for f in features:
        if "Expected" in f:
            row[f] = 120
        elif "Popularity" in f:
            row[f] = 0.7
        elif f.startswith("Day_of_Week_"):
            row[f] = 1 if "Monday" in f else 0
        elif f.startswith("Meal_Type_"):
            row[f] = 1 if "Lunch" in f else 0
        elif f.startswith("Food_Item_"):
            # prefer common staples if present
            if any(x in f for x in ("Rice", "Garri", "Bread", "Yam")):
                row[f] = 1
            else:
                row[f] = 0

    X = pd.DataFrame([row], columns=features)
    print("Example input:", X.to_dict(orient="records")[0])
    pred = model.predict(X)
    print("Prediction:", float(pred[0]))


if __name__ == "__main__":
    main()
