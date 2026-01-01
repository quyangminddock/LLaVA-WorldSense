"""
UI Module - Gradio Web Interface
Main user interface for the multimodal assistant
"""

import gradio as gr
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Generator
import time


def create_ui(llava_engine, whisper_engine, camera_engine):
    """
    Create the Gradio web interface
    
    Args:
        llava_engine: LLaVA engine instance
        whisper_engine: Whisper engine instance
        camera_engine: Camera engine instance
    """
    
    # Store conversation history for display
    chat_history = []
    
    def process_input(
        image: Optional[Image.Image],
        audio: Optional[Tuple[int, np.ndarray]],
        text_input: str,
        history: list
    ) -> Tuple[list, str, Optional[Image.Image]]:
        """Process multimodal input and generate response"""
        
        if image is None:
            return history + [("ERROR", "Please provide an image first!")], "", None
        
        # Get the question from text or audio
        question = text_input.strip()
        
        if audio is not None and not question:
            # Transcribe audio
            sample_rate, audio_data = audio
            
            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Transcribe
            result = whisper_engine.transcribe_numpy(audio_data, sample_rate)
            question = result["text"]
            
            if not question:
                return history + [("ERROR", "Could not transcribe audio. Please try again.")], "", image
        
        if not question:
            return history + [("ERROR", "Please enter a question or record audio.")], "", image
        
        # Generate response from LLaVA
        response = llava_engine.generate_response(image, question)
        
        # Update history
        history.append((f"🎤 {question}" if audio else f"💬 {question}", response))
        
        return history, "", image
    
    def capture_camera():
        """Capture frame from camera"""
        frame = camera_engine.get_frame_for_display()
        if frame is not None:
            return Image.fromarray(frame)
        return None
    
    def clear_chat():
        """Clear chat history"""
        llava_engine.clear_history()
        return [], None, ""
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 1.5em;
    }
    """
    
    # Build the interface
    with gr.Blocks(css=custom_css, title="LLaVA WorldSense") as demo:
        gr.HTML('<div class="title">🌋 LLaVA WorldSense</div>')
        gr.HTML('<div class="subtitle">Multimodal AI Assistant - See and Hear the World</div>')
        
        with gr.Row():
            # Left column - Input
            with gr.Column(scale=1):
                gr.Markdown("### 📷 Visual Input")
                
                image_input = gr.Image(
                    label="Image",
                    type="pil",
                    sources=["upload", "webcam"],
                    height=300
                )
                
                capture_btn = gr.Button("📸 Capture from Camera", variant="secondary")
                
                gr.Markdown("### 🎤 Voice Input")
                
                audio_input = gr.Audio(
                    label="Record Audio",
                    sources=["microphone"],
                    type="numpy"
                )
                
                gr.Markdown("### ⌨️ Text Input")
                
                text_input = gr.Textbox(
                    label="Type your question",
                    placeholder="What do you see in this image?",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("🚀 Ask LLaVA", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")
            
            # Right column - Output
            with gr.Column(scale=1):
                gr.Markdown("### 💬 Conversation")
                
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=500,
                    bubble_full_width=False
                )
        
        # Model info footer
        with gr.Accordion("ℹ️ Model Information", open=False):
            gr.Markdown(f"""
            - **Vision Model**: LLaVA-1.5-7B
            - **Audio Model**: Whisper ({whisper_engine.model_size})
            - **Device**: {llava_engine.device}
            
            **Tips**:
            - Use the webcam to capture live images
            - Record your question using the microphone
            - Or simply type your question
            - The model understands both English and Chinese
            """)
        
        # Event handlers
        capture_btn.click(
            fn=capture_camera,
            outputs=image_input
        )
        
        submit_btn.click(
            fn=process_input,
            inputs=[image_input, audio_input, text_input, chatbot],
            outputs=[chatbot, text_input, image_input]
        )
        
        text_input.submit(
            fn=process_input,
            inputs=[image_input, audio_input, text_input, chatbot],
            outputs=[chatbot, text_input, image_input]
        )
        
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, image_input, text_input]
        )
    
    return demo


def launch_demo(llava_engine, whisper_engine, camera_engine, share: bool = False):
    """
    Create and launch the Gradio demo
    
    Args:
        llava_engine: Initialized LLaVA engine
        whisper_engine: Initialized Whisper engine  
        camera_engine: Initialized camera engine
        share: Whether to create a public link
    """
    demo = create_ui(llava_engine, whisper_engine, camera_engine)
    demo.launch(share=share, server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    print("UI module loaded. Use launch_demo() to start the interface.")
