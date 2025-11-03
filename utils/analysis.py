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
    
    # Human-readable labels while retaining numeric values for calculations
    def _level_to_label(v):
        try:
            v = int(v)
        except Exception:
            return str(v)
        mapping = {1: 'Very Low', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Very High'}
        return mapping.get(v, str(v))
    
    # Categorize based on manual score
    df["ManualRiskCategory"] = df["RiskScore"].apply(categorize_risk)
    
    # Labels to display in UI
    df["LikelihoodLabel"] = df["Likelihood"].apply(_level_to_label)
    df["ImpactLabel"] = df["Impact"].apply(_level_to_label)
    df["RiskScoreLabel"] = df["ManualRiskCategory"]

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

    # --- AI Solution Recommendations -------------------------------------------------
    def _ai_recommendation_for_row(row):
        """Return short AI-driven solution and suggested tools based on description/category."""
        desc = str(row.get('Description', '')).lower()
        category = str(row.get('Category', '')).lower()

        def rec(solution, tools):
            return solution, ", ".join(tools)

        # Keyword-driven heuristics
        if any(k in desc for k in ["ambigu", "unclear", "confus"]) or category == "requirements":
            return rec(
                "Clarify scope; auto-generate acceptance criteria and test cases",
                ["ChatGPT/GPT-4", "Confluence/Jira AI", "GitHub Copilot Tests"]
            )

        if ("api" in desc and any(k in desc for k in ["fail", "load", "rate", "timeout"])) or category == "integration" or "external api" in desc:
            return rec(
                "Add retries/circuit breaker; AI-generated load tests and SLO monitors",
                ["k6 or Locust", "Gremlin (chaos)", "Datadog/New Relic AIOps"]
            )

        if any(k in desc for k in ["inexperienced", "new framework", "skill gap"]) or category == "resource":
            return rec(
                "AI pair-programming and code walkthroughs; targeted snippet guidance",
                ["GitHub Copilot/Cursor", "Sourcegraph Cody", "Stack Overflow AI"]
            )

        if any(k in desc for k in ["downtime", "deployment", "release"]) or category == "operational":
            return rec(
                "Blue/green or canary deploy with auto-rollback; AIOps alerting",
                ["Argo Rollouts/Flagger", "Dynatrace Davis AI", "AWS DevOps Guru"]
            )

        if ("validation" in desc or "input" in desc or "payment" in desc) and category == "technical" or "validation" in desc:
            return rec(
                "Enforce schema validation and sanitization; run SAST/DAST with autofix",
                ["Pydantic/Marshmallow", "Semgrep + AI", "GitHub CodeQL", "OWASP ZAP"]
            )

        if any(k in desc for k in ["delay", "feedback", "client"]) or category == "communication":
            return rec(
                "Auto-summarize sessions; extract requirements; generate prototypes",
                ["Notion/Microsoft Copilot", "Figma AI", "Linear/Productboard AI"]
            )

        if "document" in desc or category == "process":
            return rec(
                "Generate docs from code and create repo Q&A search",
                ["Mintlify Writer", "Docusaurus + OpenAI embeddings", "Sourcegraph + RAG"]
            )

        if any(k in desc for k in ["frequent changes", "scope", "change"]) or category == "requirements":
            return rec(
                "AI impact analysis; prioritize regression; use feature flags",
                ["Launchable (ML test selection)", "Copilot Test Gen", "Unleash/Flagsmith"]
            )

        if any(k in desc for k in ["overlapping", "dev and qa", "responsibil"]) or category == "organisational":
            return rec(
                "Auto-generate RACI and PR checklists; enforce quality gates",
                ["Confluence/Jira AI", "GitHub Actions + Copilot", "TestOps AI"]
            )

        if any(k in desc for k in ["churn", "complexity", "hotspot"]) or category == "technical":
            return rec(
                "Detect hotspots and refactor; quality gates with AI review",
                ["CodeScene", "SonarQube + Clean Code AI", "CodeClimate"]
            )

        # Fallback by category
        fallback = {
            'security': ("Run SAST/DAST; secrets scanning; fix with guided patches",
                        ["Semgrep AI", "CodeQL", "OWASP ZAP", "gitleaks"]),
            'performance': ("Profile with AI-guided hotspots; tune queries/caches",
                            ["Datadog Watchdog", "Pyroscope/Flamegraphs", "k6"]),
        }
        if category in fallback:
            sol, tools = fallback[category]
            return rec(sol, tools)
        return rec("Triage with AI assistant and propose targeted remediation", ["ChatGPT/GPT-4", "Copilot"])

    # Apply recommendations
    solutions = []
    tools_list = []
    for _, r in df.iterrows():
        sol, tools = _ai_recommendation_for_row(r)
        solutions.append(sol)
        tools_list.append(tools)
    df["AISolution"] = solutions
    df["AITools"] = tools_list

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
