"""
Create test data matching the user's uploaded image
"""
import pandas as pd

# Create the exact data from the image
data = {
    'RiskID': ['R001', 'R002', 'R003', 'R004', 'R005', 'R006', 'R007', 'R008', 'R009', 'R010'],
    'Description': [
        'Architecture requirement for user authentication',
        'Integration with external API may fail under high load',
        'Inexperienced team with new framework',
        'Server downtime risk during deployment',
        'Missing input validation in payment module',
        'Delay in client feedback cycles',
        'Poor documentation may hinder maintenance',
        'Frequent changes in requirements',
        'Overlapping responsibilities during dev and QA',
        'Module with high churn and complexity'
    ],
    'Category': ['Requirements', 'Technical', 'Resource', 'Operational', 'Technical', 
                 'Communication', 'Process', 'Requirements', 'Organisational', 'Technical'],
    'Likelihood': [2, 3, 2, 3, 4, 2, 3, 5, 3, 4],
    'Impact': [3, 4, 4, 5, 5, 3, 2, 4, 3, 4],
    'Owner': ['Dan', 'Ahmed', 'Maria', 'John', 'Ali', 'Fatima', 'Omar', 'Sara', 'Ahmed', 'Aisha'],
    'RequirementComplexity': [7, 5, 0, 0, 0, 0, 3, 9, 0, 0],
    'AmbiguityScore': [0.85, 0.3, 0, 0, 0, 0, 0.4, 0.9, 0, 0],
    'CodeChurn': [0, 40, 0, 10, 25, 0, 0, 0, 0, 55],
    'ModuleComplexity': [0, 9, 0, 7, 8, 0, 0, 0, 0, 10],
    'RevisionCount': [2, 3, 0, 0, 1, 0, 4, 6, 0, 2],
    'RiskLevel': ['High', 'Medium', 'Medium', 'High', 'High', 'Low', 'Low', 'High', 'Medium', 'High']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_path = 'uploads/test_small_dataset.xlsx'
df.to_excel(output_path, index=False)

print(f"Created test dataset with {len(df)} samples")
print(f"Saved to: {output_path}")
print(f"\nClass distribution:")
print(df['RiskLevel'].value_counts())
print(f"\nColumns: {', '.join(df.columns.tolist())}")
