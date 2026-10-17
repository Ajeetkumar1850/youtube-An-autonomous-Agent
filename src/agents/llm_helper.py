"""
Universal LLM Helper for all agents
Automatically uses configured LLM provider (Groq, Gemini, Together, or Ollama)
"""
import asyncio
from typing import Optional
import structlog
from src.config import settings
from src.cache import cache_manager

logger = structlog.get_logger()


async def generate_with_cache(
    prompt: str,
    cache_key: Optional[str] = None,
    temperature: float = None,
    max_tokens: int = None
) -> str:
    """
    Generate text using configured LLM provider with caching
    
    Args:
        prompt: Input prompt
        cache_key: Optional cache key (uses prompt hash if not provided)
        temperature: Sampling temperature
        max_tokens: Max tokens to generate
    
    Returns:
        Generated text
    """
    # Use config defaults if not specified
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens
    
    # Create cache key
    if cache_key:
        full_cache_key = f"llm:{settings.llm_provider}:{cache_key}"
    else:
        import hashlib
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:16]
        full_cache_key = f"llm:{settings.llm_provider}:{prompt_hash}"
    
    # Check cache
    cached_response = await cache_manager.get_llm_response(
        model=settings.llm_provider,
        prompt=full_cache_key
    )
    
    if cached_response:
        logger.info("llm_cache_hit", provider=settings.llm_provider)
        return cached_response
    
    # Generate with provider
    logger.info(
        "llm_generating",
        provider=settings.llm_provider,
        prompt_length=len(prompt)
    )
    
    try:
        # Get API key for provider
        api_key = None
        if settings.llm_provider == "groq":
            api_key = settings.groq_api_key
        elif settings.llm_provider == "gemini":
            api_key = settings.gemini_api_key
        elif settings.llm_provider == "together":
            api_key = settings.together_api_key
        
        # Use appropriate provider
        if settings.llm_provider == "groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            
            completion = client.chat.completions.create(
                model=settings.ollama_model or "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            response = completion.choices[0].message.content.strip()
            
        elif settings.llm_provider == "gemini":
            from google import genai
            
            client = genai.Client(api_key=api_key)
            
            result = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            response = result.text.strip() if hasattr(result, 'text') else str(result)
            
        elif settings.llm_provider == "together":
            from together import Together
            client = Together(api_key=api_key)
            
            result = client.chat.completions.create(
                model=settings.ollama_model or "meta-llama/Llama-3-8b-chat-hf",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            response = result.choices[0].message.content
            
        elif settings.llm_provider == "ollama":
            import ollama
            
            result = ollama.chat(
                model=settings.ollama_model or "llama3",
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = result['message']['content']
            
        else:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
        
        # Cache the response
        await cache_manager.set_llm_response(
            model=settings.llm_provider,
            prompt=full_cache_key,
            response=response,
            ttl=86400  # 24 hours
        )
        
        logger.info(
            "llm_completed",
            provider=settings.llm_provider,
            response_length=len(response)
        )
        
        return response
        
    except Exception as e:
        logger.error("llm_generation_failed", provider=settings.llm_provider, error=str(e))
        raise


def generate_sync(prompt: str, **kwargs) -> str:
    """
    Synchronous wrapper for generate_with_cache
    Use in non-async contexts
    """
    return asyncio.run(generate_with_cache(prompt, **kwargs))
