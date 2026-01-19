# Environment Variables Setup Guide

## 🔐 Why Use Environment Variables?

**Benefits:**
- ✅ **Security**: Keep API keys out of your code
- ✅ **Version Control**: Don't accidentally commit secrets to Git
- ✅ **Flexibility**: Easy to change settings without editing code
- ✅ **Team Collaboration**: Each developer uses their own API key

---

## 🚀 Quick Setup

### Step 1: Install python-dotenv

```powershell
# Activate your virtual environment first
venv\Scripts\activate

# Install python-dotenv
pip install python-dotenv
```

### Step 2: Create .env File

1. **Copy the template:**
   - Rename `.env.example` to `.env`
   - OR create a new file named `.env`

2. **Add your API key:**

```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Step 3: Run the Application

```powershell
python optimized_arabic_whisper.py
```

**That's it!** The script will automatically load your API key from `.env`

---

## 📁 File Structure

Your project should look like this:

```
arabic-stt/
├── venv/                          # Virtual environment (git ignored)
├── .env                           # Your API keys (git ignored) ⚠️
├── .env.example                   # Template (committed to git)
├── .gitignore                     # Tells git what to ignore
├── requirements.txt               # Dependencies
├── optimized_arabic_whisper.py   # Main application
├── test_microphone.py            # Microphone test utility
└── README.md                      # Documentation
```

---

## 🔑 Setting Up Your API Key

### Method 1: Using .env File (RECOMMENDED)

1. **Create `.env` file** in your project root:

```env
OPENAI_API_KEY=sk-proj-abc123xyz...
```

2. **Run the script** - it automatically loads the key

**Advantages:**
- ✅ Secure
- ✅ Easy to manage
- ✅ Automatically ignored by git
- ✅ Different keys per environment (dev/prod)

### Method 2: Windows Environment Variables

1. **Open System Properties:**
   - Right-click "This PC" → Properties
   - Advanced System Settings → Environment Variables

2. **Add New User Variable:**
   - Variable name: `OPENAI_API_KEY`
   - Variable value: `sk-proj-your-key-here`

3. **Restart PowerShell/CMD**

4. **Run the script**

**Advantages:**
- ✅ Available to all applications
- ✅ No .env file needed

**Disadvantages:**
- ❌ System-wide (all users can see it)
- ❌ Harder to manage multiple keys

### Method 3: PowerShell Session Variable

**Temporary (current session only):**

```powershell
$env:OPENAI_API_KEY = "sk-proj-your-key-here"
python optimized_arabic_whisper.py
```

**Advantages:**
- ✅ Quick testing
- ✅ Doesn't persist

**Disadvantages:**
- ❌ Lost when PowerShell closes

---

## ⚙️ Optional Configuration

You can customize audio settings via `.env`:

```env
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional Audio Settings
SAMPLE_RATE=16000
CHANNELS=1
ENERGY_THRESHOLD=0.03
SILENCE_DURATION=0.8
MIN_SPEECH_DURATION=1.0
MAX_SPEECH_DURATION=10.0
```

### Settings Explained

| Variable | Default | Description |
|----------|---------|-------------|
| `SAMPLE_RATE` | 16000 | Audio sample rate (Hz) - Don't change |
| `CHANNELS` | 1 | Mono (1) or Stereo (2) - Use 1 |
| `ENERGY_THRESHOLD` | 0.03 | Voice sensitivity (0.01-0.10) |
| `SILENCE_DURATION` | 0.8 | Seconds of silence before processing |
| `MIN_SPEECH_DURATION` | 1.0 | Minimum speech length (seconds) |
| `MAX_SPEECH_DURATION` | 10.0 | Maximum speech length (seconds) |

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Use `.env` file for API keys
- ✅ Add `.env` to `.gitignore`
- ✅ Commit `.env.example` as a template
- ✅ Use different keys for dev/prod
- ✅ Rotate keys periodically
- ✅ Share `.env.example`, never `.env`

### ❌ DON'T:
- ❌ Hardcode API keys in scripts
- ❌ Commit `.env` to Git
- ❌ Share API keys in chat/email
- ❌ Use production keys for testing
- ❌ Store keys in public repos
- ❌ Screenshot code with API keys

---

## 🧪 Testing Your Setup

### Check if .env is Loaded

```powershell
# Activate virtual environment
venv\Scripts\activate

# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key found!' if os.getenv('OPENAI_API_KEY') else 'API Key NOT found')"
```

**Expected output:** `API Key found!`

### Verify API Key is Valid

The application will show a warning if:
- `.env` file doesn't exist
- API key is not set
- API key is invalid (when you try to transcribe)

---

## 📋 .env File Examples

### Minimal Setup
```env
OPENAI_API_KEY=sk-proj-abc123xyz...
```

### Complete Setup
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123xyz...

# Audio Settings (Optimized for Quran recitation)
SAMPLE_RATE=16000
CHANNELS=1

# Voice Activity Detection
ENERGY_THRESHOLD=0.03
SILENCE_DURATION=0.8

# Speech Timing
MIN_SPEECH_DURATION=1.0
MAX_SPEECH_DURATION=10.0
```

### Testing Environment
```env
# Use test API key
OPENAI_API_KEY=sk-test-abc123...

# More sensitive for testing
ENERGY_THRESHOLD=0.02
SILENCE_DURATION=0.5
MIN_SPEECH_DURATION=0.7
```

---

## 🔧 Troubleshooting

### Issue: "API key not found"

**Check:**
1. `.env` file exists in project root
2. File is named exactly `.env` (not `env.txt` or `.env.txt`)
3. No spaces around `=` in `.env` file
4. `python-dotenv` is installed: `pip list | grep python-dotenv`

**Fix:**
```powershell
# Reinstall python-dotenv
pip install --force-reinstall python-dotenv

# Verify .env file
type .env  # Windows CMD
cat .env   # PowerShell/Linux
```

### Issue: "Using placeholder API key"

**Cause:** Script couldn't find `OPENAI_API_KEY` in environment

**Fix:**
1. Create `.env` file in same directory as script
2. Add: `OPENAI_API_KEY=your-key-here`
3. Restart the application

### Issue: API key in .env but not loading

**Check file location:**
```powershell
# Should be in same folder as the script
dir .env          # Windows
ls -la .env       # Linux/Mac

# Check if it's in the right place
python -c "import os; print(os.getcwd())"
```

**The `.env` file must be in the same directory where you run the script!**

### Issue: .env file is committed to Git

**Emergency fix:**
```bash
# Remove from Git (keeps local file)
git rm --cached .env

# Add to .gitignore
echo ".env" >> .gitignore

# Commit the changes
git add .gitignore
git commit -m "Remove .env from tracking"

# Change your API key immediately!
# Old key is now in Git history
```

---

## 🌍 Using Different Environments

### Development (.env.development)
```env
OPENAI_API_KEY=sk-test-dev-key...
ENERGY_THRESHOLD=0.02
```

### Production (.env.production)
```env
OPENAI_API_KEY=sk-proj-prod-key...
ENERGY_THRESHOLD=0.03
```

### Load specific environment:
```python
from dotenv import load_dotenv

# Load specific env file
load_dotenv('.env.development')
# or
load_dotenv('.env.production')
```

---

## 📚 Additional Resources

- **python-dotenv docs**: https://pypi.org/project/python-dotenv/
- **OpenAI API keys**: https://platform.openai.com/api-keys
- **Git security**: https://docs.github.com/en/code-security

---

## ✅ Pre-Commit Checklist

Before committing code:

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is up to date
- [ ] No API keys in code
- [ ] No hardcoded secrets
- [ ] `requirements.txt` includes `python-dotenv`

---

## 🎯 Quick Commands Reference

```powershell
# Create .env from template
copy .env.example .env

# Edit .env (Windows)
notepad .env

# Edit .env (PowerShell)
code .env  # VS Code
notepad++ .env  # Notepad++

# Check if .env exists
Test-Path .env

# View .env content (be careful in public!)
type .env

# Test loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY')[:10])"
```

---

**Remember:** Your `.env` file should NEVER be committed to Git! 🔒
