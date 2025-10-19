# AI Risk Analysis Tool - Usage Guide

## Quick Start Guide

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd ai-risk-tool

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Sample Data (Optional)

```bash
python create_sample_data.py
```

This creates three files in `uploads/`:
- `risk_register_template.xlsx` - Template with examples
- `risk_training_data.xlsx` - 100 sample risks for training
- `minimal_example.xlsx` - Minimal example with required fields only

### Step 3: Train the Model

```bash
python utils/train_model.py uploads/risk_training_data.xlsx
```

**Expected Output:**
```
============================================================
COMPREHENSIVE MODEL TRAINING & EVALUATION
============================================================

Loading and preprocessing data...
Data loaded: 100 samples, 7 features

TRAINING MODELS
============================================================

Random Forest
  Accuracy:  85.50%
  Precision: 84.20%
  Recall:    85.50%
  F1-Score:  84.80%

Decision Tree
  Accuracy:  78.00%
  ...

SVM
  Accuracy:  82.50%
  ...

AdaBoost
  Accuracy:  83.00%
  ...

BEST MODEL: Random Forest
F1-Score: 84.80%
============================================================
```

### Step 4: Run the Web Application

```bash
python app.py
```

Open your browser: `http://127.0.0.1:5000`

---

## Using the Web Interface

### 1. Home Page

- View model information (if trained)
- Upload Excel file with risk data
- See required and optional columns

### 2. Upload Your Data

**Required Columns:**
- `Likelihood` (1-5)
- `Impact` (1-5)
- `RiskLevel` (High/Medium/Low)

**Optional Columns (for enhanced analysis):**
- `RiskID`
- `Description`
- `Category`
- `Owner`
- `RequirementComplexity`
- `AmbiguityScore`
- `CodeChurn`
- `ModuleComplexity`
- `RevisionCount`

### 3. View Results

The results page displays:

**Performance Metrics:**
- Accuracy, Precision, Recall, F1-Score
- Brier Score (calibration)
- PR-AUC (Precision-Recall Area Under Curve)
- Per-class metrics for each risk level

**Visualizations:**
- Risk Heatmap (Likelihood × Impact)
- Priority Matrix (scatter plot)
- Risk Distribution (Manual vs AI)
- Feature Importance
- Owner Distribution (if Owner column exists)
- Category Distribution (if Category column exists)

**Detailed Table:**
- All risks with predictions
- Confidence scores
- Manual vs AI comparison

---

## Excel File Format Examples

### Minimal Format (Required Fields Only)

| Likelihood | Impact | RiskLevel |
|------------|--------|-----------|
| 4          | 5      | High      |
| 3          | 4      | High      |
| 2          | 3      | Medium    |
| 1          | 2      | Low       |

### Full Format (All Fields)

| RiskID   | Description                          | Category  | Owner        | Likelihood | Impact | RiskLevel | RequirementComplexity | AmbiguityScore | CodeChurn | ModuleComplexity | RevisionCount |
|----------|--------------------------------------|-----------|--------------|------------|--------|-----------|-----------------------|----------------|-----------|------------------|---------------|
| RISK-001 | Server infrastructure failure        | Technical | John Smith   | 4          | 5      | High      | 7.5                   | 0.65           | 75.3      | 15.2             | 25            |
| RISK-002 | Key developer resource departure     | Resource  | Sarah Johnson| 3          | 4      | High      | 5.2                   | 0.42           | 45.2      | 10.5             | 18            |
| RISK-003 | Third-party API integration issues   | Integration| Mike Chen   | 2          | 3      | Medium    | 6.8                   | 0.55           | 60.1      | 12.8             | 22            |

---

## Understanding the Metrics

### Classification Metrics

**Accuracy**: Percentage of correct predictions
- Formula: (TP + TN) / (TP + TN + FP + FN)
- Higher is better (typically 70-95%)

**Precision**: How many predicted positives are actually positive
- Formula: TP / (TP + FP)
- Important when false positives are costly

**Recall**: How many actual positives were identified
- Formula: TP / (TP + FN)
- Important when false negatives are costly

**F1-Score**: Harmonic mean of precision and recall
- Formula: 2 × (Precision × Recall) / (Precision + Recall)
- Balanced metric for overall performance

### Advanced Metrics

**Brier Score**: Measures calibration (prediction confidence accuracy)
- Range: 0 to 1
- Lower is better (0 = perfect calibration)

**PR-AUC**: Area under Precision-Recall curve
- Range: 0 to 1
- Higher is better (1 = perfect)

---

## Interpreting Results

### Risk Level Comparison

**Manual Baseline:**
- Based on Likelihood × Impact matrix
- Score ≥ 12 = High
- Score ≥ 6 = Medium
- Score < 6 = Low

**AI Prediction:**
- Uses all available features
- Learns from training data patterns
- Provides confidence scores

### When AI and Manual Disagree

Look for:
1. **Feature values**: Check RequirementComplexity, CodeChurn, etc.
2. **Confidence score**: Low confidence suggests uncertainty
3. **Context**: Some risks have hidden complexity

---

## Troubleshooting

### Error: "Missing required column"

**Solution:** Ensure your Excel file has these columns:
- `Likelihood`
- `Impact`
- `RiskLevel`

Column names are **case-sensitive**.

### Error: "Model training fails"

**Possible causes:**
1. Too few samples (need at least 20-30)
2. Missing values in required columns
3. Invalid RiskLevel values (must be: High, Medium, Low)

**Solution:**
```bash
# Check your data
python -c "import pandas as pd; df = pd.read_excel('your_file.xlsx'); print(df.info())"
```

### Low Model Accuracy (<70%)

**Possible causes:**
1. Poor data quality
2. Inconsistent labeling
3. Need more training samples
4. Need more features

**Solutions:**
- Add more training data
- Include technical features (complexity, churn)
- Review and correct RiskLevel labels
- Check for outliers or errors

### Visualizations Not Showing

**Solution:**
1. Clear browser cache (Ctrl+F5)
2. Check browser console for errors
3. Verify matplotlib installation:
   ```bash
   pip install --upgrade matplotlib seaborn
   ```

---

## Advanced Usage

### Training with Your Own Data

```bash
python utils/train_model.py path/to/your/data.xlsx
```

The script will:
1. Preprocess and validate data
2. Handle missing values
3. Balance classes (SMOTE)
4. Train 4 different models
5. Perform 5-fold cross-validation
6. Save the best model

### Using Different Models

Edit `utils/train_model.py` to adjust hyperparameters:

```python
models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200,  # Increase trees
        max_depth=15,      # Deeper trees
        random_state=42
    ),
    # ... other models
}
```

### Exporting Results

**Print Results:**
Click "Print Report" button on results page

**Save Data:**
Results are displayed in the browser. To export:
1. Right-click on table → Inspect
2. Copy table HTML
3. Paste into Excel or CSV

---

## Best Practices

### Data Collection

1. **Consistent Scoring**: Use the same likelihood/impact scale
2. **Regular Updates**: Keep risk register current
3. **Detailed Descriptions**: Help identify patterns
4. **Assign Owners**: Track responsibility

### Model Training

1. **Minimum Data**: 50+ samples for reliable training
2. **Balanced Classes**: Roughly equal High/Medium/Low
3. **Feature Engineering**: Include complexity metrics
4. **Regular Retraining**: Update model with new data

### Risk Management

1. **Review High Risks**: Prioritize immediate action
2. **Monitor Trends**: Watch for increasing risks
3. **Verify AI Predictions**: Use domain expertise
4. **Document Decisions**: Track risk responses

---

## API Usage (Advanced)

### Get Model Info

```bash
curl http://127.0.0.1:5000/api/model-info
```

Response:
```json
{
  "model_type": "RandomForestClassifier",
  "classes": ["High", "Low", "Medium"],
  "features": ["Likelihood", "Impact", ...],
  "n_features": 7
}
```

---

## Integration with Project Management Tools

### Export to Jira/Trello

1. Download results as CSV
2. Map columns:
   - RiskID → Issue ID
   - PredictedRiskLevel → Priority
   - Owner → Assignee

### Automated Workflows

Create scheduled tasks:
```bash
# Weekly risk analysis
python utils/train_model.py data/weekly_risks.xlsx
```

---

## Performance Expectations

### Training Time

- 100 samples: ~10-30 seconds
- 500 samples: ~30-60 seconds
- 1000+ samples: 1-3 minutes

### Accuracy Benchmarks

- **Good**: 75-85% accuracy
- **Excellent**: 85-95% accuracy
- **Perfect**: 95%+ (rare, check for overfitting)

### When to Retrain

- New project types
- Significant accuracy drop
- Every 3-6 months
- After major process changes

---

## Support and Further Help

### Common Questions

**Q: Can I use this for non-IT projects?**
A: Yes! Adjust categories and features to fit your domain.

**Q: How many risks do I need?**
A: Minimum 30, recommended 50-100 for good accuracy.

**Q: Is the model interpretable?**
A: Yes! Feature importance shows which factors drive predictions.

**Q: Can I export the model?**
A: Yes! Model files are in `models/` directory (.pkl format).

### Resources

- README.md - Complete documentation
- Proposal documents - Academic methodology
- Sample data - Example formats

### Contact

For research inquiries or collaboration, contact the project author.

---

**Last Updated**: 2025-10-19  
**Version**: 1.0.0
