from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from utils.analysis import analyze_risks
from utils.ml_model import train_and_predict

app = Flask(__name__)
app.secret_key = "secret123"  # for flash messages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("❌ No file part", "danger")
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("⚠️ No selected file", "danger")
        return redirect(url_for("index"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)

        # 🧠 Step 1: Train AI Model (creates .pkl files)
        ml_results = train_and_predict(filepath)

        # 🧮 Step 2: Analyze Risks (uses trained model)
        results = analyze_risks(df)

        combined_results = {
            "analysis": results,
            "ml": ml_results
        }

        return render_template("results.html", results=combined_results)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"❌ Error processing file: {str(e)}", "danger")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
