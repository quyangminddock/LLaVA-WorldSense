"""
Enhanced Web Server Module - Real-Time Jarvis System
FastAPI backend with streaming WebSocket support for continuous vision and voice
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
import json
import base64
import io
import numpy as np
from PIL import Image
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "monitoring": False,
            "last_frame_time": 0,
            "monitoring_task": None
        }
        logger.info(f"✅ Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            # Cancel monitoring task if active
            session = self.active_connections[client_id]
            if session.get("monitoring_task"):
                session["monitoring_task"].cancel()
            del self.active_connections[client_id]
            logger.info(f"❌ Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]["websocket"]
            await websocket.send_json(message)
    
    def get_session(self, client_id: str) -> Optional[dict]:
        """Get client session data"""
        return self.active_connections.get(client_id)


class WebServer:
    """Enhanced FastAPI web server for Real-Time Jarvis"""
    
    def __init__(self, llava_engine, whisper_engine, camera_engine):
        """
        Initialize the web server
        
        Args:
            llava_engine: LLaVA engine instance
            whisper_engine: Whisper engine instance
            camera_engine: Camera engine instance
        """
        self.llava_engine = llava_engine
        self.whisper_engine = whisper_engine
        self.camera_engine = camera_engine
        
        # Initialize TTS engine
        from .tts_engine import TTSEngine
        self.tts_engine = TTSEngine(backend='edge-tts')
        
        # Create FastAPI app
        self.app = FastAPI(title="LLaVA WorldSense - Jarvis", version="3.0.0")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount static files
        static_path = Path(__file__).parent.parent / "static"
        static_path.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        
        # Connection manager
        self.connection_manager = ConnectionManager()
        
        # Continuous vision settings
        self.vision_interval = 3.0  # seconds between frame analyses
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def serve_index():
            """Serve the main HTML page"""
            static_path = Path(__file__).parent.parent / "static"
            index_file = static_path / "index.html"
            
            if index_file.exists():
                return HTMLResponse(content=index_file.read_text())
            else:
                return HTMLResponse(
                    content="<h1>LLaVA WorldSense</h1><p>Static files not found. Please run setup.</p>"
                )
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "llava_loaded": self.llava_engine.model is not None,
                "whisper_loaded": self.whisper_engine.model is not None,
                "camera_available": self.camera_engine.test_connection(),
                "tts_backend": self.tts_engine.backend,
                "active_connections": len(self.connection_manager.active_connections)
            }
        
        @self.app.get("/api/tts/voices")
        async def get_tts_voices():
            """Get available TTS voices"""
            voices = await self.tts_engine.get_available_voices()
            return {"voices": voices}
        
        @self.app.post("/api/llava/query")
        async def llava_query(data: Dict[str, Any]):
            """
            Process LLaVA query (HTTP endpoint for compatibility)
            
            Expected data:
            {
                "image": "base64_encoded_image",
                "question": "What do you see?"
            }
            """
            try:
                # Decode base64 image
                image_data = base64.b64decode(data["image"].split(",")[1] if "," in data["image"] else data["image"])
                image = Image.open(io.BytesIO(image_data))
                
                # Get question
                question = data.get("question", "What do you see in this image?")
                
                # Generate response
                response = self.llava_engine.generate_response(image, question)
                
                return {
                    "success": True,
                    "response": response,
                    "question": question
                }
                
            except Exception as e:
                logger.error(f"Error in LLaVA query: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )
        
        @self.app.post("/api/whisper/transcribe")
        async def whisper_transcribe(audio: UploadFile = File(...)):
            """
            Transcribe audio file using Whisper
            
            Args:
                audio: Audio file (WAV, MP3, etc.)
            """
            try:
                # Read audio file
                audio_bytes = await audio.read()
                
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name
                
                # Transcribe
                result = self.whisper_engine.transcribe_file(temp_path)
                
                # Clean up
                Path(temp_path).unlink()
                
                return {
                    "success": True,
                    "text": result["text"],
                    "language": result.get("language", "unknown")
                }
                
            except Exception as e:
                logger.error(f"Error in Whisper transcription: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Enhanced WebSocket endpoint for real-time Jarvis interaction"""
            # Generate client ID
            client_id = f"client_{int(time.time() * 1000)}"
            await self.connection_manager.connect(websocket, client_id)
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_json()
                    
                    # Process message based on type
                    msg_type = data.get("type")
                    
                    if msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                    
                    elif msg_type == "start_monitoring":
                        # Start continuous vision monitoring
                        await self._start_monitoring(client_id, websocket)
                    
                    elif msg_type == "stop_monitoring":
                        # Stop continuous vision monitoring
                        await self._stop_monitoring(client_id)
                    
                    elif msg_type == "llava_query":
                        # Stream LLaVA response
                        logger.info(f"📨 Received llava_query from client {client_id}")
                        await self._handle_llava_stream(client_id, websocket, data)
                    
                    elif msg_type == "voice_query":
                        # Handle voice query (text already transcribed on frontend)
                        logger.info(f"🗣️ Received voice_query from client {client_id}: {data.get('text')[:50]}")
                        await self._handle_llava_stream(client_id, websocket, {
                            "image": data.get("image"),
                            "question": data.get("text")
                        })
                        logger.info(f"✅ Voice query processed for client {client_id}")
                    
                    elif msg_type == "camera_frame":
                        # Store the latest frame for continuous monitoring
                        session = self.connection_manager.get_session(client_id)
                        if session:
                            session["last_frame"] = data.get("image")
                            session["last_frame_time"] = time.time()
                    
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}"
                        })
                        
            except WebSocketDisconnect:
                self.connection_manager.disconnect(client_id)
                logger.info(f"WebSocket {client_id} disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.connection_manager.disconnect(client_id)
    
    async def _start_monitoring(self, client_id: str, websocket: WebSocket):
        """Start continuous vision monitoring for a client"""
        session = self.connection_manager.get_session(client_id)
        if not session:
            return
        
        if session["monitoring"]:
            await websocket.send_json({
                "type": "monitoring_status",
                "active": True,
                "message": "Monitoring already active"
            })
            return
        
        session["monitoring"] = True
        await websocket.send_json({
            "type": "monitoring_status",
            "active": True,
            "message": "Continuous vision monitoring started"
        })
        
        logger.info(f"🔍 Started monitoring for {client_id}")
        
        # Create background task for continuous analysis
        async def monitor_loop():
            while session["monitoring"]:
                try:
                    # Check if we have a recent frame
                    if "last_frame" in session:
                        image_data = base64.b64decode(
                            session["last_frame"].split(",")[1] if "," in session["last_frame"] else session["last_frame"]
                        )
                        image = Image.open(io.BytesIO(image_data))
                        
                        # Quick observation (simpler prompt for monitoring)
                        observation = self.llava_engine.generate_response(
                            image,
                            "Briefly describe what you see in 1-2 sentences.",
                            max_new_tokens=100,
                            temperature=0.1
                        )
                        
                        # Send vision update
                        await websocket.send_json({
                            "type": "vision_update",
                            "observation": observation,
                            "timestamp": time.time()
                        })
                    
                    # Wait before next analysis
                    await asyncio.sleep(self.vision_interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(self.vision_interval)
        
        # Start the monitoring task
        session["monitoring_task"] = asyncio.create_task(monitor_loop())
    
    async def _stop_monitoring(self, client_id: str):
        """Stop continuous vision monitoring for a client"""
        session = self.connection_manager.get_session(client_id)
        if not session:
            return
        
        session["monitoring"] = False
        if session.get("monitoring_task"):
            session["monitoring_task"].cancel()
        
        await self.connection_manager.send_message(client_id, {
            "type": "monitoring_status",
            "active": False,
            "message": "Continuous vision monitoring stopped"
        })
        
        logger.info(f"⏸️  Stopped monitoring for {client_id}")
    
    async def _handle_llava_stream(self, client_id: str, websocket: WebSocket, data: Dict[str, Any]):
        """Handle streaming LLaVA response with TTS"""
        try:
            # Decode image
            image_data = base64.b64decode(
                data["image"].split(",")[1] if "," in data["image"] else data["image"]
            )
            image = Image.open(io.BytesIO(image_data))
            
            # Get question
            raw_question = data.get("question", "What do you see?")
            
            # Enhance prompt for better conversational experience
            # This guides the model to be a helpful assistant rather than just an image captioner
            if "what" in raw_question.lower() or "describe" in raw_question.lower() or "see" in raw_question.lower():
                # For visual questions, check if user wants details
                if "detail" in raw_question.lower() or "more" in raw_question.lower():
                     question = raw_question
                else:
                     # Force concise answer for general questions
                     question = f"{raw_question} Answer concisely in 1-2 sentences. Focus on the main subject."
            else:
                # For conversational queries (Hello, who are you, etc.)
                question = f"You are Jarvis, a helpful AI assistant. The user is talking to you. Answer their question naturally and concisely in English only. User says: {raw_question}"
            
            # Send start message
            await websocket.send_json({
                "type": "llava_start",
                "question": question
            })
            
            # Stream response token by token
            full_response = ""
            for token in self.llava_engine.generate_response_stream(image, question):
                full_response += token
                await websocket.send_json({
                    "type": "response_chunk",
                    "text": token,
                    "done": False
                })
                # Small delay to make streaming visible
                await asyncio.sleep(0.05)
            
            # Generate TTS audio
            audio_url = await self.tts_engine.synthesize(full_response)
            
            # Send completion message with audio
            await websocket.send_json({
                "type": "response_complete",
                "full_text": full_response,
                "audio_url": audio_url,
                "done": True
            })
            
        except Exception as e:
            logger.error(f"Error in LLaVA stream: {e}")
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
    
    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Run the web server
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        logger.info(f"🚀 Starting Jarvis web server on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")


def create_web_server(llava_engine, whisper_engine, camera_engine):
    """
    Create and return a web server instance
    
    Args:
        llava_engine: LLaVA engine instance
        whisper_engine: Whisper engine instance
        camera_engine: Camera engine instance
        
    Returns:
        WebServer instance
    """
    return WebServer(llava_engine, whisper_engine, camera_engine)
