"""
Quick check - which services are running?
"""
import requests

print("=" * 60)
print("SERVICE STATUS CHECK")
print("=" * 60)

# Check Ollama (REQUIRED)
print("\n1. Ollama (REQUIRED):")
try:
    response = requests.get("http://localhost:11434", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama is RUNNING")
        print("   → Your project will work!")
    else:
        print("   ⚠️  Ollama responded but with error")
except requests.exceptions.ConnectionError:
    print("   ❌ Ollama is NOT RUNNING")
    print("   → Start Ollama: ollama serve")
    print("   → Download: https://ollama.ai/download")
except Exception as e:
    print(f"   ❌ Error checking Ollama: {e}")

# Check Redis (OPTIONAL)
print("\n2. Redis (Optional - for caching):")
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=2)
    r.ping()
    print("   ✅ Redis is RUNNING")
    print("   → Caching will work (5x faster LLM calls)")
except redis.exceptions.ConnectionError:
    print("   ⚠️  Redis is NOT RUNNING (optional)")
    print("   → Project will work without it")
    print("   → Caching disabled")
except ImportError:
    print("   ⚠️  Redis library not installed (optional)")
except Exception as e:
    print(f"   ⚠️  Redis check failed: {e}")

# Check PostgreSQL (OPTIONAL)
print("\n3. PostgreSQL (Optional - for job tracking):")
try:
    import psycopg2
    conn = psycopg2.connect(
        "postgresql://user:password@localhost:5432/youtube_agent",
        connect_timeout=2
    )
    conn.close()
    print("   ✅ PostgreSQL is RUNNING")
    print("   → Job tracking will work")
except Exception:
    print("   ⚠️  PostgreSQL is NOT RUNNING (optional)")
    print("   → Project will work without it")
    print("   → Jobs won't be tracked in database")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

try:
    response = requests.get("http://localhost:11434", timeout=2)
    if response.status_code == 200:
        print("\n✅ READY TO GO!")
        print("\nOllama is running - you can generate videos!")
        print("\nNext steps:")
        print("  1. Run: python main_upgraded.py")
        print("  2. Enter your niche (e.g., 'motivation')")
        print("  3. Wait 5-8 minutes for video generation")
        print("  4. Video will be uploaded to YouTube!")
    else:
        print("\n⚠️  ALMOST READY")
        print("\nOllama is responding but needs configuration")
except:
    print("\n❌ NOT READY")
    print("\n⚠️  Ollama must be running to generate videos!")
    print("\nHow to fix:")
    print("  1. Download Ollama: https://ollama.ai/download")
    print("  2. Install and start it")
    print("  3. Run: ollama pull llama3")
    print("  4. Then try again!")

print("\n" + "=" * 60)
