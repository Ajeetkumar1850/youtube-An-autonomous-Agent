# Tech Stack Interview Questions - Agentic AI Role

## Python Fundamentals

**Q: Why use asyncio in voice_agent.py?**
**A:** edge-tts is an async library. Using `asyncio.run()` creates an event loop to execute the async `text_to_speech` function. This allows non-blocking I/O operations when communicating with Microsoft's TTS service.

**Q: Explain the use of lambda functions in video_agent.py.**
**A:** Lambdas create time-dependent effects:
```python
lambda t: 1.05 + 0.03 * (t % 0.5)  # Pulse effect over time
lambda t: -100 + (t / duration_per_shot) * 200  # Linear movement
```
MoviePy evaluates these at each frame timestamp (t) to create dynamic animations.

**Q: What's the difference between `with open()` and regular file operations?**
**A:** `with` statement ensures automatic file closing even if errors occur (context manager). Prevents file locks and resource leaks.

**Q: Why use `encoding="utf-8"` when opening files?**
**A:** Hindi text uses Unicode characters. Without UTF-8 encoding, Python defaults to system encoding which may corrupt non-ASCII characters.

## Ollama & LLM

**Q: What is Ollama?**
**A:** Local LLM runtime that runs models like Llama3 on your machine. Provides OpenAI-compatible API for inference without cloud dependency.

**Q: Explain the ollama.chat() call structure.**
**A:**
```python
ollama.chat(
    model='llama3',  # Which model to use
    messages=[{
        'role': 'user',  # Message role (user/assistant/system)
        'content': prompt  # Actual prompt text
    }]
)
```
Returns response with `message.content` containing LLM output.

**Q: What are the tradeoffs of local LLM vs cloud API?**
**A:**
Local (Ollama):
- ✅ Free, no rate limits, privacy, offline
- ❌ Requires good hardware, slower, limited models

Cloud (OpenAI/Anthropic):
- ✅ Fast, powerful models, scalable
- ❌ Costs money, rate limits, latency, privacy concerns

**Q: How would you implement streaming responses?**
**A:** Use `ollama.chat(stream=True)` and iterate:
```python
for chunk in ollama.chat(model='llama3', messages=[...], stream=True):
    print(chunk['message']['content'], end='')
```

**Q: What's the difference between system and user prompts?**
**A:** 
- System: Sets context/behavior ("You are a professional writer")
- User: Actual task ("Write a story about...")
This code only uses user role, but system messages give more control over LLM behavior.

## MoviePy & Video Processing

**Q: What is MoviePy?**
**A:** Python library for video editing. Allows programmatic video creation, combining images, adding audio, applying effects, and rendering.

**Q: Explain ImageClip vs VideoClip.**
**A:**
- ImageClip: Static image converted to video clip with set duration
- VideoClip: Actual video with frames over time
ImageClip is lighter for still images with effects applied.

**Q: How does `.resize()` with lambda work?**
**A:**
```python
clip.resize(lambda t: 1 + 0.2 * (t / duration))
```
Resizes clip dynamically over time. At t=0, size is 1x. At t=duration, size is 1.2x. Creates zoom effect.

**Q: What's the purpose of `method="compose"` in concatenate_videoclips?**
**A:** Handles clips of different sizes by compositing them. Alternatives:
- `"chain"`: Clips must be same size
- `"compose"`: Allows different sizes, positions them

**Q: Why use `preset="ultrafast"` in write_videofile?**
**A:** x264 encoding presets balance speed vs compression:
- ultrafast: Fastest, larger files
- medium: Balanced (default)
- veryslow: Best compression, very slow

For automation, ultrafast prioritizes speed over file size.

**Q: Explain fps, codec, and bitrate parameters.**
**A:**
- fps=24: 24 frames per second (cinematic standard)
- codec="libx264": H.264 video compression (widely compatible)
- bitrate="2500k": 2.5 Mbps quality (balance of size/quality)
- audio_codec="aac": AAC audio compression

**Q: How would you add subtitles to the video?**
**A:**
```python
from moviepy.editor import TextClip, CompositeVideoClip

txt_clip = TextClip("Hello", fontsize=50, color='white')
txt_clip = txt_clip.set_position('bottom').set_duration(5)
video = CompositeVideoClip([video, txt_clip])
```

## Edge-TTS & Audio

**Q: What is edge-tts?**
**A:** Python library using Microsoft Edge's text-to-speech API for free. Supports multiple languages and voices without API keys.

**Q: How does edge_tts.Communicate work?**
**A:** Creates streaming TTS connection:
```python
communicate = edge_tts.Communicate(
    text="Hello",
    voice="hi-IN-SwaraNeural",  # Hindi female voice
    rate="+10%"  # 10% faster speech
)
await communicate.save("output.wav")
```

**Q: What's the difference between .wav and .mp3 audio?**
**A:**
- WAV: Uncompressed, larger, lossless quality
- MP3: Compressed, smaller, slight quality loss

Using WAV for intermediate processing ensures no quality degradation.

**Q: How would you adjust pitch or emotion in voice?**
**A:** edge-tts supports:
- Rate: `rate="+20%"` (speed)
- Volume: `volume="+10%"` (loudness)
- Pitch: `pitch="+5Hz"` (tone)

Example: `rate="+10%", pitch="-2Hz"` for slower, deeper voice.

**Q: Why use regex to clean the script?**
**A:** LLM output may contain markdown/formatting:
```python
cleaned_script = script.replace("*", "")  # Remove bold
cleaned_script = re.sub(r'\d+', '', cleaned_script)  # Remove numbers
```
TTS engines read these literally, so cleaning prevents "asterisk asterisk" in audio.

## REST APIs & HTTP

**Q: Explain the Pollinations AI API call.**
**A:**
```python
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920"
response = requests.get(url, timeout=90)
```
URL-based API: prompt in URL, returns image bytes. No auth required.

**Q: Why use urllib.parse.quote?**
**A:** Encodes special characters for URLs:
- Space → `%20`
- Comma → `%2C`
Without encoding, "cute cat, animated" breaks the URL.

**Q: What does timeout=90 do?**
**A:** Raises exception if request takes >90 seconds. Prevents indefinite hanging if API is slow/down.

**Q: How would you implement retry logic?**
**A:**
```python
import time
for attempt in range(3):
    try:
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            return response.content
    except:
        time.sleep(2 ** attempt)  # Exponential backoff
return None
```

**Q: What status codes would you check for?**
**A:**
- 200: Success
- 429: Rate limited (wait and retry)
- 500: Server error (retry)
- 400: Bad request (don't retry, fix input)
- 401: Unauthorized (check API key)

## Google APIs & OAuth

**Q: What is OAuth2 flow?**
**A:** Authorization framework allowing third-party access without passwords:
1. App requests permission from user
2. User grants access via Google login
3. App receives access token
4. App uses token to call APIs

**Q: Explain InstalledAppFlow vs other OAuth flows.**
**A:** For desktop/CLI apps (not web apps):
```python
flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    SCOPES
)
credentials = flow.run_local_server(port=0)
```
Starts local web server for OAuth callback.

**Q: What are OAuth scopes?**
**A:** Permissions requested:
```python
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
```
This scope only allows video uploading, not deleting/editing. Principle of least privilege.

**Q: How does MediaFileUpload work?**
**A:**
```python
MediaFileUpload("videos/final_video.mp4")
```
Handles chunked uploading of large files to Google APIs with automatic resume capability.

**Q: What's the difference between snippet and status in YouTube API?**
**A:**
- `snippet`: Metadata (title, description, tags, category)
- `status`: Publishing settings (privacy, publish time, license)

**Q: How would you implement progress tracking for uploads?**
**A:**
```python
from googleapiclient.http import MediaFileUpload

media = MediaFileUpload('video.mp4', chunksize=1024*1024, resumable=True)
request = youtube.videos().insert(..., media_body=media)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Uploaded {int(status.progress() * 100)}%")
```

## Regular Expressions (Regex)

**Q: Explain `re.sub(r'^\d+[\.\)]\s*', '', line)`.**
**A:**
- `^`: Start of line
- `\d+`: One or more digits
- `[\.\)]`: Literal dot or parenthesis
- `\s*`: Zero or more whitespace
- Replaces "1. ", "2) ", etc. with empty string

Removes numbering from LLM output.

**Q: What's the difference between `re.sub` and `str.replace`?**
**A:**
- `str.replace("*", "")`: Literal string matching
- `re.sub(r'\d+', '', text)`: Pattern matching (any digits)

Regex is more powerful for complex patterns.

**Q: How would you validate an email with regex?**
**A:**
```python
import re
pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
if re.match(pattern, email):
    print("Valid email")
```

## File I/O & OS Operations

**Q: Why use `os.makedirs("scenes", exist_ok=True)`?**
**A:**
- Creates directory if it doesn't exist
- `exist_ok=True`: Don't error if directory already exists
Prevents crashes on repeated runs.

**Q: What's the difference between `os.path` and `pathlib`?**
**A:**
- `os.path`: String-based, older API
- `pathlib`: Object-oriented, modern

Example:
```python
# os.path
path = os.path.join("scenes", "image.png")

# pathlib
path = Path("scenes") / "image.png"
```

**Q: How do you check if a file exists before reading?**
**A:**
```python
import os
if os.path.exists("file.txt"):
    with open("file.txt") as f:
        content = f.read()
```

**Q: Explain file modes: 'r', 'w', 'a', 'rb', 'wb'.**
**A:**
- `r`: Read text
- `w`: Write text (overwrite)
- `a`: Append text
- `rb`: Read binary (images, videos)
- `wb`: Write binary
- `r+`: Read and write

## Agent Design Patterns

**Q: What is the difference between agents and microservices?**
**A:**
Microservices:
- Independent services with APIs
- Synchronous/async communication
- Fixed behavior

Agents:
- Autonomous decision-making
- Can use tools and LLMs
- Goal-oriented behavior
- Can collaborate with other agents

**Q: What agent frameworks exist besides raw implementation?**
**A:**
- **LangGraph**: State machine for agents (from LangChain)
- **CrewAI**: Role-based multi-agent collaboration
- **AutoGen**: Microsoft's framework for agent conversations
- **LangChain**: Tools and chains for LLM apps
- **Semantic Kernel**: Microsoft's orchestration framework

**Q: How would you implement tool use in agents?**
**A:**
```python
tools = [
    {
        "name": "web_search",
        "description": "Search the web",
        "parameters": {"query": "string"}
    }
]

# LLM decides which tool to call
response = ollama.chat(model='llama3', messages=[...], tools=tools)

# Execute tool if LLM wants it
if response.get('tool_calls'):
    tool_result = execute_tool(response['tool_calls'][0])
```

**Q: What is ReAct prompting?**
**A:** Reasoning + Acting pattern:
1. **Thought**: Agent reasons about what to do
2. **Action**: Agent takes action (calls tool)
3. **Observation**: Agent sees result
4. Repeat until task complete

Example: "Thought: I need weather data. Action: call weather_api('NYC'). Observation: 72°F sunny."

**Q: How would you implement memory for agents?**
**A:**
- Short-term: Conversation history in messages array
- Long-term: Vector database (Pinecone, Weaviate) for retrieval
- Episodic: Store task outcomes for learning
- Semantic: Store facts/knowledge extracted from conversations

**Q: What's the difference between autonomous agents and chatbots?**
**A:**
Chatbots:
- React to user input
- Stateless or simple state
- Single turn or conversation

Autonomous Agents:
- Proactive goal-seeking
- Complex state management
- Use tools and external APIs
- Multi-step reasoning
- Can collaborate with other agents

## Prompt Engineering

**Q: What makes a good prompt for agents?**
**A:**
1. **Clear role**: "You are a professional YouTube strategist"
2. **Specific task**: "Generate 10 high-CTR video ideas"
3. **Constraints**: "No markdown, no numbering, 45-60 seconds"
4. **Format**: "Return as: TITLE:\n(content)\n"
5. **Examples**: Show desired output format
6. **Context**: Provide relevant information

**Q: How do you prevent LLM hallucination?**
**A:**
- Provide concrete examples
- Request citations/sources
- Use lower temperature (0.1-0.3 for factual)
- Validate output with external checks
- Use retrieval (RAG) for facts
- Implement confidence scores
- Request "I don't know" if uncertain

**Q: What is few-shot vs zero-shot prompting?**
**A:**
Zero-shot: No examples
```
Generate a video title for: AI robots
```

Few-shot: Provide examples
```
Examples:
Topic: AI robots → Title: "🤖 AI Robots Taking Over? Truth Revealed!"
Topic: Space travel → Title: "🚀 Mars in 2025? NASA's Secret Plan"

Now generate for: AI robots
```

**Q: How would you implement chain-of-thought reasoning?**
**A:**
```python
prompt = """
Think step by step:
1. What is the main topic?
2. Who is the target audience?
3. What makes this engaging?
4. Generate title based on 1-3

Topic: {topic}
"""
```
Improves reasoning for complex tasks.

## Vector Databases & RAG

**Q: Even though not in this project, explain RAG for agents.**
**A:** Retrieval Augmented Generation:
1. User query
2. Embed query as vector
3. Search vector DB for relevant docs
4. Pass docs + query to LLM
5. LLM generates answer using docs

Prevents hallucination, adds real-time knowledge.

**Q: What vector databases exist?**
**A:**
- Pinecone: Managed, easy to use
- Weaviate: Open source, GraphQL
- Chroma: Lightweight, embedded
- Qdrant: Fast, Rust-based
- FAISS: Facebook's similarity search (not full DB)

**Q: How do embeddings work?**
**A:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Hello world")  # Returns 384-dim vector

# Similar texts have similar vectors
similarity = cosine_similarity(embedding1, embedding2)
```

## Performance & Optimization

**Q: How would you profile Python code to find bottlenecks?**
**A:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
main()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

**Q: What's the difference between threading and multiprocessing?**
**A:**
Threading:
- Shared memory
- Good for I/O-bound (API calls)
- Limited by GIL in Python

Multiprocessing:
- Separate memory
- Good for CPU-bound (video encoding)
- No GIL limitation

For image generation: Use threading (I/O-bound API calls)
For video encoding: Use multiprocessing (CPU-bound)

**Q: How would you implement caching?**
**A:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def generate_script(topic):
    # LLM call
    return script

# Or use Redis for distributed caching
import redis
r = redis.Redis()

def get_cached_script(topic):
    key = hashlib.md5(topic.encode()).hexdigest()
    cached = r.get(key)
    if cached:
        return cached.decode()
    
    script = generate_script(topic)
    r.setex(key, 3600, script)  # Cache for 1 hour
    return script
```

## Testing & Quality

**Q: How would you write unit tests for agents?**
**A:**
```python
import pytest
from unittest.mock import Mock, patch

def test_research_agent():
    # Mock Ollama response
    with patch('ollama.chat') as mock_chat:
        mock_chat.return_value = {
            'message': {'content': '1. Topic 1\n2. Topic 2'}
        }
        
        result = research_topics("AI")
        
        assert "Topic 1" in result
        assert mock_chat.called
```

**Q: What's the difference between unit and integration tests?**
**A:**
Unit tests:
- Test single function/agent
- Mock dependencies
- Fast, isolated

Integration tests:
- Test agent pipeline
- Real LLM calls
- Slow, realistic

**Q: How would you implement monitoring?**
**A:**
```python
import logging
from prometheus_client import Counter, Histogram

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
video_created = Counter('videos_created_total', 'Total videos created')
generation_time = Histogram('video_generation_seconds', 'Time to generate video')

def create_video(images):
    with generation_time.time():
        logger.info(f"Creating video with {len(images)} images")
        video = # ... video creation
        video_created.inc()
        logger.info("Video created successfully")
        return video
```

## LangGraph & Agent Orchestration

**Q: What is LangGraph and why use it?**
**A:** LangGraph is a framework for building stateful multi-agent systems using graphs. Key benefits:
- **State Management**: Automatic state propagation between agents
- **Visual Workflow**: Graph-based visualization of agent flow
- **Built-in Checkpointing**: Save/restore state for recovery
- **Conditional Edges**: Dynamic routing based on state
- **Parallel Execution**: Run independent agents simultaneously
- **Type Safety**: Integration with Pydantic for validation

Better than sequential scripts because it handles state, errors, and orchestration automatically.

**Q: Explain the LangGraph workflow structure in your project.**
**A:**
```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)

# Add nodes (agents)
workflow.add_node("research", research_agent)
workflow.add_node("script", script_agent)
workflow.add_node("shots", shot_agent)
workflow.add_node("images", image_agent)
workflow.add_node("voice", voice_agent)
workflow.add_node("video", video_agent)
workflow.add_node("seo", seo_agent)
workflow.add_node("upload", upload_agent)

# Define edges (flow)
workflow.set_entry_point("research")
workflow.add_edge("research", "script")
workflow.add_edge("script", "shots")
workflow.add_edge("shots", "images")
workflow.add_edge("images", "voice")
workflow.add_edge("voice", "video")
workflow.add_edge("video", "seo")
workflow.add_edge("seo", "upload")
workflow.set_finish_point("upload")
```

**Q: How does state management work in LangGraph?**
**A:** Each agent receives the full state dictionary and returns updated state:
```python
async def research_agent(state: AgentState) -> AgentState:
    # Access previous state
    niche = state.niche
    
    # Do work
    topics = await generate_topics(niche)
    
    # Update state
    state.topics = topics
    state.selected_topic = topics[0]
    
    return state  # LangGraph propagates to next agent
```

Benefits:
- No file I/O needed
- Automatic state propagation
- Type-safe with Pydantic
- Easy to test each agent

**Q: What are conditional edges in LangGraph?**
**A:** Dynamic routing based on state conditions:
```python
def should_retry(state):
    return "retry" if state.error else "continue"

workflow.add_conditional_edges(
    "image_agent",
    should_retry,
    {
        "retry": "image_agent",  # Retry on error
        "continue": "voice_agent"  # Continue on success
    }
)
```

Use cases: Error handling, quality checks, A/B testing paths.

**Q: How would you implement parallel execution in LangGraph?**
**A:**
```python
# Generate images and voice in parallel
workflow.add_node("parallel_start", lambda s: s)
workflow.add_edge("shots", "parallel_start")

# Branch to parallel tasks
workflow.add_edge("parallel_start", "images")
workflow.add_edge("parallel_start", "voice")

# Merge results
workflow.add_node("merge", merge_results)
workflow.add_edge("images", "merge")
workflow.add_edge("voice", "merge")
workflow.add_edge("merge", "video")
```

Current project could parallelize image + voice generation for 30% speed improvement.

## FastAPI & REST API

**Q: Why FastAPI over Flask/Django?**
**A:**
- **Async Support**: Built on asyncio for non-blocking I/O
- **Type Validation**: Automatic validation with Pydantic
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Performance**: One of fastest Python frameworks
- **Modern**: Python 3.7+ type hints, async/await

Perfect for agent systems that need async operations and strong typing.

**Q: Explain async/await in your API.**
**A:**
```python
@app.post("/videos")
async def create_video(request: VideoRequest, background_tasks: BackgroundTasks):
    # Non-blocking database query
    job = await db.create_job(request.niche)
    
    # Run video generation in background
    background_tasks.add_task(process_video, job.id, request)
    
    # Return immediately (doesn't wait for video generation)
    return VideoResponse(job_id=job.id, status="pending")
```

**Benefits:**
- API responds instantly (<50ms)
- Video generation runs in background (5-8 min)
- Can handle multiple concurrent requests

**Q: How does Pydantic validation work?**
**A:**
```python
class VideoRequest(BaseModel):
    niche: str = Field(..., min_length=1, max_length=200)
    num_images: int = Field(default=6, ge=3, le=12)

# FastAPI automatically validates
@app.post("/videos")
async def create_video(request: VideoRequest):
    # request.niche is guaranteed to be 1-200 chars
    # request.num_images is guaranteed to be 3-12
```

Invalid requests return 422 with detailed error message. No manual validation needed.

**Q: Explain background tasks vs celery workers.**
**A:**
**BackgroundTasks (current):**
- Built into FastAPI
- Runs in same process
- Simple, no setup
- Good for <100 req/day

**Celery:**
- Separate worker processes
- Distributed task queue
- Redis/RabbitMQ broker
- Good for >1000 req/day

Current project uses BackgroundTasks for simplicity. Would switch to Celery at scale.

**Q: How do you handle API errors?**
**A:**
```python
from fastapi import HTTPException

@app.get("/videos/{job_id}")
async def get_status(job_id: str):
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return VideoStatusResponse.from_orm(job)

# Custom exception handler
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

## Redis & Caching

**Q: What is Redis and why use it?**
**A:** Redis is an in-memory data store. Used for:
- **Caching**: Store LLM responses (avoid duplicate API calls)
- **Session Storage**: Track job state
- **Rate Limiting**: Count requests per user
- **Pub/Sub**: Real-time notifications

Key feature: Microsecond latency vs milliseconds for disk/DB.

**Q: Explain your caching strategy.**
**A:**
```python
import hashlib
from redis import asyncio as aioredis

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost")
    
    async def get_or_generate(self, prompt: str, model: str):
        # Create cache key
        key = f"llm:{hashlib.md5((prompt + model).encode()).hexdigest()}"
        
        # Check cache
        cached = await self.redis.get(key)
        if cached:
            logger.info("Cache hit", extra={"key": key})
            return cached.decode()
        
        # Cache miss - call LLM
        logger.info("Cache miss", extra={"key": key})
        response = await ollama.chat(model=model, messages=[...])
        
        # Store in cache (24h TTL)
        await self.redis.setex(key, 86400, response)
        
        return response
```

**Impact:** 80% cache hit rate = 5x fewer LLM calls = $$ saved + faster response.

**Q: What's the difference between Redis and Memcached?**
**A:**
Redis:
- Data structures (strings, lists, sets, hashes)
- Persistence (can save to disk)
- Pub/Sub messaging
- Atomic operations
- More features

Memcached:
- Simple key-value only
- No persistence
- Slightly faster for simple ops
- Less memory overhead

Redis better for complex caching needs.

**Q: How do you handle cache invalidation?**
**A:** "Two hard things in computer science: cache invalidation and naming things"

Strategies:
1. **TTL (Time To Live)**: Auto-expire after 24h (current approach)
2. **Event-based**: Invalidate when data changes
3. **Version keys**: Include version in cache key
4. **Manual**: Flush cache on deploy/update

```python
# TTL approach
await redis.setex(key, 86400, value)  # 24h expiry

# Manual invalidation
await redis.delete(f"llm:script:*")  # Clear all script caches
```

**Q: What are Redis data types and when to use each?**
**A:**
- **String**: Simple key-value (cache entries)
- **Hash**: Store objects (user session data)
- **List**: Queues (job queue)
- **Set**: Unique items (tags, categories)
- **Sorted Set**: Leaderboards, rankings
- **Stream**: Event logs, audit trail

Example:
```python
# String for cache
await redis.set("key", "value")

# Hash for job data
await redis.hset("job:123", mapping={"status": "running", "progress": 50})

# List for queue
await redis.lpush("job_queue", job_id)
job_id = await redis.rpop("job_queue")
```

## PostgreSQL & Async SQLAlchemy

**Q: Why PostgreSQL over MySQL/SQLite?**
**A:**
PostgreSQL advantages:
- **JSON support**: Store complex data types
- **Full-text search**: Built-in search capabilities
- **JSONB indexing**: Fast JSON queries
- **Arrays**: Native array support
- **Robust**: ACID compliant, reliable
- **Extensions**: PostGIS, pg_trgm, etc.

SQLite good for dev/testing, PostgreSQL for production.

**Q: Explain async SQLAlchemy.**
**A:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Async engine
engine = create_async_engine("postgresql+asyncpg://localhost/db")

# Async session
async with AsyncSession(engine) as session:
    # Non-blocking query
    result = await session.execute(
        select(VideoJob).where(VideoJob.id == job_id)
    )
    job = result.scalar_one_or_none()
```

**Benefits:**
- Non-blocking database operations
- Handle multiple requests concurrently
- Better resource utilization

**Q: Show your database schema.**
**A:**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, Integer, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

class VideoJob(Base):
    __tablename__ = "video_jobs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    niche: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str] = mapped_column(String(100))
    
    # Output paths
    video_path: Mapped[str] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Error tracking
    error: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Q: How do you handle database migrations?**
**A:** Use Alembic (SQLAlchemy migration tool):
```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add video_jobs table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

Tracks schema changes, allows versioning, safe upgrades/rollbacks.

## Structlog & Logging

**Q: What is structlog and why use it?**
**A:** Structured logging library that outputs JSON logs:

**Traditional logging:**
```
2024-01-01 12:00:00 - INFO - Video generation started
```

**Structlog:**
```json
{
  "event": "video_generation_started",
  "job_id": "uuid-123",
  "niche": "motivation",
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info"
}
```

**Benefits:**
- Machine-readable (easy to parse)
- Searchable (query by job_id, niche, etc.)
- Context-rich (include extra fields)
- Compatible with log aggregation tools

**Q: How do you implement structlog?**
**A:**
```python
import structlog

# Configure
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

# Use
logger = structlog.get_logger()

logger.info(
    "image_generated",
    job_id=job_id,
    image_path=path,
    duration_seconds=duration
)
```

**Q: What log levels exist and when to use?**
**A:**
- **DEBUG**: Detailed info for debugging (dev only)
- **INFO**: General information (job started, completed)
- **WARNING**: Unexpected but handled (retry attempt, fallback used)
- **ERROR**: Error that affects operation (image gen failed)
- **CRITICAL**: System failure (database down, out of memory)

Example:
```python
logger.debug("Calling LLM", prompt=prompt[:100])
logger.info("video_created", job_id=job_id, duration=duration)
logger.warning("cache_miss", key=key)
logger.error("image_generation_failed", error=str(e), shot=shot)
logger.critical("database_connection_lost")
```

## Prometheus & Monitoring

**Q: What is Prometheus?**
**A:** Time-series monitoring system that collects metrics:
- **Counters**: Incrementing values (total videos created)
- **Gauges**: Current value (active jobs)
- **Histograms**: Distribution (video generation time)
- **Summaries**: Percentiles (p95, p99 latency)

Integrates with Grafana for visualization.

**Q: How do you implement Prometheus metrics?**
**A:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
videos_created = Counter('videos_created_total', 'Total videos created')
video_duration = Histogram('video_generation_seconds', 'Video generation time')
active_jobs = Gauge('active_jobs', 'Currently active jobs')

# Use metrics
def generate_video(job_id):
    active_jobs.inc()
    
    with video_duration.time():
        # ... generate video ...
        pass
    
    videos_created.inc()
    active_jobs.dec()

# Expose metrics endpoint
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Q: What metrics would you track?**
**A:**
**Business Metrics:**
- Total videos created
- Success/failure rate
- Average generation time
- Videos per day/hour

**Technical Metrics:**
- API response time (p50, p95, p99)
- Database query duration
- Cache hit rate
- LLM token usage
- Error rate by agent

**Resource Metrics:**
- CPU usage
- Memory usage
- Disk usage
- Network I/O

**Q: How would you set up alerts?**
**A:**
```yaml
# Prometheus alert rules
groups:
  - name: video_pipeline
    rules:
      - alert: HighFailureRate
        expr: rate(videos_failed_total[5m]) > 0.1
        annotations:
          summary: "Video failure rate above 10%"
      
      - alert: SlowGeneration
        expr: histogram_quantile(0.95, video_generation_seconds) > 600
        annotations:
          summary: "95th percentile generation time > 10min"
      
      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.5
        annotations:
          summary: "Cache hit rate below 50%"
```

## Tenacity & Retry Logic

**Q: What is Tenacity?**
**A:** Python retry library with decorators:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def generate_image(prompt):
    # Retries up to 3 times with exponential backoff:
    # Attempt 1: immediate
    # Attempt 2: wait 2s
    # Attempt 3: wait 4s
    response = await api_call(prompt)
    return response
```

**Q: When should you use retries?**
**A:**
**Retry (transient failures):**
- Network timeouts
- Rate limiting (429)
- Server errors (500, 502, 503)
- Temporary service unavailability

**Don't retry (permanent failures):**
- Bad request (400)
- Unauthorized (401)
- Not found (404)
- Validation errors

**Q: What retry strategies exist?**
**A:**
1. **Fixed delay**: Wait 5s between retries
2. **Exponential backoff**: Wait 1s, 2s, 4s, 8s
3. **Exponential with jitter**: Add randomness to avoid thundering herd
4. **Fibonacci backoff**: Wait 1s, 1s, 2s, 3s, 5s

```python
# Exponential backoff
@retry(wait=wait_exponential(multiplier=1, max=60))

# Fixed delay
@retry(wait=wait_fixed(5))

# Stop conditions
@retry(stop=stop_after_attempt(3))  # Max 3 attempts
@retry(stop=stop_after_delay(60))   # Stop after 60s total
```

## Async/Await & Concurrency

**Q: Explain async/await in Python.**
**A:**
**Synchronous (blocking):**
```python
def generate_images(shots):
    images = []
    for shot in shots:
        img = generate_image(shot)  # Blocks for 15s
        images.append(img)
    return images  # Takes 6 * 15 = 90s
```

**Asynchronous (non-blocking):**
```python
async def generate_images(shots):
    tasks = [generate_image(shot) for shot in shots]
    images = await asyncio.gather(*tasks)  # Parallel, takes ~15s
    return images
```

**Benefits:** 6x faster for I/O-bound operations (API calls).

**Q: When to use async vs threading vs multiprocessing?**
**A:**
**Async/await:** I/O-bound (API calls, database, file I/O)
- Single thread, event loop
- Very lightweight
- Best for: Image generation (API), database queries

**Threading:** I/O-bound with blocking libraries
- Multiple threads, shared memory
- GIL limits CPU usage
- Best for: Legacy libraries without async support

**Multiprocessing:** CPU-bound (computation)
- Multiple processes, separate memory
- No GIL limitation
- Best for: Video encoding, image processing

**Q: Show parallel image generation.**
**A:**
```python
async def generate_images_parallel(shots: List[str]) -> List[str]:
    async def generate_single(shot: str, index: int) -> str:
        logger.info("generating_image", index=index, shot=shot)
        
        # Make API call
        response = await api.generate_image(shot)
        
        # Save image
        path = f"scenes/scene{index+1}.png"
        await save_image(response, path)
        
        return path
    
    # Create tasks for all images
    tasks = [generate_single(shot, i) for i, shot in enumerate(shots)]
    
    # Run in parallel
    image_paths = await asyncio.gather(*tasks)
    
    return image_paths
```

**Result:** 90s → 15s (6x faster).

## Cloud & Deployment

**Q: How would you containerize this application?**
**A:**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
COPY requirements_upgraded.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ /app/src/
COPY main_upgraded.py /app/
WORKDIR /app

# Expose API port
EXPOSE 8000

# Run
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Q: How would you use AWS for this system?**
**A:**
- **ECS Fargate**: Run FastAPI containers
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **S3**: Store videos, images, audio
- **CloudFront**: CDN for video delivery
- **SQS**: Job queue for high volume
- **Lambda**: Lightweight tasks (SEO generation)
- **MediaConvert**: Professional video encoding
- **CloudWatch**: Centralized logging
- **Secrets Manager**: Store API keys

**Q: What about serverless architecture?**
**A:**
**Pros:**
- Auto-scaling
- Pay per use
- No server management
- Built-in HA

**Cons:**
- Cold starts (slow first request)
- Timeout limits (15 min Lambda)
- Video encoding too heavy
- Complex state management

**Hybrid Approach:** API on Lambda, video encoding on ECS/Fargate, queue with SQS.
