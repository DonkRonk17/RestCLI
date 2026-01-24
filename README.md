![RestCLI Title Card](branding/RestCLI%20Title.png)

# 🌐 RestCLI - Smart REST API Testing Tool

**Version:** 1.1.0  
**Author:** Logan Smith / Metaphy LLC  
**License:** MIT  
**GitHub:** https://github.com/DonkRonk17/RestCLI

---

## 📖 Overview

**RestCLI** is a powerful yet simple command-line tool for testing REST APIs. It combines the power of `curl` with the simplicity of modern API clients, all while maintaining **zero external dependencies**.

Perfect for developers who want a lightweight, fast, and portable way to test APIs without installing heavyweight tools like Postman or wrestling with complex `curl` commands.

---

## ✨ Features

### 🎯 Core Capabilities
- **All HTTP Methods** - GET, POST, PUT, DELETE, PATCH
- **Zero Dependencies** - Pure Python stdlib (urllib, json)
- **Smart Request History** - Automatically saves last 100 requests
- **Request Collections** - Save and replay common requests
- **Environment Variables** - Use `{{VARS}}` for tokens, URLs, etc.
- **Pretty Output** - Colorized, formatted JSON responses
- **Authentication** - Bearer token, Basic auth, API key support
- **Request Replay** - Instantly replay any historical request
- **Cross-Platform** - Works on Windows, Linux, macOS

### 🎨 User Experience
- **Beautiful CLI** - Color-coded status codes and formatted output
- **Simple Syntax** - `restcli get https://api.example.com`
- **Verbose Mode** - See full request/response details
- **Fast** - Native Python, no overhead
- **Portable** - Single file, no installation required

---

## 🚀 Quick Start

### Installation

**Option 1: Direct Download (Recommended)**
```bash
# Download the script
curl -O https://raw.githubusercontent.com/DonkRonk17/RestCLI/main/restcli.py

# Make it executable (Linux/macOS)
chmod +x restcli.py

# Run it
python restcli.py get https://api.github.com/users/octocat
```

**Option 2: Clone Repository**
```bash
git clone https://github.com/DonkRonk17/RestCLI.git
cd RestCLI
python restcli.py get https://api.github.com/users/octocat
```

**Option 3: Install with setup.py**
```bash
git clone https://github.com/DonkRonk17/RestCLI.git
cd RestCLI
pip install -e .

# Now use 'restcli' command directly
restcli get https://api.github.com/users/octocat
```

### System Requirements
- **Python 3.6+** (included with most systems)
- **No external dependencies** - uses only Python standard library

---

## 📚 Usage Guide

### Basic Requests

**GET Request**
```bash
restcli get https://api.github.com/users/octocat
```

**POST Request with JSON**
```bash
restcli post https://api.example.com/users -d '{"name": "John", "age": 30}'
```

**PUT Request**
```bash
restcli put https://api.example.com/users/123 -d '{"name": "John Doe"}'
```

**DELETE Request**
```bash
restcli delete https://api.example.com/users/123
```

**PATCH Request**
```bash
restcli patch https://api.example.com/users/123 -d '{"age": 31}'
```

### Headers

**Single Header**
```bash
restcli get https://api.example.com/data -H "Content-Type: application/json"
```

**Multiple Headers**
```bash
restcli get https://api.example.com/data \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

### Authentication

**Bearer Token**
```bash
restcli get https://api.example.com/protected --bearer YOUR_TOKEN_HERE
```

**Basic Authentication**
```bash
restcli get https://api.example.com/protected --basic username:password
```

**API Key**
```bash
restcli get https://api.example.com/data --api-key YOUR_API_KEY
```

**Custom API Key Header**
```bash
restcli get https://api.example.com/data \
  --api-key YOUR_API_KEY \
  --api-key-header "X-Custom-API-Key"
```

### Request Body

**Inline JSON**
```bash
restcli post https://api.example.com/users -d '{"name": "Alice", "email": "alice@example.com"}'
```

**From File**
```bash
restcli post https://api.example.com/users -f request.json
```

### Environment Variables

**Set Variables**
```bash
restcli env set API_URL https://api.example.com
restcli env set TOKEN abc123xyz
```

**List Variables**
```bash
restcli env list
```

**Use Variables in Requests**
```bash
restcli get {{API_URL}}/users -H "Authorization: Bearer {{TOKEN}}"
```

**Delete Variable**
```bash
restcli env delete TOKEN
```

### Request History

**View History**
```bash
restcli history
```

**View Last 10 Requests**
```bash
restcli history -l 10
```

**Replay Request**
```bash
# Replay the most recent request
restcli replay 1

# Replay the 5th most recent request
restcli replay 5
```

### Request Collections

**Save Last Request**
```bash
restcli get https://api.github.com/users/octocat
restcli collection save github_user
```

**List Collections**
```bash
restcli collection list
```

**Load and Execute Collection**
```bash
restcli collection load github_user
```

**Delete Collection**
```bash
restcli collection delete github_user
```

### Verbose Mode

**See Full Request/Response Details**
```bash
restcli get https://api.github.com/users/octocat -v
```

Output includes:
- Request method, URL, headers, body
- Response status, headers, body
- Timing and size information

### Timeout

**Custom Timeout (default: 30s)**
```bash
restcli get https://slow-api.example.com/data -t 60
```

---

## 🎯 Real-World Examples

### Example 1: GitHub API

```bash
# Get user info
restcli get https://api.github.com/users/octocat

# Get repositories
restcli get https://api.github.com/users/octocat/repos
```

### Example 2: JSONPlaceholder (Testing API)

```bash
# Get all posts
restcli get https://jsonplaceholder.typicode.com/posts

# Get single post
restcli get https://jsonplaceholder.typicode.com/posts/1

# Create post
restcli post https://jsonplaceholder.typicode.com/posts \
  -d '{"title": "My Post", "body": "Post content", "userId": 1}'

# Update post
restcli put https://jsonplaceholder.typicode.com/posts/1 \
  -d '{"id": 1, "title": "Updated", "body": "New content", "userId": 1}'

# Delete post
restcli delete https://jsonplaceholder.typicode.com/posts/1
```

### Example 3: Weather API with Environment Variables

```bash
# Set up environment
restcli env set WEATHER_API_KEY your_api_key_here
restcli env set WEATHER_URL https://api.openweathermap.org/data/2.5

# Get weather
restcli get "{{WEATHER_URL}}/weather?q=London&appid={{WEATHER_API_KEY}}"

# Save as collection
restcli collection save london_weather

# Replay anytime
restcli collection load london_weather
```

### Example 4: Protected API Workflow

```bash
# 1. Set up environment
restcli env set API_BASE https://api.example.com
restcli env set TOKEN your_bearer_token

# 2. Get user profile
restcli get {{API_BASE}}/me --bearer {{TOKEN}}

# 3. Update profile
restcli put {{API_BASE}}/me --bearer {{TOKEN}} \
  -d '{"name": "John Doe", "bio": "Developer"}'

# 4. Upload data
restcli post {{API_BASE}}/data --bearer {{TOKEN}} \
  -f data.json

# 5. Review history
restcli history -l 10
```

---

## 📂 Data Storage

RestCLI stores data in `~/.restcli/`:

```
~/.restcli/
├── history.json           # Last 100 requests
├── environment.json       # Environment variables
└── collections/           # Saved request collections
    ├── myrequest.json
    └── another.json
```

### Backup/Sync

```bash
# Backup
cp -r ~/.restcli ~/backups/restcli-backup

# Sync across machines
rsync -av ~/.restcli/ user@remote:~/.restcli/
```

---

## 🎨 Output Examples

### Successful GET Request
```
→ Request
GET https://api.github.com/users/octocat

Sending request...

200 OK
Time: 245ms | Size: 1.23 KB

{
  "login": "octocat",
  "id": 1,
  "name": "The Octocat",
  "company": "@github",
  "location": "San Francisco"
}

✓ Request saved to history
```

### Failed Request
```
→ Request
GET https://api.example.com/not-found

Sending request...

404 Not Found
Time: 123ms | Size: 45 B

{
  "error": "Resource not found"
}

✓ Request saved to history
```

---

## 🔧 Advanced Usage

### Chaining Requests with Shell Scripts

```bash
#!/bin/bash

# Get authentication token
TOKEN=$(restcli post https://api.example.com/auth \
  -d '{"username": "admin", "password": "secret"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Use token for authenticated request
restcli env set TOKEN $TOKEN
restcli get {{API_BASE}}/protected --bearer {{TOKEN}}
```

### Response Processing with jq

```bash
# Get specific field from response
restcli get https://api.github.com/users/octocat | jq '.name'

# Filter array results
restcli get https://api.github.com/users/octocat/repos | jq '.[].name'
```

### Parallel Requests

```bash
# Test multiple endpoints simultaneously
restcli get https://api.example.com/endpoint1 &
restcli get https://api.example.com/endpoint2 &
restcli get https://api.example.com/endpoint3 &
wait
```

---

## 🆚 Comparison

| Feature | RestCLI | curl | Postman | httpie |
|---------|---------|------|---------|--------|
| **Zero Dependencies** | ✅ | ✅ | ❌ | ❌ |
| **Simple Syntax** | ✅ | ⚠️ | ✅ | ✅ |
| **Request History** | ✅ | ❌ | ✅ | ❌ |
| **Collections** | ✅ | ❌ | ✅ | ❌ |
| **Environment Vars** | ✅ | ❌ | ✅ | ❌ |
| **Pretty Output** | ✅ | ❌ | ✅ | ✅ |
| **Cross-Platform** | ✅ | ✅ | ✅ | ✅ |
| **GUI** | ❌ | ❌ | ✅ | ❌ |
| **File Size** | <50KB | Varies | >100MB | Varies |

---

## 🐛 Troubleshooting

### Issue: SSL Certificate Errors

```bash
# For testing with self-signed certificates, you may need to disable verification
# (Not recommended for production)
# RestCLI uses urllib which respects system certificate stores
```

### Issue: Unicode Characters Not Displaying

RestCLI automatically handles UTF-8 encoding. If you see issues:
- **Windows**: Use PowerShell instead of CMD
- **Linux/macOS**: Ensure terminal supports UTF-8

### Issue: Timeout Errors

```bash
# Increase timeout for slow APIs
restcli get https://slow-api.example.com -t 120
```

### Issue: Permission Denied

```bash
# Make script executable (Linux/macOS)
chmod +x restcli.py
```

---

## 🎓 Tips & Best Practices

### 1. Use Environment Variables for Sensitive Data
```bash
# Good
restcli env set API_KEY secret123
restcli get {{API_URL}} --bearer {{API_KEY}}

# Bad (visible in history)
restcli get https://api.example.com --bearer secret123
```

### 2. Save Common Requests as Collections
```bash
# Save once
restcli get https://api.github.com/users/octocat
restcli collection save github_octocat

# Reuse many times
restcli collection load github_octocat
```

### 3. Use Verbose Mode for Debugging
```bash
restcli get https://api.example.com/data -v
```

### 4. Combine with Other Tools
```bash
# Pretty print with jq
restcli get https://api.github.com/users/octocat | jq '.'

# Save response to file
restcli get https://api.github.com/users/octocat > response.json

# Count array items
restcli get https://api.github.com/users/octocat/repos | jq 'length'
```

---

## 📊 Project Statistics

- **Lines of Code:** ~700
- **Dependencies:** 0 (pure Python stdlib)
- **File Size:** ~25 KB
- **Python Version:** 3.6+
- **Platforms:** Windows, Linux, macOS

---

<img width="1536" height="1024" alt="RestCLI Logo" src="https://github.com/user-attachments/assets/79a9ba28-20ad-4be2-b576-95c2295d798c" />

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🔗 Links

- **GitHub Repository:** https://github.com/DonkRonk17/RestCLI
- **Report Issues:** https://github.com/DonkRonk17/RestCLI/issues

---

## 🌟 Why RestCLI?

**RestCLI was built to solve a simple problem:** developers need a fast, simple way to test APIs without installing heavy tools or memorizing complex `curl` syntax.

### Perfect For:
- 🏃 **Quick API testing** - No setup, just run
- 🔧 **Development** - Test your own APIs during development
- 📚 **Learning** - Understand HTTP requests/responses
- 🤖 **Automation** - Integrate into scripts and CI/CD
- 🚀 **Production debugging** - Lightweight tool for server environments

### Not For:
- ❌ Complex API test suites (use Postman/Insomnia)
- ❌ Load testing (use Apache Bench/JMeter)
- ❌ GraphQL (use dedicated GraphQL clients)

---

## 🙏 Credits

Created by **Randell Logan Smith and Team Brain** at [Metaphy LLC](https://metaphysicsandcomputing.com)

Part of the HMSS (Heavenly Morning Star System) ecosystem.

---

**Zero dependencies. Maximum utility. Pure Python.**
