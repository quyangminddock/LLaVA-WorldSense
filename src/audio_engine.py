"""
Audio Engine - Whisper Speech-to-Text
Handles audio recording and transcription
"""

import whisper
import numpy as np
import tempfile
import wave
import os
from typing import Optional, Tuple
from threading import Thread, Event
import queue


class WhisperEngine:
    """Wrapper for OpenAI Whisper audio transcription"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper engine
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stop_event = Event()
        
    def load_model(self) -> bool:
        """Load the Whisper model"""
        try:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            return False
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'zh') or None for auto-detect
            
        Returns:
            Dictionary with 'text' and 'language' keys
        """
        if self.model is None:
            return {"text": "Error: Model not loaded", "language": None}
        
        try:
            options = {}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_path, **options)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown")
            }
        except Exception as e:
            return {"text": f"Error: {str(e)}", "language": None}
    
    def transcribe_numpy(
        self,
        audio_array: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio from numpy array
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of the audio
            language: Language code or None for auto-detect
            
        Returns:
            Dictionary with 'text' and 'language' keys
        """
        if self.model is None:
            return {"text": "Error: Model not loaded", "language": None}
        
        try:
            # Ensure audio is float32 and normalized
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)
            
            # Normalize if needed
            if audio_array.max() > 1.0:
                audio_array = audio_array / 32768.0
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                import librosa
                audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
            
            options = {}
            if language:
                options["language"] = language
            
            result = self.model.transcribe(audio_array, **options)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown")
            }
        except Exception as e:
            return {"text": f"Error: {str(e)}", "language": None}
    
    def save_audio_to_temp(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> str:
        """
        Save audio data to a temporary WAV file
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        # Convert to int16 if float
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            audio_data = (audio_data * 32767).astype(np.int16)
        
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        return temp_file.name
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "loaded": self.model is not None
        }


def record_audio_gradio(audio_tuple: Tuple[int, np.ndarray]) -> Tuple[int, np.ndarray]:
    """
    Process audio from Gradio audio component
    
    Args:
        audio_tuple: Tuple of (sample_rate, audio_array) from Gradio
        
    Returns:
        Same tuple for further processing
    """
    if audio_tuple is None:
        return None
    
    sample_rate, audio_array = audio_tuple
    
    # Convert stereo to mono if needed
    if len(audio_array.shape) > 1:
        audio_array = audio_array.mean(axis=1)
    
    return (sample_rate, audio_array)


# Demo/test function
if __name__ == "__main__":
    engine = WhisperEngine(model_size="base")
    print("Whisper Engine initialized")
    print(f"Model info: {engine.get_model_info()}")
    
    # Test loading
    if engine.load_model():
        print("Model loaded successfully!")
