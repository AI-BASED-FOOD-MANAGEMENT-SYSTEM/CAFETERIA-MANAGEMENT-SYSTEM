import pandas as pd
import joblib
import os

# Load trained attendance model
model_path = os.path.join(os.path.dirname(__file__), "../../attendance_model.pkl")
model = joblib.load(model_path)

# -----------------------------
# FUNCTION FOR LIVE PREDICTION
# -----------------------------

def predict_attendance(day, meal_type, food_item, popularity_index):
    
    # Create input dictionary
    input_data = {
        "Day_of_Week": [day],
        "Meal_Type": [meal_type],
        "Food_Item": [food_item],
        "Popularity_Index": [popularity_index]
    }
    
    # Convert to DataFrame
    input_df = pd.DataFrame(input_data)
    
    # One-hot encode like training
    input_df = pd.get_dummies(input_df)
    
    # Align with training features
    model_features = model.feature_names_in_
    input_df = input_df.reindex(columns=model_features, fill_value=0)
    
    # Predict attendance
    predicted_students = model.predict(input_df)[0]
    
    return round(predicted_students)


# -----------------------------
# PORTION + RISK CALCULATION
# -----------------------------

def calculate_serving_strategy(predicted_students):
    
    buffer_percentage = 0.07  # 7% safety buffer
    
    suggested_portions = int(predicted_students * (1 + buffer_percentage))
    
    if buffer_percentage <= 0.05:
        risk = "Low"
    elif buffer_percentage <= 0.10:
        risk = "Medium"
    else:
        risk = "High"
    
    return suggested_portions, risk


# -----------------------------
# TEST EXAMPLE
# -----------------------------

if __name__ == "__main__":
    
    print("\n" + "="*50)
    print("FOOD DEMAND PREDICTION SYSTEM")
    print("="*50 + "\n")
    
    # Get user input
    day = input("Enter Day of Week (e.g., Monday, Tuesday, etc.): ").strip()
    meal_type = input("Enter Meal Type (e.g., Lunch, Supper, Breakfast): ").strip()
    food_item = input("Enter Food Item (e.g., Rice, Garri, Bread & Egg, etc.): ").strip()
    
    try:
        popularity_index = float(input("Enter Popularity Index (0.0 - 1.0): ").strip())
        if not (0 <= popularity_index <= 1):
            print("⚠️ Popularity Index should be between 0.0 and 1.0. Using 0.5 as default.")
            popularity_index = 0.5
    except ValueError:
        print("⚠️ Invalid input. Using default popularity index 0.5.")
        popularity_index = 0.5
    
    print("\n" + "-"*50)
    print("Processing...")
    print("-"*50 + "\n")
    
    # Make prediction
    predicted_students = predict_attendance(
        day=day,
        meal_type=meal_type,
        food_item=food_item,
        popularity_index=popularity_index
    )
    
    # Calculate serving strategy
    portions, risk = calculate_serving_strategy(predicted_students)
    
    # Display results
    print("📊 PREDICTION RESULTS:")
    print("-"*50)
    print(f"Day:                   {day}")
    print(f"Meal Type:             {meal_type}")
    print(f"Food Item:             {food_item}")
    print(f"Popularity Index:      {popularity_index}")
    print("-"*50)
    print(f"Predicted Students:    {predicted_students}")
    print(f"Suggested Portions:    {portions}")
    print(f"Waste Risk Level:      {risk}")
    print("="*50 + "\n")
