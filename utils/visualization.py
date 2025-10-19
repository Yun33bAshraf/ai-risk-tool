"""
Visualization module for AI Risk Analysis Tool
Implements heat maps, trend analysis, feature importance, and comparison charts
Based on usability research (Cöltekin et al., 2021; Ruppert et al., 2022; Huang et al., 2024)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def generate_risk_heatmap(df, title="Risk Heatmap (Likelihood × Impact)"):
    """
    Generate 3×3 risk heatmap with clear labels and numeric annotations
    Following usability guidelines (Cöltekin et al., 2021; McDowell et al., 2022)
    """
    # Create pivot table
    pivot = pd.pivot_table(
        df,
        values='RiskScore',
        index='Likelihood',
        columns='Impact',
        aggfunc='count',
        fill_value=0
    )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Generate heatmap with clear color scale
    sns.heatmap(
        pivot,
        annot=True,
        fmt='d',
        cmap='RdYlGn_r',
        cbar_kws={'label': 'Number of Risks'},
        linewidths=1,
        linecolor='gray',
        ax=ax,
        vmin=0
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Impact', fontsize=12, fontweight='bold')
    ax.set_ylabel('Likelihood', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_priority_matrix(df):
    """
    Generate priority matrix visualization showing risk distribution
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot with risk categories
    if 'PredictedRiskLevel' in df.columns:
        risk_col = 'PredictedRiskLevel'
    elif 'ManualRiskCategory' in df.columns:
        risk_col = 'ManualRiskCategory'
    else:
        risk_col = None
    
    if risk_col:
        colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        for risk_level in ['High', 'Medium', 'Low']:
            subset = df[df[risk_col] == risk_level]
            ax.scatter(
                subset['Impact'],
                subset['Likelihood'],
                c=colors.get(risk_level, 'blue'),
                label=risk_level,
                s=100,
                alpha=0.6,
                edgecolors='black'
            )
    else:
        ax.scatter(df['Impact'], df['Likelihood'], s=100, alpha=0.6, edgecolors='black')
    
    # Add grid zones
    ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=3.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=2.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=3.5, color='gray', linestyle='--', alpha=0.5)
    
    ax.set_xlabel('Impact', fontsize=12, fontweight='bold')
    ax.set_ylabel('Likelihood', fontsize=12, fontweight='bold')
    ax.set_title('Risk Priority Matrix', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_feature_importance(model, feature_names, top_n=10):
    """
    Visualize feature importance from trained model
    Critical for interpretability (Zhang et al., 2023; Kim et al., 2024)
    """
    # Get feature importances
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        return None
    
    # Create dataframe
    feat_imp_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=False).head(top_n)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(feat_imp_df['Feature'], feat_imp_df['Importance'], color='steelblue')
    ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Feature', fontsize=12, fontweight='bold')
    ax.set_title('Top Feature Importance', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f'{width:.3f}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_confusion_matrix_plot(cm, class_names):
    """
    Visualize confusion matrix for model evaluation
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names,
        cbar_kws={'label': 'Count'},
        ax=ax
    )
    
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_risk_distribution(df):
    """
    Generate bar chart showing risk distribution by category
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Manual vs Predicted distribution
    if 'ManualRiskCategory' in df.columns:
        manual_counts = df['ManualRiskCategory'].value_counts()
        colors_manual = [{'High': 'red', 'Medium': 'orange', 'Low': 'green'}.get(x, 'blue') 
                        for x in manual_counts.index]
        ax1.bar(manual_counts.index, manual_counts.values, color=colors_manual, alpha=0.7, edgecolor='black')
        ax1.set_title('Manual Risk Distribution', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax1.set_xlabel('Risk Level', fontsize=10, fontweight='bold')
        
        # Add count labels
        for i, (idx, val) in enumerate(manual_counts.items()):
            ax1.text(i, val + 0.5, str(val), ha='center', fontweight='bold')
    
    if 'PredictedRiskLevel' in df.columns:
        pred_counts = df['PredictedRiskLevel'].value_counts()
        colors_pred = [{'High': 'red', 'Medium': 'orange', 'Low': 'green'}.get(x, 'blue') 
                      for x in pred_counts.index]
        ax2.bar(pred_counts.index, pred_counts.values, color=colors_pred, alpha=0.7, edgecolor='black')
        ax2.set_title('AI-Predicted Risk Distribution', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax2.set_xlabel('Risk Level', fontsize=10, fontweight='bold')
        
        # Add count labels
        for i, (idx, val) in enumerate(pred_counts.items()):
            ax2.text(i, val + 0.5, str(val), ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_owner_distribution(df):
    """
    Visualize risk distribution by owner
    """
    if 'Owner' not in df.columns:
        return None
    
    owner_counts = df['Owner'].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(owner_counts.index, owner_counts.values, color='coral', edgecolor='black')
    ax.set_xlabel('Number of Risks', fontsize=12, fontweight='bold')
    ax.set_ylabel('Owner', fontsize=12, fontweight='bold')
    ax.set_title('Risk Distribution by Owner (Top 10)', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                str(int(width)),
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_category_distribution(df):
    """
    Visualize risk distribution by category
    """
    if 'Category' not in df.columns:
        return None
    
    category_counts = df['Category'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create pie chart
    colors = plt.cm.Set3(range(len(category_counts)))
    wedges, texts, autotexts = ax.pie(
        category_counts.values,
        labels=category_counts.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        explode=[0.05] * len(category_counts)
    )
    
    # Enhance text
    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    ax.set_title('Risk Distribution by Category', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_model_comparison(results_dict):
    """
    Compare performance metrics across multiple models
    """
    if not results_dict or len(results_dict) < 2:
        return None
    
    models = list(results_dict.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    
    # Prepare data
    data = {metric: [] for metric in metrics}
    for model in models:
        for metric in metrics:
            value = results_dict[model].get(metric, 0)
            data[metric].append(value * 100 if value <= 1 else value)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(models))
    width = 0.2
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, metric in enumerate(metrics):
        offset = width * (i - 1.5)
        bars = ax.bar(x + offset, data[metric], width, label=metric.capitalize(), color=colors[i])
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend(loc='lower right')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_roc_curve(fpr, tpr, auc_score, model_name="Model"):
    """
    Generate ROC curve visualization
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc_score:.2f})')
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    ax.set_title(f'ROC Curve - {model_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def generate_trend_analysis(df_list, labels):
    """
    Generate trend analysis showing how risks change over time
    df_list: list of dataframes representing different time periods
    labels: list of time period labels
    """
    if not df_list or len(df_list) < 2:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Track risk levels over time
    risk_levels = ['High', 'Medium', 'Low']
    colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
    
    for risk_level in risk_levels:
        counts = []
        for df in df_list:
            if 'PredictedRiskLevel' in df.columns:
                count = (df['PredictedRiskLevel'] == risk_level).sum()
            elif 'ManualRiskCategory' in df.columns:
                count = (df['ManualRiskCategory'] == risk_level).sum()
            else:
                count = 0
            counts.append(count)
        
        ax.plot(labels, counts, marker='o', linewidth=2, 
               label=risk_level, color=colors[risk_level], markersize=8)
    
    ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Risks', fontsize=12, fontweight='bold')
    ax.set_title('Risk Trend Analysis Over Time', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig_to_base64(fig)
