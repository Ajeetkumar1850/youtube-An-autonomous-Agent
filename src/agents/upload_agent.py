"""
Upload Agent - Upgraded with better error handling (optional step)
"""
import os
from typing import Dict, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.config import settings

logger = structlog.get_logger()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=2, min=10, max=60),
    reraise=True
)
def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "22"
) -> Dict[str, str]:
    """
    Upload video to YouTube
    
    Returns dict with video_id and url
    """
    logger.info(
        "upload_agent_started",
        video_path=video_path,
        title=title
    )
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(settings.youtube_client_secret_path):
        logger.warning(
            "youtube_credentials_missing",
            path=settings.youtube_client_secret_path
        )
        raise FileNotFoundError(
            f"YouTube credentials not found at {settings.youtube_client_secret_path}"
        )
    
    try:
        # Authentication
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.youtube_client_secret_path,
            SCOPES
        )
        
        credentials = flow.run_local_server(port=0)
        
        # Build YouTube service
        youtube = build("youtube", "v3", credentials=credentials)
        
        logger.info("youtube_authenticated")
        
        # Upload video
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": "private"
                }
            },
            media_body=MediaFileUpload(video_path, resumable=True)
        )
        
        logger.info("uploading_to_youtube")
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info("upload_progress", progress_percent=progress)
        
        video_id = response["id"]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        logger.info(
            "upload_agent_completed",
            video_id=video_id,
            youtube_url=youtube_url
        )
        
        return {
            "video_id": video_id,
            "url": youtube_url
        }
        
    except Exception as e:
        logger.error("youtube_upload_failed", error=str(e), exc_info=True)
        raise


def upload_agent_node(state: Dict) -> Dict:
    """LangGraph node for upload agent"""
    video_path = state.get("video_path")
    seo_title = state.get("seo_title", "AI Generated Video")
    seo_description = state.get("seo_description", "Created with AI")
    seo_tags = state.get("seo_tags", ["AI"])
    
    if not video_path:
        raise ValueError("No video available for upload")
    
    try:
        result = upload_to_youtube(
            video_path=video_path,
            title=seo_title,
            description=seo_description,
            tags=seo_tags,
            category_id=settings.youtube_category_id
        )
        
        return {
            **state,
            "youtube_video_id": result["video_id"],
            "youtube_url": result["url"]
        }
        
    except FileNotFoundError as e:
        # Skip upload if credentials missing (development mode)
        logger.warning("skipping_youtube_upload", reason=str(e))
        return {
            **state,
            "youtube_video_id": None,
            "youtube_url": None
        }
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        # Don't fail entire pipeline if upload fails
        return {
            **state,
            "youtube_video_id": None,
            "youtube_url": None,
            "error": f"Upload failed: {str(e)}"
        }
