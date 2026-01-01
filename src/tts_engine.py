"""
TTS Engine Module - Text-to-Speech for Jarvis Voice Output
Supports multiple TTS backends for flexible deployment
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional, List
import uuid

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine with multiple backend support"""
    
    def __init__(self, backend: str = 'edge-tts', audio_dir: str = 'static/audio'):
        """
        Initialize TTS engine
        
        Args:
            backend: TTS backend to use ('edge-tts', 'pyttsx3', 'gtts')
            audio_dir: Directory to store generated audio files
        """
        self.backend = backend
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Voice settings
        self.voice = 'en-US-GuyNeural'  # Default Jarvis-like voice
        self.rate = '+0%'
        self.pitch = '+0Hz'
        
        # Initialize backend
        self._init_backend()
    
    def _init_backend(self):
        """Initialize the selected TTS backend"""
        if self.backend == 'edge-tts':
            try:
                import edge_tts
                self.tts_module = edge_tts
                logger.info("✅ Edge-TTS initialized")
            except ImportError:
                logger.warning("⚠️  edge-tts not installed, falling back to gtts")
                self.backend = 'gtts'
                self._init_backend()
        
        elif self.backend == 'gtts':
            try:
                from gtts import gTTS
                self.tts_module = gTTS
                logger.info("✅ gTTS initialized")
            except ImportError:
                logger.error("❌ No TTS backend available. Install: pip install edge-tts")
                self.tts_module = None
        
        elif self.backend == 'pyttsx3':
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                logger.info("✅ pyttsx3 initialized")
            except Exception as e:
                logger.warning(f"⚠️  pyttsx3 initialization failed: {e}, falling back to gtts")
                self.backend = 'gtts'
                self._init_backend()
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> Optional[str]:
        """
        Generate speech audio from text
        
        Args:
            text: Text to synthesize
            voice: Voice ID (optional, uses default if not specified)
            
        Returns:
            Relative path to audio file, or None if failed
        """
        if not text or not text.strip():
            return None
        
        # Use custom voice or default
        selected_voice = voice or self.voice
        
        # Generate unique filename based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        filename = f"jarvis_{text_hash}_{uuid.uuid4().hex[:6]}.mp3"
        filepath = self.audio_dir / filename
        
        try:
            if self.backend == 'edge-tts':
                await self._synthesize_edge_tts(text, filepath, selected_voice)
            elif self.backend == 'gtts':
                await self._synthesize_gtts(text, filepath)
            elif self.backend == 'pyttsx3':
                await self._synthesize_pyttsx3(text, filepath)
            else:
                logger.error("No TTS backend available")
                return None
            
            # Return relative path for web access
            return f"/static/audio/{filename}"
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None
    
    async def _synthesize_edge_tts(self, text: str, filepath: Path, voice: str):
        """Synthesize using Edge-TTS (Microsoft Azure voices)"""
        communicate = self.tts_module.Communicate(text, voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(str(filepath))
        logger.info(f"🔊 Generated TTS: {filepath.name}")
    
    async def _synthesize_gtts(self, text: str, filepath: Path):
        """Synthesize using gTTS (Google Text-to-Speech)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._gtts_sync, text, filepath)
    
    def _gtts_sync(self, text: str, filepath: Path):
        """Synchronous gTTS generation"""
        tts = self.tts_module(text=text, lang='en', slow=False)
        tts.save(str(filepath))
        logger.info(f"🔊 Generated TTS: {filepath.name}")
    
    async def _synthesize_pyttsx3(self, text: str, filepath: Path):
        """Synthesize using pyttsx3 (offline)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._pyttsx3_sync, text, filepath)
    
    def _pyttsx3_sync(self, text: str, filepath: Path):
        """Synchronous pyttsx3 generation"""
        self.tts_engine.save_to_file(text, str(filepath))
        self.tts_engine.runAndWait()
        logger.info(f"🔊 Generated TTS: {filepath.name}")
    
    async def get_available_voices(self) -> List[dict]:
        """Get list of available voices"""
        if self.backend == 'edge-tts':
            try:
                voices = await self.tts_module.list_voices()
                return [
                    {
                        'name': v['ShortName'],
                        'language': v['Locale'],
                        'gender': v['Gender']
                    }
                    for v in voices
                    if 'en-' in v['Locale']  # Filter English voices
                ]
            except Exception as e:
                logger.error(f"Failed to list voices: {e}")
                return []
        
        elif self.backend == 'gtts':
            return [{'name': 'Google TTS', 'language': 'en', 'gender': 'neutral'}]
        
        elif self.backend == 'pyttsx3':
            voices = self.tts_engine.getProperty('voices')
            return [
                {
                    'name': v.name,
                    'language': v.languages[0] if v.languages else 'unknown',
                    'gender': 'unknown'
                }
                for v in voices
            ]
        
        return []
    
    def set_voice(self, voice: str):
        """Set the default voice"""
        self.voice = voice
        logger.info(f"Voice set to: {voice}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old audio files"""
        import time
        current_time = time.time()
        count = 0
        
        for file in self.audio_dir.glob("jarvis_*.mp3"):
            if current_time - file.stat().st_mtime > max_age_hours * 3600:
                file.unlink()
                count += 1
        
        if count > 0:
            logger.info(f"🧹 Cleaned up {count} old audio files")


# For testing
if __name__ == "__main__":
    async def test():
        tts = TTSEngine(backend='edge-tts')
        
        # Test synthesis
        audio_path = await tts.synthesize("Hello, I am Jarvis. How may I assist you today?")
        print(f"Generated: {audio_path}")
        
        # List voices
        voices = await tts.get_available_voices()
        print(f"Available voices: {len(voices)}")
        for v in voices[:5]:
            print(f"  - {v['name']} ({v['language']})")
    
    asyncio.run(test())
