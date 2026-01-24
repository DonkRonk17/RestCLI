# 🌐 RestCLI - Quick Start Guides

**Version:** 1.1.0  
**Last Updated:** January 24, 2026

---

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Use RestCLI to verify API responses during code review

### Step 1: Verify Installation

```bash
# Navigate to RestCLI
cd C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI

# Check it works
python restcli.py --help
```

**Expected:** Help menu displays with all commands.

### Step 2: First API Test

```bash
# Quick test - GitHub Zen API
python restcli.py get https://api.github.com/zen
```

**Expected:** 200 OK with a GitHub quote.

### Step 3: Validate API Response Structure

```bash
# Get structured data
python restcli.py get https://api.github.com/users/octocat

# Check for expected fields visually
# Should see: login, id, name, company, location
```

### Step 4: Save Common Validation Requests

```bash
# Test an endpoint
python restcli.py get https://api.github.com/users/octocat

# Save it for repeated use
python restcli.py collection save github_user_check

# Later, quick validation:
python restcli.py collection load github_user_check
```

### Forge Review Workflow Integration

```python
# forge_api_review.py - Use during code reviews
import subprocess
from pathlib import Path

RESTCLI = Path(r"C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI\restcli.py")

def verify_endpoint(url: str, expected_fields: list) -> bool:
    """Verify API returns expected fields."""
    result = subprocess.run(
        f"python {RESTCLI} get {url}",
        shell=True, capture_output=True, text=True
    )
    
    for field in expected_fields:
        if f'"{field}"' not in result.stdout:
            print(f"[!] Missing field: {field}")
            return False
    
    print(f"[OK] All fields present in {url}")
    return True

# During review:
verify_endpoint(
    "https://api.github.com/users/octocat",
    ["login", "id", "name"]
)
```

### Next Steps for Forge
1. Read [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Forge section
2. Create collections for common review endpoints
3. Add API validation to review checklist

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Use RestCLI during tool development for API testing

### Step 1: Verify Setup

```bash
# Navigate to RestCLI
cd C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI

# Run self-test
python test_restcli.py
```

**Expected:** All 47 tests pass.

### Step 2: Quick API Test

```bash
# Test any API endpoint
python restcli.py get https://api.github.com/zen

# With verbose mode for debugging
python restcli.py get https://api.github.com/zen -v
```

### Step 3: POST Request Testing

```bash
# Test POST to mock API
python restcli.py post https://jsonplaceholder.typicode.com/posts \
    -d '{"title": "Test", "body": "Content", "userId": 1}'
```

**Expected:** 201 Created with new resource ID.

### Step 4: Environment Variables for Development

```bash
# Set up development environment
python restcli.py env set DEV_API https://jsonplaceholder.typicode.com
python restcli.py env set TEST_TOKEN dev_token_123

# Use in requests
python restcli.py get {{DEV_API}}/posts/1
python restcli.py post {{DEV_API}}/posts -d '{"title": "Test"}' --bearer {{TEST_TOKEN}}
```

### Atlas Development Workflow

```python
# atlas_dev_testing.py - Quick API tests during builds
import subprocess
from pathlib import Path

RESTCLI = Path(r"C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI\restcli.py")

def quick_test(url: str) -> bool:
    """Quick API availability test."""
    result = subprocess.run(
        f"python {RESTCLI} get {url}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout

# During tool development:
if quick_test("https://api.github.com/zen"):
    print("[OK] External API available - proceeding with build")
else:
    print("[!] External API down - check network")
```

### Next Steps for Atlas
1. Add RestCLI tests to tool build workflow
2. Create collections for common test APIs
3. Use history replay for debugging

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** API testing and monitoring on Linux systems

### Step 1: Linux Installation

```bash
# Clone from GitHub
cd ~/Documents/AutoProjects
git clone https://github.com/DonkRonk17/RestCLI.git
cd RestCLI

# Verify Python 3
python3 --version  # Should be 3.6+

# Test
python3 restcli.py --help
```

### Step 2: First Request

```bash
# Simple GET
python3 restcli.py get https://api.github.com/zen

# With verbose output
python3 restcli.py get https://api.github.com/zen -v
```

### Step 3: Create Alias (Optional)

```bash
# Add to ~/.bashrc
echo 'alias restcli="python3 ~/Documents/AutoProjects/RestCLI/restcli.py"' >> ~/.bashrc
source ~/.bashrc

# Now use directly
restcli get https://api.github.com/zen
```

### Step 4: API Monitoring Script

```bash
#!/bin/bash
# clio_api_health.sh - Put in ~/scripts/

RESTCLI="python3 ~/Documents/AutoProjects/RestCLI/restcli.py"

# Check critical endpoints
endpoints=(
    "https://api.github.com/zen"
    "https://jsonplaceholder.typicode.com/posts/1"
)

for url in "${endpoints[@]}"; do
    result=$($RESTCLI get "$url" 2>&1)
    if echo "$result" | grep -q "200 OK"; then
        echo "[OK] $url"
    else
        echo "[FAIL] $url"
    fi
done
```

### Step 5: Cron for Scheduled Monitoring

```bash
# Edit crontab
crontab -e

# Add line to check every hour
0 * * * * /home/user/scripts/clio_api_health.sh >> /var/log/api_health.log 2>&1
```

### Platform-Specific Features
- Works with bash pipes: `restcli get URL | jq '.name'`
- Combine with watch: `watch -n 60 'restcli get https://api.example.com/health'`
- Log to syslog: `restcli get URL | logger -t api_test`

### Next Steps for Clio
1. Create monitoring script for critical APIs
2. Set up cron for scheduled checks
3. Integrate with ABIOS for alerts

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Cross-platform API validation

### Step 1: Platform Detection

```python
# nexus_setup.py - Verify RestCLI on current platform
import platform
from pathlib import Path

# Detect platform and set path
if platform.system() == "Windows":
    RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"
else:
    RESTCLI = Path.home() / "Documents/AutoProjects/RestCLI/restcli.py"

print(f"Platform: {platform.system()}")
print(f"RestCLI: {RESTCLI}")
print(f"Exists: {RESTCLI.exists()}")
```

### Step 2: Cross-Platform Wrapper

```python
# nexus_restcli.py - Cross-platform RestCLI wrapper
import subprocess
import platform
from pathlib import Path

def get_restcli():
    """Get RestCLI path for current platform."""
    home = Path.home()
    if platform.system() == "Windows":
        return home / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"
    return home / "Documents/AutoProjects/RestCLI/restcli.py"

def api_test(url: str, method: str = "get") -> dict:
    """Run cross-platform API test."""
    restcli = get_restcli()
    
    result = subprocess.run(
        f"python {restcli} {method} {url}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    return {
        "success": result.returncode == 0,
        "platform": platform.system(),
        "output": result.stdout
    }

# Test
result = api_test("https://api.github.com/zen")
print(f"Test on {result['platform']}: {'OK' if result['success'] else 'FAIL'}")
```

### Step 3: Platform-Specific Tests

```python
# Test platform compatibility
def verify_cross_platform():
    """Verify RestCLI works on current platform."""
    tests = [
        ("GET", "https://api.github.com/zen"),
        ("POST", "https://jsonplaceholder.typicode.com/posts"),
    ]
    
    restcli = get_restcli()
    results = []
    
    for method, url in tests:
        result = subprocess.run(
            f"python {restcli} {method} {url}" + 
            (" -d '{\"test\": true}'" if method == "POST" else ""),
            shell=True,
            capture_output=True,
            text=True
        )
        results.append((method, url, result.returncode == 0))
    
    return results

# Run verification
for method, url, passed in verify_cross_platform():
    print(f"[{'OK' if passed else 'FAIL'}] {method} {url[:40]}...")
```

### Platform Considerations
- **Windows**: Paths with OneDrive work correctly
- **Linux**: Use python3 explicitly
- **macOS**: Same as Linux, python3 preferred

### Next Steps for Nexus
1. Test on all available platforms
2. Report any platform-specific issues
3. Create cross-platform test suite

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Bulk API testing without API costs

### Step 1: Verify Free Access

```bash
# No API key or payment needed!
cd C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI
python restcli.py --help

# RestCLI is 100% free - no tokens, no costs
```

### Step 2: Bulk Testing

```bash
# Test multiple endpoints quickly
python restcli.py get https://api.github.com/zen
python restcli.py get https://jsonplaceholder.typicode.com/posts/1
python restcli.py get https://httpbin.org/get

# View what we tested
python restcli.py history -l 5
```

### Step 3: Batch Script for Automation

```bash
# bolt_batch_test.bat (Windows)
@echo off
cd C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI

echo [INFO] Starting batch API tests...

python restcli.py get https://api.github.com/zen
python restcli.py get https://jsonplaceholder.typicode.com/posts/1
python restcli.py get https://httpbin.org/get

echo [INFO] Tests complete. History:
python restcli.py history -l 5
```

### Step 4: Save Reusable Test Suites

```bash
# Create test suite as collections
python restcli.py get https://api.github.com/zen
python restcli.py collection save test_github

python restcli.py get https://jsonplaceholder.typicode.com/posts/1
python restcli.py collection save test_jsonplaceholder

# Later, replay entire suite:
python restcli.py collection load test_github
python restcli.py collection load test_jsonplaceholder
```

### Cost-Free Benefits
- No API tokens needed
- No rate limits (beyond target APIs)
- Test as much as needed
- Perfect for CI/CD pipelines

### Automation Script

```python
# bolt_automation.py - Bulk testing without costs
import subprocess
from pathlib import Path

RESTCLI = Path(r"C:\Users\logan\OneDrive\Documents\AutoProjects\RestCLI\restcli.py")

def bulk_test(urls: list) -> dict:
    """Test multiple URLs and return results."""
    results = {}
    
    for url in urls:
        result = subprocess.run(
            f"python {RESTCLI} get {url}",
            shell=True,
            capture_output=True,
            text=True
        )
        results[url] = "200" in result.stdout
    
    return results

# Free bulk testing
urls = [
    "https://api.github.com/zen",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://httpbin.org/get"
]

for url, passed in bulk_test(urls).items():
    print(f"[{'OK' if passed else 'FAIL'}] {url}")
```

### Next Steps for Bolt
1. Create batch scripts for common tests
2. Build collection library for reuse
3. Integrate with CI/CD pipelines

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Integration Examples: [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/RestCLI/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS (tool builder)

---

## 🚀 COMMON FIRST TASKS

After setup, try these common tasks:

### 1. Quick Health Check
```bash
python restcli.py get https://api.github.com/zen
```

### 2. Test with Authentication
```bash
python restcli.py env set TOKEN your_token
python restcli.py get https://api.example.com/me --bearer {{TOKEN}}
```

### 3. Save Frequent Request
```bash
python restcli.py get https://your.api.com/endpoint
python restcli.py collection save my_request
```

### 4. View History
```bash
python restcli.py history -l 10
```

### 5. Replay Last Request
```bash
python restcli.py replay 1
```

---

**Last Updated:** January 24, 2026  
**Maintained By:** ATLAS (Team Brain)  
**For:** Logan Smith / Metaphy LLC
