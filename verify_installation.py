"""
Installation Verification Script
Tests all components to ensure proper setup
"""

import sys
import os

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    required_packages = [
        'flask',
        'pandas',
        'numpy',
        'sklearn',
        'matplotlib',
        'seaborn',
        'openpyxl',
        'joblib',
        'imblearn',
        'scipy'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                __import__('sklearn')
            elif package == 'imblearn':
                __import__('imblearn')
            else:
                __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing.append(package)
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n[SUCCESS] All dependencies installed")
        return True


def check_directories():
    """Check if all required directories exist"""
    print("\n" + "="*60)
    print("CHECKING DIRECTORY STRUCTURE")
    print("="*60)
    
    required_dirs = [
        'models',
        'uploads',
        'utils',
        'templates',
        'static'
    ]
    
    all_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] {dir_name}/")
        else:
            print(f"[MISSING] {dir_name}/")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] All directories present")
    else:
        print("\n[WARNING] Some directories missing (will be created automatically)")
    
    return all_exist


def check_files():
    """Check if all required files exist"""
    print("\n" + "="*60)
    print("CHECKING CORE FILES")
    print("="*60)
    
    required_files = {
        'app.py': 'Flask application',
        'requirements.txt': 'Dependencies list',
        'README.md': 'Main documentation',
        'utils/preprocess.py': 'Preprocessing module',
        'utils/ml_model.py': 'ML model module',
        'utils/analysis.py': 'Analysis module',
        'utils/visualization.py': 'Visualization module',
        'utils/train_model.py': 'Training script',
        'templates/index.html': 'Home page template',
        'templates/results.html': 'Results page template'
    }
    
    all_exist = True
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path:<35} ({size:,} bytes)")
        else:
            print(f"[MISSING] {file_path:<35}")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] All core files present")
    else:
        print("\n[ERROR] Some core files missing")
    
    return all_exist


def check_sample_data():
    """Check if sample data files exist"""
    print("\n" + "="*60)
    print("CHECKING SAMPLE DATA")
    print("="*60)
    
    sample_files = [
        'uploads/risk_training_data.xlsx',
        'uploads/risk_register_template.xlsx',
        'uploads/minimal_example.xlsx'
    ]
    
    exists_count = 0
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path} ({size:,} bytes)")
            exists_count += 1
        else:
            print(f"[NOT FOUND] {file_path}")
    
    if exists_count == 0:
        print("\n[INFO] No sample data found")
        print("Run: python create_sample_data.py")
        return False
    elif exists_count < len(sample_files):
        print(f"\n[INFO] {exists_count}/{len(sample_files)} sample files found")
        return True
    else:
        print("\n[SUCCESS] All sample data files present")
        return True


def check_trained_model():
    """Check if a trained model exists"""
    print("\n" + "="*60)
    print("CHECKING TRAINED MODEL")
    print("="*60)
    
    model_files = [
        'models/risk_model.pkl',
        'models/label_encoder.pkl',
        'models/feature_names.pkl'
    ]
    
    all_exist = True
    
    for file_path in model_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path} ({size:,} bytes)")
        else:
            print(f"[NOT FOUND] {file_path}")
            all_exist = False
    
    if all_exist:
        print("\n[SUCCESS] Trained model found")
        return True
    else:
        print("\n[INFO] No trained model found")
        print("Run: python utils/train_model.py uploads/risk_training_data.xlsx")
        return False


def test_imports():
    """Test importing core modules"""
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)
    
    modules = [
        ('utils.preprocess', 'RiskDataPreprocessor'),
        ('utils.ml_model', 'train_and_predict'),
        ('utils.analysis', 'analyze_risks'),
        ('utils.visualization', 'generate_risk_heatmap')
    ]
    
    all_success = True
    
    for module_name, class_or_func in modules:
        try:
            module = __import__(module_name, fromlist=[class_or_func])
            getattr(module, class_or_func)
            print(f"[OK] {module_name}.{class_or_func}")
        except Exception as e:
            print(f"[ERROR] {module_name}.{class_or_func}: {str(e)}")
            all_success = False
    
    if all_success:
        print("\n[SUCCESS] All modules import successfully")
    else:
        print("\n[ERROR] Some modules failed to import")
    
    return all_success


def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("AI RISK ANALYSIS TOOL - INSTALLATION VERIFICATION")
    print("="*70)
    
    results = {
        'Dependencies': check_dependencies(),
        'Directories': check_directories(),
        'Core Files': check_files(),
        'Sample Data': check_sample_data(),
        'Trained Model': check_trained_model(),
        'Module Imports': test_imports()
    }
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for check_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    
    if all_passed:
        print("[SUCCESS] All verification checks passed!")
        print("\nYou can now:")
        print("  1. Generate sample data: python create_sample_data.py")
        print("  2. Train model: python utils/train_model.py uploads/risk_training_data.xlsx")
        print("  3. Run application: python app.py")
    else:
        print("[WARNING] Some checks failed")
        print("\nRecommended actions:")
        
        if not results['Dependencies']:
            print("  1. Install dependencies: pip install -r requirements.txt")
        if not results['Sample Data']:
            print("  2. Generate sample data: python create_sample_data.py")
        if not results['Trained Model']:
            print("  3. Train model: python utils/train_model.py uploads/risk_training_data.xlsx")
        
        print("  4. Then run: python app.py")
    
    print("\n" + "="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
