from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
import os

# database helper
from model.models.db_utils import get_engine


def load_data():
    """Load training data from Postgres. If the table is empty or doesn't exist,
    fall back to the Excel sheet and populate the database.
    """
    engine = get_engine()
    try:
        df = pd.read_sql("SELECT * FROM historical_data", engine)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        # first‑time startup, read from Excel and push to database
        data_path = os.path.join(os.path.dirname(__file__), "../data/raw/Structured_Operational_Food_Data_v4_Cleaned.xlsx")
        df = pd.read_excel(data_path)
        # create table automatically with pandas
        df.to_sql("historical_data", engine, if_exists="replace", index=False)
    return df

# Load data
data = load_data()

# Target
y = data["Expected_Students"]

# Features
X = data.drop(columns=["Expected_Students"])

# One-hot encode
X = pd.get_dummies(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🚀 Random Forest Model
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("Model Retrained Successfully ✅")
print("MAE:", round(mae, 2))
print("R²:", round(r2, 3))

# Save
model_save_path = os.path.join(os.path.dirname(__file__), "../../attendance_model.pkl")
joblib.dump(model, model_save_path)