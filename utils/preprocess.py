"""
Data preprocessing module for AI Risk Analysis Tool
Implements data cleaning, validation, feature engineering, and class imbalance handling
Aligned with methodology requirements from ISO 31000 and PMBOK frameworks
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
import warnings
warnings.filterwarnings('ignore')


class RiskDataPreprocessor:
    """
    Comprehensive data preprocessing for risk analysis
    Handles missing values, outliers, feature engineering, and class imbalance
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        
    def validate_data(self, df):
        """
        Validate that required columns exist and data types are correct
        Based on ISO 31000 and PMBOK risk register requirements
        """
        required_numeric = ["Likelihood", "Impact"]
        optional_numeric = [
            "RequirementComplexity", "AmbiguityScore", 
            "CodeChurn", "ModuleComplexity", "RevisionCount"
        ]
        
        # Check for required columns
        missing_cols = [col for col in required_numeric if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate numeric columns
        for col in required_numeric:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    raise ValueError(f"Column {col} cannot be converted to numeric")
        
        # Handle optional numeric columns
        for col in optional_numeric:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    warnings.warn(f"Column {col} has non-numeric values, filling with 0")
                    df[col] = 0
        
        return df
    
    def handle_missing_values(self, df):
        """
        Handle missing values using domain-appropriate strategies
        Numeric: median imputation
        Categorical: mode or 'Unknown'
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Fill numeric with median
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                print(f"  - Filled {col} missing values with median: {median_val}")
        
        # Fill categorical with mode or 'Unknown'
        for col in categorical_cols:
            if df[col].isnull().any():
                if col in ['Category', 'Owner']:
                    df[col].fillna('Unknown', inplace=True)
                elif col == 'Description':
                    df[col].fillna('No description provided', inplace=True)
                else:
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                    df[col].fillna(mode_val, inplace=True)
                print(f"  - Filled {col} missing values")
        
        return df
    
    def engineer_features(self, df):
        """
        Create derived features for enhanced risk prediction
        Based on empirical studies (Al-Habaibeh et al., 2021; Zhang et al., 2023)
        """
        # Basic risk score (manual scoring baseline)
        if 'Likelihood' in df.columns and 'Impact' in df.columns:
            df['RiskScore'] = df['Likelihood'] * df['Impact']
        
        # Complexity indicators (if available)
        complexity_cols = ['RequirementComplexity', 'ModuleComplexity']
        available_complexity = [col for col in complexity_cols if col in df.columns]
        if available_complexity:
            df['AvgComplexity'] = df[available_complexity].mean(axis=1)
        
        # Change indicators
        if 'CodeChurn' in df.columns and 'RevisionCount' in df.columns:
            df['ChangeIntensity'] = df['CodeChurn'] * df['RevisionCount']
        
        # Risk category from manual score (for baseline comparison)
        if 'RiskScore' in df.columns:
            df['ManualRiskCategory'] = df['RiskScore'].apply(self._categorize_risk)
        
        return df
    
    def _categorize_risk(self, score):
        """Categorize risk based on traditional likelihood × impact matrix"""
        if score >= 12:  # High threshold (e.g., 3×4, 4×3, 4×4)
            return 'High'
        elif score >= 6:  # Medium threshold
            return 'Medium'
        else:
            return 'Low'
    
    def detect_outliers(self, df, columns=None):
        """
        Detect outliers using IQR method
        Returns boolean mask of outliers
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        outlier_mask = pd.Series([False] * len(df), index=df.index)
        
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            col_outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_mask = outlier_mask | col_outliers
            
            if col_outliers.any():
                print(f"  - Detected {col_outliers.sum()} outliers in {col}")
        
        return outlier_mask
    
    def balance_classes(self, X, y, method='smote'):
        """
        Handle class imbalance using SMOTE or SMOTETomek
        Critical for accurate risk prediction (Sun et al., 2023; Kumar & Patil, 2023)
        """
        original_counts = pd.Series(y).value_counts()
        print(f"\nOriginal class distribution:")
        for label, count in original_counts.items():
            print(f"  {label}: {count}")
        
        # Check if dataset is too small for SMOTE
        min_class_count = original_counts.min()
        
        if min_class_count < 2:
            print(f"[WARNING] Smallest class has only {min_class_count} sample(s)")
            print("   SMOTE requires at least 2 samples per class")
            print("   Skipping balancing - need more data")
            return X, y
        
        try:
            # Calculate k_neighbors based on smallest class
            # SMOTE needs k_neighbors < smallest class size
            k_neighbors = min(5, min_class_count - 1)
            
            if k_neighbors < 1:
                print("[WARNING] Not enough samples for SMOTE (need at least 2 per class)")
                print("   Continuing with original imbalanced data...")
                return X, y
            
            if method == 'smote':
                sampler = SMOTE(random_state=42, k_neighbors=k_neighbors)
            elif method == 'smotetomek':
                sampler = SMOTETomek(random_state=42, smote=SMOTE(random_state=42, k_neighbors=k_neighbors))
            else:
                raise ValueError(f"Unknown balancing method: {method}")
            
            X_balanced, y_balanced = sampler.fit_resample(X, y)
            
            balanced_counts = pd.Series(y_balanced).value_counts()
            print(f"\nBalanced class distribution:")
            for label, count in balanced_counts.items():
                print(f"  {label}: {count}")
            
            return X_balanced, y_balanced
            
        except Exception as e:
            print(f"[WARNING] Could not balance classes - {str(e)}")
            print("   Continuing with original data...")
            return X, y
    
    def prepare_features(self, df, target_col='RiskLevel', feature_cols=None):
        """
        Prepare feature matrix and target vector
        Returns X, y, and feature names
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")
        
        # Define default feature columns if not provided
        if feature_cols is None:
            feature_cols = [
                'Likelihood', 'Impact', 'RequirementComplexity', 
                'AmbiguityScore', 'CodeChurn', 'ModuleComplexity', 'RevisionCount'
            ]
            # Keep only columns that exist
            feature_cols = [col for col in feature_cols if col in df.columns]
            
            # Add engineered features if they exist
            engineered = ['RiskScore', 'AvgComplexity', 'ChangeIntensity']
            feature_cols += [col for col in engineered if col in df.columns]
        
        X = df[feature_cols].copy()
        y = df[target_col].copy()
        
        self.feature_names = feature_cols
        
        return X, y, feature_cols
    
    def full_pipeline(self, df, target_col='RiskLevel', balance=True, balance_method='smote'):
        """
        Complete preprocessing pipeline
        Returns cleaned X, y, feature names, and processed dataframe
        """
        print("\n" + "="*60)
        print("PREPROCESSING PIPELINE")
        print("="*60)
        
        # Step 1: Validate
        print("\n1. Validating data...")
        df = self.validate_data(df)
        print("   [OK] Data validation complete")
        
        # Step 2: Handle missing values
        print("\n2. Handling missing values...")
        df = self.handle_missing_values(df)
        print("   [OK] Missing values handled")
        
        # Step 3: Engineer features
        print("\n3. Engineering features...")
        df = self.engineer_features(df)
        print("   [OK] Feature engineering complete")
        
        # Step 4: Detect outliers (for information only)
        print("\n4. Detecting outliers...")
        outlier_mask = self.detect_outliers(df)
        print(f"   [INFO] Total outliers detected: {outlier_mask.sum()}")
        
        # Step 5: Prepare features
        print("\n5. Preparing features...")
        X, y, feature_names = self.prepare_features(df, target_col)
        print(f"   [OK] Features prepared: {len(feature_names)} features")
        print(f"   Features: {', '.join(feature_names)}")
        
        # Step 6: Balance classes if requested
        if balance:
            print("\n6. Balancing classes...")
            X, y = self.balance_classes(X, y, method=balance_method)
        
        print("\n" + "="*60)
        print("PREPROCESSING COMPLETE")
        print("="*60 + "\n")
        
        return X, y, feature_names, df


def load_and_preprocess(filepath, target_col='RiskLevel', balance=True):
    """
    Convenience function to load Excel file and preprocess in one step
    """
    df = pd.read_excel(filepath)
    preprocessor = RiskDataPreprocessor()
    X, y, feature_names, df_processed = preprocessor.full_pipeline(
        df, target_col=target_col, balance=balance
    )
    return X, y, feature_names, df_processed, preprocessor
