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
        total=total,
        prompt=prompt[:100]
    )
    
    # Enhanced prompt
    enhanced_prompt = f"{prompt}, professional photography, high quality, 4k, detailed"
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # Use smaller size for faster generation
    url = f"{settings.image_api_url}/{encoded_prompt}?width=1080&height=1920&nologo=true"
    
    try:
        # Increased timeout to 60 seconds
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status == 200:
                # Create scenes folder
                os.makedirs(settings.scenes_dir, exist_ok=True)
                
                filepath = os.path.join(settings.scenes_dir, filename)
                
                # Write image data
                content = await response.read()
                
                # Check if valid image (at least 10KB)
                if len(content) < 10000:
                    raise ValueError(f"Image too small: {len(content)} bytes")
                
                with open(filepath, "wb") as f:
                    f.write(content)
                
                file_size = len(content)
                logger.info(
                    "image_generated",
                    filename=filename,
                    size_kb=file_size // 1024,
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
        logger.error("image_generation_timeout", filename=filename, timeout=60)
        raise
    except Exception as e:
        logger.error("image_generation_error", filename=filename, error=str(e))
        raise


async def generate_images_parallel(shots: List[str], batch_size: int = 3) -> List[str]:
    """
    Generate images with simple sequential processing
    """
    logger.info("image_agent_started", total_images=len(shots))
    
    image_paths = []
    
    import requests
    
    for i, shot in enumerate(shots):
        filename = f"scene{i + 1}.png"
        logger.info(f"Generating image {i+1}/{len(shots)}: {shot[:50]}...")
        
        try:
            # Enhanced prompt
            enhanced_prompt = f"{shot}, professional photography, high quality, detailed"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Simple URL
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
            
            # Synchronous request with timeout
            response = requests.get(url, timeout=45)
            
            if response.status_code == 200 and len(response.content) > 10000:
                # Create scenes folder
                os.makedirs(settings.scenes_dir, exist_ok=True)
                
                filepath = os.path.join(settings.scenes_dir, filename)
                
                # Write image
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                image_paths.append(filepath)
                logger.info(f"SUCCESS: Image {i+1}/{len(shots)}, size={len(response.content)//1024}KB")
            else:
                logger.error(f"FAILED: Image {i+1}/{len(shots)}, status={response.status_code}")
                
        except Exception as e:
            logger.error(f"FAILED: Image {i+1}/{len(shots)}", error=str(e))
        
        # Wait 2 seconds between images
        if i < len(shots) - 1:
            await asyncio.sleep(2)
    
    logger.info(f"image_agent_completed: {len(image_paths)}/{len(shots)} images generated")
    
    if len(image_paths) == 0:
        raise ValueError(f"All images failed to generate")
    
    if len(image_paths) < len(shots) // 2:
        raise ValueError(f"Too many images failed. Only {len(image_paths)}/{len(shots)} generated")
    
    return image_paths


def image_agent_node(state: Dict) -> Dict:
    """LangGraph node for image agent"""
    import asyncio
    
    shots = state.get("shots")
    
    if not shots:
        raise ValueError("No shots available for image generation")
    
    # Generate images sequentially with delays
    image_paths = asyncio.run(generate_images_parallel(shots, batch_size=1))
    
    return {
        **state,
        "image_paths": image_paths
    }
