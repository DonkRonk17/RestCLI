# 🌐 RestCLI - Integration Plan

**Version:** 1.1.0  
**Last Updated:** January 24, 2026  
**Author:** ATLAS (Team Brain)

---

## 🎯 INTEGRATION GOALS

This document outlines how RestCLI integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools
3. BCH (Beacon Command Hub) - if applicable
4. Logan's workflows

---

## 📦 BCH INTEGRATION

### Overview

RestCLI can be integrated into BCH (Beacon Command Hub) as an API testing utility. This allows agents to test API endpoints, verify server health, and debug connectivity issues directly from BCH commands.

### BCH Commands (Proposed)

```
@restcli get <url>           - Quick GET request
@restcli post <url> <json>   - POST with JSON body
@restcli test <collection>   - Run saved collection
@restcli health              - Test all registered APIs
```

### Implementation Steps

1. **Add to BCH imports:**
   ```python
   import subprocess
   from pathlib import Path
   
   RESTCLI_PATH = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"
   ```

2. **Create command handler:**
   ```python
   async def handle_restcli(args: list, context: dict) -> str:
       """Handle @restcli commands in BCH."""
       cmd = ' '.join(args)
       result = subprocess.run(
           f"python {RESTCLI_PATH} {cmd}",
           shell=True,
           capture_output=True,
           text=True
       )
       return result.stdout or result.stderr
   ```

3. **Register with command router:**
   ```python
   COMMANDS["restcli"] = handle_restcli
   ```

4. **Test integration:**
   ```
   BCH> @restcli get https://api.github.com/zen
   BCH> @restcli history -l 5
   ```

### Use Cases in BCH

1. **API Health Checks:**
   - Test if backend services are responding
   - Verify authentication tokens are valid
   - Check API rate limits

2. **Development Testing:**
   - Quick API calls without leaving BCH
   - Test new endpoints during development
   - Debug request/response issues

3. **Automation:**
   - Scheduled API health monitoring
   - Automated test suites via collections

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Primary Use Case | Integration Method | Priority |
|-------|------------------|-------------------|----------|
| **Forge** | API spec verification, review API responses | CLI + Python | HIGH |
| **Atlas** | Test APIs during tool development | CLI + Python | HIGH |
| **Clio** | Linux API testing, server health checks | CLI | MEDIUM |
| **Nexus** | Cross-platform API validation | CLI + Python | MEDIUM |
| **Bolt** | Bulk API testing, automation scripts | CLI | LOW |

---

### Agent-Specific Workflows

#### 🔥 Forge (Orchestrator / Reviewer)

**Primary Use Case:** Verify API specifications match actual responses during code review.

**Integration Steps:**
1. Import RestCLI functionality
2. Create validation wrapper
3. Add to review checklist

**Example Workflow:**
```python
# forge_api_validation.py
import subprocess
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from synapselink import quick_send

def validate_api_endpoint(url: str, expected_fields: list) -> dict:
    """Validate API endpoint returns expected fields."""
    result = subprocess.run(
        f"python restcli.py get {url}",
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(Path.home() / "OneDrive/Documents/AutoProjects/RestCLI")
    )
    
    # Parse JSON from output (skip status line)
    lines = result.stdout.strip().split('\n')
    json_lines = []
    in_json = False
    for line in lines:
        if line.strip().startswith('{'):
            in_json = True
        if in_json:
            json_lines.append(line)
    
    try:
        data = json.loads('\n'.join(json_lines))
    except json.JSONDecodeError:
        return {"valid": False, "error": "Could not parse JSON response"}
    
    # Check expected fields
    missing = [f for f in expected_fields if f not in data]
    
    if missing:
        return {
            "valid": False,
            "missing_fields": missing,
            "response": data
        }
    
    return {"valid": True, "response": data}

# Example usage in Forge review
result = validate_api_endpoint(
    "https://api.github.com/users/octocat",
    ["login", "id", "name", "email"]
)

if result["valid"]:
    print("[OK] API response matches specification")
else:
    print(f"[!] Missing fields: {result.get('missing_fields')}")
    quick_send("LOGAN", "API Validation Issue", 
               f"Missing fields in response: {result.get('missing_fields')}")
```

**Forge Review Checklist:**
- [ ] API endpoints documented
- [ ] Response format matches spec
- [ ] Authentication working
- [ ] Error responses handled

---

#### ⚡ Atlas (Executor / Builder)

**Primary Use Case:** Test APIs during tool development and debugging.

**Integration Steps:**
1. Add RestCLI to tool build workflow
2. Create test helpers for API-dependent tools
3. Use for debugging network issues

**Example Workflow:**
```python
# atlas_api_testing.py - Part of tool development workflow
import subprocess
import sys
from pathlib import Path

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def test_api_during_build(api_url: str, method: str = "get", data: str = None) -> bool:
    """Quick API test during tool development."""
    cmd = f"python {RESTCLI} {method} {api_url}"
    if data:
        cmd += f" -d '{data}'"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Check for success (200-299 status codes)
    if "200" in result.stdout or "201" in result.stdout:
        print(f"[OK] API test passed: {method.upper()} {api_url}")
        return True
    else:
        print(f"[X] API test failed: {method.upper()} {api_url}")
        print(result.stdout)
        return False

# During tool development:
# 1. Test external API dependencies
test_api_during_build("https://api.github.com/zen")

# 2. Test POST operations
test_api_during_build(
    "https://jsonplaceholder.typicode.com/posts",
    method="post",
    data='{"title": "Test", "body": "Content", "userId": 1}'
)

# 3. Save common requests for repeated testing
subprocess.run(f"python {RESTCLI} collection save dev_test", shell=True)
```

**Atlas Build Integration:**
```python
# Add to tool build checklist
def verify_api_dependencies():
    """Check all API dependencies before finalizing tool."""
    apis = [
        "https://api.github.com/zen",  # GitHub status
        # Add other APIs your tool depends on
    ]
    
    all_ok = True
    for api in apis:
        if not test_api_during_build(api):
            all_ok = False
    
    return all_ok
```

---

#### 🐧 Clio (Linux / Ubuntu Agent)

**Primary Use Case:** Server health monitoring and API testing on Linux systems.

**Platform Considerations:**
- RestCLI works identically on Linux
- Can be added to cron for scheduled testing
- Integrates with Linux monitoring tools

**Example:**
```bash
#!/bin/bash
# clio_api_monitor.sh - Run via cron for monitoring

cd ~/Documents/AutoProjects/RestCLI

# Test critical APIs
python3 restcli.py get https://api.example.com/health > /tmp/api_health.log 2>&1

# Check result
if grep -q "200 OK" /tmp/api_health.log; then
    echo "[OK] API healthy"
else
    # Alert via SynapseLink
    python3 -c "
from synapselink import quick_send
quick_send('FORGE,LOGAN', 'API Health Alert', 'API not responding!', priority='HIGH')
"
fi
```

**Cron Setup:**
```bash
# Add to crontab -e
*/15 * * * * /home/user/scripts/clio_api_monitor.sh
```

---

#### 🌐 Nexus (Multi-Platform Agent)

**Primary Use Case:** Cross-platform API validation and compatibility testing.

**Cross-Platform Notes:**
- RestCLI uses Python pathlib for cross-platform paths
- UTF-8 encoding handled automatically
- Works on Windows, Linux, macOS

**Example:**
```python
# nexus_cross_platform_test.py
import platform
import subprocess
from pathlib import Path

def get_restcli_path():
    """Get RestCLI path based on platform."""
    home = Path.home()
    
    if platform.system() == "Windows":
        return home / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"
    else:  # Linux/macOS
        return home / "Documents/AutoProjects/RestCLI/restcli.py"

def test_on_current_platform():
    """Run API tests on current platform."""
    restcli = get_restcli_path()
    
    print(f"Testing on {platform.system()}")
    print(f"RestCLI path: {restcli}")
    
    result = subprocess.run(
        f"python {restcli} get https://api.github.com/zen",
        shell=True,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    return "200 OK" in result.stdout

# Run test
if test_on_current_platform():
    print(f"[OK] RestCLI works on {platform.system()}")
else:
    print(f"[X] RestCLI issue on {platform.system()}")
```

---

#### 🆓 Bolt (Cline / Free Executor)

**Primary Use Case:** Bulk API testing and automation without API costs.

**Cost Considerations:**
- RestCLI is 100% free (no API costs)
- Perfect for repetitive testing
- Use for automated test suites

**Example:**
```bash
# bolt_bulk_test.sh - Bulk API testing
#!/bin/bash

cd ~/Documents/AutoProjects/RestCLI

# Test multiple endpoints
ENDPOINTS=(
    "https://api.github.com/zen"
    "https://jsonplaceholder.typicode.com/posts/1"
    "https://httpbin.org/get"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Testing: $endpoint"
    python restcli.py get "$endpoint" | head -5
    echo "---"
done

# Save history for review
python restcli.py history -l 10
```

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With AgentHealth

**Correlation Use Case:** Track API testing sessions alongside agent health.

**Integration Pattern:**
```python
from agenthealth import AgentHealth
import subprocess
from pathlib import Path

health = AgentHealth()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Start health tracking
session_id = "api_test_session_001"
health.start_session("ATLAS", session_id=session_id)

try:
    # Run API tests
    result = subprocess.run(
        f"python {RESTCLI} get https://api.github.com/zen",
        shell=True,
        capture_output=True,
        text=True
    )
    
    # Log activity
    health.heartbeat("ATLAS", status="testing_apis")
    
    if "200 OK" in result.stdout:
        health.log_event("ATLAS", "api_test_success", {"url": "github.com/zen"})
    else:
        health.log_error("ATLAS", "API test failed")

finally:
    health.end_session("ATLAS", session_id=session_id)
```

---

### With SynapseLink

**Notification Use Case:** Alert team on API test results.

**Integration Pattern:**
```python
from synapselink import quick_send
import subprocess
from pathlib import Path

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_api_test(url: str) -> tuple:
    """Run API test and return success status and output."""
    result = subprocess.run(
        f"python {RESTCLI} get {url}",
        shell=True,
        capture_output=True,
        text=True
    )
    success = "200" in result.stdout or "201" in result.stdout
    return success, result.stdout

# Test and notify
url = "https://api.example.com/health"
success, output = run_api_test(url)

if success:
    quick_send(
        "TEAM",
        "API Test: SUCCESS",
        f"Endpoint {url} is responding correctly.\n\n{output[:500]}",
        priority="NORMAL"
    )
else:
    quick_send(
        "FORGE,LOGAN",
        "API Test: FAILED",
        f"Endpoint {url} is not responding!\n\n{output}",
        priority="HIGH"
    )
```

---

### With TaskQueuePro

**Task Management Use Case:** Track API testing as formal tasks.

**Integration Pattern:**
```python
from taskqueuepro import TaskQueuePro
import subprocess
from pathlib import Path

queue = TaskQueuePro()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Create task
task_id = queue.create_task(
    title="API Integration Test Suite",
    agent="ATLAS",
    priority=2,
    metadata={
        "tool": "RestCLI",
        "endpoints": ["github.com", "jsonplaceholder.com"]
    }
)

queue.start_task(task_id)

try:
    # Run tests
    endpoints = [
        "https://api.github.com/zen",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    results = {}
    for endpoint in endpoints:
        result = subprocess.run(
            f"python {RESTCLI} get {endpoint}",
            shell=True,
            capture_output=True,
            text=True
        )
        results[endpoint] = "200" in result.stdout
    
    # Complete task
    all_passed = all(results.values())
    queue.complete_task(
        task_id,
        result={
            "status": "success" if all_passed else "partial_failure",
            "results": results
        }
    )

except Exception as e:
    queue.fail_task(task_id, error=str(e))
```

---

### With MemoryBridge

**Context Persistence Use Case:** Store API test history in memory core.

**Integration Pattern:**
```python
from memorybridge import MemoryBridge
import subprocess
import json
from pathlib import Path
from datetime import datetime

memory = MemoryBridge()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Load API test history
api_history = memory.get("restcli_test_history", default=[])

# Run test
result = subprocess.run(
    f"python {RESTCLI} get https://api.github.com/zen",
    shell=True,
    capture_output=True,
    text=True
)

# Record result
api_history.append({
    "timestamp": datetime.now().isoformat(),
    "url": "https://api.github.com/zen",
    "success": "200" in result.stdout,
    "agent": "ATLAS"
})

# Keep last 100 entries
if len(api_history) > 100:
    api_history = api_history[-100:]

# Save to memory core
memory.set("restcli_test_history", api_history)
memory.sync()
```

---

### With SessionReplay

**Debugging Use Case:** Record API test sessions for later replay.

**Integration Pattern:**
```python
from sessionreplay import SessionReplay
import subprocess
from pathlib import Path

replay = SessionReplay()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Start recording
session_id = replay.start_session("ATLAS", task="API Integration Testing")

# Log test start
replay.log_input(session_id, "Starting API test suite with RestCLI")

# Run tests
urls = [
    "https://api.github.com/zen",
    "https://jsonplaceholder.typicode.com/posts/1"
]

for url in urls:
    replay.log_input(session_id, f"Testing: {url}")
    
    result = subprocess.run(
        f"python {RESTCLI} get {url}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    replay.log_output(session_id, result.stdout[:500])

# End session
replay.end_session(session_id, status="COMPLETED")
```

---

### With ContextCompressor

**Token Optimization Use Case:** Compress API response data before sharing.

**Integration Pattern:**
```python
from contextcompressor import ContextCompressor
import subprocess
from pathlib import Path

compressor = ContextCompressor()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Get large API response
result = subprocess.run(
    f"python {RESTCLI} get https://api.github.com/users/octocat/repos",
    shell=True,
    capture_output=True,
    text=True
)

# Compress for sharing
compressed = compressor.compress_text(
    result.stdout,
    query="repository names and descriptions",
    method="summary"
)

print(f"Original: {len(result.stdout)} chars")
print(f"Compressed: {len(compressed.compressed_text)} chars")
print(f"Savings: {compressed.compression_ratio:.1%}")
```

---

### With ConfigManager

**Configuration Use Case:** Centralize RestCLI settings.

**Integration Pattern:**
```python
from configmanager import ConfigManager
import subprocess
from pathlib import Path

config = ConfigManager()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Load RestCLI config
restcli_config = config.get("restcli", {
    "default_timeout": 30,
    "verbose_by_default": False,
    "common_endpoints": {
        "github_zen": "https://api.github.com/zen",
        "jsonplaceholder": "https://jsonplaceholder.typicode.com"
    }
})

# Use configured endpoints
for name, url in restcli_config["common_endpoints"].items():
    timeout = restcli_config["default_timeout"]
    
    result = subprocess.run(
        f"python {RESTCLI} get {url} -t {timeout}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    print(f"[{name}]: {'OK' if '200' in result.stdout else 'FAIL'}")
```

---

### With CollabSession

**Coordination Use Case:** Multi-agent API testing coordination.

**Integration Pattern:**
```python
from collabsession import CollabSession
import subprocess
from pathlib import Path

collab = CollabSession()
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Start collaboration session
session_id = collab.start_session(
    "api_integration_test",
    participants=["ATLAS", "CLIO"]
)

# ATLAS handles GitHub API tests
collab.lock_resource(session_id, "github_api", "ATLAS")

try:
    result = subprocess.run(
        f"python {RESTCLI} get https://api.github.com/zen",
        shell=True,
        capture_output=True,
        text=True
    )
    
    collab.add_note(session_id, "ATLAS", f"GitHub API: {'OK' if '200' in result.stdout else 'FAIL'}")

finally:
    collab.unlock_resource(session_id, "github_api")
    collab.end_session(session_id)
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)

**Goal:** All agents aware and can use basic features

**Steps:**
1. ✅ Tool deployed to GitHub
2. ☐ Quick-start guides sent via Synapse
3. ☐ Each agent tests basic workflow
4. ☐ Feedback collected

**Success Criteria:**
- All 5 agents have used RestCLI at least once
- No blocking issues reported

### Phase 2: Integration (Week 2-3)

**Goal:** Integrated into daily workflows

**Steps:**
1. ☐ Add to BCH command palette
2. ☐ Create integration examples with existing tools
3. ☐ Update agent-specific workflows
4. ☐ Monitor usage patterns

**Success Criteria:**
- Used daily by at least 3 agents
- Integration examples tested

### Phase 3: Optimization (Week 4+)

**Goal:** Optimized and fully adopted

**Steps:**
1. ☐ Collect efficiency metrics
2. ☐ Implement v1.2 improvements
3. ☐ Create advanced workflow examples
4. ☐ Full Team Brain ecosystem integration

**Success Criteria:**
- Measurable time savings (5+ min/day)
- Positive feedback from all agents
- v1.2 improvements identified

---

## 📊 SUCCESS METRICS

**Adoption Metrics:**
- Number of agents using tool: Target 5/5
- Daily usage count: Track via history.json
- Integration with other tools: 5+ integrations

**Efficiency Metrics:**
- Time saved per API test: ~2-5 minutes vs curl
- Reduced context switching: All testing from CLI
- Debugging time reduction: History + replay features

**Quality Metrics:**
- Bug reports: Track via GitHub Issues
- Feature requests: Collect via Synapse
- User satisfaction: Qualitative feedback

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths

```python
# For subprocess calls (most common)
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Full command
f"python {RESTCLI} <command>"
```

### Configuration Integration

**Config File:** `~/.restcli/environment.json`

**Shared Config Example:**
```json
{
  "API_URL": "https://api.example.com",
  "TOKEN": "your_token_here",
  "VERSION": "v1"
}
```

### Error Handling Integration

**Standard Return Codes:**
- 0: Success (200-299 status)
- 1: Error (network, timeout, auth)

**Parsing Response:**
```python
result = subprocess.run(...)
if result.returncode == 0:
    # Parse JSON from stdout
else:
    # Handle error from stderr
```

### Logging Integration

**Log Format:** Compatible with Team Brain standard

**Log Location:** `~/.restcli/history.json`

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy
- Minor updates (v1.x): Monthly
- Major updates (v2.0+): Quarterly
- Security patches: Immediate

### Support Channels
- GitHub Issues: Bug reports
- Synapse: Team Brain discussions
- Direct to Builder: Complex issues

### Known Limitations
- No GraphQL support (REST only)
- No streaming responses
- Limited to JSON content type

### Planned Improvements (v1.2)
- [ ] Response body filtering (jq-like)
- [ ] Request chaining
- [ ] Performance benchmarking
- [ ] Export to curl format

---

## 📚 ADDITIONAL RESOURCES

- Main Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Quick Start Guides: [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- GitHub: https://github.com/DonkRonk17/RestCLI

---

**Last Updated:** January 24, 2026  
**Maintained By:** ATLAS (Team Brain)  
**For:** Logan Smith / Metaphy LLC
