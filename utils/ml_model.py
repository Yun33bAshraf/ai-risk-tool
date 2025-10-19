"""
Enhanced ML Model Module with Comprehensive Metrics
Supports multiple algorithms and detailed evaluation
Aligned with proposal requirements for academic rigor
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
    brier_score_loss, average_precision_score
)
import joblib
import os

MODEL_PATH = "models/risk_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"
FEATURES_PATH = "models/feature_names.pkl"

os.makedirs("models", exist_ok=True)


def calculate_comprehensive_metrics(y_true, y_pred, y_pred_proba, class_names):
    """
    Calculate comprehensive evaluation metrics
    Returns dict with all metrics required by proposal
    """
    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )
    
    # Brier score (calibration)
    brier = None
    if y_pred_proba is not None:
        try:
            n_classes = len(class_names)
            y_true_binary = np.zeros((len(y_true), n_classes))
            for i, label in enumerate(y_true):
                y_true_binary[i, label] = 1
            brier = np.mean([brier_score_loss(y_true_binary[:, i], y_pred_proba[:, i]) 
                           for i in range(n_classes)])
        except:
            brier = None
    
    # PR-AUC
    pr_auc = None
    if y_pred_proba is not None:
        try:
            pr_auc = average_precision_score(
                pd.get_dummies(y_true).values,
                y_pred_proba,
                average='weighted'
            )
        except:
            pr_auc = None
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'brier_score': brier,
        'pr_auc': pr_auc,
        'confusion_matrix': cm.tolist(),
        'per_class_metrics': {
            'precision': precision_per_class.tolist(),
            'recall': recall_per_class.tolist(),
            'f1': f1_per_class.tolist(),
            'support': support.tolist()
        }
    }


def train_and_predict(uploaded_file_path, model_type='auto'):
    """
    Enhanced prediction with comprehensive metrics
    Supports pre-trained model or trains new one with full evaluation
    
    Args:
        uploaded_file_path: Path to Excel file with risk data
        model_type: 'auto' to use saved model, or specify algorithm name
    
    Returns:
        Dict with predictions, metrics, and visualizations
    """
    df = pd.read_excel(uploaded_file_path)

    # Define feature columns (flexible handling)
    potential_features = [
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount"
    ]
    
    # Check which features are available
    available_features = [col for col in potential_features if col in df.columns]
    
    if len(available_features) < 2:
        raise ValueError(f"Need at least Likelihood and Impact columns. Found: {df.columns.tolist()}")
    
    # Check for target column
    if "RiskLevel" not in df.columns:
        raise ValueError("Missing required column: RiskLevel")
    
    # Prepare features and target
    X = df[available_features]
    y = df["RiskLevel"]

    # Try loading pre-trained model
    if model_type == 'auto' and os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        
        # Load feature names if available
        if os.path.exists(FEATURES_PATH):
            saved_features = joblib.load(FEATURES_PATH)
            # Ensure feature compatibility
            if set(saved_features) != set(available_features):
                print(f"⚠️ Warning: Feature mismatch. Training new model...")
                model = None
        
        if model is not None:
            retrained = False
            print("✅ Loaded existing trained model.")
        else:
            retrained = True
    else:
        retrained = True

    # Train new model if needed
    if retrained:
        print("⚙️ Training new model using uploaded file...")
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data for evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train model (Random Forest as default best model)
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(model, MODEL_PATH)
        joblib.dump(le, ENCODER_PATH)
        joblib.dump(available_features, FEATURES_PATH)
        
        print(f"✅ Model trained and saved")

    # Predict for all uploaded data
    y_encoded = le.transform(y)
    preds_encoded = model.predict(X)
    preds = le.inverse_transform(preds_encoded)
    
    # Get probabilities
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)
        confidences = [f"{max(prob) * 100:.1f}%" for prob in probs]
    else:
        probs = None
        confidences = ["N/A"] * len(preds)

    # Add predictions to dataframe
    df["PredictedRisk"] = preds
    df["Confidence"] = confidences
    df["ActualRisk"] = df["RiskLevel"]

    # Calculate comprehensive metrics
    metrics = calculate_comprehensive_metrics(
        y_encoded, preds_encoded, probs, le.classes_
    )
    
    # Get feature importance if available
    feature_importance = None
    if hasattr(model, 'feature_importances_'):
        feature_importance = dict(zip(available_features, model.feature_importances_.tolist()))

    # Prepare detailed results
    results = {
        "accuracy": round(metrics['accuracy'] * 100, 2),
        "precision": round(metrics['precision'] * 100, 2),
        "recall": round(metrics['recall'] * 100, 2),
        "f1_score": round(metrics['f1'] * 100, 2),
        "brier_score": round(metrics['brier_score'], 4) if metrics['brier_score'] else None,
        "pr_auc": round(metrics['pr_auc'], 4) if metrics['pr_auc'] else None,
        "confusion_matrix": metrics['confusion_matrix'],
        "class_names": le.classes_.tolist(),
        "feature_importance": feature_importance,
        "retrained": retrained,
        "model_type": model.__class__.__name__,
        "predictions": df[[
            "Likelihood", "Impact", "PredictedRisk", "Confidence", "ActualRisk"
        ]].to_dict(orient="records"),
        "per_class_metrics": {
            class_name: {
                'precision': round(metrics['per_class_metrics']['precision'][i] * 100, 2),
                'recall': round(metrics['per_class_metrics']['recall'][i] * 100, 2),
                'f1': round(metrics['per_class_metrics']['f1'][i] * 100, 2),
                'support': int(metrics['per_class_metrics']['support'][i])
            }
            for i, class_name in enumerate(le.classes_)
        }
    }

    return results


def get_model_info():
    """
    Get information about the currently saved model
    """
    if not os.path.exists(MODEL_PATH):
        return None
    
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH) if os.path.exists(ENCODER_PATH) else None
    features = joblib.load(FEATURES_PATH) if os.path.exists(FEATURES_PATH) else None
    
    return {
        'model_type': model.__class__.__name__,
        'classes': le.classes_.tolist() if le else None,
        'features': features,
        'n_features': len(features) if features else None
    }
