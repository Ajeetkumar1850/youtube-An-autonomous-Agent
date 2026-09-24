"""
Image Agent - Upgraded with async, retry, and parallel generation
"""
import os
import asyncio
from typing import Dict, List
import aiohttp
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog
from src.config import settings

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    reraise=True
)
async def generate_single_image(
    session: aiohttp.ClientSession,
    prompt: str,
    filename: str,
    index: int,
    total: int
) -> str:
    """
    Generate a single image using Pollinations AI
    """
    logger.info(
        "generating_image",
        filename=filename,
        index=index,
        total=total
    )
    
    # Enhanced prompt
    enhanced_prompt = f"{prompt}, character in motion, animated pose, expressive face with emotion, dynamic action"
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    url = f"{settings.image_api_url}/{encoded_prompt}?width=1080&height=1920&model=flux&enhance=true&nologo=true"
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=settings.image_api_timeout)) as response:
            if response.status == 200:
                # Create scenes folder
                os.makedirs(settings.scenes_dir, exist_ok=True)
                
                filepath = os.path.join(settings.scenes_dir, filename)
                
                # Write image data
                content = await response.read()
                with open(filepath, "wb") as f:
                    f.write(content)
                
                file_size = len(content)
                logger.info(
                    "image_generated",
                    filename=filename,
                    size_bytes=file_size,
                    progress=f"{index}/{total}"
                )
                
                return filepath
            else:
                error_msg = f"HTTP {response.status}"
                logger.error(
                    "image_generation_failed",
                    filename=filename,
                    status=response.status
                )
                raise aiohttp.ClientError(error_msg)
                
    except asyncio.TimeoutError:
        logger.error("image_generation_timeout", filename=filename)
        raise
    except Exception as e:
        logger.error("image_generation_error", filename=filename, error=str(e))
        raise


async def generate_images_parallel(shots: List[str], batch_size: int = 2) -> List[str]:
    """
    Generate images in parallel batches to avoid rate limiting
    """
    logger.info("image_agent_started", total_images=len(shots), batch_size=batch_size)
    
    image_paths = []
    
    async with aiohttp.ClientSession() as session:
        # Process in batches
        for batch_start in range(0, len(shots), batch_size):
            batch_end = min(batch_start + batch_size, len(shots))
            batch = shots[batch_start:batch_end]
            
            logger.info(
                "processing_batch",
                batch_num=batch_start // batch_size + 1,
                total_batches=(len(shots) + batch_size - 1) // batch_size
            )
            
            # Create tasks for this batch
            tasks = []
            for i, shot in enumerate(batch):
                global_index = batch_start + i
                filename = f"scene{global_index + 1}.png"
                
                task = generate_single_image(
                    session,
                    shot,
                    filename,
                    global_index + 1,
                    len(shots)
                )
                tasks.append(task)
            
            # Run batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error("batch_image_failed", error=str(result))
                    # Use placeholder or skip
                    continue
                else:
                    image_paths.append(result)
            
            # Delay between batches to avoid rate limiting
            if batch_end < len(shots):
                await asyncio.sleep(2)
    
    logger.info(
        "image_agent_completed",
        generated=len(image_paths),
        required=len(shots)
    )
    
    if len(image_paths) < len(shots) // 2:
        raise ValueError(f"Too many images failed. Only {len(image_paths)}/{len(shots)} generated")
    
    return image_paths


def image_agent_node(state: Dict) -> Dict:
    """LangGraph node for image agent"""
    import asyncio
    
    shots = state.get("shots")
    
    if not shots:
        raise ValueError("No shots available for image generation")
    
    image_paths = asyncio.run(generate_images_parallel(shots, batch_size=2))
    
    return {
        **state,
        "image_paths": image_paths
    }
