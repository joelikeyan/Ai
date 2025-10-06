"""
Configuration settings for the multimodal AI system
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AudioConfig(BaseModel):
    """Audio processing configuration"""
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    tts_voice_id: Optional[str] = None
    tts_rate: int = 200
    tts_volume: float = 0.9
    stt_model_path: str = "models/vosk-model-small-en-us-0.15"

class ModelConfig(BaseModel):
    """AI model configuration"""
    llm_model: str = "llama3.1:8b"  # Ollama model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    image_model: str = "microsoft/git-base-coco"  # For image captioning
    device: str = "auto"  # auto, cpu, cuda, mps
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9

class UIConfig(BaseModel):
    """User interface configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    auto_speak: bool = True
    auto_play_audio: bool = True
    theme: str = "dark"

class SystemConfig(BaseModel):
    """System-wide configuration"""
    data_dir: Path = Path("data")
    models_dir: Path = Path("models")
    temp_dir: Path = Path("temp")
    log_level: str = "INFO"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_audio_formats: list = [".wav", ".mp3", ".m4a", ".flac"]
    supported_image_formats: list = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]

class Config:
    """Main configuration class"""
    def __init__(self):
        self.audio = AudioConfig()
        self.model = ModelConfig()
        self.ui = UIConfig()
        self.system = SystemConfig()
        
        # Create necessary directories
        self.system.data_dir.mkdir(exist_ok=True)
        self.system.models_dir.mkdir(exist_ok=True)
        self.system.temp_dir.mkdir(exist_ok=True)
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Audio settings
        if os.getenv("TTS_VOICE_ID"):
            self.audio.tts_voice_id = os.getenv("TTS_VOICE_ID")
        if os.getenv("TTS_RATE"):
            self.audio.tts_rate = int(os.getenv("TTS_RATE"))
        
        # Model settings
        if os.getenv("LLM_MODEL"):
            self.model.llm_model = os.getenv("LLM_MODEL")
        if os.getenv("DEVICE"):
            self.model.device = os.getenv("DEVICE")
        
        # UI settings
        if os.getenv("HOST"):
            self.ui.host = os.getenv("HOST")
        if os.getenv("PORT"):
            self.ui.port = int(os.getenv("PORT"))
        if os.getenv("DEBUG"):
            self.ui.debug = os.getenv("DEBUG").lower() == "true"

# Global config instance
config = Config()