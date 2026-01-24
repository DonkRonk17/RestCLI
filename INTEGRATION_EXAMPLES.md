# 🌐 RestCLI - Integration Examples

**Version:** 1.1.0  
**Last Updated:** January 24, 2026

---

## 🎯 INTEGRATION PHILOSOPHY

RestCLI is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: RestCLI + AgentHealth](#pattern-1-restcli--agenthealth)
2. [Pattern 2: RestCLI + SynapseLink](#pattern-2-restcli--synapselink)
3. [Pattern 3: RestCLI + TaskQueuePro](#pattern-3-restcli--taskqueuepro)
4. [Pattern 4: RestCLI + MemoryBridge](#pattern-4-restcli--memorybridge)
5. [Pattern 5: RestCLI + SessionReplay](#pattern-5-restcli--sessionreplay)
6. [Pattern 6: RestCLI + ContextCompressor](#pattern-6-restcli--contextcompressor)
7. [Pattern 7: RestCLI + ConfigManager](#pattern-7-restcli--configmanager)
8. [Pattern 8: RestCLI + CollabSession](#pattern-8-restcli--collabsession)
9. [Pattern 9: Multi-Tool API Testing Workflow](#pattern-9-multi-tool-api-testing-workflow)
10. [Pattern 10: Full Team Brain API Stack](#pattern-10-full-team-brain-api-stack)

---

## Pattern 1: RestCLI + AgentHealth

**Use Case:** Correlate API testing sessions with agent health monitoring

**Why:** Understand how API testing affects agent performance and track API health over time

**Code:**

```python
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from agenthealth import AgentHealth

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    """Run RestCLI command and return success status and output."""
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    success = "200" in result.stdout or "201" in result.stdout
    return success, result.stdout

# Initialize health tracking
health = AgentHealth()

# Start session with shared ID
session_id = f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
health.start_session("ATLAS", session_id=session_id)

try:
    # Log start of API testing
    health.heartbeat("ATLAS", status="testing_apis")
    
    # Run API tests
    endpoints = [
        "https://api.github.com/zen",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    results = {}
    for url in endpoints:
        success, output = run_restcli(f"get {url}")
        results[url] = success
        
        if success:
            health.log_event("ATLAS", "api_test_success", {"url": url})
        else:
            health.log_error("ATLAS", f"API test failed: {url}")
    
    # Log completion
    all_passed = all(results.values())
    health.heartbeat("ATLAS", status="completed" if all_passed else "partial_failure")

finally:
    health.end_session("ATLAS", session_id=session_id)

# Print results
for url, passed in results.items():
    print(f"[{'OK' if passed else 'FAIL'}] {url}")
```

**Result:** Correlated health and API test data for analysis

---

## Pattern 2: RestCLI + SynapseLink

**Use Case:** Notify Team Brain when API tests complete or fail

**Why:** Keep team informed of API status automatically

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from synapselink import quick_send

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    """Run RestCLI command and return success status and output."""
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    success = "200" in result.stdout or "201" in result.stdout
    return success, result.stdout

# Test critical API endpoint
url = "https://api.github.com/zen"
success, output = run_restcli(f"get {url}")

# Notify team based on result
if success:
    quick_send(
        "TEAM",
        "API Health Check: SUCCESS",
        f"Endpoint: {url}\n\n"
        f"Status: 200 OK\n\n"
        f"Response preview:\n{output[:300]}...",
        priority="NORMAL"
    )
    print("[OK] API healthy, team notified")
else:
    quick_send(
        "FORGE,LOGAN",
        "API Health Check: FAILED",
        f"Endpoint: {url}\n\n"
        f"Status: FAILED\n\n"
        f"Output:\n{output}\n\n"
        "Please investigate immediately.",
        priority="HIGH"
    )
    print("[!] API failed, team alerted")
```

**Result:** Team stays informed without manual status updates

---

## Pattern 3: RestCLI + TaskQueuePro

**Use Case:** Manage API testing as formal tracked tasks

**Why:** Track API operations alongside other agent tasks

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from taskqueuepro import TaskQueuePro

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout, result.stdout

# Initialize queue
queue = TaskQueuePro()

# Create task
task_id = queue.create_task(
    title="API Integration Test Suite",
    agent="ATLAS",
    priority=2,
    metadata={
        "tool": "RestCLI",
        "test_count": 3,
        "category": "api_testing"
    }
)

# Mark as in-progress
queue.start_task(task_id)

try:
    # Execute tests
    endpoints = [
        ("github_zen", "https://api.github.com/zen"),
        ("jsonplaceholder", "https://jsonplaceholder.typicode.com/posts/1"),
        ("httpbin", "https://httpbin.org/get")
    ]
    
    results = {}
    for name, url in endpoints:
        success, _ = run_restcli(f"get {url}")
        results[name] = "PASS" if success else "FAIL"
    
    # Complete task
    all_passed = all(r == "PASS" for r in results.values())
    queue.complete_task(
        task_id,
        result={
            "status": "success" if all_passed else "partial_failure",
            "pass_count": sum(1 for r in results.values() if r == "PASS"),
            "fail_count": sum(1 for r in results.values() if r == "FAIL"),
            "details": results
        }
    )
    
    print(f"[OK] Task completed: {results}")

except Exception as e:
    queue.fail_task(task_id, error=str(e))
    print(f"[X] Task failed: {e}")
```

**Result:** Centralized task tracking across all tools

---

## Pattern 4: RestCLI + MemoryBridge

**Use Case:** Persist API test results to memory core

**Why:** Maintain long-term history of API health trends

**Code:**

```python
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from memorybridge import MemoryBridge

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout, result.stdout

# Initialize memory
memory = MemoryBridge()

# Load existing API health history
api_health_history = memory.get("api_health_history", default=[])

# Run API test
url = "https://api.github.com/zen"
success, output = run_restcli(f"get {url}")

# Extract response time from output (e.g., "Time: 245ms")
import re
time_match = re.search(r'Time:\s*(\d+)ms', output)
response_time_ms = int(time_match.group(1)) if time_match else None

# Add to history
api_health_history.append({
    "timestamp": datetime.now().isoformat(),
    "url": url,
    "success": success,
    "response_time_ms": response_time_ms,
    "agent": "ATLAS"
})

# Keep last 1000 entries
if len(api_health_history) > 1000:
    api_health_history = api_health_history[-1000:]

# Save to memory core
memory.set("api_health_history", api_health_history)
memory.sync()

print(f"[OK] Test recorded. Total history: {len(api_health_history)} entries")
```

**Result:** Historical data persisted in memory core for trend analysis

---

## Pattern 5: RestCLI + SessionReplay

**Use Case:** Record API test sessions for debugging

**Why:** Replay API operations when issues occur

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from sessionreplay import SessionReplay

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout, result.stdout

# Initialize replay
replay = SessionReplay()

# Start recording
session_id = replay.start_session("ATLAS", task="API Integration Testing")

try:
    # Log test plan
    replay.log_input(session_id, "Starting API test suite with 3 endpoints")
    
    # Run tests and record each
    endpoints = [
        "https://api.github.com/zen",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpbin.org/get"
    ]
    
    all_passed = True
    for url in endpoints:
        replay.log_input(session_id, f"Testing: {url}")
        
        success, output = run_restcli(f"get {url}")
        
        if success:
            replay.log_output(session_id, f"[OK] {url} - 200 OK\n{output[:200]}...")
        else:
            replay.log_error(session_id, f"[FAIL] {url}\n{output}")
            all_passed = False
    
    # End session
    status = "COMPLETED" if all_passed else "COMPLETED_WITH_FAILURES"
    replay.end_session(session_id, status=status)
    
    print(f"[OK] Session recorded: {session_id}")

except Exception as e:
    replay.log_error(session_id, str(e))
    replay.end_session(session_id, status="FAILED")
    print(f"[X] Session failed: {e}")
```

**Result:** Full session replay available for debugging

---

## Pattern 6: RestCLI + ContextCompressor

**Use Case:** Compress large API responses before sharing

**Why:** Save tokens when sharing API data with other agents

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from contextcompressor import ContextCompressor

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Get large API response
result = subprocess.run(
    f"python {RESTCLI} get https://api.github.com/users/octocat/repos",
    shell=True, capture_output=True, text=True
)

# Initialize compressor
compressor = ContextCompressor()

# Compress the response
compressed = compressor.compress_text(
    result.stdout,
    query="repository names, descriptions, and star counts",
    method="summary"
)

# Show compression stats
original_tokens = len(result.stdout) // 4  # Rough token estimate
compressed_tokens = len(compressed.compressed_text) // 4

print(f"Original: ~{original_tokens} tokens")
print(f"Compressed: ~{compressed_tokens} tokens")
print(f"Savings: ~{original_tokens - compressed_tokens} tokens ({(1 - compressed_tokens/original_tokens)*100:.1f}%)")
print()
print("Compressed summary:")
print(compressed.compressed_text)
```

**Result:** 70-90% token savings on large API responses

---

## Pattern 7: RestCLI + ConfigManager

**Use Case:** Centralize RestCLI configuration

**Why:** Share API endpoints and settings across tools

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from configmanager import ConfigManager

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

# Initialize config
config = ConfigManager()

# Load RestCLI configuration
restcli_config = config.get("restcli", {
    "default_timeout": 30,
    "verbose_by_default": False,
    "common_endpoints": {
        "github_zen": "https://api.github.com/zen",
        "github_user": "https://api.github.com/users/octocat",
        "jsonplaceholder": "https://jsonplaceholder.typicode.com/posts/1",
        "httpbin": "https://httpbin.org/get"
    },
    "health_check_endpoints": [
        "https://api.github.com/zen"
    ]
})

# Use configured settings
timeout = restcli_config["default_timeout"]
verbose = "-v" if restcli_config["verbose_by_default"] else ""

# Test all configured endpoints
print("Testing configured endpoints:")
for name, url in restcli_config["common_endpoints"].items():
    result = subprocess.run(
        f"python {RESTCLI} get {url} -t {timeout} {verbose}",
        shell=True, capture_output=True, text=True
    )
    status = "OK" if "200" in result.stdout else "FAIL"
    print(f"  [{status}] {name}")

# Update config if needed
restcli_config["last_test_run"] = "2026-01-24"
config.set("restcli", restcli_config)
config.save()

print("[OK] Configuration saved")
```

**Result:** Centralized configuration management

---

## Pattern 8: RestCLI + CollabSession

**Use Case:** Coordinate API testing across multiple agents

**Why:** Prevent conflicts when agents test same endpoints

**Code:**

```python
import subprocess
import sys
from pathlib import Path

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from collabsession import CollabSession

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout, result.stdout

# Initialize collaboration
collab = CollabSession()

# Start coordination session for API testing
session_id = collab.start_session(
    "api_testing_session",
    participants=["ATLAS", "CLIO", "NEXUS"]
)

try:
    # ATLAS claims the API testing resource
    collab.lock_resource(session_id, "api_rate_limit", "ATLAS")
    
    # Log our activity
    collab.add_note(session_id, "ATLAS", "Starting GitHub API tests")
    
    # Run tests (within rate limits since we have the lock)
    endpoints = [
        "https://api.github.com/zen",
        "https://api.github.com/users/octocat"
    ]
    
    for url in endpoints:
        success, _ = run_restcli(f"get {url}")
        collab.add_note(
            session_id, 
            "ATLAS", 
            f"{'[OK]' if success else '[FAIL]'} {url}"
        )
    
    # Release lock for other agents
    collab.unlock_resource(session_id, "api_rate_limit")
    collab.add_note(session_id, "ATLAS", "Testing complete, resource released")

finally:
    collab.end_session(session_id)

print("[OK] Coordinated testing complete")
```

**Result:** Safe concurrent API testing without rate limit conflicts

---

## Pattern 9: Multi-Tool API Testing Workflow

**Use Case:** Complete API testing workflow using multiple tools

**Why:** Demonstrate real production scenario

**Code:**

```python
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Setup all tools
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))
from agenthealth import AgentHealth
from synapselink import quick_send
from sessionreplay import SessionReplay
from memorybridge import MemoryBridge

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

def run_restcli(cmd: str) -> tuple:
    result = subprocess.run(
        f"python {RESTCLI} {cmd}",
        shell=True, capture_output=True, text=True
    )
    return "200" in result.stdout, result.stdout

# Initialize all tools
health = AgentHealth()
replay = SessionReplay()
memory = MemoryBridge()

# Create shared session ID
session_id = f"api_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Start all tracking
health.start_session("ATLAS", session_id=session_id)
replay_id = replay.start_session("ATLAS", task="API Integration Workflow")

try:
    # Log workflow start
    replay.log_input(replay_id, "Starting multi-tool API testing workflow")
    health.heartbeat("ATLAS", status="workflow_started")
    
    # Define test suite
    endpoints = [
        ("GitHub Zen", "https://api.github.com/zen"),
        ("GitHub User", "https://api.github.com/users/octocat"),
        ("JSONPlaceholder", "https://jsonplaceholder.typicode.com/posts/1")
    ]
    
    results = {}
    all_passed = True
    
    for name, url in endpoints:
        replay.log_input(replay_id, f"Testing: {name}")
        health.heartbeat("ATLAS", status=f"testing_{name.lower().replace(' ', '_')}")
        
        success, output = run_restcli(f"get {url}")
        results[name] = {
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            replay.log_output(replay_id, f"[OK] {name} passed")
            health.log_event("ATLAS", "api_test_success", {"endpoint": name})
        else:
            replay.log_error(replay_id, f"[FAIL] {name}")
            health.log_error("ATLAS", f"API test failed: {name}")
            all_passed = False
    
    # Save results to memory
    history = memory.get("api_workflow_history", default=[])
    history.append({
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "all_passed": all_passed
    })
    memory.set("api_workflow_history", history[-100:])  # Keep last 100
    memory.sync()
    
    # Complete sessions
    replay.end_session(replay_id, status="COMPLETED" if all_passed else "COMPLETED_WITH_FAILURES")
    health.end_session("ATLAS", session_id=session_id, status="success" if all_passed else "partial_failure")
    
    # Notify team
    if all_passed:
        quick_send(
            "TEAM",
            "API Workflow Complete: All Tests Passed",
            f"Session: {session_id}\n\n"
            f"Results: {len(results)} endpoints tested, all passed\n\n"
            f"Details: {results}",
            priority="NORMAL"
        )
    else:
        failed = [name for name, r in results.items() if not r["success"]]
        quick_send(
            "FORGE,LOGAN",
            "API Workflow: Some Tests Failed",
            f"Session: {session_id}\n\n"
            f"Failed endpoints: {', '.join(failed)}\n\n"
            f"Details: {results}",
            priority="HIGH"
        )
    
    print(f"[OK] Workflow complete. Results: {results}")

except Exception as e:
    replay.log_error(replay_id, str(e))
    replay.end_session(replay_id, status="FAILED")
    health.log_error("ATLAS", str(e))
    health.end_session("ATLAS", session_id=session_id, status="error")
    
    quick_send(
        "FORGE,LOGAN",
        "API Workflow FAILED",
        f"Error: {e}\n\nSession: {session_id}",
        priority="HIGH"
    )
    
    print(f"[X] Workflow failed: {e}")
```

**Result:** Fully instrumented, coordinated API testing workflow

---

## Pattern 10: Full Team Brain API Stack

**Use Case:** Ultimate integration - all tools working together for production API monitoring

**Why:** Production-grade API health monitoring system

**Code:**

```python
#!/usr/bin/env python3
"""
Full Team Brain API Monitoring Stack

This script demonstrates complete integration of RestCLI with all Team Brain tools
for production-grade API health monitoring.

Run as: python api_monitor_stack.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

# Setup
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Import all tools
from agenthealth import AgentHealth
from synapselink import quick_send
from sessionreplay import SessionReplay
from memorybridge import MemoryBridge
from configmanager import ConfigManager
from taskqueuepro import TaskQueuePro

RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"

class APIMonitoringStack:
    """Full Team Brain API monitoring integration."""
    
    def __init__(self, agent: str = "ATLAS"):
        self.agent = agent
        self.health = AgentHealth()
        self.replay = SessionReplay()
        self.memory = MemoryBridge()
        self.config = ConfigManager()
        self.queue = TaskQueuePro()
        
        # Load configuration
        self.endpoints = self.config.get("api_monitoring", {
            "endpoints": [
                {"name": "GitHub", "url": "https://api.github.com/zen"},
                {"name": "JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1"}
            ],
            "alert_threshold": 2,  # Alert after 2 consecutive failures
            "check_interval": 300  # 5 minutes
        })
    
    def run_test(self, url: str) -> tuple:
        """Run single API test."""
        result = subprocess.run(
            f"python {RESTCLI} get {url}",
            shell=True, capture_output=True, text=True
        )
        return "200" in result.stdout, result.stdout
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        session_id = f"api_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start tracking
        self.health.start_session(self.agent, session_id=session_id)
        replay_id = self.replay.start_session(self.agent, task="API Monitoring Cycle")
        task_id = self.queue.create_task(
            title="API Health Check Cycle",
            agent=self.agent,
            priority=1
        )
        self.queue.start_task(task_id)
        
        try:
            results = {}
            failures = []
            
            for endpoint in self.endpoints["endpoints"]:
                name = endpoint["name"]
                url = endpoint["url"]
                
                self.replay.log_input(replay_id, f"Checking: {name}")
                success, output = self.run_test(url)
                
                results[name] = {
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
                
                if not success:
                    failures.append(name)
                    self.health.log_error(self.agent, f"API down: {name}")
                    self.replay.log_error(replay_id, f"FAIL: {name}")
                else:
                    self.replay.log_output(replay_id, f"OK: {name}")
            
            # Save to memory
            history = self.memory.get("api_monitor_history", default=[])
            history.append({
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "failures": failures
            })
            self.memory.set("api_monitor_history", history[-500:])
            self.memory.sync()
            
            # Alert if needed
            if failures:
                quick_send(
                    "FORGE,LOGAN",
                    f"API Alert: {len(failures)} endpoint(s) down",
                    f"Failed: {', '.join(failures)}\n\n"
                    f"Session: {session_id}",
                    priority="HIGH"
                )
            
            # Complete tracking
            self.queue.complete_task(task_id, result={"failures": len(failures)})
            self.replay.end_session(replay_id, status="COMPLETED")
            self.health.end_session(self.agent, session_id=session_id)
            
            return results, failures
            
        except Exception as e:
            self.queue.fail_task(task_id, error=str(e))
            self.replay.end_session(replay_id, status="FAILED")
            self.health.end_session(self.agent, session_id=session_id)
            raise

def main():
    """Main entry point."""
    print("=" * 60)
    print("TEAM BRAIN API MONITORING STACK")
    print("=" * 60)
    
    monitor = APIMonitoringStack()
    results, failures = monitor.run_monitoring_cycle()
    
    print("\nResults:")
    for name, result in results.items():
        status = "[OK]" if result["success"] else "[FAIL]"
        print(f"  {status} {name}")
    
    if failures:
        print(f"\n[!] {len(failures)} failure(s) - team notified")
    else:
        print("\n[OK] All endpoints healthy")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
```

**Result:** Production-grade API monitoring with full Team Brain integration

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✅ SynapseLink - Team notifications
2. ✅ AgentHealth - Health correlation
3. ✅ SessionReplay - Debugging

**Week 2 (Productivity):**
4. ☐ TaskQueuePro - Task management
5. ☐ MemoryBridge - Data persistence
6. ☐ ConfigManager - Configuration

**Week 3 (Advanced):**
7. ☐ ContextCompressor - Token optimization
8. ☐ CollabSession - Multi-agent coordination
9. ☐ Full stack integration

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**
```python
# Ensure all tools are in Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Then import
from agenthealth import AgentHealth
```

**RestCLI Path Issues:**
```python
# Use pathlib for cross-platform paths
from pathlib import Path
RESTCLI = Path.home() / "OneDrive/Documents/AutoProjects/RestCLI/restcli.py"
```

**Subprocess Encoding:**
```python
# Always use text=True for string output
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

---

**Last Updated:** January 24, 2026  
**Maintained By:** ATLAS (Team Brain)  
**For:** Logan Smith / Metaphy LLC
