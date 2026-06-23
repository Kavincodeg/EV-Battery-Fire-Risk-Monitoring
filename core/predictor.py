import joblib

# Load trained models
degradation_model = joblib.load("models/degradation_model.pkl")
fire_risk_model = joblib.load("models/fire_risk_model.pkl")

def predict_capacity(temperature):
    """
    Predict battery capacity based on temperature
    """
    return float(degradation_model.predict([[temperature]])[0])

def predict_fire_risk(temperature, capacity):
    """
    Predict fire risk level:
    0 = Safe
    1 = Warning
    2 = Critical
    """
    return int(fire_risk_model.predict([[temperature, capacity]])[0])
