#!/usr/bin/env python3
"""
Setup verification script for Contract Agent Backend.
Run this after cloning the repository to verify all dependencies are correctly installed.
"""
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.11 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python version {version.major}.{version.minor}.{version.micro} is too old.")
        print("   Required: Python 3.11 or higher")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Contract Agent Backend - Setup Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check Python version
    print("1. Checking Python version...")
    if not check_python_version():
        all_ok = False
    print()
    
    # Check core packages
    print("2. Checking core dependencies...")
    core_packages = [
        ("fastapi", "fastapi"),
        ("pydantic", "pydantic"),
        ("SQLAlchemy", "sqlalchemy"),
        ("uvicorn", "uvicorn"),
        ("alembic", "alembic"),
        ("psycopg2-binary", "psycopg2"),
        ("python-jose", "jose"),
        ("passlib", "passlib"),
        ("python-dotenv", "dotenv"),
    ]
    
    for package, import_name in core_packages:
        if not check_package(package, import_name):
            all_ok = False
    print()
    
    # Check AI/ML packages
    print("3. Checking AI/ML dependencies...")
    ai_packages = [
        ("openai", "openai"),
        ("pinecone-client", "pinecone"),
        ("tiktoken", "tiktoken"),
    ]
    
    for package, import_name in ai_packages:
        if not check_package(package, import_name):
            all_ok = False
    print()
    
    # Check document processing
    print("4. Checking document processing dependencies...")
    doc_packages = [
        ("PyMuPDF", "fitz"),
        ("python-docx", "docx"),
    ]
    
    for package, import_name in doc_packages:
        if not check_package(package, import_name):
            all_ok = False
    print()
    
    # Final result
    print("=" * 60)
    if all_ok:
        print("✅ All checks passed! Your environment is ready.")
        return 0
    else:
        print("❌ Some checks failed. Please install missing packages:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

