"""
Audio processing for speech-to-text and text-to-speech functionality
"""
import os
import wave
import tempfile
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import pyaudio
import pyttsx3
import vosk
import json
from loguru import logger
import config

class TextToSpeech:
    """Text-to-speech engine with multiple voice options"""
    
    def __init__(self):
        self.engine = None
        self.voices = {}
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine and load available voices"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            for i, voice in enumerate(voices):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                self.voices[i] = voice_info
                logger.info(f"Voice {i}: {voice.name} ({voice_info['gender']})")
            
            # Set default voice
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Set default properties
            self.engine.setProperty('rate', config.audio.tts_rate)
            self.engine.setProperty('volume', config.audio.tts_volume)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            raise
    
    def set_voice(self, voice_id: str):
        """Set the voice for TTS"""
        try:
            self.engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
    
    def set_rate(self, rate: int):
        """Set the speech rate"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set the volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', volume)
    
    def speak(self, text: str, blocking: bool = True):
        """Convert text to speech"""
        if not text.strip():
            return
        
        try:
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Non-blocking speech
                def speak_async():
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                thread = threading.Thread(target=speak_async)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            logger.error(f"Error during TTS: {e}")
    
    def save_to_file(self, text: str, output_path: str):
        """Save speech to audio file"""
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            logger.info(f"Speech saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
    
    def get_available_voices(self) -> Dict[int, Dict[str, Any]]:
        """Get list of available voices"""
        return self.voices.copy()

class SpeechToText:
    """Speech-to-text engine using Vosk"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or config.audio.stt_model_path
        self.model = None
        self.recognizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the Vosk model"""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Vosk model not found at: {self.model_path}")
                raise FileNotFoundError(f"Vosk model not found at: {self.model_path}")
            
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, config.audio.sample_rate)
            logger.info("Vosk model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Vosk model: {e}")
            raise
    
    def transcribe_audio_file(self, audio_path: str) -> str:
        """Transcribe audio file to text"""
        try:
            # Ensure audio is in correct format
            processed_path = self._prepare_audio(audio_path)
            
            with open(processed_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                return result.get('text', '').strip()
            else:
                result = json.loads(self.recognizer.PartialResult())
                return result.get('partial', '').strip()
                
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            return ""
    
    def transcribe_microphone(self, duration: int = 5) -> str:
        """Transcribe from microphone for specified duration"""
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=config.audio.channels,
                rate=config.audio.sample_rate,
                input=True,
                frames_per_buffer=config.audio.chunk_size
            )
            
            logger.info(f"Recording for {duration} seconds...")
            frames = []
            
            for _ in range(0, int(config.audio.sample_rate / config.audio.chunk_size * duration)):
                data = stream.read(config.audio.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Process audio data
            audio_data = b''.join(frames)
            
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                return result.get('text', '').strip()
            else:
                result = json.loads(self.recognizer.PartialResult())
                return result.get('partial', '').strip()
                
        except Exception as e:
            logger.error(f"Error transcribing from microphone: {e}")
            return ""
    
    def _prepare_audio(self, audio_path: str) -> str:
        """Prepare audio file for Vosk (16kHz mono WAV)"""
        try:
            # Check if already in correct format
            with wave.open(audio_path, 'rb') as wf:
                if (wf.getnchannels() == 1 and 
                    wf.getsampwidth() == 2 and 
                    wf.getframerate() == 16000):
                    return audio_path
            
            # Convert to required format
            output_path = str(Path(audio_path).with_suffix('.16kmono.wav'))
            
            # Use ffmpeg for conversion
            cmd = [
                'ffmpeg', '-y', '-i', audio_path,
                '-ac', '1', '-ar', '16000', '-f', 'wav',
                output_path
            ]
            
            subprocess.run(cmd, check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error preparing audio: {e}")
            return audio_path

class AudioPlayer:
    """Audio playback functionality"""
    
    def __init__(self):
        self.is_playing = False
        self.current_thread = None
    
    def play_audio_file(self, audio_path: str, blocking: bool = True):
        """Play audio file"""
        try:
            if blocking:
                self._play_blocking(audio_path)
            else:
                self._play_non_blocking(audio_path)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def _play_blocking(self, audio_path: str):
        """Play audio file synchronously"""
        if os.name == 'nt':  # Windows
            import winsound
            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
        else:  # Linux/macOS
            for cmd in [['afplay', audio_path], ['aplay', audio_path], 
                       ['paplay', audio_path], ['ffplay', '-nodisp', '-autoexit', audio_path]]:
                try:
                    subprocess.run(cmd, check=True, 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
    
    def _play_non_blocking(self, audio_path: str):
        """Play audio file asynchronously"""
        def play_async():
            self.is_playing = True
            self._play_blocking(audio_path)
            self.is_playing = False
        
        self.current_thread = threading.Thread(target=play_async)
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def stop_playback(self):
        """Stop current audio playback"""
        if self.current_thread and self.current_thread.is_alive():
            # Note: This is a simple implementation
            # For more robust stopping, you'd need to use a different approach
            self.is_playing = False

class AudioProcessor:
    """Main audio processing coordinator"""
    
    def __init__(self):
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        self.player = AudioPlayer()
    
    def speak_text(self, text: str, voice_id: str = None, blocking: bool = True):
        """Convert text to speech and optionally play it"""
        if voice_id:
            self.tts.set_voice(voice_id)
        
        if config.ui.auto_speak:
            self.tts.speak(text, blocking=blocking)
    
    def transcribe_audio(self, audio_path: str = None, use_microphone: bool = False, 
                        duration: int = 5) -> str:
        """Transcribe audio to text"""
        if use_microphone:
            return self.stt.transcribe_microphone(duration)
        elif audio_path:
            return self.stt.transcribe_audio_file(audio_path)
        else:
            return ""
    
    def play_audio(self, audio_path: str, blocking: bool = True):
        """Play audio file"""
        if config.ui.auto_play_audio:
            self.player.play_audio_file(audio_path, blocking)
    
    def save_speech(self, text: str, output_path: str, voice_id: str = None):
        """Save text as speech to file"""
        if voice_id:
            self.tts.set_voice(voice_id)
        self.tts.save_to_file(text, output_path)
    
    def get_available_voices(self) -> Dict[int, Dict[str, Any]]:
        """Get available TTS voices"""
        return self.tts.get_available_voices()