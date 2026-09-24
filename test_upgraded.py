"""
Quick test script for upgraded agents
Tests individual agents without full workflow
"""
import asyncio
from src.agents.research_agent import research_topics
from src.agents.script_agent import generate_script
from src.agents.shot_agent import generate_shots
from src.cache import cache_manager
from src.logging_config import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger()


async def test_research_agent():
    """Test research agent"""
    print("\n" + "=" * 60)
    print("Testing Research Agent")
    print("=" * 60)
    
    try:
        result = await research_topics("motivation")
        print(f"\n✓ Generated {len(result['topics'])} topics")
        print("\nFirst 3 topics:")
        for topic in result['topics'][:3]:
            print(f"  • {topic}")
    except Exception as e:
        print(f"\n✗ Failed: {e}")


async def test_script_agent():
    """Test script agent"""
    print("\n" + "=" * 60)
    print("Testing Script Agent")
    print("=" * 60)
    
    try:
        script = await generate_script("एक छोटे बच्चे की दोस्ती की कहानी")
        print(f"\n✓ Generated script ({len(script)} chars)")
        print(f"\nFirst 200 chars:\n{script[:200]}...")
    except Exception as e:
        print(f"\n✗ Failed: {e}")


async def test_shot_agent():
    """Test shot agent"""
    print("\n" + "=" * 60)
    print("Testing Shot Agent")
    print("=" * 60)
    
    test_script = """
    एक बार की बात है, एक छोटा बच्चा था जो बहुत अकेला था।
    एक दिन उसे एक छोटा पिल्ला मिला। वे दोनों अच्छे दोस्त बन गए।
    """
    
    try:
        shots = await generate_shots(test_script, num_shots=6)
        print(f"\n✓ Generated {len(shots)} shots")
        print("\nFirst 2 shots:")
        for i, shot in enumerate(shots[:2], 1):
            print(f"\n  {i}. {shot[:100]}...")
    except Exception as e:
        print(f"\n✗ Failed: {e}")


async def test_cache():
    """Test Redis cache"""
    print("\n" + "=" * 60)
    print("Testing Redis Cache")
    print("=" * 60)
    
    try:
        await cache_manager.connect()
        
        # Test set and get
        await cache_manager.set("test_key", {"hello": "world"}, ttl=60)
        value = await cache_manager.get("test_key")
        
        if value and value.get("hello") == "world":
            print("\n✓ Cache working correctly")
        else:
            print("\n✗ Cache not working as expected")
        
        # Test metrics
        await cache_manager.increment_metric("test_metric")
        count = await cache_manager.get_metric("test_metric")
        print(f"✓ Metrics working (count: {count})")
        
        await cache_manager.disconnect()
        
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        print("Make sure Redis is running: redis-server")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("UPGRADED AGENT TESTS")
    print("=" * 60)
    
    # Test cache first
    await test_cache()
    
    # Test agents
    await test_research_agent()
    await test_script_agent()
    await test_shot_agent()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
