# 🌐 RestCLI - Usage Examples

**Version:** 1.1.0  
**Last Updated:** January 24, 2026

---

## 📚 Table of Contents

1. [Example 1: Basic GET Request](#example-1-basic-get-request)
2. [Example 2: POST Request with JSON](#example-2-post-request-with-json)
3. [Example 3: Using Headers](#example-3-using-headers)
4. [Example 4: Bearer Token Authentication](#example-4-bearer-token-authentication)
5. [Example 5: Environment Variables](#example-5-environment-variables)
6. [Example 6: Request History and Replay](#example-6-request-history-and-replay)
7. [Example 7: Request Collections](#example-7-request-collections)
8. [Example 8: Reading Body from File](#example-8-reading-body-from-file)
9. [Example 9: Verbose Mode Debugging](#example-9-verbose-mode-debugging)
10. [Example 10: Complete API Workflow](#example-10-complete-api-workflow)
11. [Example 11: Error Handling](#example-11-error-handling)
12. [Example 12: Integration with SynapseLink](#example-12-integration-with-synapselink)

---

## Example 1: Basic GET Request

**Scenario:** You want to quickly test if an API endpoint is working.

**Steps:**

```bash
# Step 1: Make a simple GET request to GitHub API
python restcli.py get https://api.github.com/users/octocat
```

**Expected Output:**

```
Sending request...

200 OK
Time: 245ms | Size: 1.43 KB

{
  "login": "octocat",
  "id": 583231,
  "node_id": "MDQ6VXNlcjU4MzIzMQ==",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
  "name": "The Octocat",
  "company": "@github",
  "location": "San Francisco"
  ...
}

[OK] Request saved to history
```

**What You Learned:**
- How to make a basic GET request
- Response includes status code, timing, and size
- JSON responses are automatically formatted
- Request is saved to history for later replay

---

## Example 2: POST Request with JSON

**Scenario:** You need to create a new resource via a REST API.

**Steps:**

```bash
# Step 1: POST a new user to JSONPlaceholder API (test API)
python restcli.py post https://jsonplaceholder.typicode.com/posts -d '{"title": "My Post", "body": "This is the content", "userId": 1}'
```

**Expected Output:**

```
Sending request...

201 Created
Time: 189ms | Size: 112 B

{
  "title": "My Post",
  "body": "This is the content",
  "userId": 1,
  "id": 101
}

[OK] Request saved to history
```

**What You Learned:**
- How to send JSON data with POST requests
- Use `-d` flag for inline JSON data
- Content-Type is automatically set to `application/json`
- Response shows the created resource with new ID

---

## Example 3: Using Headers

**Scenario:** You need to send custom headers with your request.

**Steps:**

```bash
# Step 1: Send request with custom headers
python restcli.py get https://httpbin.org/headers -H "X-Custom-Header: MyValue" -H "Accept: application/json"
```

**Expected Output:**

```
Sending request...

200 OK
Time: 156ms | Size: 342 B

{
  "headers": {
    "Accept": "application/json",
    "Host": "httpbin.org",
    "User-Agent": "RestCLI/1.1.0",
    "X-Custom-Header": "MyValue"
  }
}

[OK] Request saved to history
```

**What You Learned:**
- Use `-H` flag multiple times for multiple headers
- Format: `-H "Header-Name: Header-Value"`
- RestCLI adds User-Agent automatically

---

## Example 4: Bearer Token Authentication

**Scenario:** You need to access a protected API endpoint.

**Steps:**

```bash
# Step 1: Set up your token (secure way using env vars)
python restcli.py env set TOKEN your_actual_token_here

# Step 2: Make authenticated request
python restcli.py get https://api.github.com/user --bearer {{TOKEN}}
```

**Alternative (inline token):**

```bash
python restcli.py get https://api.github.com/user --bearer ghp_xxxxxxxxxxxx
```

**Expected Output:**

```
Sending request...

200 OK
Time: 312ms | Size: 2.1 KB

{
  "login": "your_username",
  "id": 12345678,
  "name": "Your Name",
  "email": "your@email.com"
  ...
}

[OK] Request saved to history
```

**What You Learned:**
- Use `--bearer` for OAuth 2.0 Bearer token auth
- Environment variables protect sensitive tokens
- Use `{{VAR}}` syntax to reference env vars

---

## Example 5: Environment Variables

**Scenario:** You want to store reusable values like API URLs and tokens.

**Steps:**

```bash
# Step 1: Set environment variables
python restcli.py env set API_URL https://api.example.com
python restcli.py env set VERSION v1
python restcli.py env set TOKEN secret_token_123

# Step 2: List all variables
python restcli.py env list

# Step 3: Use variables in requests
python restcli.py get "{{API_URL}}/{{VERSION}}/users" --bearer {{TOKEN}}

# Step 4: Get a specific variable
python restcli.py env get TOKEN

# Step 5: Delete a variable
python restcli.py env delete TOKEN
```

**Expected Output (env list):**

```
Environment Variables

  API_URL = https://api.example.com
  TOKEN = secret_token_123
  VERSION = v1
```

**What You Learned:**
- `env set KEY value` - Create/update variable
- `env list` - Show all variables
- `env get KEY` - Show specific variable
- `env delete KEY` - Remove variable
- Use `{{KEY}}` in requests to substitute values

---

## Example 6: Request History and Replay

**Scenario:** You want to see past requests and replay them.

**Steps:**

```bash
# Step 1: Make some requests first
python restcli.py get https://api.github.com/zen
python restcli.py get https://api.github.com/users/octocat
python restcli.py post https://jsonplaceholder.typicode.com/posts -d '{"title": "Test"}'

# Step 2: View request history
python restcli.py history

# Step 3: View last 5 requests only
python restcli.py history -l 5

# Step 4: Replay the most recent request
python restcli.py replay 1

# Step 5: Replay the 3rd most recent request
python restcli.py replay 3
```

**Expected Output (history):**

```
Request History (3 entries)

  1. 2026-01-24 10:30:15 | POST   | 201 | 189ms | https://jsonplaceholder.typicode.com/pos...
  2. 2026-01-24 10:29:45 | GET    | 200 | 245ms | https://api.github.com/users/octocat
  3. 2026-01-24 10:29:30 | GET    | 200 |  89ms | https://api.github.com/zen

Use 'restcli replay <number>' to replay a request
```

**What You Learned:**
- History keeps last 100 requests
- Shows method, status, timing, and URL
- Replay any request by its number (1 = most recent)
- Great for debugging and retesting

---

## Example 7: Request Collections

**Scenario:** You want to save frequently-used requests for quick access.

**Steps:**

```bash
# Step 1: Make a request you want to save
python restcli.py get https://api.github.com/users/octocat

# Step 2: Save the last request to a collection
python restcli.py collection save github_user

# Step 3: List saved collections
python restcli.py collection list

# Step 4: Load and execute a saved collection
python restcli.py collection load github_user

# Step 5: Delete a collection
python restcli.py collection delete github_user
```

**Expected Output (collection list):**

```
Saved Collections

  github_user - GET https://api.github.com/users/octocat
  create_post - POST https://jsonplaceholder.typicode.com/pos...
```

**What You Learned:**
- `collection save NAME` - Save last request
- `collection list` - Show all collections
- `collection load NAME` - Execute saved request
- `collection delete NAME` - Remove collection
- Collections persist between sessions

---

## Example 8: Reading Body from File

**Scenario:** You have a complex JSON payload in a file.

**Steps:**

```bash
# Step 1: Create a JSON file with your request body
echo '{"title": "Complex Post", "body": "This is a longer body with multiple lines and special characters: \"quotes\" and 'apostrophes'", "userId": 1}' > request_body.json

# Step 2: Use the file in your POST request
python restcli.py post https://jsonplaceholder.typicode.com/posts -f request_body.json
```

**Expected Output:**

```
Sending request...

201 Created
Time: 178ms | Size: 156 B

{
  "title": "Complex Post",
  "body": "This is a longer body with multiple lines and special characters...",
  "userId": 1,
  "id": 101
}

[OK] Request saved to history
```

**What You Learned:**
- Use `-f` or `--data-file` for body from file
- Great for complex JSON payloads
- File must contain valid JSON
- Environment variables work in file content too

---

## Example 9: Verbose Mode Debugging

**Scenario:** You need to see full request and response details for debugging.

**Steps:**

```bash
# Use -v flag for verbose output
python restcli.py get https://api.github.com/users/octocat -v
```

**Expected Output:**

```
→ Request
GET https://api.github.com/users/octocat

Headers:
  User-Agent: RestCLI/1.1.0

Sending request...

← Response
200 OK
Time: 267ms
Size: 1.43 KB

Headers:
  Content-Type: application/json; charset=utf-8
  Cache-Control: public, max-age=60, s-maxage=60
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 58
  X-RateLimit-Reset: 1706097600
  ...

Body:
{
  "login": "octocat",
  ...
}

[OK] Request saved to history
```

**What You Learned:**
- Verbose mode shows full request details
- See all response headers
- Useful for debugging rate limits, caching, etc.
- Essential when diagnosing API issues

---

## Example 10: Complete API Workflow

**Scenario:** Complete CRUD workflow with a REST API.

**Steps:**

```bash
# Setup environment
python restcli.py env set API_BASE https://jsonplaceholder.typicode.com

# CREATE - Add a new post
python restcli.py post {{API_BASE}}/posts -d '{"title": "New Post", "body": "Content here", "userId": 1}'
# Response: 201 Created, id: 101

# READ - Get the post (using fake ID since JSONPlaceholder doesn't persist)
python restcli.py get {{API_BASE}}/posts/1

# UPDATE - Modify the post
python restcli.py put {{API_BASE}}/posts/1 -d '{"id": 1, "title": "Updated Title", "body": "New content", "userId": 1}'

# PARTIAL UPDATE - Change just one field
python restcli.py patch {{API_BASE}}/posts/1 -d '{"title": "Patched Title"}'

# DELETE - Remove the post
python restcli.py delete {{API_BASE}}/posts/1

# Review what we did
python restcli.py history -l 5
```

**Expected Output (history after workflow):**

```
Request History (5 entries)

  1. 2026-01-24 10:45:23 | DELETE | 200 |  98ms | https://jsonplaceholder.typicode.com/pos...
  2. 2026-01-24 10:45:12 | PATCH  | 200 | 123ms | https://jsonplaceholder.typicode.com/pos...
  3. 2026-01-24 10:45:01 | PUT    | 200 | 145ms | https://jsonplaceholder.typicode.com/pos...
  4. 2026-01-24 10:44:50 | GET    | 200 |  87ms | https://jsonplaceholder.typicode.com/pos...
  5. 2026-01-24 10:44:38 | POST   | 201 | 189ms | https://jsonplaceholder.typicode.com/pos...
```

**What You Learned:**
- Complete CRUD operations with RestCLI
- POST = Create, GET = Read, PUT = Update, PATCH = Partial Update, DELETE = Remove
- Environment variables keep URLs clean
- History tracks your entire workflow

---

## Example 11: Error Handling

**Scenario:** Understanding how RestCLI handles errors.

**Steps:**

```bash
# Test 1: Invalid URL
python restcli.py get https://nonexistent.invalid

# Test 2: 404 Not Found
python restcli.py get https://api.github.com/users/nonexistent_user_12345

# Test 3: 401 Unauthorized
python restcli.py get https://api.github.com/user

# Test 4: Timeout (slow server)
python restcli.py get https://httpbin.org/delay/60 -t 5

# Test 5: Invalid JSON body
python restcli.py post https://jsonplaceholder.typicode.com/posts -d 'not valid json'
```

**Expected Outputs:**

```
# Invalid URL
[X] Error: [Errno 11001] getaddrinfo failed
Duration: 1.23s

# 404 Not Found
404 Not Found
Time: 156ms | Size: 83 B

{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest"
}

# Timeout
[X] Error: <urlopen error timed out>
Duration: 5.01s
```

**What You Learned:**
- RestCLI shows clear error messages
- Network errors are caught gracefully
- HTTP errors show response body
- Use `-t` to adjust timeout
- Errors are still saved to history

---

## Example 12: Integration with SynapseLink

**Scenario:** Using RestCLI in a Team Brain workflow with SynapseLink notifications.

**Steps:**

```python
# Python script: api_test_workflow.py
import subprocess
import sys
sys.path.insert(0, 'C:/Users/logan/OneDrive/Documents/AutoProjects/SynapseLink')
from synapselink import quick_send

def run_restcli(cmd):
    """Run RestCLI command and return output."""
    result = subprocess.run(
        f"python restcli.py {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout

# Test API endpoint
success, output = run_restcli("get https://api.github.com/zen")

if success:
    quick_send(
        "TEAM",
        "API Test Successful",
        f"GitHub API is responding.\n\nResponse:\n{output}",
        priority="NORMAL"
    )
else:
    quick_send(
        "FORGE,LOGAN",
        "API Test FAILED",
        f"GitHub API test failed!\n\nOutput:\n{output}",
        priority="HIGH"
    )

print("[OK] Test complete, team notified via SynapseLink")
```

**Run the Script:**

```bash
python api_test_workflow.py
```

**Expected Output:**

```
[OK] Test complete, team notified via SynapseLink
```

**What You Learned:**
- RestCLI integrates easily with Python scripts
- Combine with SynapseLink for team notifications
- Automate API testing in Team Brain workflows
- Report success/failure to the team automatically

---

## 📊 Quick Reference

| Command | Description |
|---------|-------------|
| `get URL` | GET request |
| `post URL -d JSON` | POST with data |
| `put URL -d JSON` | PUT (full update) |
| `patch URL -d JSON` | PATCH (partial update) |
| `delete URL` | DELETE request |
| `-H "Header: Value"` | Add header |
| `-d '{"json": "data"}'` | Inline body |
| `-f file.json` | Body from file |
| `--bearer TOKEN` | Bearer auth |
| `--basic user:pass` | Basic auth |
| `-v` | Verbose output |
| `-t SECONDS` | Timeout |
| `env set KEY VALUE` | Set variable |
| `env list` | List variables |
| `history` | Show history |
| `replay N` | Replay request N |
| `collection save NAME` | Save request |
| `collection load NAME` | Load request |

---

## 🔗 Related Documentation

- **README.md** - Full documentation
- **CHEAT_SHEET.txt** - Quick command reference
- **INTEGRATION_PLAN.md** - Team Brain integration guide
- **QUICK_START_GUIDES.md** - Agent-specific guides

---

**Built with precision by ATLAS (Team Brain)**  
**For Logan Smith / Metaphy LLC**
