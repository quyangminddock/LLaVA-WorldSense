"""
LLaVA Engine - Vision Language Model Wrapper
Handles model loading and image understanding
"""

import torch
from PIL import Image
from typing import Optional, Tuple, List
import requests
from io import BytesIO


class LLaVAEngine:
    """Wrapper for LLaVA model inference"""
    
    def __init__(
        self,
        model_path: str = "liuhaotian/llava-v1.5-7b",
        device: str = "auto",
        use_4bit: bool = True,
        fast_mode: bool = True
    ):
        """
        Initialize LLaVA engine
        
        Args:
            model_path: HuggingFace model path or local path
            device: Device to use ('auto', 'cuda', 'mps', 'cpu')
            use_4bit: Enable 4-bit quantization
            fast_mode: Enable fast inference mode
        """
        self.model_path = model_path
        self.device = self._get_device(device)
        self.use_4bit = use_4bit
        self.fast_mode = fast_mode
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.context_len = None
        self.conversation_history = []
        
        # Detect if this is a TinyLLaVA model
        self.is_tiny_llava = 'tinyllava' in model_path.lower() or 'tiny-llava' in model_path.lower()
        
        print(f"🚀 LLaVA Engine initialized:")
        print(f"   - Model type: {'TinyLLaVA' if self.is_tiny_llava else 'Standard LLaVA'}")
        print(f"   - 4-bit quantization: {'✅ Enabled' if use_4bit else '❌ Disabled'}")
        print(f"   - Fast mode: {'✅ Enabled' if fast_mode else '❌ Disabled'}")
        
    def _get_device(self, device: str) -> str:
        """Determine the best available device"""
        if device != "auto":
            return device
        
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def load_model(self) -> bool:
        """Load the LLaVA model with optional quantization"""
        try:
            print(f"Loading {'TinyLLaVA' if self.is_tiny_llava else 'LLaVA'} model: {self.model_path}")
            print(f"Using device: {self.device}")
            
            if self.is_tiny_llava:
                # TinyLLaVA loading path
                return self._load_tinyllava()
            else:
                # Standard LLaVA loading path
                return self._load_standard_llava()
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def _load_standard_llava(self) -> bool:
        """Load standard LLaVA model"""
        try:
            from llava.model.builder import load_pretrained_model
            from llava.mm_utils import get_model_name_from_path
            
            model_name = get_model_name_from_path(self.model_path)
            
            # Prepare loading kwargs
            load_kwargs = {
                "model_path": self.model_path,
                "model_base": None,
                "model_name": model_name,
                "device": self.device
            }
            
            # Add 4-bit quantization if enabled
            if self.use_4bit and self.device in ["cuda", "mps"]:
                try:
                    from transformers import BitsAndBytesConfig
                    print("⚡ Enabling 4-bit quantization for faster inference...")
                    load_kwargs["load_in_4bit"] = True
                    load_kwargs["bnb_4bit_compute_dtype"] = torch.float16
                except ImportError:
                    print("⚠️ bitsandbytes not available, loading without quantization")
            
            self.tokenizer, self.model, self.image_processor, self.context_len = load_pretrained_model(
                **load_kwargs
            )
            
            print("✅ Standard LLaVA model loaded successfully!")
            if self.use_4bit:
                print("   Memory reduced by ~75% with 4-bit quantization")
            return True
            
        except ImportError:
            print("❌ LLaVA package not found. Please install it:")
            print("   git clone https://github.com/haotian-liu/LLaVA.git")
            print("   cd LLaVA && pip install -e .")
            return False
    
    def _load_tinyllava(self) -> bool:
        """Load TinyLLaVA model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print("📦 Loading TinyLLaVA with trust_remote_code=True...")
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                # MPS usually has issues with fp16 for some models (NaN errors)
                # Using float32 for MPS to ensure stability
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Move to device
            if self.device == "cuda":
                self.model = self.model.cuda()
            elif self.device == "mps":
                self.model = self.model.to(self.device)
            
            # Load tokenizer
            config = self.model.config
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast=False,
                model_max_length=getattr(config, 'tokenizer_model_max_length', 2048),
                padding_side=getattr(config, 'tokenizer_padding_side', 'right')
            )
            
            # TinyLLaVA doesn't use separate image_processor in the same way
            self.image_processor = None
            self.context_len = getattr(config, 'tokenizer_model_max_length', 2048)
            
            print("✅ TinyLLaVA model loaded successfully!")
            print(f"   Model size: ~3.1B parameters")
            print(f"   Expected memory: ~12GB (FP32) or ~6GB (FP16)" if self.device == "cuda" else f"   Expected memory: ~12GB (FP32 on MPS)")
            return True
            
        except ImportError as e:
            print(f"❌ Required packages not found: {e}")
            print("   Please install: pip install transformers torch")
            return False
    
    def process_image(self, image: Image.Image) -> torch.Tensor:
        """Process an image for model input"""
        if self.is_tiny_llava:
            # TinyLLaVA handles images internally in model.chat or via different processor
            # We just return the image itself or None depending on usage
            return image
            
        if self.image_processor is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        image_tensor = self.image_processor.preprocess(image, return_tensors='pt')['pixel_values']
        
        if self.device == "cuda":
            image_tensor = image_tensor.half().cuda()
        elif self.device == "mps":
            image_tensor = image_tensor.to(self.device)
        
        return image_tensor

    
    def generate_response(
        self,
        image: Image.Image,
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None,
        top_p: float = 0.7
    ) -> str:
        """
        Generate a response for an image and prompt
        
        Args:
            image: PIL Image to analyze
            prompt: User's question about the image
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text response
        """
        if self.model is None:
            return "Error: Model not loaded. Please wait for model initialization."
        
        # Apply fast mode defaults if not specified
        if max_new_tokens is None:
            max_new_tokens = 64 if self.fast_mode else 512
        if temperature is None:
            temperature = 0 if self.fast_mode else 0.2
            
        if self.is_tiny_llava:
            return self._generate_tinyllava(image, prompt, max_new_tokens, temperature, top_p)
        else:
            return self._generate_standard_llava(image, prompt, max_new_tokens, temperature, top_p)

    def _generate_tinyllava(
        self,
        image: Image.Image,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float
    ) -> str:
        """Generate response using TinyLLaVA model"""
        import tempfile
        import os
        
        temp_image_path = None
        try:
            # TinyLLaVA expects a file path string for the image
            # Save PIL image to temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                image.save(f, format="JPEG")
                temp_image_path = f.name
            
            # TinyLLaVA's chat method signature:
            # (prompt: str, tokenizer=None, image: str = None, max_new_tokens: int = 512, num_beams=1, top_p=None, temperature=0)
            
            # Call model.chat
            response, _ = self.model.chat(
                prompt=prompt,
                image=temp_image_path,
                tokenizer=self.tokenizer,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )
            
            return response
            
        except Exception as e:
            return f"Error generating TinyLLaVA response: {str(e)}"
        finally:
            # Clean up temporary file
            if temp_image_path and os.path.exists(temp_image_path):
                try:
                    os.remove(temp_image_path)
                except Exception:
                    pass

    def _generate_standard_llava(
        self,
        image: Image.Image,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float
    ) -> str:
        """Generate response using standard LLaVA model"""
        try:
            from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
            from llava.conversation import conv_templates, SeparatorStyle
            from llava.mm_utils import tokenizer_image_token, KeywordsStoppingCriteria
            
            # Prepare conversation
            conv = conv_templates["llava_v1"].copy()
            
            # Add image token to prompt if not present
            if DEFAULT_IMAGE_TOKEN not in prompt:
                prompt = DEFAULT_IMAGE_TOKEN + "\n" + prompt
            
            conv.append_message(conv.roles[0], prompt)
            conv.append_message(conv.roles[1], None)
            full_prompt = conv.get_prompt()
            
            # Tokenize
            input_ids = tokenizer_image_token(
                full_prompt, 
                self.tokenizer, 
                IMAGE_TOKEN_INDEX, 
                return_tensors='pt'
            ).unsqueeze(0)
            
            if self.device == "cuda":
                input_ids = input_ids.cuda()
            elif self.device == "mps":
                input_ids = input_ids.to(self.device)
            
            # Process image
            image_tensor = self.process_image(image)
            
            # Stopping criteria
            stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
            keywords = [stop_str]
            stopping_criteria = KeywordsStoppingCriteria(keywords, self.tokenizer, input_ids)
            
            # Generate with optimized settings
            with torch.inference_mode():
                output_ids = self.model.generate(
                    input_ids,
                    images=image_tensor,
                    do_sample=temperature > 0,  # Greedy if temperature=0
                    temperature=max(temperature, 0.01) if temperature > 0 else 1.0,
                    top_p=top_p if temperature > 0 else 1.0,
                    max_new_tokens=max_new_tokens,
                    num_beams=1,  # Single beam for speed
                    use_cache=True,
                    stopping_criteria=[stopping_criteria]
                )
            
            # Decode response
            outputs = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
            outputs = outputs.strip()
            
            if outputs.endswith(stop_str):
                outputs = outputs[:-len(stop_str)].strip()
            
            # Store in history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": outputs
            })
            
            return outputs
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_response_stream(
        self,
        image: Image.Image,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.7
    ):
        """
        Generate a streaming response for an image and prompt (token by token)
        
        Args:
            image: PIL Image to analyze
            prompt: User's question about the image
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Yields:
            Generated tokens as they are produced
        """
        if self.model is None:
            yield "Error: Model not loaded. Please wait for model initialization."
            return
        
        if self.is_tiny_llava:
            # TinyLLaVA streaming simulation
            # Since model.chat doesn't support streaming easily, we generate first then yield chunks
            full_response = self.generate_response(image, prompt, max_new_tokens, temperature, top_p)
            
            # Simulate streaming by yielding words
            words = full_response.split(' ')
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                
        else:
            # Standard LLaVA streaming logic
            try:
                from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
                from llava.conversation import conv_templates, SeparatorStyle
                from llava.mm_utils import tokenizer_image_token, KeywordsStoppingCriteria
                
                # Prepare conversation
                conv = conv_templates["llava_v1"].copy()
                
                # Add image token to prompt if not present
                if DEFAULT_IMAGE_TOKEN not in prompt:
                    prompt = DEFAULT_IMAGE_TOKEN + "\n" + prompt
                
                conv.append_message(conv.roles[0], prompt)
                conv.append_message(conv.roles[1], None)
                full_prompt = conv.get_prompt()
                
                # Tokenize
                input_ids = tokenizer_image_token(
                    full_prompt, 
                    self.tokenizer, 
                    IMAGE_TOKEN_INDEX, 
                    return_tensors='pt'
                ).unsqueeze(0)
                
                if self.device == "cuda":
                    input_ids = input_ids.cuda()
                elif self.device == "mps":
                    input_ids = input_ids.to(self.device)
                
                # Process image
                image_tensor = self.process_image(image)
                
                # Stopping criteria
                stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
                keywords = [stop_str]
                stopping_criteria = KeywordsStoppingCriteria(keywords, self.tokenizer, input_ids)
                
                # Streaming generation using TextIteratorStreamer
                try:
                    from transformers import TextIteratorStreamer
                    from threading import Thread
                    
                    streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True)
                    
                    generation_kwargs = dict(
                        input_ids=input_ids,
                        images=image_tensor,
                        do_sample=temperature > 0,
                        temperature=temperature,
                        top_p=top_p,
                        max_new_tokens=max_new_tokens,
                        use_cache=True,
                        stopping_criteria=[stopping_criteria],
                        streamer=streamer
                    )
                    
                    # Start generation in separate thread
                    thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
                    thread.start()
                    
                    # Yield tokens as they're generated
                    full_response = ""
                    for new_text in streamer:
                        if new_text and new_text != stop_str:
                            full_response += new_text
                            yield new_text
                    
                    thread.join()
                    
                    # Clean up response
                    if full_response.endswith(stop_str):
                        full_response = full_response[:-len(stop_str)].strip()
                    
                    # Store in history
                    self.conversation_history.append({
                        "role": "user",
                        "content": prompt
                    })
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": full_response
                    })
                    
                except ImportError:
                    # Fallback to non-streaming if TextIteratorStreamer not available
                    print("⚠️  TextIteratorStreamer not available, using non-streaming mode")
                    response = self.generate_response(image, prompt, max_new_tokens, temperature, top_p)
                    # Yield in chunks to simulate streaming
                    words = response.split()
                    for word in words:
                        yield word + " "
                
            except Exception as e:
                yield f"Error generating response: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "context_length": self.context_len,
            "loaded": self.model is not None
        }


# Demo/test function
if __name__ == "__main__":
    engine = LLaVAEngine()
    print("LLaVA Engine initialized")
    print(f"Model info: {engine.get_model_info()}")
