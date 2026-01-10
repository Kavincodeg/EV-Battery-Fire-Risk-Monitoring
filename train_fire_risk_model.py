import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
data = pd.read_csv("data/battery_metadata.csv")

# Keep only required columns
data = data[["ambient_temperature", "Capacity"]]

# Convert to numeric
data["ambient_temperature"] = pd.to_numeric(data["ambient_temperature"], errors="coerce")
data["Capacity"] = pd.to_numeric(data["Capacity"], errors="coerce")

# Remove NaN rows
data = data.dropna()

# Fire risk labeling
def classify_risk(row):
    if row["ambient_temperature"] >= 45 and row["Capacity"] <= 1.6:
        return 2  # Critical
    elif row["ambient_temperature"] >= 35:
        return 1  # Warning
    else:
        return 0  # Safe

data["FireRisk"] = data.apply(classify_risk, axis=1)

# Features and target
X = data[["ambient_temperature", "Capacity"]]
y = data["FireRisk"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("Fire Risk Detection Model Trained Successfully")
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, "models/fire_risk_model.pkl")
