# 🚀 Start Services - Quick Guide

Your project needs these services running:

## 1. Start Ollama (REQUIRED) ✅

**Check if running:**
```bash
curl http://localhost:11434
```

**If not running, start Ollama:**

**Windows:**
- Open Ollama application from Start Menu
- Or run: `ollama serve` in a terminal

**Linux/Mac:**
```bash
ollama serve
```

**Verify it's working:**
```bash
ollama list
# Should show available models
```

**If you don't have Ollama installed:**
- Download from: https://ollama.ai/download
- Install and run
- Pull the model: `ollama pull llama3`

---

## 2. Start Redis (Optional - for caching)

**The project will work without Redis**, but caching won't work.

**Windows:**
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use WSL: `sudo service redis-server start`

**Linux:**
```bash
sudo service redis-server start
```

**Mac:**
```bash
brew services start redis
```

**To skip Redis:** The project will still work, just without caching.

---

## 3. Start PostgreSQL (Optional - for job tracking)

**The project will work without PostgreSQL**, but job tracking won't be saved.

**Windows:**
- Install PostgreSQL from: https://www.postgresql.org/download/windows/
- Start from Services

**Linux:**
```bash
sudo service postgresql start
```

**Mac:**
```bash
brew services start postgresql
```

**To skip PostgreSQL:** The project will still work, just won't track jobs in database.

---

## Quick Start (Minimum Requirements)

**Only Ollama is REQUIRED. Everything else is optional!**

1. **Start Ollama**:
   ```bash
   ollama serve
   # In another terminal:
   ollama pull llama3
   ```

2. **Run your project**:
   ```bash
   python main_upgraded.py
   ```

That's it! Redis and PostgreSQL are optional enhancements.

---

## Test if Services are Running

```bash
# Test Ollama
curl http://localhost:11434
# Should return: "Ollama is running"

# Test Redis (optional)
redis-cli ping
# Should return: PONG

# Test PostgreSQL (optional)
psql -U postgres -c "SELECT 1"
# Should return: 1
```

---

## If Services Fail

**Ollama connection refused:**
1. Start Ollama: `ollama serve`
2. Pull model: `ollama pull llama3`
3. Test: `ollama run llama3 "hello"`

**Redis connection refused:**
- It's optional! Project will work without it.
- To fix: Install and start Redis

**PostgreSQL connection refused:**
- It's optional! Project will work without it.
- To fix: Install and start PostgreSQL

---

## Start Project After Services

```bash
# Method 1: CLI (recommended for testing)
python main_upgraded.py

# Method 2: Web UI
streamlit run app.py

# Method 3: API Server
uvicorn src.api.main:app --reload
```

---

## Current Status Check

Run this to check what's working:
```bash
python test_system_health.py
```

Will show:
- ✓ What's working
- ✗ What needs to be started
- ⚠ What's optional

---

**Bottom Line:** Start Ollama, then run your project! Everything else is optional.
