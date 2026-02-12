#!/usr/bin/env python3
"""
Startup Check - Verify LinkedIn Post Generator Setup
================================================
Run this script to verify your environment is properly configured.
"""

import sys
import os


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERROR] Python version {version.major}.{version.minor}.{version.micro} is too old")
        print("   Requires Python 3.8 or higher")
        return False


def check_dependencies():
    """Check required dependencies."""
    required_packages = [
        'streamlit',
        'langchain', 
        'langchain_groq',
        'sentence_transformers',
        'requests',
        'dotenv'
    ]
    
    # Optional packages (with fallbacks)
    optional_packages = [
        'chromadb'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERROR] {package} - MISSING")
            missing.append(package)
    
    # Check optional packages
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[WARNING] {package} - MISSING (fallback available)")
    
    return len(missing) == 0


def check_env_file():
    """Check .env file and API key."""
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"[OK] {env_file} file exists")
        
        # Try to load environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                print(f"[OK] GROQ_API_KEY is set ({api_key[:10]}...)")
                return True
            else:
                print("[ERROR] GROQ_API_KEY not found in .env")
                return False
                
        except ImportError:
            print("[ERROR] python-dotenv not installed")
            return False
    else:
        print(f"[ERROR] {env_file} file not found")
        print("   Copy .env.example to .env and add your API key")
        return False


def check_directory_structure():
    """Check project directory structure."""
    required_dirs = ['core', 'loaders', 'ui', 'utils']
    required_files = [
        'app.py',
        'requirements.txt',
        'core/__init__.py',
        'core/models.py',
        'core/llm.py',
        'core/generator.py',
        'ui/components.py',
        'utils/logger.py'
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[ERROR] {dir_name}/ directory missing")
            all_good = False
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"[OK] {file_name} exists")
        else:
            print(f"[ERROR] {file_name} missing")
            all_good = False
    
    return all_good


def test_imports():
    """Test critical imports."""
    try:
        from core.generator import LinkedInGenerator
        print("[OK] Core imports working")
        
        # Test generator initialization
        generator = LinkedInGenerator()
        print("[OK] Generator initialization successful")
        return True
        
    except Exception as e:
        print(f"[ERROR] Import/initialization failed: {e}")
        return False


def main():
    """Run all checks."""
    print("LinkedIn Post Generator - Startup Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Directory Structure", check_directory_structure),
        ("Import Test", test_imports)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    if all(results):
        print("ALL CHECKS PASSED!")
        print("\nYou're ready to run:")
        print("   streamlit run app.py")
        print("\nOpen http://localhost:8501 in your browser")
    else:
        print("Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and add GROQ_API_KEY")
        print("3. Ensure you're in the project directory")


if __name__ == "__main__":
    main()
