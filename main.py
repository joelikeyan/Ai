#!/usr/bin/env python3
"""
Multimodal AI System - Main Entry Point
A fully local, censorship-free multimodal AI system with vocal responses and read aloud features.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from loguru import logger
import config
from web_interface import run_server

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import torch
        import transformers
        import pyttsx3
        import vosk
        import fastapi
        import uvicorn
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        logger.error("Missing dependencies:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        logger.info("Install dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def check_ollama():
    """Check if Ollama is running and has the required model"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            if config.model.llm_model not in model_names:
                logger.warning(f"Model {config.model.llm_model} not found.")
                logger.info(f"Available models: {model_names}")
                logger.info(f"To install the model, run: ollama pull {config.model.llm_model}")
                return False
            return True
    except Exception as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        logger.info("Please install and start Ollama from: https://ollama.ai/")
        return False

def download_vosk_model():
    """Download Vosk model if not present"""
    model_path = Path(config.audio.stt_model_path)
    if model_path.exists():
        logger.info("Vosk model already present")
        return True
    
    logger.info("Downloading Vosk model...")
    try:
        import urllib.request
        import zipfile
        
        model_path.parent.mkdir(parents=True, exist_ok=True)
        zip_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        zip_path = model_path.parent / "vosk-model-small-en-us-0.15.zip"
        
        urllib.request.urlretrieve(zip_url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_path.parent)
        
        zip_path.unlink()  # Remove zip file
        logger.info("Vosk model downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading Vosk model: {e}")
        return False

def setup_environment():
    """Set up the environment and download required models"""
    logger.info("Setting up Multimodal AI System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Download Vosk model
    if not download_vosk_model():
        logger.warning("Vosk model download failed. STT functionality may not work.")
    
    # Check Ollama
    if not check_ollama():
        logger.warning("Ollama not available. LLM functionality may not work.")
        logger.info("To fix this:")
        logger.info("1. Install Ollama from https://ollama.ai/")
        logger.info("2. Run: ollama pull llama3.1:8b")
        logger.info("3. Start Ollama service")
    
    logger.info("Environment setup complete!")

def run_cli_mode():
    """Run in CLI mode for testing"""
    from ai_models import MultimodalAI
    from audio_processor import AudioProcessor
    
    logger.info("Starting CLI mode...")
    
    ai = MultimodalAI()
    audio = AudioProcessor()
    
    print("\n" + "="*50)
    print("Multimodal AI System - CLI Mode")
    print("="*50)
    print("Commands:")
    print("  - Type a message and press Enter to chat")
    print("  - Type 'voice' to start voice input")
    print("  - Type 'image <path>' to process an image")
    print("  - Type 'quit' to exit")
    print("="*50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'voice':
                print("Recording... (5 seconds)")
                text = audio.transcribe_audio(use_microphone=True, duration=5)
                if text:
                    print(f"Transcribed: {text}")
                    response = ai.process_text(text)
                    print(f"AI: {response}")
                    audio.speak_text(response)
                else:
                    print("No speech detected")
            elif user_input.startswith('image '):
                image_path = user_input[6:].strip()
                if Path(image_path).exists():
                    response = ai.process_image(image_path, "both")
                    print(f"AI: {response}")
                    audio.speak_text(response)
                else:
                    print("Image file not found")
            elif user_input:
                response = ai.process_text(user_input)
                print(f"AI: {response}")
                audio.speak_text(response)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    print("\nGoodbye!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Multimodal AI System")
    parser.add_argument("--mode", choices=["web", "cli"], default="web",
                       help="Run mode: web interface or CLI")
    parser.add_argument("--setup", action="store_true",
                       help="Run setup and exit")
    parser.add_argument("--host", default=config.ui.host,
                       help="Host for web interface")
    parser.add_argument("--port", type=int, default=config.ui.port,
                       help="Port for web interface")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if args.debug else "INFO")
    
    # Update config with command line arguments
    config.ui.host = args.host
    config.ui.port = args.port
    config.ui.debug = args.debug
    
    if args.setup:
        setup_environment()
        return
    
    # Run setup
    setup_environment()
    
    if args.mode == "cli":
        run_cli_mode()
    else:
        logger.info(f"Starting web interface on {config.ui.host}:{config.ui.port}")
        logger.info("Open your browser and go to: http://localhost:8000")
        run_server()

if __name__ == "__main__":
    main()