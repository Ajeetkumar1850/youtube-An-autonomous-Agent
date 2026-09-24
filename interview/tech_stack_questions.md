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

## Cloud & Deployment

**Q: How would you containerize this application?**
**A:**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run
CMD ["python", "main.py"]
```

**Q: How would you use AWS for this system?**
**A:**
- **S3**: Store videos, images, audio
- **Lambda**: Run lightweight agents
- **ECS/EKS**: Run video encoding (CPU/GPU)
- **SQS**: Message queue for agents
- **DynamoDB**: Store metadata
- **CloudWatch**: Logging and monitoring
- **MediaConvert**: Professional video encoding
- **Secrets Manager**: Store API keys

**Q: What about serverless architecture?**
**A:**
Pros:
- Auto-scaling
- Pay per use
- No server management

Cons:
- Cold starts (slow first request)
- Timeout limits (15 min Lambda)
- Video encoding too heavy for Lambda

Hybrid: Use Lambda for lightweight agents, ECS for video encoding.
