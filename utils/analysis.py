import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
import base64
import joblib

MODEL_PATH = "models/risk_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"

def analyze_risks(df):
    # Ensure required columns exist
    required_cols = [
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df["RiskScore"] = df["Likelihood"] * df["Impact"]

    # Predict if model exists
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        features = df[required_cols]
        preds_encoded = model.predict(features)
        preds = le.inverse_transform(preds_encoded)
        df["PredictedRiskLevel"] = preds
    else:
        df["PredictedRiskLevel"] = "N/A (model not found)"

    # Summary
    summary_raw = df["PredictedRiskLevel"].value_counts().to_dict()
    summary = {k.lower(): v for k, v in summary_raw.items()}

    # Heatmap
    heatmap_base64 = generate_heatmap(df)

    return {
        "summary": summary,
        "data": df.to_dict(orient="records"),
        "heatmap": heatmap_base64
    }

def generate_heatmap(df):
    pivot = pd.pivot_table(
        df,
        values="RiskScore",
        index="Likelihood",
        columns="Impact",
        aggfunc="count",
        fill_value=0
    )

    plt.figure(figsize=(6, 5))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="RdYlGn_r", cbar_kws={'label': 'Number of Risks'})
    plt.title("Risk Heatmap (Likelihood × Impact)")
    plt.xlabel("Impact")
    plt.ylabel("Likelihood")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return img_base64
