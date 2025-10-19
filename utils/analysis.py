"""
Enhanced Analysis Module for AI Risk Analysis Tool
Includes comprehensive visualizations and trend analysis
Aligned with proposal requirements for clear communication
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
import base64
import joblib
from utils.visualization import (
    generate_risk_heatmap,
    generate_priority_matrix,
    generate_risk_distribution,
    generate_owner_distribution,
    generate_category_distribution,
    generate_feature_importance
)

MODEL_PATH = "models/risk_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"
FEATURES_PATH = "models/feature_names.pkl"


def analyze_risks(df):
    """
    Comprehensive risk analysis with multiple visualizations
    Returns analysis results with heatmaps, distributions, and statistics
    """
    # Ensure minimum required columns exist
    if "Likelihood" not in df.columns or "Impact" not in df.columns:
        raise ValueError("Missing required columns: Likelihood and/or Impact")

    # Calculate basic risk score (manual baseline)
    df["RiskScore"] = df["Likelihood"] * df["Impact"]
    
    # Categorize based on manual score
    df["ManualRiskCategory"] = df["RiskScore"].apply(categorize_risk)

    # Try to load and use model for predictions
    potential_features = [
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount"
    ]
    
    available_features = [col for col in potential_features if col in df.columns]
    
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            le = joblib.load(ENCODER_PATH)
            
            # Load saved feature names
            if os.path.exists(FEATURES_PATH):
                saved_features = joblib.load(FEATURES_PATH)
                # Use saved features if they match
                if set(saved_features).issubset(set(df.columns)):
                    available_features = saved_features
            
            # Predict
            features = df[available_features]
            preds_encoded = model.predict(features)
            preds = le.inverse_transform(preds_encoded)
            df["PredictedRiskLevel"] = preds
            
            # Get confidence if model supports probabilities
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(features)
                df["PredictionConfidence"] = [f"{max(prob)*100:.1f}%" for prob in probs]
            
            model_used = True
        except Exception as e:
            print(f"⚠️ Warning: Could not use model - {str(e)}")
            df["PredictedRiskLevel"] = df["ManualRiskCategory"]
            model_used = False
    else:
        df["PredictedRiskLevel"] = df["ManualRiskCategory"]
        model_used = False

    # Summary statistics
    summary_raw = df["PredictedRiskLevel"].value_counts().to_dict()
    summary = {k.lower() if isinstance(k, str) else k: v for k, v in summary_raw.items()}
    
    manual_summary = df["ManualRiskCategory"].value_counts().to_dict()
    manual_summary = {k.lower(): v for k, v in manual_summary.items()}

    # Generate visualizations
    visualizations = {}
    
    # 1. Risk heatmap
    try:
        visualizations['heatmap'] = generate_risk_heatmap(df)
    except Exception as e:
        print(f"Warning: Could not generate heatmap - {e}")
        visualizations['heatmap'] = None
    
    # 2. Priority matrix
    try:
        visualizations['priority_matrix'] = generate_priority_matrix(df)
    except Exception as e:
        print(f"Warning: Could not generate priority matrix - {e}")
        visualizations['priority_matrix'] = None
    
    # 3. Risk distribution comparison
    try:
        visualizations['distribution'] = generate_risk_distribution(df)
    except Exception as e:
        print(f"Warning: Could not generate distribution - {e}")
        visualizations['distribution'] = None
    
    # 4. Owner distribution (if available)
    if 'Owner' in df.columns:
        try:
            visualizations['owner_dist'] = generate_owner_distribution(df)
        except Exception as e:
            print(f"Warning: Could not generate owner distribution - {e}")
            visualizations['owner_dist'] = None
    
    # 5. Category distribution (if available)
    if 'Category' in df.columns:
        try:
            visualizations['category_dist'] = generate_category_distribution(df)
        except Exception as e:
            print(f"Warning: Could not generate category distribution - {e}")
            visualizations['category_dist'] = None
    
    # 6. Feature importance (if model exists)
    if model_used and os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            if hasattr(model, 'feature_importances_'):
                visualizations['feature_importance'] = generate_feature_importance(
                    model, available_features
                )
        except Exception as e:
            print(f"Warning: Could not generate feature importance - {e}")
            visualizations['feature_importance'] = None

    # Calculate additional statistics
    stats = {
        'total_risks': len(df),
        'high_risk_count': (df['PredictedRiskLevel'] == 'High').sum(),
        'medium_risk_count': (df['PredictedRiskLevel'] == 'Medium').sum(),
        'low_risk_count': (df['PredictedRiskLevel'] == 'Low').sum(),
        'avg_likelihood': df['Likelihood'].mean(),
        'avg_impact': df['Impact'].mean(),
        'avg_risk_score': df['RiskScore'].mean(),
        'model_used': model_used
    }

    return {
        "summary": summary,
        "manual_summary": manual_summary,
        "data": df.to_dict(orient="records"),
        "visualizations": visualizations,
        "stats": stats
    }


def categorize_risk(score):
    """
    Categorize risk based on traditional likelihood × impact matrix
    Aligned with ISO 31000 and PMBOK frameworks
    """
    if score >= 12:  # High threshold (e.g., 3×4, 4×3, 4×4, 4×5, 5×4, 5×5)
        return 'High'
    elif score >= 6:  # Medium threshold
        return 'Medium'
    else:
        return 'Low'
