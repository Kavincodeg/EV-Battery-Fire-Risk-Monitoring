import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load dataset
data = pd.read_csv("data/battery_metadata.csv")

# Keep only required columns
data = data[["ambient_temperature", "Capacity"]]

# Convert to numeric (force errors to NaN)
data["ambient_temperature"] = pd.to_numeric(data["ambient_temperature"], errors="coerce")
data["Capacity"] = pd.to_numeric(data["Capacity"], errors="coerce")

# Remove rows with NaN
data = data.dropna()

# Features and target
X = data[["ambient_temperature"]]
y = data["Capacity"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("Battery Degradation Model Trained Successfully")
print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

# Save model
joblib.dump(model, "models/degradation_model.pkl")
