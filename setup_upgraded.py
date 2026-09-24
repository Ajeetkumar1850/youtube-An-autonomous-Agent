"""
Setup script for upgraded YouTube Autonomous Agent
Creates necessary directories and initializes database
"""
import os
import asyncio
from src.database import init_db
from src.config import settings
import structlog

logger = structlog.get_logger()


async def setup():
    """Run setup tasks"""
    print("=" * 60)
    print("YouTube Autonomous Agent - Setup")
    print("=" * 60)
    print()
    
    # Create directories
    directories = [
        settings.scenes_dir,
        settings.audio_dir,
        settings.videos_dir,
        "src/agents",
        "src/api",
        "src/models",
        "src/workflow"
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print()
    
    # Initialize database
    print("🗄️  Initializing database...")
    try:
        await init_db()
        print("  ✓ Database tables created")
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        print("  ℹ️  Make sure PostgreSQL is running and DATABASE_URL is correct")
    
    print()
    
    # Check services
    print("🔍 Checking services...")
    
    # Check Ollama
    try:
        import ollama
        models = ollama.list()
        print(f"  ✓ Ollama running ({len(models['models'])} models)")
    except Exception as e:
        print(f"  ✗ Ollama not accessible: {e}")
        print("  ℹ️  Install Ollama and run: ollama pull llama3")
    
    # Check Redis
    try:
        from src.cache import cache_manager
        await cache_manager.connect()
        await cache_manager.redis_client.ping()
        print("  ✓ Redis connected")
        await cache_manager.disconnect()
    except Exception as e:
        print(f"  ✗ Redis not accessible: {e}")
        print("  ℹ️  Install Redis and start: redis-server")
    
    print()
    print("=" * 60)
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("  1. Copy .env.example to .env and configure")
    print("  2. Run CLI: python main_upgraded.py")
    print("  3. Run API: python -m uvicorn src.api.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(setup())
