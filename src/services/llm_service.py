"""
LLM Service with multiple free API providers
Supports: Groq (fast & free), Google Gemini, Together AI, Ollama
"""
import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger()


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass


class GroqProvider(LLMProvider):
    """Groq - Fast & Free (Recommended)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Groq not installed. Install with: pip install groq"
            )
    
    async def generate(self, prompt: str, model: str = "llama-3.1-8b-instant", **kwargs) -> str:
        """Generate response using Groq"""
        try:
            logger.info("groq_generating", model=model, prompt_length=len(prompt))
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            
            response = completion.choices[0].message.content
            
            logger.info("groq_completed", response_length=len(response))
            return response
            
        except Exception as e:
            logger.error("groq_failed", error=str(e))
            raise


class GeminiProvider(LLMProvider):
    """Google Gemini - Free & Good"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except ImportError:
            raise ImportError(
                "Google Generative AI not installed. "
                "Install with: pip install google-generativeai"
            )
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            logger.info("gemini_generating", prompt_length=len(prompt))
            
            response = self.model.generate_content(prompt)
            result = response.text
            
            logger.info("gemini_completed", response_length=len(result))
            return result
            
        except Exception as e:
            logger.error("gemini_failed", error=str(e))
            raise


class TogetherProvider(LLMProvider):
    """Together AI - Many models available"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from together import Together
            self.client = Together(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Together not installed. Install with: pip install together"
            )
    
    async def generate(self, prompt: str, model: str = "meta-llama/Llama-3-8b-chat-hf", **kwargs) -> str:
        """Generate response using Together AI"""
        try:
            logger.info("together_generating", model=model, prompt_length=len(prompt))
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            
            result = response.choices[0].message.content
            
            logger.info("together_completed", response_length=len(result))
            return result
            
        except Exception as e:
            logger.error("together_failed", error=str(e))
            raise


class OllamaProvider(LLMProvider):
    """Ollama - Local & Free"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        try:
            import ollama
            self.client = ollama
        except ImportError:
            raise ImportError(
                "Ollama not installed. Install with: pip install ollama"
            )
    
    async def generate(self, prompt: str, model: str = "llama3", **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            logger.info("ollama_generating", model=model, prompt_length=len(prompt))
            
            response = self.client.chat(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response['message']['content']
            
            logger.info("ollama_completed", response_length=len(result))
            return result
            
        except Exception as e:
            logger.error("ollama_failed", error=str(e))
            raise


class LLMService:
    """
    Unified LLM service supporting multiple providers
    """
    
    def __init__(
        self,
        provider: str = "groq",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider_name = provider.lower()
        
        # Initialize provider
        if self.provider_name == "groq":
            if not api_key:
                raise ValueError("Groq requires API key. Get from: https://console.groq.com/")
            self.provider = GroqProvider(api_key)
            
        elif self.provider_name == "gemini":
            if not api_key:
                raise ValueError("Gemini requires API key. Get from: https://makersuite.google.com/")
            self.provider = GeminiProvider(api_key)
            
        elif self.provider_name == "together":
            if not api_key:
                raise ValueError("Together requires API key. Get from: https://api.together.xyz/")
            self.provider = TogetherProvider(api_key)
            
        elif self.provider_name == "ollama":
            self.provider = OllamaProvider(base_url or "http://localhost:11434")
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info("llm_service_initialized", provider=self.provider_name)
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using configured LLM provider
        
        Args:
            prompt: Input prompt
            model: Model name (optional, uses provider default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        logger.info(
            "llm_service_generating",
            provider=self.provider_name,
            prompt_length=len(prompt)
        )
        
        kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if model:
            kwargs["model"] = model
        
        response = await self.provider.generate(prompt, **kwargs)
        
        return response


# Helper function for backward compatibility
async def generate_with_llm(
    prompt: str,
    provider: str = "groq",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick helper to generate text with any provider
    
    Example:
        # Groq (fast & free)
        response = await generate_with_llm(
            prompt="Tell me about AI",
            provider="groq",
            api_key="your-groq-key"
        )
        
        # Gemini
        response = await generate_with_llm(
            prompt="Tell me about AI",
            provider="gemini",
            api_key="your-gemini-key"
        )
    """
    service = LLMService(provider=provider, api_key=api_key)
    return await service.generate(prompt, model=model, **kwargs)
