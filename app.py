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

app = Flask(__name__)
app.secret_key = "secret123"  # for flash messages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    """Main page with upload form"""
    # Get model info if available
    model_info = get_model_info()
    return render_template("index.html", model_info=model_info)

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
