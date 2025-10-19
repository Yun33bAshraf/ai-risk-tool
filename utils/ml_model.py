import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

MODEL_PATH = "models/risk_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"

os.makedirs("models", exist_ok=True)

def train_and_predict(uploaded_file_path):
    """
    Uses pre-trained model if available.
    Otherwise trains a new model using the uploaded Excel file
    and returns predictions + accuracy report.
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score
    import joblib
    import os

    MODEL_PATH = "models/risk_model.pkl"
    ENCODER_PATH = "models/label_encoder.pkl"
    os.makedirs("models", exist_ok=True)

    # Load uploaded Excel file as dataset
    df = pd.read_excel(uploaded_file_path)

    # Ensure required columns exist
    required_cols = [
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount", "RiskLevel"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Prepare features and target
    X = df[[
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount"
    ]]
    y = df["RiskLevel"]

    # Try loading pre-trained model
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        print("✅ Loaded existing trained model.")
        retrained = False
    else:
        # Train new model
        print("⚙️ No model found — training a new one using uploaded file...")
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(le, ENCODER_PATH)
        retrained = True

    # Predict for uploaded data
    preds_encoded = model.predict(X)
    preds = le.inverse_transform(preds_encoded)

    # Compute confidence
    confidences = [f"{max(prob) * 100:.1f}%" for prob in model.predict_proba(X)]
    df["PredictedRisk"] = preds
    df["Confidence"] = confidences

    # If retrained, compute accuracy; else mark as N/A
    accuracy = 0.0
    if retrained:
        from sklearn.metrics import accuracy_score
        y_encoded = le.transform(y)
        accuracy = accuracy_score(y_encoded, preds_encoded)

    # Prepare result dict
    results = {
        "accuracy": round(accuracy * 100, 2) if retrained else "N/A (used saved model)",
        "predictions": df[[
            "Likelihood", "Impact", "PredictedRisk", "Confidence", "RiskLevel"
        ]].to_dict(orient="records"),
    }

    return results