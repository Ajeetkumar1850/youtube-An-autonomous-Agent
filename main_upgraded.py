"""
Upgraded CLI runner for video generation
Uses LangGraph workflow with modern async patterns
"""
import asyncio
import sys
from datetime import datetime
from src.config import settings
from src.logging_config import configure_logging
from src.workflow.video_graph import create_video_graph
import structlog

# Configure logging
configure_logging()
logger = structlog.get_logger()


async def main():
    """Main entry point for CLI video generation"""
    
    print("=" * 60)
    print("YouTube Autonomous Agent - Upgraded Version 2.0")
    print("=" * 60)
    print()
    
    # Get user input
    niche = input("Enter niche: ").strip()
    
    if not niche:
        print("❌ Niche cannot be empty")
        sys.exit(1)
    
    num_images = input(f"Number of images (3-12, default 6): ").strip()
    num_images = int(num_images) if num_images.isdigit() else 6
    num_images = max(3, min(12, num_images))
    
    print(f"\n✓ Niche: {niche}")
    print(f"✓ Images: {num_images}")
    print()
    
    # Create workflow
    logger.info("creating_workflow")
    video_graph = create_video_graph()
    
    # Initial state
    initial_state = {
        "job_id": f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "niche": niche,
        "num_images": num_images,
        "error": None
    }
    
    print("🚀 Starting video generation pipeline...\n")
    start_time = datetime.now()
    
    try:
        # Execute workflow
        final_state = await video_graph.ainvoke(initial_state)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Display results
        print("\n" + "=" * 60)
        print("✅ Pipeline Completed Successfully!")
        print("=" * 60)
        print(f"\n⏱️  Total Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"\n📊 Results:")
        print(f"  • Topics: {len(final_state.get('topics', []))} found")
        print(f"  • Selected: {final_state.get('selected_topic', 'N/A')[:50]}...")
        print(f"  • Script: {len(final_state.get('script', ''))} characters")
        print(f"  • Images: {len(final_state.get('image_paths', []))} generated")
        print(f"  • Audio: {final_state.get('audio_path', 'N/A')}")
        print(f"  • Video: {final_state.get('video_path', 'N/A')}")
        print(f"  • SEO Title: {final_state.get('seo_title', 'N/A')}")
        
        if final_state.get('youtube_url'):
            print(f"  • YouTube: {final_state['youtube_url']}")
        else:
            print(f"  • YouTube: Skipped (no credentials)")
        
        print("\n" + "=" * 60)
        
        logger.info(
            "cli_execution_completed",
            duration_seconds=duration,
            video_path=final_state.get('video_path')
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        logger.warning("pipeline_interrupted")
        sys.exit(1)
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n\n❌ Pipeline Failed after {duration:.1f} seconds")
        print(f"Error: {str(e)}")
        logger.error("pipeline_failed", error=str(e), duration=duration, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
