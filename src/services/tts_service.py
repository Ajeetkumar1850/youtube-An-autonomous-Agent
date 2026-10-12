"""
Multi-Provider Text-to-Speech Service
Supports: Edge TTS (free), Azure, ElevenLabs, Google TTS
"""
import os
from abc import ABC, abstractmethod
from typing import Optional
import edge_tts
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()


class TTSProvider(ABC):
    """Base class for TTS providers"""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """Synthesize speech from text"""
        pass


class EdgeTTSProvider(TTSProvider):
    """Microsoft Edge TTS Provider (Free)"""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """Generate speech using Edge TTS"""
        logger.info(
            "edge_tts_generating",
            voice=voice,
            text_length=len(text),
            rate=rate
        )
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate
            )
            
            await communicate.save(output_path)
            
            # Verify output
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"TTS output not created: {output_path}")
            
            size = os.path.getsize(output_path)
            if size == 0:
                raise ValueError("TTS output file is empty")
            
            logger.info("edge_tts_completed", output_path=output_path, size_bytes=size)
            return output_path
            
        except Exception as e:
            logger.error("edge_tts_failed", error=str(e))
            raise


class AzureTTSProvider(TTSProvider):
    """Microsoft Azure Speech Service"""
    
    def __init__(self, speech_key: str, speech_region: str):
        self.speech_key = speech_key
        self.speech_region = speech_region
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.speechsdk = speechsdk
        except ImportError:
            raise ImportError(
                "Azure Speech SDK not installed. "
                "Install with: pip install azure-cognitiveservices-speech"
            )
    
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """Generate speech using Azure"""
        logger.info("azure_tts_generating", voice=voice, text_length=len(text))
        
        try:
            speech_config = self.speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            speech_config.speech_synthesis_voice_name = voice
            
            audio_config = self.speechsdk.audio.AudioOutputConfig(
                filename=output_path
            )
            
            synthesizer = self.speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("azure_tts_completed", output_path=output_path)
                return output_path
            else:
                raise Exception(f"Azure TTS failed: {result.reason}")
                
        except Exception as e:
            logger.error("azure_tts_failed", error=str(e))
            raise


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS Provider (Premium Quality)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        try:
            from elevenlabs import generate, save
            self.generate = generate
            self.save = save
        except ImportError:
            raise ImportError(
                "ElevenLabs SDK not installed. "
                "Install with: pip install elevenlabs"
            )
    
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """Generate speech using ElevenLabs"""
        logger.info("elevenlabs_tts_generating", voice=voice, text_length=len(text))
        
        try:
            audio = self.generate(
                text=text,
                voice=voice,
                api_key=self.api_key
            )
            
            self.save(audio, output_path)
            
            logger.info("elevenlabs_tts_completed", output_path=output_path)
            return output_path
            
        except Exception as e:
            logger.error("elevenlabs_tts_failed", error=str(e))
            raise


class GoogleTTSProvider(TTSProvider):
    """Google Cloud Text-to-Speech"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        
        try:
            from google.cloud import texttospeech
            self.texttospeech = texttospeech
        except ImportError:
            raise ImportError(
                "Google Cloud TTS not installed. "
                "Install with: pip install google-cloud-texttospeech"
            )
    
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """Generate speech using Google Cloud TTS"""
        logger.info("google_tts_generating", voice=voice, text_length=len(text))
        
        try:
            # Set credentials if provided
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            client = self.texttospeech.TextToSpeechClient()
            
            synthesis_input = self.texttospeech.SynthesisInput(text=text)
            
            # Parse voice (format: "language-code-VoiceName")
            language_code = "-".join(voice.split("-")[:2])
            
            voice_params = self.texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice
            )
            
            audio_config = self.texttospeech.AudioConfig(
                audio_encoding=self.texttospeech.AudioEncoding.LINEAR16
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            logger.info("google_tts_completed", output_path=output_path)
            return output_path
            
        except Exception as e:
            logger.error("google_tts_failed", error=str(e))
            raise


class TTSService:
    """
    Unified TTS service supporting multiple providers
    """
    
    def __init__(
        self,
        provider: str = "edge",
        azure_key: Optional[str] = None,
        azure_region: Optional[str] = None,
        elevenlabs_key: Optional[str] = None,
        google_credentials: Optional[str] = None
    ):
        self.provider_name = provider.lower()
        
        # Initialize providers
        self.providers = {
            "edge": EdgeTTSProvider(),
        }
        
        # Add Azure if credentials provided
        if azure_key and azure_region:
            self.providers["azure"] = AzureTTSProvider(azure_key, azure_region)
        
        # Add ElevenLabs if API key provided
        if elevenlabs_key:
            self.providers["elevenlabs"] = ElevenLabsTTSProvider(elevenlabs_key)
        
        # Add Google if credentials provided
        if google_credentials:
            self.providers["google"] = GoogleTTSProvider(google_credentials)
        
        # Check if requested provider is available
        if self.provider_name not in self.providers:
            logger.warning(
                f"Provider '{self.provider_name}' not available, falling back to Edge TTS"
            )
            self.provider_name = "edge"
    
    async def generate(
        self,
        text: str,
        voice: str,
        output_path: str,
        rate: str = "+0%",
        volume: float = 1.0
    ) -> str:
        """
        Generate speech using configured provider
        
        Args:
            text: Text to synthesize
            voice: Voice model name
            output_path: Output file path
            rate: Speech rate (e.g., "+10%", "-10%")
            volume: Volume multiplier (0.0 to 2.0)
        
        Returns:
            Path to generated audio file
        """
        provider = self.providers[self.provider_name]
        
        logger.info(
            "tts_service_generating",
            provider=self.provider_name,
            voice=voice,
            text_length=len(text)
        )
        
        result = await provider.synthesize(text, voice, output_path, rate, volume)
        
        return result
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return list(self.providers.keys())


# Helper function for backward compatibility
async def generate_voice_with_service(
    text: str,
    output_path: str,
    provider: str = "edge",
    voice: str = "hi-IN-SwaraNeural",
    rate: str = "+10%",
    volume: float = 1.0,
    **provider_credentials
) -> str:
    """
    Generate voice using TTS service
    
    Example:
        # Edge TTS (default)
        await generate_voice_with_service(text, "output.wav")
        
        # Azure
        await generate_voice_with_service(
            text, "output.wav",
            provider="azure",
            azure_key="your-key",
            azure_region="eastus"
        )
    """
    service = TTSService(provider=provider, **provider_credentials)
    return await service.generate(text, voice, output_path, rate, volume)
