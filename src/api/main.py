"""
FastAPI application for video generation service
"""
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import structlog

from src.config import settings
from src.database import init_db, get_db
from src.cache import cache_manager
from src.logging_config import configure_logging
from src.models.schemas import (
    VideoRequest,
    VideoResponse,
    VideoStatusResponse,
    VideoStatus,
    HealthResponse
)
from src.models.database import VideoJob
from src.workflow.video_graph import create_video_graph

# Configure logging
configure_logging()
logger = structlog.get_logger()

# Prometheus metrics
video_requests_total = Counter(
    'video_requests_total',
    'Total video generation requests'
)
video_completed_total = Counter(
    'video_completed_total',
    'Total completed videos'
)
video_failed_total = Counter(
    'video_failed_total',
    'Total failed videos'
)
video_duration_seconds = Histogram(
    'video_generation_duration_seconds',
    'Time taken to generate video'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("application_starting")
    
    # Initialize database
    await init_db()
    logger.info("database_initialized")
    
    # Connect to Redis
    await cache_manager.connect()
    
    # Create LangGraph workflow
    app.state.video_graph = create_video_graph()
    logger.info("workflow_graph_created")
    
    logger.info("application_ready", host=settings.api_host, port=settings.api_port)
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")
    await cache_manager.disconnect()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title="YouTube Autonomous Agent API",
    description="AI-powered automated YouTube video generation pipeline",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "YouTube Autonomous Agent",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    services = {}
    
    # Check database
    try:
        await db.execute("SELECT 1")
        services["database"] = "connected"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        await cache_manager.redis_client.ping()
        services["redis"] = "connected"
    except Exception as e:
        services["redis"] = f"error: {str(e)}"
    
    # Check Ollama
    try:
        import ollama
        ollama.list()
        services["ollama"] = "running"
    except Exception as e:
        services["ollama"] = f"error: {str(e)}"
    
    overall_status = "healthy" if all(
        "connected" in str(v) or "running" in str(v)
        for v in services.values()
    ) else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/videos", response_model=VideoResponse)
async def create_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new video generation job
    The video will be generated asynchronously in the background
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    logger.info(
        "video_request_received",
        job_id=job_id,
        niche=request.niche,
        num_images=request.num_images
    )
    
    # Create database record
    video_job = VideoJob(
        job_id=job_id,
        niche=request.niche,
        num_images=request.num_images,
        status=VideoStatus.PENDING,
        current_step="Job created"
    )
    
    db.add(video_job)
    await db.commit()
    
    # Increment metrics
    video_requests_total.inc()
    await cache_manager.increment_metric("total_videos")
    
    # Schedule background task
    background_tasks.add_task(
        process_video_job,
        job_id,
        request.niche,
        request.num_images
    )
    
    return VideoResponse(
        job_id=job_id,
        status=VideoStatus.PENDING,
        message="Video generation job created successfully",
        created_at=datetime.utcnow()
    )


@app.get("/videos/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of a video generation job"""
    
    # Try cache first
    cached_status = await cache_manager.get_job_status(job_id)
    if cached_status:
        return VideoStatusResponse(**cached_status)
    
    # Query database
    from sqlalchemy import select
    result = await db.execute(
        select(VideoJob).where(VideoJob.job_id == job_id)
    )
    video_job = result.scalar_one_or_none()
    
    if not video_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Calculate progress
    status_progress = {
        VideoStatus.PENDING: 0,
        VideoStatus.RESEARCHING: 10,
        VideoStatus.SCRIPTING: 20,
        VideoStatus.GENERATING_SHOTS: 30,
        VideoStatus.GENERATING_IMAGES: 50,
        VideoStatus.GENERATING_VOICE: 65,
        VideoStatus.CREATING_VIDEO: 75,
        VideoStatus.GENERATING_SEO: 85,
        VideoStatus.UPLOADING: 90,
        VideoStatus.COMPLETED: 100,
        VideoStatus.FAILED: video_job.progress or 0
    }
    
    response = VideoStatusResponse(
        job_id=video_job.job_id,
        status=video_job.status,
        progress=status_progress.get(video_job.status, 0),
        current_step=video_job.current_step or "Processing",
        error=video_job.error,
        video_url=video_job.video_path,
        youtube_url=video_job.youtube_url,
        created_at=video_job.created_at,
        updated_at=video_job.updated_at
    )
    
    # Cache for 30 seconds
    await cache_manager.set_job_status(
        job_id,
        response.model_dump(),
        ttl=30
    )
    
    return response


async def process_video_job(job_id: str, niche: str, num_images: int):
    """
    Background task to process video generation using LangGraph
    """
    from sqlalchemy import select, update
    from src.database import AsyncSessionLocal
    
    start_time = datetime.utcnow()
    
    logger.info("video_job_started", job_id=job_id, niche=niche)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get the workflow graph
            video_graph = app.state.video_graph
            
            # Initial state
            initial_state = {
                "job_id": job_id,
                "niche": niche,
                "num_images": num_images,
                "error": None
            }
            
            # Run the workflow
            final_state = await video_graph.ainvoke(initial_state)
            
            # Update database with final state
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            await db.execute(
                update(VideoJob)
                .where(VideoJob.job_id == job_id)
                .values(
                    status=VideoStatus.COMPLETED,
                    progress=100,
                    current_step="Completed",
                    script=final_state.get("script"),
                    video_path=final_state.get("video_path"),
                    youtube_url=final_state.get("youtube_url"),
                    seo_title=final_state.get("seo_title"),
                    duration_seconds=duration,
                    completed_at=datetime.utcnow()
                )
            )
            await db.commit()
            
            # Update metrics
            video_completed_total.inc()
            video_duration_seconds.observe(duration)
            await cache_manager.increment_metric("completed_videos")
            
            logger.info(
                "video_job_completed",
                job_id=job_id,
                duration_seconds=duration
            )
            
        except Exception as e:
            # Handle failure
            logger.error(
                "video_job_failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )
            
            await db.execute(
                update(VideoJob)
                .where(VideoJob.job_id == job_id)
                .values(
                    status=VideoStatus.FAILED,
                    error=str(e),
                    current_step="Failed"
                )
            )
            await db.commit()
            
            video_failed_total.inc()
            await cache_manager.increment_metric("failed_videos")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
