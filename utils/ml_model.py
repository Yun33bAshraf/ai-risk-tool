"""
Enhanced ML Model Module with Comprehensive Metrics
Supports multiple algorithms and detailed evaluation
Aligned with proposal requirements for academic rigor
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, brier_score_loss, average_precision_score
)
import joblib
import os

MODEL_PATH = "models/risk_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"
FEATURES_PATH = "models/feature_names.pkl"

os.makedirs("models", exist_ok=True)


def calculate_comprehensive_metrics(y_true, y_pred, y_pred_proba, class_names):
    if len(y_true) == 0:
        return {
            'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0,
            'brier_score': None, 'pr_auc': None,
            'confusion_matrix': [],
            'per_class_metrics': {'precision': [], 'recall': [], 'f1': [], 'support': []}
        }

    accuracy = accuracy_score(y_true, y_pred)

    try:
        precision_pc, recall_pc, f1_pc, support_pc = precision_recall_fscore_support(
            y_true, y_pred, average=None, zero_division=0
        )
    except:
        precision_pc = recall_pc = f1_pc = support_pc = np.array([])

    try:
        precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
    except:
        precision_w = recall_w = f1_w = 0.0

    try:
        cm = confusion_matrix(y_true, y_pred)
        cm_list = cm.tolist() if cm.size > 0 else []
    except:
        cm_list = []

    brier = None
    if y_pred_proba is not None and len(class_names) > 1:
        try:
            y_bin = pd.get_dummies(y_true).reindex(columns=range(len(class_names)), fill_value=0).values
            brier = np.mean([
                brier_score_loss(y_bin[:, i], y_pred_proba[:, i])
                for i in range(len(class_names))
            ])
        except:
            brier = None

    pr_auc = None
    if y_pred_proba is not None and len(class_names) > 1:
        try:
            y_bin = pd.get_dummies(y_true).reindex(columns=class_names, fill_value=0)
            pr_auc = average_precision_score(y_bin, y_pred_proba, average='weighted')
        except:
            pr_auc = None

    return {
        'accuracy': accuracy,
        'precision': precision_w,
        'recall': recall_w,
        'f1': f1_w,
        'brier_score': brier,
        'pr_auc': pr_auc,
        'confusion_matrix': cm_list,
        'per_class_metrics': {
            'precision': precision_pc.tolist() if len(precision_pc) > 0 else [],
            'recall': recall_pc.tolist() if len(recall_pc) > 0 else [],
            'f1': f1_pc.tolist() if len(f1_pc) > 0 else [],
            'support': support_pc.tolist() if len(support_pc) > 0 else []
        }
    }


def train_and_predict(uploaded_file_path, model_type='auto'):
    df = pd.read_excel(uploaded_file_path)

    potential_features = [
        "Likelihood", "Impact", "RequirementComplexity",
        "AmbiguityScore", "CodeChurn", "ModuleComplexity", "RevisionCount"
    ]
    
    available_features = [col for col in potential_features if col in df.columns]
    
    if len(available_features) < 2:
        raise ValueError(f"Need at least Likelihood and Impact columns. Found: {df.columns.tolist()}")
    
    if "RiskLevel" not in df.columns:
        raise ValueError("Missing required column: RiskLevel")
    
    X = df[available_features]
    y = df["RiskLevel"]

    retrained = True
    eval_on_train = True

    if model_type == 'auto' and os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        
        if os.path.exists(FEATURES_PATH):
            saved_features = joblib.load(FEATURES_PATH)
            if set(saved_features) != set(available_features):
                print("Warning: Feature mismatch. Training new model...")
                model = None
        
        if model is not None:
            retrained = False
            print("Loaded existing trained model.")
        else:
            retrained = True
    else:
        retrained = True

    if retrained:
        print("Training new model using uploaded file...")
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        n_samples = len(y_encoded)
        n_classes = len(le.classes_)

        if n_samples < 30:
            print(f"Dataset too small ({n_samples} rows) → training on full data.")
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
            model.fit(X, y_encoded)
            eval_on_train = True
            X_train = X_test = X
            y_train = y_test = y_encoded
        else:
            min_test = max(0.2, n_classes / n_samples + 0.05)
            test_size = min(0.3, min_test)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded,
                test_size=test_size,
                random_state=42,
                stratify=y_encoded
            )

            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
            model.fit(X_train, y_train)
            eval_on_train = False

        joblib.dump(model, MODEL_PATH)
        joblib.dump(le, ENCODER_PATH)
        joblib.dump(available_features, FEATURES_PATH)
        print("Model trained and saved")
    else:
        eval_on_train = True
        print("Using loaded model → evaluating on full dataset")

    y_encoded = le.transform(y)
    preds_encoded = model.predict(X)
    preds = le.inverse_transform(preds_encoded)

    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)
        confidences = [f"{max(prob) * 100:.1f}%" for prob in probs]
    else:
        probs = None
        confidences = ["N/A"] * len(preds)

    df["PredictedRisk"] = preds
    df["Confidence"] = confidences
    df["ActualRisk"] = df["RiskLevel"]

    if eval_on_train:
        y_true_eval = y_encoded
        y_pred_eval = model.predict(X)
        y_proba_eval = model.predict_proba(X) if hasattr(model, "predict_proba") else None
    else:
        y_true_eval = y_test
        y_pred_eval = model.predict(X_test)
        y_proba_eval = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

    metrics = calculate_comprehensive_metrics(
        y_true_eval, y_pred_eval, y_proba_eval, le.classes_
    )

    feature_importance = None
    if hasattr(model, 'feature_importances_'):
        feature_importance = dict(zip(available_features, model.feature_importances_.tolist()))

    # Safe n_samples
    try:
        n_samples = len(y_encoded)
    except:
        n_samples = len(df)

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
        },
        "data_size_warning": n_samples < 30
    }

    return results


def get_model_info():
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