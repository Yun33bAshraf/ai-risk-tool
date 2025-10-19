# AI-Assisted Risk Analysis Tool

**Academic Research Project**: Developing a Tool for Identifying and Visualising Project Risks in IT Project Management

---

## 📋 Overview

This tool implements a lightweight AI-assisted risk analysis system designed to help IT project managers identify, categorize, and visualize project risks efficiently. The project is grounded in established frameworks (ISO 31000, PMBOK, PRINCE2) and empirical machine learning research.

### Key Features

- **Multiple ML Algorithms**: Random Forest, Decision Tree, SVM, AdaBoost
- **Comprehensive Evaluation**: Precision, Recall, F1-Score, PR-AUC, Brier Score
- **5-Fold Cross-Validation**: Robust model evaluation
- **Rich Visualizations**: Heat maps, priority matrices, feature importance charts
- **Baseline Comparison**: Manual vs AI-powered risk scoring
- **Class Imbalance Handling**: SMOTE and SMOTETomek implementation

---

## 🎯 Research Foundation

This tool addresses the gap between formal risk management frameworks and practical implementation in SMEs. It combines:

- **Standards Compliance**: ISO 31000, PMBOK, PRINCE2
- **Empirical Research**: Al-Habaibeh et al. (2021), Zhang et al. (2023), Abdelgadir et al. (2021)
- **Usability Studies**: Cöltekin et al. (2021), Ruppert et al. (2022), Huang et al. (2024)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Excel files (.xlsx or .xls) for risk data

### Installation

1. **Clone or download the repository**
```bash
cd ai-risk-tool
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Train the model (first-time setup)**
```bash
python utils/train_model.py uploads/risk_training_data.xlsx
```

2. **Start the Flask web application**
```bash
python app.py
```

3. **Open your browser**
Navigate to: `http://127.0.0.1:5000`

4. **Upload your risk data**
Upload an Excel file with your risk register and get instant AI-powered analysis!

---

## 📊 Data Format

### Required Columns

Your Excel file **must** include:

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `Likelihood` | Integer | 1-5 | Probability of risk occurring |
| `Impact` | Integer | 1-5 | Severity if risk occurs |
| `RiskLevel` | String | High/Medium/Low | Actual risk classification (for training) |

### Optional Columns (Enhanced Analysis)

| Column | Type | Description |
|--------|------|-------------|
| `Description` | String | Text description of the risk |
| `Category` | String | Risk category (Technical, Resource, Schedule, etc.) |
| `Owner` | String | Person responsible for the risk |
| `RequirementComplexity` | Float | Complexity score of requirements |
| `AmbiguityScore` | Float | Ambiguity indicator |
| `CodeChurn` | Float | Code change frequency |
| `ModuleComplexity` | Float | Cyclomatic complexity |
| `RevisionCount` | Integer | Number of revisions |

### Example Data Format

```
| Likelihood | Impact | RiskLevel | Description                  | Category  | Owner  |
|------------|--------|-----------|------------------------------|-----------|--------|
| 4          | 5      | High      | Server infrastructure failure| Technical | John   |
| 2          | 3      | Medium    | Resource shortage            | Resource  | Sarah  |
| 1          | 2      | Low       | Minor UI bugs                | Technical | Mike   |
```

---

## 🧠 Model Training

### Training All Models

The `train_model.py` script trains and compares 4 different algorithms:

```bash
python utils/train_model.py <path_to_training_data.xlsx>
```

**Output:**
- Trains: Random Forest, Decision Tree, SVM, AdaBoost
- Evaluates: Accuracy, Precision, Recall, F1-Score, PR-AUC, Brier Score
- Performs: 5-fold cross-validation
- Saves: Best model to `models/` directory
- Generates: Comparison visualizations

### Model Performance Metrics

The tool calculates:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **PR-AUC**: Area under precision-recall curve
- **Brier Score**: Calibration measure (lower is better)
- **Confusion Matrix**: Detailed classification results

---

## 📈 Visualizations

The tool generates multiple visualizations following academic usability research:

1. **Risk Heatmap**: Likelihood × Impact distribution
2. **Priority Matrix**: Scatter plot with risk categories
3. **Risk Distribution**: Manual vs AI-predicted comparison
4. **Feature Importance**: Top contributing features
5. **Owner Distribution**: Risks by responsible person
6. **Category Distribution**: Pie chart of risk types
7. **Confusion Matrix**: Model classification performance

All visualizations follow clear design principles:
- Limited color scales
- Clear legends and labels
- Numeric annotations
- Consistent axes

---

## 🔧 Project Structure

```
ai-risk-tool/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── models/                     # Trained model storage
│   ├── risk_model.pkl         # Best trained model
│   ├── label_encoder.pkl      # Label encoder
│   └── feature_names.pkl      # Feature list
│
├── uploads/                    # Upload directory
│   └── risk_training_data.xlsx # Sample training data
│
├── utils/                      # Core modules
│   ├── preprocess.py          # Data preprocessing & validation
│   ├── ml_model.py            # Model training & prediction
│   ├── analysis.py            # Risk analysis logic
│   ├── visualization.py       # Chart generation
│   └── train_model.py         # Comprehensive training script
│
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   └── results.html           # Results display
│
└── static/                     # Static assets
    └── style.css              # Custom styles
```

---

## 🔬 Academic Methodology

### Research Design
- **Type**: Applied development with artefact creation
- **Approach**: Quantitative experimental
- **Validation**: Empirical testing on representative datasets

### Data Processing Pipeline

1. **Validation**: Check required columns and data types
2. **Missing Value Handling**: Median for numeric, mode for categorical
3. **Feature Engineering**: Derive complexity and change indicators
4. **Outlier Detection**: IQR method for anomaly identification
5. **Class Balancing**: SMOTE/SMOTETomek for imbalanced data
6. **Model Training**: Multiple algorithms with cross-validation

### Evaluation Strategy

Following methodology requirements:
- **5-Fold Cross-Validation**: Ensures robustness
- **Multiple Metrics**: Comprehensive performance assessment
- **Feature Importance**: Interpretability and transparency
- **Baseline Comparison**: Manual scoring vs AI predictions

---

## 📚 Theoretical Framework

### Framework Alignment

**ISO 31000 Risk Management**
- Risk identification process
- Likelihood and impact assessment
- Risk categorization and prioritization

**PMBOK (Project Management Body of Knowledge)**
- Risk register structure
- Qualitative risk analysis
- Risk response planning

**PRINCE2**
- Risk management strategy
- Risk identification techniques
- Risk assessment matrices

### Empirical Foundation

The tool implements methods validated in peer-reviewed research:

- **Requirement Risk Prediction**: Al-Habaibeh et al. (2021), Zhang et al. (2023)
- **Ensemble Methods**: Abdelgadir et al. (2021), Chen & Lee (2025)
- **Software Defect Prediction**: Wang et al. (2021), Kim et al. (2024)
- **Visualization Usability**: Cöltekin et al. (2021), McDowell et al. (2022)

---

## 🧪 Testing & Validation

### Running Tests

```bash
# Train model with validation
python utils/train_model.py uploads/risk_training_data.xlsx

# Check model info
python -c "from utils.ml_model import get_model_info; print(get_model_info())"
```

### Expected Outputs

- **Training Accuracy**: 80-95% (depends on data quality)
- **Cross-Validation Std**: < 5% (indicates stability)
- **Feature Importance**: Top features should align with domain knowledge
- **Confusion Matrix**: Should show clear diagonal pattern

---

## 🎓 Research Contributions

This tool contributes to:

1. **Accessibility**: Makes AI-assisted risk analysis available to SMEs
2. **Interpretability**: Uses explainable models (Decision Trees, Feature Importance)
3. **Validation**: Implements comprehensive evaluation metrics
4. **Usability**: Follows evidence-based visualization design
5. **Framework Integration**: Bridges academic standards with practical tools

---

## 📦 Dependencies

Core libraries:
- **Flask**: Web framework
- **pandas**: Data manipulation
- **scikit-learn**: Machine learning algorithms
- **imbalanced-learn**: Class balancing (SMOTE)
- **matplotlib**: Visualization
- **seaborn**: Statistical plots
- **openpyxl**: Excel file handling
- **joblib**: Model serialization

---

## 🐛 Troubleshooting

### Common Issues

**1. "Missing required column" error**
- Ensure your Excel file has `Likelihood`, `Impact`, and `RiskLevel` columns
- Check column names match exactly (case-sensitive)

**2. Model training fails**
- Verify you have at least 20-30 samples
- Check for missing values in required columns
- Ensure `RiskLevel` contains only: High, Medium, Low

**3. Visualizations not showing**
- Clear browser cache
- Check console for JavaScript errors
- Verify matplotlib backend is compatible

**4. Low model accuracy**
- Increase training data size
- Add more features (complexity, churn, etc.)
- Check for data quality issues

---

## 🔮 Future Enhancements

Potential extensions for academic research:

- [ ] Deep learning models (LSTM, Transformers)
- [ ] Fuzzy logic rule-based systems
- [ ] Real-time risk monitoring dashboard
- [ ] Integration with project management tools (Jira, Trello)
- [ ] Multi-language support
- [ ] Automated report generation (PDF/Word)
- [ ] Time-series trend analysis
- [ ] Risk interdependency mapping

---

## 📖 Citation

If you use this tool in your research, please cite:

```
AI-Assisted Risk Analysis in IT Project Management:
Developing a Tool for Identifying and Visualising Project Risks
[Author Name], [Year]
[Institution]
```

---

## 📄 License

This is an academic research project. Please contact the author for usage permissions.

---

## 👤 Contact

For questions, issues, or research collaboration:
- **Email**: [your-email@university.edu]
- **Institution**: [Your University]
- **Project**: MSc/PhD Research in IT Project Management

---

## 🙏 Acknowledgments

This research builds upon:
- ISO 31000 Risk Management Guidelines
- PMBOK® Guide (Project Management Institute)
- PRINCE2® Framework
- Empirical studies by Al-Habaibeh, Zhang, Abdelgadir, and others

---

**Last Updated**: 2025-10-19
**Version**: 1.0.0
**Status**: Active Research Project
