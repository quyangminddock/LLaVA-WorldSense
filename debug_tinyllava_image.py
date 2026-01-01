
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import numpy as np

model_path = "tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B"

print(f"Loading model from {model_path}...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        trust_remote_code=True,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    
    # Create a dummy image
    image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
    
    print("\n Testing model.chat with PIL image...")
    try:
        response, _ = model.chat(
            prompt="What is this?",
            image=image,
            tokenizer=tokenizer,
            max_new_tokens=10,
            temperature=0.1
        )
        print(f"✅ Success! Response: {response}")
    except Exception as e:
        print(f"❌ Failed with PIL image: {e}")
        
except Exception as e:
    print(f"Error: {e}")
