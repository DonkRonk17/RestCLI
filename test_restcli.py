#!/usr/bin/env python3
"""
Manual Test Suite for RestCLI v1.0.0
Run these tests to verify all functionality works correctly.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run command and return result"""
    print(f"\n{'='*70}")
    print(f"TEST: {cmd}")
    print('='*70)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    print(f"Exit Code: {result.exitcode}")
    return result.exitcode == 0

def main():
    """Run all manual tests"""
    print("\n🧪 RestCLI v1.0.0 - Manual Test Suite\n")
    
    tests = [
        ("Help Display", "python restcli.py"),
        ("GET Request", "python restcli.py get https://api.github.com/users/octocat"),
        ("GET with Verbose", "python restcli.py get https://api.github.com/zen -v"),
        ("POST Request (file)", "python restcli.py post https://jsonplaceholder.typicode.com/posts -f test_data.json"),
        ("Environment Set", "python restcli.py env set TEST_VAR test_value"),
        ("Environment List", "python restcli.py env list"),
        ("Environment Get", "python restcli.py env get TEST_VAR"),
        ("Environment Delete", "python restcli.py env delete TEST_VAR"),
        ("History Display", "python restcli.py history"),
        ("History Limited", "python restcli.py history -l 5"),
        ("Replay Request", "python restcli.py replay 1"),
        ("Collection Save", "python restcli.py collection save test_collection"),
        ("Collection List", "python restcli.py collection list"),
        ("Collection Load", "python restcli.py collection load test_collection"),
        ("Collection Delete", "python restcli.py collection delete test_collection"),
    ]
    
    # Create test data file
    test_data = '{"title": "Test", "body": "Test body", "userId": 1}'
    Path("test_data.json").write_text(test_data)
    
    passed = 0
    failed = 0
    
    for test_name, command in tests:
        try:
            if run_command(command):
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                failed += 1
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} ERROR: {e}")
    
    # Cleanup
    Path("test_data.json").unlink(missing_ok=True)
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print('='*70)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
