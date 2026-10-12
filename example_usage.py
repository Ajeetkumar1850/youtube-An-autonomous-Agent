"""
Example Usage of Enhanced Services

This file demonstrates how to use all the new features:
- Multi-provider TTS
- Subtitle generation
- Background music mixing
- Video effects and transitions
"""
import asyncio
import os
from src.services import (
    TTSService,
    SubtitleService,
    BGMService,
    VideoEffectsService
)
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip


async def example_1_multi_provider_tts():
    """Example 1: Generate voice with different TTS providers"""
    print("\n" + "="*50)
    print("Example 1: Multi-Provider TTS")
    print("="*50)
    
    text = "यह एक उदाहरण है। हम विभिन्न टीटीएस प्रदाताओं का परीक्षण कर रहे हैं।"
    
    # Edge TTS (free, always works)
    print("\n1. Generating with Edge TTS (free)...")
    tts_edge = TTSService(provider="edge")
    audio_edge = await tts_edge.generate(
        text=text,
        voice="hi-IN-SwaraNeural",
        output_path="example_output/edge_voice.wav"
    )
    print(f"   ✓ Generated: {audio_edge}")
    
    # You can try other providers if you have credentials:
    # tts_azure = TTSService(provider="azure", azure_key="...", azure_region="...")
    # audio_azure = await tts_azure.generate(...)
    
    return audio_edge


async def example_2_generate_subtitles():
    """Example 2: Generate subtitles using Whisper"""
    print("\n" + "="*50)
    print("Example 2: Subtitle Generation")
    print("="*50)
    
    audio_path = "example_output/edge_voice.wav"
    
    if not os.path.exists(audio_path):
        print("   ⚠ Audio file not found. Run example 1 first.")
        return None
    
    try:
        print("\n1. Generating subtitles with Whisper...")
        subtitle_service = SubtitleService(
            provider="whisper",
            whisper_model_size="base",  # Options: tiny, base, small, medium, large
            whisper_device="cpu"
        )
        
        # Generate subtitle segments
        segments = await subtitle_service.generate(
            audio_path=audio_path,
            mode="sentence"  # or "word" for word-level
        )
        
        print(f"   ✓ Generated {len(segments)} subtitle segments")
        
        # Save as SRT file
        srt_path = "example_output/subtitles.srt"
        await subtitle_service.save_srt(audio_path, srt_path, mode="sentence")
        print(f"   ✓ Saved SRT: {srt_path}")
        
        # Preview first few segments
        print("\n   Preview:")
        for seg in segments[:3]:
            print(f"   [{seg.start:.2f}s - {seg.end:.2f}s] {seg.text}")
        
        return srt_path
        
    except ImportError:
        print("   ⚠ faster-whisper not installed")
        print("   Install with: pip install faster-whisper")
        return None


async def example_3_background_music():
    """Example 3: Mix voice with background music"""
    print("\n" + "="*50)
    print("Example 3: Background Music Mixing")
    print("="*50)
    
    voice_path = "example_output/edge_voice.wav"
    
    if not os.path.exists(voice_path):
        print("   ⚠ Voice file not found. Run example 1 first.")
        return None
    
    bgm_service = BGMService(music_dir="resource/songs")
    
    # Check available music
    music_files = bgm_service.get_available_music()
    print(f"\n1. Available music files: {len(music_files)}")
    
    if not music_files:
        print("   ⚠ No music files found in resource/songs/")
        print("   Add MP3/WAV files to resource/songs/ to use this feature")
        return None
    
    print(f"   Files: {[os.path.basename(f) for f in music_files]}")
    
    # Get BGM (random selection)
    print("\n2. Selecting random BGM...")
    bgm_path = bgm_service.get_bgm(bgm_type="random")
    print(f"   Selected: {os.path.basename(bgm_path)}")
    
    # Mix audio
    print("\n3. Mixing voice + BGM...")
    mixed_path = "example_output/mixed_audio.wav"
    result = bgm_service.mix_audio(
        voice_audio_path=voice_path,
        bgm_audio_path=bgm_path,
        output_path=mixed_path,
        voice_volume=1.0,
        bgm_volume=0.2,  # BGM at 20% volume
        apply_ducking=True  # Reduce BGM when voice plays
    )
    print(f"   ✓ Mixed audio: {result}")
    
    return result


def example_4_video_effects():
    """Example 4: Apply video effects and transitions"""
    print("\n" + "="*50)
    print("Example 4: Video Effects & Transitions")
    print("="*50)
    
    # Check if we have scene images
    scene_path = "scenes/scene1.png"
    if not os.path.exists(scene_path):
        print("   ⚠ Scene image not found. Generate images first.")
        return None
    
    effects_service = VideoEffectsService()
    
    print("\n1. Creating video clip from image...")
    clip = ImageClip(scene_path).set_duration(5)
    print(f"   ✓ Clip created: {clip.duration}s, {clip.size}")
    
    # Apply animation preset
    print("\n2. Applying 'talking_head' animation...")
    clip = effects_service.apply_animation_preset(
        clip,
        preset="talking_head",
        intensity=0.03
    )
    print("   ✓ Animation applied")
    
    # Apply transition
    print("\n3. Applying fade transition...")
    clip = effects_service.apply_transition(
        clip,
        transition_type="fade",
        duration=0.5
    )
    print("   ✓ Transition applied")
    
    # Apply visual effect
    print("\n4. Applying vignette effect...")
    clip = effects_service.apply_effect(
        clip,
        effect_type="vignette",
        intensity=0.3
    )
    print("   ✓ Effect applied")
    
    # Save video
    output_path = "example_output/test_effects.mp4"
    print(f"\n5. Saving video to {output_path}...")
    clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False
    )
    print(f"   ✓ Video saved: {output_path}")
    
    return output_path


def example_5_complete_workflow():
    """Example 5: Complete workflow with all features"""
    print("\n" + "="*50)
    print("Example 5: Complete Workflow")
    print("="*50)
    
    async def run_workflow():
        # 1. Generate voice
        print("\n1. Generating voice...")
        tts = TTSService(provider="edge")
        voice_path = await tts.generate(
            text="यह एक पूर्ण उदाहरण है जिसमें सभी सुविधाएं शामिल हैं।",
            voice="hi-IN-SwaraNeural",
            output_path="example_output/complete_voice.wav"
        )
        print(f"   ✓ Voice: {voice_path}")
        
        # 2. Mix with BGM (if available)
        bgm_service = BGMService()
        music_files = bgm_service.get_available_music()
        
        if music_files:
            print("\n2. Mixing with background music...")
            bgm_path = bgm_service.get_bgm("random")
            audio_path = bgm_service.mix_audio(
                voice_path,
                bgm_path,
                "example_output/complete_audio.wav",
                bgm_volume=0.2
            )
            print(f"   ✓ Mixed audio: {audio_path}")
        else:
            print("\n2. Skipping BGM (no music files)")
            audio_path = voice_path
        
        # 3. Generate subtitles
        try:
            print("\n3. Generating subtitles...")
            subtitle = SubtitleService(provider="whisper")
            srt_path = await subtitle.save_srt(
                audio_path,
                "example_output/complete_subs.srt"
            )
            print(f"   ✓ Subtitles: {srt_path}")
        except ImportError:
            print("\n3. Skipping subtitles (Whisper not installed)")
            srt_path = None
        
        # 4. Create video with effects
        if os.path.exists("scenes/scene1.png"):
            print("\n4. Creating video with effects...")
            effects = VideoEffectsService()
            
            # Load image
            clip = ImageClip("scenes/scene1.png")
            
            # Get audio duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            
            clip = clip.set_duration(duration)
            
            # Apply effects
            clip = effects.apply_animation_preset(clip, "emotion_pulse")
            clip = effects.apply_transition(clip, "fade", 0.5)
            clip = effects.apply_effect(clip, "vignette", intensity=0.3)
            
            # Add audio
            audio = AudioFileClip(audio_path)
            clip = clip.set_audio(audio)
            
            # Save final video
            output = "example_output/complete_video.mp4"
            clip.write_videofile(
                output,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast"
            )
            print(f"   ✓ Final video: {output}")
            
            # Clean up
            clip.close()
            audio.close()
            
            return output
        else:
            print("\n4. Skipping video (no scene images)")
            return None
    
    return asyncio.run(run_workflow())


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print(" Enhanced Services - Example Usage")
    print("="*60)
    
    # Create output directory
    os.makedirs("example_output", exist_ok=True)
    
    try:
        # Example 1: TTS
        await example_1_multi_provider_tts()
        
        # Example 2: Subtitles
        await example_2_generate_subtitles()
        
        # Example 3: BGM
        await example_3_background_music()
        
        # Example 4: Video Effects
        example_4_video_effects()
        
        # Example 5: Complete Workflow
        example_5_complete_workflow()
        
        print("\n" + "="*60)
        print(" ✅ All examples completed!")
        print(" Check 'example_output/' directory for results")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
    
    # Or run individual examples:
    # asyncio.run(example_1_multi_provider_tts())
    # asyncio.run(example_2_generate_subtitles())
    # asyncio.run(example_3_background_music())
    # example_4_video_effects()
