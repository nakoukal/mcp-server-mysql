#!/usr/bin/env python3
"""
Test runner for MySQL MCP Server
Runs all available tests and provides summary
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def run_test(test_file):
    """Run a single test file and return result"""
    print(f"\n🧪 Running {test_file}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path("tests") / test_file)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {test_file} PASSED")
            if result.stdout:
                # Show last few lines of output for summary
                lines = result.stdout.strip().split('\n')
                for line in lines[-3:]:
                    if '🏁' in line or '✅' in line or 'completed' in line:
                        print(f"   {line}")
            return True
        else:
            print(f"❌ {test_file} FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file} TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"💥 {test_file} ERROR: {e}")
        return False

def main():
    """Run all tests and provide summary"""
    print("🚀 MySQL MCP Server Test Suite")
    print("=" * 60)
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    # Test files to run
    test_files = [
        "test_live_mysql.py",
        "test_database_switching.py",
        "test_no_default_database.py"
    ]
    
    # Check if test files exist
    missing_tests = []
    for test_file in test_files:
        if not (Path("tests") / test_file).exists():
            missing_tests.append(test_file)
    
    if missing_tests:
        print(f"⚠️  Missing test files: {', '.join(missing_tests)}")
        return False
    
    # Run tests
    results = []
    for test_file in test_files:
        results.append(run_test(test_file))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, test_file in enumerate(test_files):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"   {test_file:<30} {status}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! MySQL MCP Server is fully functional.")
        return True
    else:
        print(f"💥 {total - passed} test(s) failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
