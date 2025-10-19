"""
Comprehensive Model Training Script for AI Risk Analysis Tool
Implements multiple ML algorithms with full evaluation metrics
Supports: Random Forest, Decision Tree, SVM, AdaBoost
Includes: 5-fold cross-validation, feature importance, confusion matrix, calibration
Aligned with methodology from proposal (Abdelgadir et al., 2021; Al-Habaibeh et al., 2021)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, brier_score_loss,
    roc_auc_score, average_precision_score, make_scorer
)
import joblib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.preprocess import load_and_preprocess
from utils.visualization import (
    generate_confusion_matrix_plot, 
    generate_feature_importance,
    generate_model_comparison
)


def evaluate_model_comprehensive(model, X_train, X_test, y_train, y_test, class_names):
    """
    Comprehensive model evaluation with all required metrics
    Returns: dict with all evaluation results
    """
    # Train model
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
    
    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    # Precision, Recall, F1
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, average='weighted', zero_division=0
    )
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Brier Score (calibration) - for binary and multiclass
    brier = None
    if y_pred_proba is not None:
        try:
            # For multiclass, calculate average brier score
            n_classes = len(class_names)
            y_test_binary = np.zeros((len(y_test), n_classes))
            for i, label in enumerate(y_test):
                y_test_binary[i, label] = 1
            brier = np.mean([brier_score_loss(y_test_binary[:, i], y_pred_proba[:, i]) 
                           for i in range(n_classes)])
        except:
            brier = None
    
    # PR-AUC
    pr_auc = None
    if y_pred_proba is not None:
        try:
            pr_auc = average_precision_score(
                pd.get_dummies(y_test).values, 
                y_pred_proba, 
                average='weighted'
            )
        except:
            pr_auc = None
    
    # ROC-AUC for multiclass
    roc_auc = None
    if y_pred_proba is not None and len(class_names) > 2:
        try:
            roc_auc = roc_auc_score(
                pd.get_dummies(y_test).values,
                y_pred_proba,
                average='weighted',
                multi_class='ovr'
            )
        except:
            roc_auc = None
    
    return {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'brier_score': brier,
        'pr_auc': pr_auc,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'predictions': y_pred,
        'probabilities': y_pred_proba
    }


def cross_validate_model(model, X, y, cv=5):
    """
    Perform k-fold cross-validation
    Returns mean and std of key metrics
    """
    scoring = {
        'accuracy': 'accuracy',
        'precision': 'precision_weighted',
        'recall': 'recall_weighted',
        'f1': 'f1_weighted'
    }
    
    cv_results = cross_validate(
        model, X, y, cv=cv, scoring=scoring, 
        return_train_score=False, n_jobs=-1
    )
    
    return {
        'accuracy_mean': cv_results['test_accuracy'].mean(),
        'accuracy_std': cv_results['test_accuracy'].std(),
        'precision_mean': cv_results['test_precision'].mean(),
        'precision_std': cv_results['test_precision'].std(),
        'recall_mean': cv_results['test_recall'].mean(),
        'recall_std': cv_results['test_recall'].std(),
        'f1_mean': cv_results['test_f1'].mean(),
        'f1_std': cv_results['test_f1'].std(),
    }


def train_all_models(filepath, output_dir="models", balance=True):
    """
    Train all models and compare performance
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE MODEL TRAINING & EVALUATION")
    print("="*70)
    
    # Load and preprocess data
    print("\nLoading and preprocessing data...")
    X, y, feature_names, df_processed, preprocessor = load_and_preprocess(
        filepath, balance=balance
    )
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    class_names = le.classes_
    
    print(f"\n[OK] Data loaded: {len(X)} samples, {len(feature_names)} features")
    print(f"   Classes: {', '.join(class_names)}")
    
    # Determine appropriate test size based on dataset size
    n_classes = len(class_names)
    n_samples = len(X)
    
    # Calculate minimum test size needed for stratification
    min_test_size = n_classes  # At least 1 sample per class
    
    if n_samples < 20:
        # Small dataset: use larger test size to ensure stratification works
        test_size = max(min_test_size, int(n_samples * 0.3))
        print(f"\n[INFO] Small dataset detected ({n_samples} samples)")
        print(f"   Adjusting test size to {test_size} samples for proper stratification")
        
        # Check if we have enough samples for each class
        class_counts = pd.Series(y_encoded).value_counts()
        min_class_count = class_counts.min()
        
        if min_class_count < 2:
            print(f"\n[WARNING] Some classes have very few samples (min: {min_class_count})")
            print(f"   Disabling stratification to avoid errors")
            stratify_param = None
        else:
            stratify_param = y_encoded
    else:
        # Normal dataset: use 20% test size
        test_size = 0.2
        stratify_param = y_encoded
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=42, stratify=stratify_param
    )
    
    print(f"   Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Define models (following proposal: RF, DT, SVM, AdaBoost)
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=100, 
            max_depth=10,
            random_state=42, 
            n_jobs=-1
        ),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=10, 
            random_state=42
        ),
        'SVM': SVC(
            kernel='rbf', 
            probability=True, 
            random_state=42
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=50, 
            random_state=42
        )
    }
    
    # Train and evaluate all models
    results = {}
    
    print("\n" + "="*70)
    print("TRAINING MODELS")
    print("="*70)
    
    for model_name, model in models.items():
        print(f"\n{'-'*70}")
        print(f"{model_name}")
        print(f"{'-'*70}")
        
        # Evaluate on train/test split
        print("   Training and evaluating...")
        eval_results = evaluate_model_comprehensive(
            model, X_train, X_test, y_train, y_test, class_names
        )
        
        # Cross-validation
        print("   Performing 5-fold cross-validation...")
        cv_results = cross_validate_model(model, X, y_encoded, cv=5)
        
        # Store results
        results[model_name] = {
            **eval_results,
            'cv_results': cv_results
        }
        
        # Print results
        print(f"\n   Results:")
        print(f"      Accuracy:  {eval_results['accuracy']*100:.2f}%")
        print(f"      Precision: {eval_results['precision']*100:.2f}%")
        print(f"      Recall:    {eval_results['recall']*100:.2f}%")
        print(f"      F1-Score:  {eval_results['f1']*100:.2f}%")
        if eval_results['brier_score']:
            print(f"      Brier:     {eval_results['brier_score']:.4f}")
        if eval_results['pr_auc']:
            print(f"      PR-AUC:    {eval_results['pr_auc']:.4f}")
        
        print(f"\n   Cross-Validation (5-fold):")
        print(f"      Accuracy:  {cv_results['accuracy_mean']*100:.2f}% (±{cv_results['accuracy_std']*100:.2f}%)")
        print(f"      Precision: {cv_results['precision_mean']*100:.2f}% (±{cv_results['precision_std']*100:.2f}%)")
        print(f"      Recall:    {cv_results['recall_mean']*100:.2f}% (±{cv_results['recall_std']*100:.2f}%)")
        print(f"      F1-Score:  {cv_results['f1_mean']*100:.2f}% (±{cv_results['f1_std']*100:.2f}%)")
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['f1'])
    best_model = results[best_model_name]['model']
    
    print("\n" + "="*70)
    print(f"BEST MODEL: {best_model_name}")
    print(f"   F1-Score: {results[best_model_name]['f1']*100:.2f}%")
    print("="*70)
    
    # Save best model
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "risk_model.pkl")
    encoder_path = os.path.join(output_dir, "label_encoder.pkl")
    features_path = os.path.join(output_dir, "feature_names.pkl")
    
    joblib.dump(best_model, model_path)
    joblib.dump(le, encoder_path)
    joblib.dump(feature_names, features_path)
    
    print(f"\nSaved:")
    print(f"   Model:    {model_path}")
    print(f"   Encoder:  {encoder_path}")
    print(f"   Features: {features_path}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # Confusion matrix for best model
    cm_img = generate_confusion_matrix_plot(
        results[best_model_name]['confusion_matrix'],
        class_names
    )
    
    # Feature importance for best model
    feat_imp_img = generate_feature_importance(best_model, feature_names)
    
    # Model comparison
    comparison_data = {
        name: {
            'accuracy': res['accuracy'],
            'precision': res['precision'],
            'recall': res['recall'],
            'f1': res['f1']
        }
        for name, res in results.items()
    }
    comparison_img = generate_model_comparison(comparison_data)
    
    print("   [OK] Visualizations generated")
    
    # Summary report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    print("\nModel Performance Comparison:")
    print(f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
    print("-"*70)
    for name, res in results.items():
        print(f"{name:<20} {res['accuracy']*100:>10.2f}%  {res['precision']*100:>10.2f}%  "
              f"{res['recall']*100:>10.2f}%  {res['f1']*100:>10.2f}%")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70 + "\n")
    
    return results, best_model_name, le, feature_names


if __name__ == "__main__":
    # Default training file
    training_file = "uploads/risk_training_data.xlsx"
    
    if len(sys.argv) > 1:
        training_file = sys.argv[1]
    
    if not os.path.exists(training_file):
        print(f"[ERROR] Training file not found: {training_file}")
        print(f"   Please provide a valid Excel file path")
        sys.exit(1)
    
    # Train all models
    results, best_model, le, features = train_all_models(training_file)
    
    print("\n[SUCCESS] You can now use the trained model with the Flask app!")
    print("   Run: python app.py")
