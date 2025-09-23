"""
first-time setup and validation script
run this after cloning to ensure everything is configured correctly
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """ensure python 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"ERROR: python 3.9+ required (you have {version.major}.{version.minor})")
        return False
    print(f"OK python {version.major}.{version.minor}.{version.micro}")
    return True


def check_directories():
    """ensure all required directories exist"""
    dirs = ['data', 'data/raw', 'data/processed', 'models', 'notebooks', 'src']
    
    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"OK created {dir_path}/")
        else:
            print(f"OK {dir_path}/ exists")
    
    return True


def check_required_files():
    """verify core files exist"""
    files = [
        'requirements.txt',
        'app.py',
        'config.py',
        'src/data_collection.py',
        'src/preprocessing.py',
        'src/models.py',
        'src/anomaly_detection.py',
        'src/visualizations.py'
    ]
    
    missing = []
    for file_path in files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"ERROR: {file_path} missing")
        else:
            print(f"OK {file_path}")
    
    return len(missing) == 0


def check_dependencies():
    """check if dependencies can be imported"""
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'pytrends': 'pytrends.request',
        'prophet': 'prophet',
        'statsmodels': 'statsmodels.tsa.arima.model',
        'sklearn': 'sklearn',
        'plotly': 'plotly',
        'streamlit': 'streamlit'
    }
    
    missing = []
    for name, import_path in required.items():
        try:
            __import__(import_path)
            print(f"OK {name}")
        except ImportError:
            missing.append(name)
            print(f"ERROR: {name} not installed")
    
    if missing:
        print(f"\ninstall missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True


def display_next_steps():
    """show user what to do next"""
    print("\n" + "="*60)
    print("SUCCESS! SETUP COMPLETE!")
    print("="*60)
    
    print("\nSTEPS: next steps:")
    print("\n1. collect data from google trends (10-15 minutes):")
    print("   python src/data_collection.py")
    
    print("\n2. preprocess data:")
    print("   python src/preprocessing.py")
    
    print("\n3. train models:")
    print("   python src/train_models.py")
    
    print("\n4. detect anomalies:")
    print("   python src/anomaly_detection.py")
    
    print("\n5. launch dashboard:")
    print("   streamlit run app.py")
    
    print("\nTIP: or run everything at once:")
    print("   python run_pipeline.py pipeline")
    
    print("\nDOCS: documentation:")
    print("   - QUICKSTART.md - beginner guide")
    print("   - GUIDE.md - detailed reference")
    print("   - EXAMPLES.md - code examples")
    print("   - PORTFOLIO.md - technical overview")
    
    print("\nNOTE:  important notes:")
    print("   - google trends has rate limits (be patient)")
    print("   - first data collection takes 10-15 minutes")
    print("   - data is real and anonymized from google")
    print()


def main():
    print("🧠 mental health trends - setup validation")
    print("="*60)
    
    print("\nchecking python version...")
    if not check_python_version():
        sys.exit(1)
    
    print("\nchecking directory structure...")
    if not check_directories():
        sys.exit(1)
    
    print("\nchecking required files...")
    if not check_required_files():
        sys.exit(1)
    
    print("\nchecking dependencies...")
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\nERROR: some dependencies missing")
        print("\nrun: pip install -r requirements.txt")
        sys.exit(1)
    
    display_next_steps()


if __name__ == '__main__':
    main()
