## How the AI Risk Tool Works

This file gives a plain-English walkthrough of what happens in the project: the data flow, key pages, and how results are produced.

### 1) Core Idea
- Help SME project managers analyze project risks quickly.
- Combine a simple manual risk matrix (Likelihood × Impact) with an ML model and clear visualizations.

### 2) Main User Flows
1. Upload → Results (primary artefact demo)
   - Upload an Excel risk register on the Home page.
   - The app computes manual scores, runs ML predictions (if a model exists or can be trained), and renders charts and metrics on the Results page.

2. Parameters Scoring (quick scenario demo)
   - On the Parameters page, enter project size, budget, duration, experience, complexity, dependencies.
   - The app translates those into Likelihood/Impact, shows your position on a risk matrix, and lists tailored recommendations with “why these” triggers.

3. Framework Benchmarking (comparative analysis)
   - On the Benchmark page, rate ISO 31000, PMBOK, PRINCE2 on SME-relevant criteria.
   - The app computes averages, recommends a primary framework, and shows bar charts.

4. Usability Feedback (evaluation support)
   - On the Feedback page, submit ease/clarity/alignment scores and comments.
   - Stored locally in `uploads/feedback.csv` for your dissertation’s evaluation section.

### 3) What Happens After You Upload a File
Inputs
- Required: `Likelihood` (1–5), `Impact` (1–5), `RiskLevel` (High/Medium/Low)
- Optional: `Description`, `Category`, `Owner`, and technical features (`RequirementComplexity`, `CodeChurn`, etc.)

Processing (simplified)
1) Pre-checks and messages for very small datasets (helps interpret results).
2) ML Step (`utils/ml_model.py`)
   - If a model exists and features match, load it; otherwise, train a Random Forest on your file.
   - Predict risk levels, compute probabilities, and create performance metrics (Accuracy, Precision, Recall, F1, Brier, PR-AUC, Confusion Matrix).
3) Analysis Step (`utils/analysis.py`)
   - Compute manual `RiskScore = Likelihood × Impact` and `ManualRiskCategory`.
   - If a model exists, add `PredictedRiskLevel` and confidence.
   - Generate short AI-oriented recommendations per row based on keywords/categories.
4) Visualization Step (`utils/visualization.py`)
   - Create heatmap, priority matrix, distribution comparison, feature importance (if model supports), and optional owner/category charts.

Outputs (Results page)
- A risk table showing manual vs AI results and recommendations.
- Performance metrics cards and per-class table.
- Visual charts to aid interpretation and reporting.

### 4) Parameters Page: How Scores Are Derived
- The tool maps your inputs to Likelihood and Impact using simple heuristics:
  - Higher technical complexity, dependencies, size, and duration increase Likelihood.
  - Higher budget and complexity increase Impact (experience slightly moderates both).
- Category thresholds follow the standard matrix:
  - High ≥ 12, Medium ≥ 6, else Low (all from Likelihood × Impact).
- You see a mini heatmap with an “X” marking your inputs.
- Recommendations are tied to triggers (e.g., high complexity → architecture review).

### 5) Benchmarking Page: What It Proves
- You rate frameworks on: complexity/docs, cost/resources, adaptability, IT fit.
- The page computes average scores and displays:
  - A bar chart of average scores per framework.
  - A grouped bar chart by criterion.
- The recommendation summarizes which framework to use as a base and where to tailor.

### 6) Files You’ll Interact With
- `app.py`: Flask routes for Home/Upload, Results, Parameters, Benchmark, Feedback.
- `templates/`: Pages for UI; notably `index.html`, `results.html`, `parameters.html`, `benchmark.html`, `feedback.html`.
- `utils/`:
  - `ml_model.py`: Training, loading, predicting, and metrics.
  - `analysis.py`: Manual scoring, recommendations, chart orchestration.
  - `visualization.py`: Chart generation helpers.
  - `preprocess.py`: Data cleaning (used by training).
- `uploads/`: Example Excel files; model training inputs; feedback CSV.
- `models/`: Saved model, encoder, and feature names when trained.
- `CONCEPTUAL_FRAMEWORK.md`: The SME-tailored conceptual framework with feedback loops.

### 7) How This Satisfies the Research Requirements
- Artefact prototype with inputs, scoring, visuals, recommendations (3.5.2).
- Comparative analysis via benchmarking (3.4.2).
- Parameters-based demonstration and rationale (3.2 & 3.5.1 feedback loop in practice).
- Functional and usability evaluation support with metrics and feedback capture (3.6).

### 8) How to Run Quickly
```bash
pip install -r requirements.txt
python app.py
# Optional (sample data & training)
python create_sample_data.py
python utils/train_model.py uploads/risk_training_data.xlsx
```


