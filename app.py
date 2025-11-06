"""
Flask Application for AI Risk Analysis Tool
Enhanced with comprehensive metrics and visualizations
Aligned with academic proposal requirements
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
from utils.analysis import analyze_risks
from utils.ml_model import train_and_predict, get_model_info
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "secret123"  # for flash messages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
FEEDBACK_FILE = os.path.join(UPLOAD_FOLDER, "feedback.csv")

@app.route("/")
def index():
    """Main page with upload form"""
    # Get model info if available
    model_info = get_model_info()
    return render_template("index.html", model_info=model_info)

@app.route("/parameters", methods=["GET", "POST"])
def parameters():
    """Simple parameters input to compute composite risk and suggestions"""
    if request.method == "POST":
        try:
            project_size = float(request.form.get("project_size", 0))
            budget = float(request.form.get("budget", 0))
            duration = float(request.form.get("duration", 0))
            team_experience = float(request.form.get("team_experience", 3))  # 1-5
            technical_complexity = float(request.form.get("technical_complexity", 3))  # 1-5
            dependencies = float(request.form.get("dependencies", 0))

            # Heuristic mapping → Likelihood & Impact (1–5)
            # Higher complexity/dependencies/size/duration increase Likelihood; lower experience increases Likelihood
            likelihood = min(5, max(1, round(
                0.3 * (technical_complexity) +
                0.2 * (dependencies / 3.0 + 1) +
                0.2 * (project_size / 5.0 + 1) +
                0.2 * (duration / 6.0 + 1) +
                0.1 * (6 - team_experience)
            )))

            # Impact grows with budget, size, complexity; mitigated slightly by experience
            impact = min(5, max(1, round(
                0.35 * (technical_complexity) +
                0.25 * (project_size / 5.0 + 1) +
                0.25 * (min(budget, 1000000) / 250000.0 + 1) +
                0.15 * (6 - team_experience)
            )))

            score = likelihood * impact

            def categorize(s):
                if s >= 12:
                    return "High"
                elif s >= 6:
                    return "Medium"
                return "Low"

            category = categorize(score)

            # Minimal recommendations
            recs = []
            if technical_complexity >= 4:
                recs.append("Spike high-risk components; add architecture review")
            if dependencies >= 3:
                recs.append("Add dependency risk register; contract SLAs; retries/circuit breakers")
            if team_experience <= 2:
                recs.append("Pair programming/mentoring; define coding standards and checklists")
            if duration >= 9:
                recs.append("Stage gates and mid-project risk reassessment")
            if budget >= 250000:
                recs.append("Cost contingency 10–15% and risk reserves")
            if not recs:
                recs.append("Maintain weekly risk review and update owners")

            # Build rationale (what triggered recommendations)
            triggers = []
            if technical_complexity >= 4:
                triggers.append("High technical complexity increases both likelihood and impact")
            if dependencies >= 3:
                triggers.append("Multiple external dependencies raise likelihood of integration failures")
            if team_experience <= 2:
                triggers.append("Low team experience increases likelihood of delivery risks")
            if duration >= 9:
                triggers.append("Long duration projects accumulate uncertainty over time")
            if budget >= 250000:
                triggers.append("Large budget elevates business impact of risk events")

            # Generate a small heatmap visualization with the (L, I) point
            fig, ax = plt.subplots(figsize=(4, 4))
            # Create 5x5 categorical grid based on score thresholds
            grid = [[(i+1) * (j+1) for j in range(5)] for i in range(5)]
            # Map to categories for colormap
            cat = [[(2 if s >= 12 else 1 if s >= 6 else 0) for s in row] for row in grid]
            cmap = sns.color_palette(["#198754", "#FFC107", "#DC3545"], as_cmap=True)
            sns.heatmap(cat, cmap=cmap, cbar=False, linewidths=0.5, linecolor="#ffffff", ax=ax,
                        xticklabels=[1,2,3,4,5], yticklabels=[1,2,3,4,5])
            ax.invert_yaxis()
            ax.set_xlabel("Impact")
            ax.set_ylabel("Likelihood")
            # Plot marker (likelihood is y, impact is x)
            ax.scatter([impact - 0.5], [likelihood - 0.5], s=120, c="#000000", marker="x", linewidths=2)
            ax.set_title("Risk Matrix (X marks your input)")
            buf = BytesIO()
            plt.tight_layout()
            fig.savefig(buf, format='png', dpi=150)
            plt.close(fig)
            heatmap_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            results = {
                "likelihood": likelihood,
                "impact": impact,
                "score": score,
                "category": category,
                "recommendations": recs,
                "triggers": triggers,
                "inputs": {
                    "project_size": project_size,
                    "budget": budget,
                    "duration": duration,
                    "team_experience": team_experience,
                    "technical_complexity": technical_complexity,
                    "dependencies": dependencies
                },
                "heatmap": heatmap_b64
            }
            return render_template("parameters.html", results=results)
        except Exception as e:
            flash(f"❌ Error computing risk: {str(e)}", "danger")
            return render_template("parameters.html", results=None)
    return render_template("parameters.html", results=None)

@app.route("/benchmark", methods=["GET", "POST"])
def benchmark():
    """Framework benchmarking for ISO 31000, PMBOK, PRINCE2"""
    frameworks = ["ISO 31000", "PMBOK", "PRINCE2"]
    criteria = [
        ("complexity", "Complexity & Documentation Demand"),
        ("cost", "Cost/Resource Demand"),
        ("adaptability", "Adaptability/Scalability"),
        ("it_fit", "Suitability for IT Projects")
    ]
    scores = None
    if request.method == "POST":
        try:
            scores = {}
            for fw in frameworks:
                scores[fw] = {}
                for key, _ in criteria:
                    val = float(request.form.get(f"{fw}_{key}", 3))
                    scores[fw][key] = val
            # Aggregate: higher is better; compute average
            aggregates = {fw: round(sum(scores[fw].values()) / len(criteria), 2) for fw in frameworks}
            # Simple recommendation logic
            best_fw = max(aggregates, key=aggregates.get)
            rec_text = f"Recommend {best_fw} as primary basis; tailor with best elements from others."
            # --- Visualizations ---
            charts = {}
            # 1) Overall averages bar chart
            fig1, ax1 = plt.subplots(figsize=(5, 3.2))
            ax1.bar(list(aggregates.keys()), list(aggregates.values()), color=["#0d6efd", "#20c997", "#ffc107"]) 
            ax1.set_ylim(0, 5)
            ax1.set_ylabel("Average Score (1–5)")
            ax1.set_title("Framework Average Scores")
            for i, v in enumerate(aggregates.values()):
                ax1.text(i, v + 0.1, f"{v}", ha='center', fontsize=9)
            buf1 = BytesIO()
            plt.tight_layout()
            fig1.savefig(buf1, format='png', dpi=150)
            plt.close(fig1)
            charts['avg_bar'] = base64.b64encode(buf1.getvalue()).decode('utf-8')

            # 2) Grouped bars per criterion
            import numpy as np
            labels = [label for _, label in criteria]
            x = np.arange(len(labels))
            width = 0.25
            fig2, ax2 = plt.subplots(figsize=(6.5, 3.6))
            for idx, fw in enumerate(frameworks):
                vals = [scores[fw][key] for key, _ in criteria]
                ax2.bar(x + (idx - 1) * width, vals, width, label=fw)
            ax2.set_ylabel("Score (1–5)")
            ax2.set_title("Scores by Criterion")
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels, rotation=10)
            ax2.set_ylim(0, 5)
            ax2.legend()
            buf2 = BytesIO()
            plt.tight_layout()
            fig2.savefig(buf2, format='png', dpi=150)
            plt.close(fig2)
            charts['criteria_bars'] = base64.b64encode(buf2.getvalue()).decode('utf-8')

            return render_template("benchmark.html", frameworks=frameworks, criteria=criteria, scores=scores, aggregates=aggregates, recommendation=rec_text, charts=charts)
        except Exception as e:
            flash(f"❌ Error processing scores: {str(e)}", "danger")
    return render_template("benchmark.html", frameworks=frameworks, criteria=criteria, scores=scores)

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """Collect usability feedback and store to CSV"""
    if request.method == "POST":
        try:
            name = request.form.get("name", "Anonymous")
            role = request.form.get("role", "")
            ease = int(request.form.get("ease", 3))
            clarity = int(request.form.get("clarity", 3))
            alignment = int(request.form.get("alignment", 3))
            comments = request.form.get("comments", "")

            row = {
                "Name": name,
                "Role": role,
                "EaseOfUse": ease,
                "Clarity": clarity,
                "SMEAlignment": alignment,
                "Comments": comments
            }
            if os.path.exists(FEEDBACK_FILE):
                df = pd.read_csv(FEEDBACK_FILE)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            else:
                df = pd.DataFrame([row])
            df.to_csv(FEEDBACK_FILE, index=False)
            flash("✅ Feedback submitted. Thank you!", "success")
        except Exception as e:
            flash(f"❌ Could not save feedback: {str(e)}", "danger")
    # Show recent feedback count
    count = 0
    if os.path.exists(FEEDBACK_FILE):
        try:
            count = len(pd.read_csv(FEEDBACK_FILE))
        except Exception:
            count = 0
    return render_template("feedback.html", count=count)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and risk analysis"""
    if "file" not in request.files:
        flash("❌ No file part", "danger")
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("⚠️ No selected file", "danger")
        return redirect(url_for("index"))

    # Check file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash("❌ Please upload an Excel file (.xlsx or .xls)", "danger")
        return redirect(url_for("index"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Load data
        df = pd.read_excel(filepath)
        
        print(f"\n{'='*70}")
        print("FILE UPLOADED")
        print(f"{'='*70}")
        print(f"   File: {file.filename}")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        print(f"{'='*70}\n")
        
        # Check if dataset is very small
        if len(df) < 10:
            flash("⚠️ Warning: Dataset has fewer than 10 samples. Results may not be reliable. Consider adding more data.", "warning")
        elif len(df) < 30:
            flash("⚠️ Note: Small dataset detected. For best results, use 30+ samples with balanced classes.", "info")

        # Step 1: ML Model Training & Prediction
        print("Running ML Model Training & Prediction...")
        ml_results = train_and_predict(filepath)
        print("[OK] ML Model complete\n")

        # Step 2: Comprehensive Risk Analysis
        print("Running Comprehensive Risk Analysis...")
        analysis_results = analyze_risks(df)
        print("[OK] Analysis complete\n")

        # Combine results
        combined_results = {
            "analysis": analysis_results,
            "ml": ml_results,
            "filename": file.filename,
            "row_count": len(df)
        }

        print(f"{'='*70}")
        print("PROCESSING COMPLETE - Displaying Results")
        print(f"{'='*70}\n")

        return render_template("results.html", results=combined_results)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n{'='*70}")
        print("ERROR OCCURRED")
        print(f"{'='*70}")
        print(error_trace)
        print(f"{'='*70}\n")
        
        flash(f"❌ Error processing file: {str(e)}", "danger")
        return redirect(url_for("index"))

@app.route("/about")
def about():
    """About page with methodology information"""
    return render_template("about.html")

@app.route("/api/model-info")
def api_model_info():
    """API endpoint to get current model information"""
    info = get_model_info()
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "No model found"}), 404

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AI RISK ANALYSIS TOOL")
    print("="*70)
    print("   Academic Research Project")
    print("   AI-Assisted Risk Analysis in IT Project Management")
    print("="*70)
    print("\n   Starting Flask server...")
    print("   Open http://127.0.0.1:5000 in your browser")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True)
