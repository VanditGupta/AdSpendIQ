#!/usr/bin/env python3
"""
Test Runner for Ad Campaign Analytics Project
Runs all PyTest tests and provides a summary
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests and display results"""
    print("🚀 Ad Campaign Analytics - Test Suite")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found. Please activate it first.")
        print("   Run: source venv/bin/activate")
        return False
    
    # Run tests with coverage
    try:
        print("🧪 Running tests with coverage...")
        result = subprocess.run([
            'venv/bin/python', '-m', 'pytest', 
            'tests/', '-v', '--tb=short',
            '--cov=scripts', '--cov=dbt',
            '--cov-report=term-missing'
        ], capture_output=True, text=True)
        
        # Print test output
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        # Check if tests passed
        if result.returncode == 0:
            print("\n🎉 All tests passed successfully!")
            return True
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_great_expectations():
    """Run Great Expectations data validation"""
    print("\n🔍 Running Great Expectations Data Validation...")
    print("=" * 50)
    
    try:
        # Check if Great Expectations directory exists
        if not os.path.exists('great_expectations'):
            print("❌ Great Expectations not initialized. Skipping validation.")
            return False
        
        # Run validation script
        result = subprocess.run([
            'venv/bin/python', 'great_expectations/validate_ad_data.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Validation warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running Great Expectations: {e}")
        return False

def main():
    """Main test runner function"""
    print("🧪 Ad Campaign Analytics Test Suite")
    print("=" * 50)
    
    # Run PyTest tests
    tests_passed = run_tests()
    
    # Run Great Expectations validation
    ge_passed = run_great_expectations()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"✅ PyTest Tests: {'PASSED' if tests_passed else 'FAILED'}")
    print(f"🔍 Data Validation: {'PASSED' if ge_passed else 'FAILED'}")
    
    if tests_passed and ge_passed:
        print("\n🎉 All tests and validations passed!")
        print("🚀 Your data pipeline is ready for production!")
        return 0
    else:
        print("\n⚠️  Some tests or validations failed.")
        print("🔧 Please review and fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
