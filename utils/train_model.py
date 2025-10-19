# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import classification_report
# import joblib
# import os

# # Load dataset
# df = pd.read_excel("data/risk_training_data.xlsx")

# # Features and target
# X = df[["Likelihood", "Impact", "RequirementComplexity", "AmbiguityScore",
#         "CodeChurn", "ModuleComplexity", "RevisionCount"]]
# y = df["RiskLevel"]

# # Encode target if needed
# le = LabelEncoder()
# y_encoded = le.fit_transform(y)

# # Split data
# X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# # Train model
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # Evaluate
# y_pred = model.predict(X_test)
# print(classification_report(y_test, y_pred, target_names=le.classes_))

# # Save model and label encoder
# os.makedirs("models", exist_ok=True)
# joblib.dump(model, "models/risk_model.pkl")
# joblib.dump(le, "models/label_encoder.pkl")

# print("✅ Model trained and saved successfully!")
