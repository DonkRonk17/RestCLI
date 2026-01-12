#!/usr/bin/env python3
"""
RestCLI v1.0.0 - Smart REST API Testing Tool
A powerful yet simple CLI tool for testing REST APIs with zero dependencies.

Author: Logan Smith / Metaphy LLC
License: MIT
GitHub: https://github.com/DonkRonk17/RestCLI
"""

import sys
import io
import json
import urllib.request
import urllib.error
import urllib.parse
import time
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Ensure UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

__version__ = "1.0.0"

# Data storage paths
DATA_DIR = Path.home() / ".restcli"
HISTORY_FILE = DATA_DIR / "history.json"
COLLECTIONS_DIR = DATA_DIR / "collections"
ENV_FILE = DATA_DIR / "environment.json"


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'


def ensure_data_dirs():
    """Create data directories if they don't exist"""
    DATA_DIR.mkdir(exist_ok=True)
    COLLECTIONS_DIR.mkdir(exist_ok=True)
    
    if not HISTORY_FILE.exists():
        save_json(HISTORY_FILE, [])
    
    if not ENV_FILE.exists():
        save_json(ENV_FILE, {})


def save_json(filepath: Path, data: Any):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Any:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] if 'history' in str(filepath) else {}


def replace_env_vars(text: str, env: Dict[str, str]) -> str:
    """Replace {{VAR}} with environment variable values"""
    result = text
    for key, value in env.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def parse_headers(header_list: List[str]) -> Dict[str, str]:
    """Parse header strings in format 'Key: Value'"""
    headers = {}
    for header in header_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers


def format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def print_banner():
    """Print RestCLI banner"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════╗
║  {Colors.BOLD}RestCLI v{__version__}{Colors.RESET}{Colors.CYAN} - Smart REST API Testing     ║
║  Zero dependencies • Simple • Powerful            ║
╚═══════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_request_info(method: str, url: str, headers: Dict[str, str], body: Optional[str]):
    """Print formatted request information"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}→ Request{Colors.RESET}")
    print(f"{Colors.BOLD}{method.upper()}{Colors.RESET} {url}")
    
    if headers:
        print(f"\n{Colors.GRAY}Headers:{Colors.RESET}")
        for key, value in headers.items():
            print(f"  {Colors.CYAN}{key}:{Colors.RESET} {value}")
    
    if body:
        print(f"\n{Colors.GRAY}Body:{Colors.RESET}")
        try:
            formatted = json.dumps(json.loads(body), indent=2)
            print(formatted)
        except json.JSONDecodeError:
            print(body)


def print_response_info(response: urllib.request.http.client.HTTPResponse, 
                       body: str, duration: float):
    """Print formatted response information"""
    status_code = response.status
    status_color = Colors.GREEN if 200 <= status_code < 300 else Colors.YELLOW if 300 <= status_code < 400 else Colors.RED
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}← Response{Colors.RESET}")
    print(f"{status_color}{Colors.BOLD}{status_code} {response.reason}{Colors.RESET}")
    print(f"{Colors.GRAY}Time: {format_duration(duration)}{Colors.RESET}")
    print(f"{Colors.GRAY}Size: {format_size(len(body.encode('utf-8')))}{Colors.RESET}")
    
    # Print response headers
    print(f"\n{Colors.GRAY}Headers:{Colors.RESET}")
    for key, value in response.headers.items():
        print(f"  {Colors.CYAN}{key}:{Colors.RESET} {value}")
    
    # Print response body
    print(f"\n{Colors.GRAY}Body:{Colors.RESET}")
    content_type = response.headers.get('Content-Type', '')
    
    if 'application/json' in content_type:
        try:
            formatted = json.dumps(json.loads(body), indent=2)
            print(formatted)
        except json.JSONDecodeError:
            print(body)
    else:
        # Show first 1000 chars for non-JSON
        if len(body) > 1000:
            print(body[:1000])
            print(f"\n{Colors.GRAY}... ({len(body) - 1000} more characters){Colors.RESET}")
        else:
            print(body)


def make_request(method: str, url: str, headers: Optional[Dict[str, str]] = None,
                body: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    """Make HTTP request and return response details"""
    
    if headers is None:
        headers = {}
    
    # Set default headers
    if 'User-Agent' not in headers:
        headers['User-Agent'] = f'RestCLI/{__version__}'
    
    # Prepare request data
    data = None
    if body:
        data = body.encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
    
    # Create request
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method.upper()
    )
    
    # Make request and measure time
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode('utf-8', errors='replace')
            duration = time.time() - start_time
            
            return {
                'success': True,
                'status': response.status,
                'reason': response.reason,
                'headers': dict(response.headers),
                'body': response_body,
                'duration': duration,
                'size': len(response_body.encode('utf-8'))
            }
    
    except urllib.error.HTTPError as e:
        duration = time.time() - start_time
        error_body = e.read().decode('utf-8', errors='replace')
        
        return {
            'success': False,
            'status': e.code,
            'reason': e.reason,
            'headers': dict(e.headers),
            'body': error_body,
            'duration': duration,
            'size': len(error_body.encode('utf-8'))
        }
    
    except urllib.error.URLError as e:
        duration = time.time() - start_time
        return {
            'success': False,
            'error': str(e.reason),
            'duration': duration
        }
    
    except Exception as e:
        duration = time.time() - start_time
        return {
            'success': False,
            'error': str(e),
            'duration': duration
        }


def save_to_history(method: str, url: str, headers: Dict[str, str],
                   body: Optional[str], response: Dict[str, Any]):
    """Save request to history"""
    history = load_json(HISTORY_FILE)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'method': method.upper(),
        'url': url,
        'headers': headers,
        'body': body,
        'response': {
            'status': response.get('status'),
            'duration': response.get('duration'),
            'size': response.get('size')
        }
    }
    
    history.append(entry)
    
    # Keep only last 100 entries
    if len(history) > 100:
        history = history[-100:]
    
    save_json(HISTORY_FILE, history)


def cmd_request(args):
    """Execute HTTP request"""
    ensure_data_dirs()
    
    # Load environment variables
    env = load_json(ENV_FILE)
    
    # Replace env vars in URL
    url = replace_env_vars(args.url, env)
    
    # Parse headers
    headers = parse_headers(args.header) if args.header else {}
    
    # Replace env vars in headers
    for key in headers:
        headers[key] = replace_env_vars(headers[key], env)
    
    # Handle authentication
    if args.bearer:
        token = replace_env_vars(args.bearer, env)
        headers['Authorization'] = f'Bearer {token}'
    elif args.basic:
        import base64
        credentials = replace_env_vars(args.basic, env)
        encoded = base64.b64encode(credentials.encode()).decode()
        headers['Authorization'] = f'Basic {encoded}'
    elif args.api_key:
        key = replace_env_vars(args.api_key, env)
        headers[args.api_key_header] = key
    
    # Read body from file or argument
    body = None
    if args.data:
        body = replace_env_vars(args.data, env)
    elif args.data_file:
        try:
            with open(args.data_file, 'r', encoding='utf-8') as f:
                body = f.read()
            body = replace_env_vars(body, env)
        except Exception as e:
            print(f"{Colors.RED}✗ Error reading file: {e}{Colors.RESET}")
            return
    
    # Print request info if verbose
    if args.verbose:
        print_request_info(args.method, url, headers, body)
    
    # Make request
    print(f"\n{Colors.GRAY}Sending request...{Colors.RESET}")
    response = make_request(args.method, url, headers, body, args.timeout)
    
    # Handle errors
    if not response.get('success') and 'error' in response:
        print(f"\n{Colors.RED}✗ Error: {response['error']}{Colors.RESET}")
        print(f"{Colors.GRAY}Duration: {format_duration(response['duration'])}{Colors.RESET}")
        return
    
    # Print response
    if args.verbose:
        # Create a mock response object
        class MockResponse:
            def __init__(self, status, reason, headers):
                self.status = status
                self.reason = reason
                self.headers = headers
        
        mock_resp = MockResponse(
            response['status'],
            response['reason'],
            response['headers']
        )
        print_response_info(mock_resp, response['body'], response['duration'])
    else:
        # Simple output
        status_color = Colors.GREEN if response['status'] < 300 else Colors.YELLOW if response['status'] < 400 else Colors.RED
        print(f"\n{status_color}{Colors.BOLD}{response['status']} {response['reason']}{Colors.RESET}")
        print(f"{Colors.GRAY}Time: {format_duration(response['duration'])} | Size: {format_size(response['size'])}{Colors.RESET}")
        
        # Pretty print JSON body
        if response['body']:
            try:
                formatted = json.dumps(json.loads(response['body']), indent=2)
                print(f"\n{formatted}")
            except json.JSONDecodeError:
                print(f"\n{response['body']}")
    
    # Save to history
    save_to_history(args.method, url, headers, body, response)
    
    print(f"\n{Colors.GREEN}✓ Request saved to history{Colors.RESET}")


def cmd_history(args):
    """Show request history"""
    ensure_data_dirs()
    history = load_json(HISTORY_FILE)
    
    if not history:
        print(f"{Colors.YELLOW}No requests in history{Colors.RESET}")
        return
    
    # Show last N entries
    entries = history[-args.limit:] if args.limit else history
    
    print(f"\n{Colors.BOLD}Request History ({len(entries)} entries){Colors.RESET}\n")
    
    for i, entry in enumerate(reversed(entries), 1):
        timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        method = entry['method']
        url = entry['url']
        status = entry['response'].get('status', 'ERR')
        duration = entry['response'].get('duration', 0)
        
        status_color = Colors.GREEN if status < 300 else Colors.YELLOW if status < 400 else Colors.RED if status else Colors.GRAY
        
        print(f"{Colors.GRAY}{i:3d}.{Colors.RESET} {Colors.CYAN}{timestamp}{Colors.RESET} | "
              f"{Colors.BOLD}{method:6s}{Colors.RESET} | "
              f"{status_color}{status}{Colors.RESET} | "
              f"{Colors.GRAY}{format_duration(duration)}{Colors.RESET} | "
              f"{url[:60]}")
    
    print(f"\n{Colors.GRAY}Use 'restcli replay <number>' to replay a request{Colors.RESET}")


def cmd_replay(args):
    """Replay a request from history"""
    ensure_data_dirs()
    history = load_json(HISTORY_FILE)
    
    if not history:
        print(f"{Colors.YELLOW}No requests in history{Colors.RESET}")
        return
    
    # Get entry by index (counting from end)
    try:
        index = -args.number
        entry = history[index]
    except IndexError:
        print(f"{Colors.RED}✗ Invalid history index: {args.number}{Colors.RESET}")
        return
    
    # Recreate request
    print(f"{Colors.CYAN}Replaying request from {entry['timestamp']}{Colors.RESET}")
    
    # Make request
    response = make_request(
        entry['method'],
        entry['url'],
        entry.get('headers', {}),
        entry.get('body'),
        30
    )
    
    # Print response
    status_color = Colors.GREEN if response.get('status', 0) < 300 else Colors.RED
    print(f"\n{status_color}{Colors.BOLD}{response.get('status', 'ERR')} {response.get('reason', 'Error')}{Colors.RESET}")
    print(f"{Colors.GRAY}Time: {format_duration(response['duration'])}{Colors.RESET}")
    
    if response.get('body'):
        try:
            formatted = json.dumps(json.loads(response['body']), indent=2)
            print(f"\n{formatted}")
        except json.JSONDecodeError:
            print(f"\n{response['body']}")


def cmd_env(args):
    """Manage environment variables"""
    ensure_data_dirs()
    env = load_json(ENV_FILE)
    
    if args.action == 'set':
        if not args.key or not args.value:
            print(f"{Colors.RED}✗ Both key and value required for 'set'{Colors.RESET}")
            return
        
        env[args.key] = args.value
        save_json(ENV_FILE, env)
        print(f"{Colors.GREEN}✓ Set {args.key} = {args.value}{Colors.RESET}")
    
    elif args.action == 'get':
        if args.key:
            value = env.get(args.key, '')
            if value:
                print(f"{args.key} = {value}")
            else:
                print(f"{Colors.YELLOW}Variable '{args.key}' not found{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Key required for 'get'{Colors.RESET}")
    
    elif args.action == 'list':
        if not env:
            print(f"{Colors.YELLOW}No environment variables set{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}Environment Variables{Colors.RESET}\n")
        for key, value in sorted(env.items()):
            print(f"  {Colors.CYAN}{key}{Colors.RESET} = {value}")
    
    elif args.action == 'delete':
        if not args.key:
            print(f"{Colors.RED}✗ Key required for 'delete'{Colors.RESET}")
            return
        
        if args.key in env:
            del env[args.key]
            save_json(ENV_FILE, env)
            print(f"{Colors.GREEN}✓ Deleted {args.key}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Variable '{args.key}' not found{Colors.RESET}")


def cmd_collection(args):
    """Manage request collections"""
    ensure_data_dirs()
    
    if args.action == 'save':
        if not args.name:
            print(f"{Colors.RED}✗ Collection name required{Colors.RESET}")
            return
        
        # Get last request from history
        history = load_json(HISTORY_FILE)
        if not history:
            print(f"{Colors.YELLOW}No requests in history to save{Colors.RESET}")
            return
        
        last_request = history[-1]
        
        # Save to collection file
        collection_file = COLLECTIONS_DIR / f"{args.name}.json"
        save_json(collection_file, last_request)
        
        print(f"{Colors.GREEN}✓ Saved last request to collection '{args.name}'{Colors.RESET}")
    
    elif args.action == 'load':
        if not args.name:
            print(f"{Colors.RED}✗ Collection name required{Colors.RESET}")
            return
        
        collection_file = COLLECTIONS_DIR / f"{args.name}.json"
        if not collection_file.exists():
            print(f"{Colors.YELLOW}Collection '{args.name}' not found{Colors.RESET}")
            return
        
        request = load_json(collection_file)
        
        # Execute request
        print(f"{Colors.CYAN}Loading collection '{args.name}'{Colors.RESET}")
        
        response = make_request(
            request['method'],
            request['url'],
            request.get('headers', {}),
            request.get('body'),
            30
        )
        
        # Print response
        status_color = Colors.GREEN if response.get('status', 0) < 300 else Colors.RED
        print(f"\n{status_color}{Colors.BOLD}{response.get('status', 'ERR')} {response.get('reason', 'Error')}{Colors.RESET}")
        print(f"{Colors.GRAY}Time: {format_duration(response['duration'])}{Colors.RESET}")
        
        if response.get('body'):
            try:
                formatted = json.dumps(json.loads(response['body']), indent=2)
                print(f"\n{formatted}")
            except json.JSONDecodeError:
                print(f"\n{response['body']}")
    
    elif args.action == 'list':
        collections = list(COLLECTIONS_DIR.glob('*.json'))
        
        if not collections:
            print(f"{Colors.YELLOW}No collections saved{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}Saved Collections{Colors.RESET}\n")
        for collection in sorted(collections):
            name = collection.stem
            request = load_json(collection)
            method = request.get('method', 'GET')
            url = request.get('url', '')
            
            print(f"  {Colors.CYAN}{name}{Colors.RESET} - {Colors.BOLD}{method}{Colors.RESET} {url[:50]}")
    
    elif args.action == 'delete':
        if not args.name:
            print(f"{Colors.RED}✗ Collection name required{Colors.RESET}")
            return
        
        collection_file = COLLECTIONS_DIR / f"{args.name}.json"
        if collection_file.exists():
            collection_file.unlink()
            print(f"{Colors.GREEN}✓ Deleted collection '{args.name}'{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Collection '{args.name}' not found{Colors.RESET}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RestCLI - Smart REST API Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  restcli get https://api.github.com/users/octocat
  restcli post https://api.example.com/users -d '{"name": "John"}'
  restcli get https://api.example.com/data -H "Authorization: Bearer {{TOKEN}}"
  restcli env set TOKEN abc123
  restcli history
  restcli replay 1
  restcli collection save myrequest
  restcli collection load myrequest
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # HTTP methods (GET, POST, PUT, DELETE, PATCH)
    for method in ['get', 'post', 'put', 'delete', 'patch']:
        method_parser = subparsers.add_parser(method, help=f'{method.upper()} request')
        method_parser.add_argument('url', help='Request URL')
        method_parser.add_argument('-H', '--header', action='append', help='Request header (can be used multiple times)')
        method_parser.add_argument('-d', '--data', help='Request body data')
        method_parser.add_argument('-f', '--data-file', help='Read body from file')
        method_parser.add_argument('--bearer', help='Bearer token authentication')
        method_parser.add_argument('--basic', help='Basic authentication (username:password)')
        method_parser.add_argument('--api-key', help='API key value')
        method_parser.add_argument('--api-key-header', default='X-API-Key', help='API key header name (default: X-API-Key)')
        method_parser.add_argument('-t', '--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
        method_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        method_parser.set_defaults(method=method, func=cmd_request)
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show request history')
    history_parser.add_argument('-l', '--limit', type=int, help='Limit number of entries')
    history_parser.set_defaults(func=cmd_history)
    
    # Replay command
    replay_parser = subparsers.add_parser('replay', help='Replay request from history')
    replay_parser.add_argument('number', type=int, help='History entry number (from most recent)')
    replay_parser.set_defaults(func=cmd_replay)
    
    # Environment command
    env_parser = subparsers.add_parser('env', help='Manage environment variables')
    env_parser.add_argument('action', choices=['set', 'get', 'list', 'delete'], help='Action to perform')
    env_parser.add_argument('key', nargs='?', help='Variable key')
    env_parser.add_argument('value', nargs='?', help='Variable value')
    env_parser.set_defaults(func=cmd_env)
    
    # Collection command
    collection_parser = subparsers.add_parser('collection', help='Manage request collections')
    collection_parser.add_argument('action', choices=['save', 'load', 'list', 'delete'], help='Action to perform')
    collection_parser.add_argument('name', nargs='?', help='Collection name')
    collection_parser.set_defaults(func=cmd_collection)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
