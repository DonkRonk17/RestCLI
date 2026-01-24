#!/usr/bin/env python3
"""
Comprehensive Test Suite for RestCLI v1.1.0

Tests cover:
- Core functionality (HTTP methods, requests)
- Environment variable management
- Request history
- Collections management
- Input parsing and validation
- Error handling
- Edge cases

Run: python test_restcli.py
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from restcli import (
    replace_env_vars,
    parse_headers,
    format_size,
    format_duration,
    save_json,
    load_json,
    ensure_data_dirs,
    DATA_DIR,
    HISTORY_FILE,
    COLLECTIONS_DIR,
    ENV_FILE
)


class TestHelperFunctions(unittest.TestCase):
    """Test helper/utility functions."""
    
    def test_replace_env_vars_single(self):
        """Test replacing single environment variable."""
        env = {"TOKEN": "abc123"}
        result = replace_env_vars("Bearer {{TOKEN}}", env)
        self.assertEqual(result, "Bearer abc123")
    
    def test_replace_env_vars_multiple(self):
        """Test replacing multiple environment variables."""
        env = {"HOST": "api.example.com", "VERSION": "v1"}
        result = replace_env_vars("https://{{HOST}}/{{VERSION}}/data", env)
        self.assertEqual(result, "https://api.example.com/v1/data")
    
    def test_replace_env_vars_not_found(self):
        """Test behavior when variable not found."""
        env = {}
        result = replace_env_vars("{{MISSING}}", env)
        self.assertEqual(result, "{{MISSING}}")  # Unchanged
    
    def test_replace_env_vars_empty(self):
        """Test with empty environment."""
        result = replace_env_vars("no variables", {})
        self.assertEqual(result, "no variables")
    
    def test_parse_headers_single(self):
        """Test parsing single header."""
        headers = parse_headers(["Content-Type: application/json"])
        self.assertEqual(headers, {"Content-Type": "application/json"})
    
    def test_parse_headers_multiple(self):
        """Test parsing multiple headers."""
        headers = parse_headers([
            "Content-Type: application/json",
            "Authorization: Bearer token"
        ])
        self.assertEqual(headers, {
            "Content-Type": "application/json",
            "Authorization": "Bearer token"
        })
    
    def test_parse_headers_with_spaces(self):
        """Test parsing headers with extra spaces."""
        headers = parse_headers(["  Content-Type  :   application/json  "])
        self.assertEqual(headers, {"Content-Type": "application/json"})
    
    def test_parse_headers_no_colon(self):
        """Test parsing header without colon (invalid)."""
        headers = parse_headers(["InvalidHeader"])
        self.assertEqual(headers, {})  # Should be ignored
    
    def test_parse_headers_empty(self):
        """Test parsing empty header list."""
        headers = parse_headers([])
        self.assertEqual(headers, {})
    
    def test_format_size_bytes(self):
        """Test formatting byte sizes."""
        self.assertEqual(format_size(100), "100.00 B")
        self.assertEqual(format_size(500), "500.00 B")
    
    def test_format_size_kilobytes(self):
        """Test formatting kilobyte sizes."""
        result = format_size(1024)
        self.assertIn("KB", result)
    
    def test_format_size_megabytes(self):
        """Test formatting megabyte sizes."""
        result = format_size(1024 * 1024)
        self.assertIn("MB", result)
    
    def test_format_size_gigabytes(self):
        """Test formatting gigabyte sizes."""
        result = format_size(1024 * 1024 * 1024)
        self.assertIn("GB", result)
    
    def test_format_duration_milliseconds(self):
        """Test formatting sub-second durations."""
        self.assertEqual(format_duration(0.5), "500ms")
        self.assertEqual(format_duration(0.1), "100ms")
    
    def test_format_duration_seconds(self):
        """Test formatting second-range durations."""
        result = format_duration(2.5)
        self.assertIn("2.50s", result)
    
    def test_format_duration_minutes(self):
        """Test formatting minute-range durations."""
        result = format_duration(90)
        self.assertIn("1m", result)


class TestJsonOperations(unittest.TestCase):
    """Test JSON save/load operations."""
    
    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "test.json"
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_json_dict(self):
        """Test saving dictionary to JSON."""
        data = {"key": "value", "number": 42}
        save_json(self.test_file, data)
        
        self.assertTrue(self.test_file.exists())
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, data)
    
    def test_save_json_list(self):
        """Test saving list to JSON."""
        data = [1, 2, 3, "four"]
        save_json(self.test_file, data)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, data)
    
    def test_save_json_unicode(self):
        """Test saving unicode content to JSON."""
        data = {"message": "Hello, 世界!"}
        save_json(self.test_file, data)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["message"], "Hello, 世界!")
    
    def test_load_json_existing(self):
        """Test loading existing JSON file."""
        data = {"test": "data"}
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        loaded = load_json(self.test_file)
        self.assertEqual(loaded, data)
    
    def test_load_json_not_found(self):
        """Test loading non-existent file."""
        result = load_json(self.test_dir / "nonexistent.json")
        self.assertEqual(result, {})  # Default for non-history files
    
    def test_load_json_history_not_found(self):
        """Test loading non-existent history file."""
        result = load_json(self.test_dir / "history.json")
        self.assertEqual(result, [])  # Default for history files
    
    def test_load_json_invalid(self):
        """Test loading invalid JSON file."""
        with open(self.test_file, 'w') as f:
            f.write("not valid json")
        
        result = load_json(self.test_file)
        self.assertEqual(result, {})  # Returns empty on error


class TestDataDirectories(unittest.TestCase):
    """Test data directory management."""
    
    def setUp(self):
        """Backup original data directory."""
        self.original_data_dir = DATA_DIR
        self.original_history_file = HISTORY_FILE
        self.original_collections_dir = COLLECTIONS_DIR
        self.original_env_file = ENV_FILE
    
    def test_data_dir_constant(self):
        """Test DATA_DIR is in user home."""
        self.assertTrue(str(DATA_DIR).startswith(str(Path.home())))
        self.assertIn(".restcli", str(DATA_DIR))
    
    def test_history_file_path(self):
        """Test history file is in data directory."""
        self.assertEqual(HISTORY_FILE.parent, DATA_DIR)
        self.assertEqual(HISTORY_FILE.name, "history.json")
    
    def test_collections_dir_path(self):
        """Test collections directory is in data directory."""
        self.assertEqual(COLLECTIONS_DIR.parent, DATA_DIR)
        self.assertEqual(COLLECTIONS_DIR.name, "collections")
    
    def test_env_file_path(self):
        """Test environment file is in data directory."""
        self.assertEqual(ENV_FILE.parent, DATA_DIR)
        self.assertEqual(ENV_FILE.name, "environment.json")


class TestInputValidation(unittest.TestCase):
    """Test input validation and edge cases."""
    
    def test_parse_headers_colon_in_value(self):
        """Test parsing header with colon in value."""
        headers = parse_headers(["Authorization: Bearer abc:123:xyz"])
        self.assertEqual(headers["Authorization"], "Bearer abc:123:xyz")
    
    def test_replace_env_vars_nested_brackets(self):
        """Test nested brackets don't break parsing."""
        env = {"VAR": "value"}
        result = replace_env_vars("{{{VAR}}}", env)
        self.assertEqual(result, "{value}")  # Inner brackets replaced
    
    def test_format_size_zero(self):
        """Test formatting zero bytes."""
        self.assertEqual(format_size(0), "0.00 B")
    
    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        self.assertEqual(format_duration(0), "0ms")
    
    def test_parse_headers_url_value(self):
        """Test parsing header with URL as value."""
        headers = parse_headers(["Referer: https://example.com/path?query=value"])
        self.assertEqual(headers["Referer"], "https://example.com/path?query=value")


class TestErrorConditions(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_replace_env_vars_special_chars(self):
        """Test env vars with special regex characters."""
        env = {"URL": "https://api.example.com/data?filter=a&sort=b"}
        result = replace_env_vars("{{URL}}", env)
        self.assertEqual(result, "https://api.example.com/data?filter=a&sort=b")
    
    def test_parse_headers_empty_value(self):
        """Test header with empty value."""
        headers = parse_headers(["X-Empty:"])
        self.assertEqual(headers["X-Empty"], "")
    
    def test_format_size_negative(self):
        """Test negative size (edge case)."""
        # Should handle gracefully
        result = format_size(-100)
        self.assertIsInstance(result, str)
    
    def test_parse_headers_multiple_colons(self):
        """Test header with multiple colons."""
        headers = parse_headers(["X-Data: a:b:c:d"])
        self.assertEqual(headers["X-Data"], "a:b:c:d")


class TestColorClass(unittest.TestCase):
    """Test Colors class."""
    
    def test_colors_exist(self):
        """Test color constants are defined."""
        from restcli import Colors
        
        self.assertTrue(hasattr(Colors, 'RESET'))
        self.assertTrue(hasattr(Colors, 'BOLD'))
        self.assertTrue(hasattr(Colors, 'RED'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'YELLOW'))
        self.assertTrue(hasattr(Colors, 'BLUE'))
        self.assertTrue(hasattr(Colors, 'CYAN'))
    
    def test_colors_are_strings(self):
        """Test color constants are strings."""
        from restcli import Colors
        
        self.assertIsInstance(Colors.RESET, str)
        self.assertIsInstance(Colors.RED, str)
        self.assertIsInstance(Colors.GREEN, str)
    
    def test_colors_are_ansi(self):
        """Test color constants are ANSI escape codes."""
        from restcli import Colors
        
        self.assertTrue(Colors.RESET.startswith('\033['))
        self.assertTrue(Colors.RED.startswith('\033['))


class TestModuleStructure(unittest.TestCase):
    """Test module structure and exports."""
    
    def test_version_defined(self):
        """Test version is defined."""
        from restcli import __version__
        self.assertIsInstance(__version__, str)
        self.assertIn(".", __version__)  # Version should have dot separator
    
    def test_main_function_exists(self):
        """Test main function exists."""
        from restcli import main
        self.assertTrue(callable(main))
    
    def test_command_functions_exist(self):
        """Test command functions exist."""
        from restcli import cmd_request, cmd_history, cmd_replay, cmd_env, cmd_collection
        
        self.assertTrue(callable(cmd_request))
        self.assertTrue(callable(cmd_history))
        self.assertTrue(callable(cmd_replay))
        self.assertTrue(callable(cmd_env))
        self.assertTrue(callable(cmd_collection))


class TestMakeRequestFunction(unittest.TestCase):
    """Test make_request function."""
    
    def test_make_request_exists(self):
        """Test make_request function exists."""
        from restcli import make_request
        self.assertTrue(callable(make_request))
    
    def test_make_request_signature(self):
        """Test make_request has correct signature."""
        from restcli import make_request
        import inspect
        
        sig = inspect.signature(make_request)
        params = list(sig.parameters.keys())
        
        self.assertIn('method', params)
        self.assertIn('url', params)


class TestPrintFunctions(unittest.TestCase):
    """Test print/display functions."""
    
    def test_print_banner_exists(self):
        """Test print_banner function exists."""
        from restcli import print_banner
        self.assertTrue(callable(print_banner))
    
    def test_print_request_info_exists(self):
        """Test print_request_info function exists."""
        from restcli import print_request_info
        self.assertTrue(callable(print_request_info))
    
    def test_print_response_info_exists(self):
        """Test print_response_info function exists."""
        from restcli import print_response_info
        self.assertTrue(callable(print_response_info))


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: RestCLI v1.1.0")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestJsonOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestDataDirectories))
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestColorClass))
    suite.addTests(loader.loadTestsFromTestCase(TestModuleStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestMakeRequestFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestPrintFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    print(f"[OK] Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
