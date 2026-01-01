#!/usr/bin/env python3
"""Test LLaVA model loading with detailed error reporting"""

import sys
import traceback

print("=" * 60)
print("Testing LLaVA Model Loading")
print("=" * 60)

# Step 1: Import LLaVA modules
print("\n[1/4] Importing LLaVA modules...")
try:
    from llava.model.builder import load_pretrained_model
    from llava.mm_utils import get_model_name_from_path
    print("✅ LLaVA modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LLaVA: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Get model name
print("\n[2/4] Getting model name...")
try:
    model_path = "liuhaotian/llava-v1.5-7b"
    model_name = get_model_name_from_path(model_path)
    print(f"✅ Model name: {model_name}")
except Exception as e:
    print(f"❌ Failed to get model name: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Determine device
print("\n[3/4] Determining device...")
import torch
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
print(f"✅ Using device: {device}")

# Step 4: Load model
print("\n[4/4] Loading model (this may take a while)...")
print(f"Model path: {model_path}")
print(f"Model name: {model_name}")
print(f"Device: {device}")

try:
    tokenizer, model, image_processor, context_len = load_pretrained_model(
        model_path=model_path,
        model_base=None,
        model_name=model_name,
        device=device
    )
    print("\n" + "=" * 60)
    print("✅ LLaVA model loaded successfully!")
    print("=" * 60)
    print(f"Context length: {context_len}")
    print(f"Model type: {type(model)}")
    print(f"Tokenizer type: {type(tokenizer)}")
    
except Exception as e:
    print("\n" + "=" * 60)
    print(f"❌ Failed to load model: {e}")
    print("=" * 60)
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
