#!/usr/bin/env python3
"""
Test runner script that works both locally and in Docker
"""
import subprocess
import sys
import os

def run_tests():
    """Run pytest tests with proper configuration"""
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add current directory to Python path
    sys.path.insert(0, script_dir)
    
    try:
        # Run pytest with explicit configuration
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--no-header'
        ], check=True, capture_output=True, text=True)
        
        print("✅ All tests passed!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Tests failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
