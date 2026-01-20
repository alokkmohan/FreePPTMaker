# API Key Setup Guide

## 🔐 Securing Your Claude API Key

**IMPORTANT:** Never commit API keys to GitHub!

---

## Method 1: Environment Variable (Recommended)

### Windows:
```cmd
set CLAUDE_API_KEY=your-api-key-here
```

### Linux/Mac:
```bash
export CLAUDE_API_KEY="your-api-key-here"
```

### Permanent Setup:

**Windows:**
1. Search "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `CLAUDE_API_KEY`
6. Variable value: Your API key
7. Click OK

**Linux/Mac:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export CLAUDE_API_KEY="your-api-key-here"
```
Then run: `source ~/.bashrc`

---

## Method 2: .env File (For Development)

1. Create `.env` file in project root:
```
CLAUDE_API_KEY=your-api-key-here
```

2. Add `.env` to `.gitignore`:
```
echo ".env" >> .gitignore
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

4. Load in your code:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Method 3: Direct in Code (NOT Recommended)

**⚠️ Only for local testing. NEVER commit this!**

```python
# In claude_content_analyzer.py
CLAUDE_API_KEY = "your-api-key-here"  # DO NOT COMMIT THIS
```

---

## Get Your API Key

1. Go to: https://console.anthropic.com/
2. Sign in or create account
3. Navigate to API Keys section
4. Create new key or copy existing one

---

## Verify Setup

Run this test:
```python
import os
print("API Key loaded:", bool(os.getenv("CLAUDE_API_KEY")))
```

Should print: `API Key loaded: True`

---

## Security Best Practices

✅ **DO:**
- Use environment variables
- Use `.env` file (add to `.gitignore`)
- Rotate keys regularly
- Use different keys for dev/prod

❌ **DON'T:**
- Hardcode keys in source code
- Commit keys to Git
- Share keys publicly
- Use production keys in development

---

## Troubleshooting

**Error: "Claude API key not found"**
- Check if environment variable is set
- Restart terminal/IDE after setting
- Verify variable name is exactly `CLAUDE_API_KEY`

**Error: "Invalid API key"**
- Check for extra spaces
- Verify key starts with `sk-ant-`
- Generate new key from console

---

## GitHub Security

If you accidentally pushed a key:

1. **Immediately revoke it** at https://console.anthropic.com/
2. Generate new key
3. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch path/to/file.py" \
   --prune-empty --tag-name-filter cat -- --all
   ```
4. Force push: `git push origin --force --all`

---

**Your API key is like a password - keep it secret, keep it safe!** 🔐
