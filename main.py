#!/usr/bin/env python3
"""
LLaVA WorldSense - Multimodal AI Assistant
Main entry point for the application

Combines:
- LLaVA (Large Language and Vision Assistant) for image understanding
- OpenAI Whisper for speech-to-text
- OpenCV for camera capture
- Gradio for web interface
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.llava_engine import LLaVAEngine
from src.audio_engine import WhisperEngine
from src.camera_engine import CameraEngine
from src.ui import launch_demo


def parse_args():
    parser = argparse.ArgumentParser(
        description="LLaVA WorldSense - Multimodal AI Assistant"
    )
    
    parser.add_argument(
        "--llava-model",
        type=str,
        default="liuhaotian/llava-v1.5-7b",
        help="LLaVA model path (default: liuhaotian/llava-v1.5-7b)"
    )
    
    parser.add_argument(
        "--whisper-model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "mps", "cpu"],
        help="Device to use for LLaVA (default: auto)"
    )
    
    parser.add_argument(
        "--camera-id",
        type=int,
        default=0,
        help="Camera device ID (default: 0)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link"
    )
    
    parser.add_argument(
        "--skip-llava",
        action="store_true",
        help="Skip loading LLaVA model (for testing UI only)"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Use modern web interface instead of Gradio"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for web server (default: 8080)"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("🌋 LLaVA WorldSense - Multimodal AI Assistant")
    print("=" * 60)
    print()
    
    # Initialize engines
    print("📦 Initializing components...")
    print()
    
    # Camera engine
    print("📷 Setting up camera...")
    camera_engine = CameraEngine(camera_id=args.camera_id)
    if camera_engine.test_connection():
        print(f"   Camera info: {camera_engine.get_camera_info()}")
    else:
        print("   ⚠️  Camera not available, but you can still upload images")
    print()
    
    # Whisper engine
    print("🎤 Loading Whisper model...")
    whisper_engine = WhisperEngine(model_size=args.whisper_model)
    whisper_engine.load_model()
    print()
    
    # LLaVA engine
    print("🔮 Loading LLaVA model...")
    llava_engine = LLaVAEngine(
        model_path=args.llava_model,
        device=args.device
    )
    
    if not args.skip_llava:
        if not llava_engine.load_model():
            print()
            print("❌ Failed to load LLaVA model.")
            print("   Please ensure you have installed the LLaVA package:")
            print()
            print("   git clone https://github.com/haotian-liu/LLaVA.git")
            print("   cd LLaVA && pip install -e .")
            print()
            sys.exit(1)
    else:
        print("   ⚠️  Skipping LLaVA model (--skip-llava flag)")
    
    print()
    print("=" * 60)
    print("🚀 Starting web interface...")
    print("=" * 60)
    print()
    
    # Launch the appropriate interface
    if args.web:
        # Modern web interface
        from src.web_server import create_web_server
        
        web_server = create_web_server(
            llava_engine=llava_engine,
            whisper_engine=whisper_engine,
            camera_engine=camera_engine
        )
        
        print(f"🌐 Modern Web UI: http://localhost:{args.port}")
        print()
        web_server.run(port=args.port)
    else:
        # Traditional Gradio interface
        launch_demo(
            llava_engine=llava_engine,
            whisper_engine=whisper_engine,
            camera_engine=camera_engine,
            share=args.share
        )


if __name__ == "__main__":
    main()
