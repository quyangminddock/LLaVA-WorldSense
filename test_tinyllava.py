#!/usr/bin/env python3
"""
Test script for LLaVA Engine with TinyLLaVA support
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.llava_engine import LLaVAEngine

def main():
    parser = argparse.ArgumentParser(description="Test LLaVA Engine")
    parser.add_argument("--model", type=str, default="tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B", help="Model path")
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/mps/cpu/auto)")
    args = parser.parse_args()

    print("=" * 60)
    print(f"🧪 Testing LLaVA Engine with model: {args.model}")
    print("=" * 60)

    try:
        # Initialize engine
        engine = LLaVAEngine(
            model_path=args.model,
            device=args.device,
            use_4bit=True,
            fast_mode=True
        )

        # Load model
        print("\n📥 Loading model...")
        if engine.load_model():
            print("\n✅ Model loaded successfully!")
            
            # Print model info
            info = engine.get_model_info()
            print("\n📊 Model Info:")
            for k, v in info.items():
                print(f"  - {k}: {v}")
                
            print(f"  - Is TinyLLaVA: {engine.is_tiny_llava}")
            
        else:
            print("\n❌ Failed to load model")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
