
import inspect
from transformers import AutoModelForCausalLM

model_path = "tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B"

print(f"Loading model from {model_path}...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        trust_remote_code=True,
        device_map="auto"
    )
    
    print("\n Inspecting model.chat method:")
    if hasattr(model, 'chat'):
        sig = inspect.signature(model.chat)
        print(f"Signature: {sig}")
        print(f"Docstring: {model.chat.__doc__}")
    else:
        print("Model does not have a chat method!")

except Exception as e:
    print(f"Error: {e}")
