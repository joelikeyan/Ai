"""
Web interface for the multimodal AI system using FastAPI
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger
import config
from ai_models import MultimodalAI
from audio_processor import AudioProcessor

# Initialize FastAPI app
app = FastAPI(title="Multimodal AI System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
ai_system = MultimodalAI()
audio_processor = AudioProcessor()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            await self.send_personal_message(message, connection)

manager = ConnectionManager()

# Static files and templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main interface"""
    return templates.TemplateResponse("index.html", {
        "request": {},
        "config": {
            "auto_speak": config.ui.auto_speak,
            "auto_play_audio": config.ui.auto_play_audio,
            "theme": config.ui.theme
        }
    })

@app.get("/api/voices")
async def get_voices():
    """Get available TTS voices"""
    try:
        voices = audio_processor.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving voices")

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    voice_id: Optional[str] = Form(None),
    speak_response: bool = Form(True)
):
    """Process chat message with optional image"""
    try:
        # Save uploaded image if provided
        image_path = None
        if image:
            image_path = config.system.temp_dir / f"upload_{int(time.time())}_{image.filename}"
            with open(image_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
        
        # Process with AI system
        if image_path:
            response = ai_system.process_multimodal(message, image_path)
        else:
            response = ai_system.process_text(message)
        
        # Generate speech if requested
        audio_path = None
        if speak_response and config.ui.auto_speak:
            audio_path = config.system.temp_dir / f"response_{int(time.time())}.wav"
            audio_processor.save_speech(response, str(audio_path), voice_id)
        
        # Clean up temporary image
        if image_path and image_path.exists():
            image_path.unlink()
        
        return {
            "response": response,
            "audio_path": str(audio_path) if audio_path else None,
            "conversation_id": len(ai_system.get_conversation_history())
        }
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail="Error processing request")

@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    use_microphone: bool = Form(False),
    duration: int = Form(5)
):
    """Transcribe audio to text"""
    try:
        if use_microphone:
            text = audio_processor.transcribe_audio(use_microphone=True, duration=duration)
        else:
            # Save uploaded audio file
            audio_path = config.system.temp_dir / f"audio_{int(time.time())}_{audio.filename}"
            with open(audio_path, "wb") as buffer:
                content = await audio.read()
                buffer.write(content)
            
            text = audio_processor.transcribe_audio(str(audio_path))
            
            # Clean up
            if audio_path.exists():
                audio_path.unlink()
        
        return {"text": text}
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail="Error transcribing audio")

@app.post("/api/speak")
async def speak_text(
    text: str = Form(...),
    voice_id: Optional[str] = Form(None),
    save_to_file: bool = Form(False)
):
    """Convert text to speech"""
    try:
        audio_path = None
        if save_to_file:
            audio_path = config.system.temp_dir / f"speech_{int(time.time())}.wav"
            audio_processor.save_speech(text, str(audio_path), voice_id)
        else:
            audio_processor.speak_text(text, voice_id)
        
        return {
            "success": True,
            "audio_path": str(audio_path) if audio_path else None
        }
        
    except Exception as e:
        logger.error(f"Error speaking text: {e}")
        raise HTTPException(status_code=500, detail="Error speaking text")

@app.get("/api/conversation")
async def get_conversation():
    """Get conversation history"""
    try:
        history = ai_system.get_conversation_history()
        return {"conversation": history}
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation")

@app.delete("/api/conversation")
async def clear_conversation():
    """Clear conversation history"""
    try:
        ai_system.clear_history()
        return {"success": True}
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail="Error clearing conversation")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat":
                # Process chat message
                text = message_data.get("message", "")
                response = ai_system.process_text(text)
                
                # Send response back
                await manager.send_personal_message(
                    json.dumps({
                        "type": "response",
                        "message": response,
                        "timestamp": time.time()
                    }),
                    websocket
                )
                
                # Speak response if enabled
                if config.ui.auto_speak:
                    audio_processor.speak_text(response)
            
            elif message_type == "voice_input":
                # Process voice input
                duration = message_data.get("duration", 5)
                text = audio_processor.transcribe_audio(use_microphone=True, duration=duration)
                
                if text:
                    response = ai_system.process_text(text)
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "voice_response",
                            "transcribed": text,
                            "response": response,
                            "timestamp": time.time()
                        }),
                        websocket
                    )
                    
                    if config.ui.auto_speak:
                        audio_processor.speak_text(response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Get system status"""
    try:
        return {
            "status": "running",
            "ai_models_loaded": True,
            "audio_processor_ready": True,
            "active_connections": len(manager.active_connections),
            "config": {
                "auto_speak": config.ui.auto_speak,
                "auto_play_audio": config.ui.auto_play_audio,
                "theme": config.ui.theme
            }
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"status": "error", "message": str(e)}

def run_server():
    """Run the web server"""
    logger.info(f"Starting server on {config.ui.host}:{config.ui.port}")
    uvicorn.run(
        "web_interface:app",
        host=config.ui.host,
        port=config.ui.port,
        reload=config.ui.debug,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()