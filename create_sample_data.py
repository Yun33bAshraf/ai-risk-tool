"""
Sample Data Generator for AI Risk Analysis Tool
Creates Excel templates with realistic IT project risk data
Aligned with ISO 31000 and PMBOK risk register requirements
"""

import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Sample data for realistic IT project risks
RISK_DESCRIPTIONS = [
    "Server infrastructure failure during peak hours",
    "Database migration data corruption",
    "Third-party API integration issues",
    "Insufficient user acceptance testing coverage",
    "Key developer resource departure",
    "Cloud service provider outage",
    "Security vulnerability in authentication module",
    "Requirements ambiguity in reporting features",
    "Legacy system compatibility problems",
    "Budget overrun in development phase",
    "Schedule delay due to scope creep",
    "Performance degradation under load",
    "Cross-browser compatibility issues",
    "Mobile responsiveness problems",
    "Data privacy compliance gaps",
    "Insufficient backup and recovery procedures",
    "Network bandwidth limitations",
    "Version control conflicts in codebase",
    "Inadequate documentation for maintenance",
    "Vendor contract termination risk",
    "Technology stack obsolescence",
    "Team skill gap in new technologies",
    "Communication breakdown between teams",
    "Client requirement changes mid-project",
    "Testing environment instability",
    "Deployment automation failures",
    "Code quality degradation over time",
    "Technical debt accumulation",
    "Integration testing bottlenecks",
    "Production incident response delays",
    "Inadequate error handling in critical paths",
    "Insufficient monitoring and alerting",
    "Customer data security breach",
    "Regulatory compliance violations",
    "License agreement violations",
    "Scalability limitations in architecture",
    "Dependency on single point of failure",
    "Inadequate disaster recovery plan",
    "User training and adoption resistance",
    "Post-deployment support resource shortage"
]

CATEGORIES = [
    "Technical", "Resource", "Schedule", "Budget", "Quality",
    "Security", "Compliance", "Integration", "Performance", "External"
]

OWNERS = [
    "John Smith", "Sarah Johnson", "Mike Chen", "Emily Brown",
    "David Wilson", "Lisa Anderson", "Tom Martinez", "Jane Davis",
    "Robert Lee", "Maria Garcia"
]


def calculate_risk_level(likelihood, impact):
    """Calculate risk level based on likelihood and impact"""
    score = likelihood * impact
    if score >= 12:
        return 'High'
    elif score >= 6:
        return 'Medium'
    else:
        return 'Low'


def generate_risk_data(n_samples=100):
    """
    Generate realistic risk data for training
    
    Args:
        n_samples: Number of risk samples to generate
    
    Returns:
        DataFrame with risk data
    """
    data = []
    
    for i in range(n_samples):
        # Select random description
        description = random.choice(RISK_DESCRIPTIONS)
        
        # Generate likelihood and impact (1-5 scale)
        # Create some correlation - complex requirements tend to have higher risk
        likelihood = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.2, 0.1])
        impact = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.2, 0.1])
        
        # Calculate risk level
        risk_level = calculate_risk_level(likelihood, impact)
        
        # Generate technical features
        requirement_complexity = np.random.uniform(1, 10)
        ambiguity_score = np.random.uniform(0, 1)
        code_churn = np.random.uniform(0, 100)
        module_complexity = np.random.uniform(1, 20)
        revision_count = np.random.randint(1, 50)
        
        # Adjust features based on risk level for better correlation
        if risk_level == 'High':
            requirement_complexity += 2
            ambiguity_score += 0.2
            code_churn += 20
            module_complexity += 5
            revision_count += 10
        elif risk_level == 'Medium':
            requirement_complexity += 1
            ambiguity_score += 0.1
            code_churn += 10
            module_complexity += 2
            revision_count += 5
        
        # Ensure values stay in valid ranges
        requirement_complexity = min(requirement_complexity, 10)
        ambiguity_score = min(ambiguity_score, 1)
        code_churn = min(code_churn, 150)
        module_complexity = min(module_complexity, 30)
        revision_count = min(revision_count, 100)
        
        # Create risk record
        risk = {
            'RiskID': f'RISK-{i+1:03d}',
            'Description': description,
            'Category': random.choice(CATEGORIES),
            'Owner': random.choice(OWNERS),
            'Likelihood': likelihood,
            'Impact': impact,
            'RiskLevel': risk_level,
            'RequirementComplexity': round(requirement_complexity, 2),
            'AmbiguityScore': round(ambiguity_score, 3),
            'CodeChurn': round(code_churn, 2),
            'ModuleComplexity': round(module_complexity, 2),
            'RevisionCount': revision_count,
            'Status': random.choice(['Open', 'In Progress', 'Mitigated', 'Closed']),
            'DateIdentified': f'2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}'
        }
        
        data.append(risk)
    
    return pd.DataFrame(data)


def create_template(filename='risk_register_template.xlsx'):
    """
    Create a blank template with column headers and instructions
    """
    template_data = {
        'RiskID': ['RISK-001', 'RISK-002', 'RISK-003'],
        'Description': [
            'Example: Server infrastructure failure',
            'Example: Key developer departure',
            'Example: Third-party API issues'
        ],
        'Category': ['Technical', 'Resource', 'Integration'],
        'Owner': ['John Smith', 'Sarah Johnson', 'Mike Chen'],
        'Likelihood': [4, 3, 2],
        'Impact': [5, 4, 3],
        'RiskLevel': ['High', 'High', 'Medium'],
        'RequirementComplexity': [7.5, 5.2, 6.8],
        'AmbiguityScore': [0.65, 0.42, 0.55],
        'CodeChurn': [75.3, 45.2, 60.1],
        'ModuleComplexity': [15.2, 10.5, 12.8],
        'RevisionCount': [25, 18, 22],
        'Status': ['Open', 'In Progress', 'Open'],
        'DateIdentified': ['2024-01-15', '2024-02-20', '2024-03-10']
    }
    
    df = pd.DataFrame(template_data)
    df.to_excel(filename, index=False, sheet_name='Risk Register')
    print(f"[OK] Template created: {filename}")
    return df


def create_training_data(filename='risk_training_data.xlsx', n_samples=100):
    """
    Create training data with realistic risk scenarios
    """
    df = generate_risk_data(n_samples)
    df.to_excel(filename, index=False, sheet_name='Training Data')
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"[OK] Training Data Created: {filename}")
    print(f"{'='*60}")
    print(f"Total Samples: {len(df)}")
    print(f"\nRisk Level Distribution:")
    print(df['RiskLevel'].value_counts())
    print(f"\nCategory Distribution:")
    print(df['Category'].value_counts())
    print(f"{'='*60}\n")
    
    return df


def create_minimal_example(filename='minimal_example.xlsx'):
    """
    Create minimal example with only required fields
    """
    minimal_data = {
        'Likelihood': [4, 3, 2, 5, 1, 4, 3, 2, 5, 3],
        'Impact': [5, 4, 3, 4, 2, 4, 5, 2, 5, 3],
        'RiskLevel': ['High', 'High', 'Medium', 'High', 'Low', 
                      'High', 'High', 'Low', 'High', 'Medium']
    }
    
    df = pd.DataFrame(minimal_data)
    df.to_excel(filename, index=False, sheet_name='Risks')
    print(f"[OK] Minimal example created: {filename}")
    return df


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SAMPLE DATA GENERATOR")
    print("="*60 + "\n")
    
    # Create all sample files
    print("Creating sample files...\n")
    
    # 1. Full template with examples
    template = create_template('uploads/risk_register_template.xlsx')
    
    # 2. Training data
    training = create_training_data('uploads/risk_training_data.xlsx', n_samples=100)
    
    # 3. Minimal example
    minimal = create_minimal_example('uploads/minimal_example.xlsx')
    
    print("\n" + "="*60)
    print("ALL SAMPLE FILES CREATED SUCCESSFULLY")
    print("="*60)
    print("\nFiles created in 'uploads/' directory:")
    print("  1. risk_register_template.xlsx - Full template with examples")
    print("  2. risk_training_data.xlsx - Training data (100 samples)")
    print("  3. minimal_example.xlsx - Minimal example (required fields only)")
    print("\n" + "="*60 + "\n")
