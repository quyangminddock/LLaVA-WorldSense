"""
Camera Engine - OpenCV Webcam Capture
Handles camera initialization and frame capture
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Generator
from threading import Thread, Event
import time


class CameraEngine:
    """Wrapper for OpenCV camera operations"""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Initialize camera engine
        
        Args:
            camera_id: Camera device ID (0 for default)
            width: Capture width
            height: Capture height
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_streaming = False
        self.stop_event = Event()
        self.current_frame = None
        
    def open(self) -> bool:
        """Open the camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ Cannot open camera {self.camera_id}")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            print(f"✅ Camera {self.camera_id} opened successfully!")
            print(f"   Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error opening camera: {e}")
            return False
    
    def close(self):
        """Close the camera"""
        self.stop_streaming()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("Camera closed")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame
        
        Returns:
            Frame as numpy array (BGR format) or None if failed
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        self.current_frame = frame
        return frame
    
    def capture_pil_image(self) -> Optional[Image.Image]:
        """
        Capture a frame and convert to PIL Image
        
        Returns:
            PIL Image (RGB format) or None if failed
        """
        frame = self.capture_frame()
        
        if frame is None:
            return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return Image.fromarray(rgb_frame)
    
    def get_frame_for_display(self) -> Optional[np.ndarray]:
        """
        Get current frame in RGB format for display
        
        Returns:
            Frame as numpy array (RGB format) or None
        """
        frame = self.capture_frame()
        
        if frame is None:
            return None
        
        # Convert BGR to RGB for display
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def stream_frames(self) -> Generator[np.ndarray, None, None]:
        """
        Generator that yields frames continuously
        
        Yields:
            Frames as numpy arrays (RGB format)
        """
        self.is_streaming = True
        self.stop_event.clear()
        
        while not self.stop_event.is_set():
            frame = self.get_frame_for_display()
            
            if frame is not None:
                yield frame
            
            # Small delay to prevent overwhelming
            time.sleep(0.033)  # ~30 FPS
        
        self.is_streaming = False
    
    def stop_streaming(self):
        """Stop the frame streaming"""
        self.stop_event.set()
        self.is_streaming = False
    
    def test_connection(self) -> bool:
        """
        Test if camera is accessible
        
        Returns:
            True if camera works, False otherwise
        """
        try:
            if self.cap is None:
                self.open()
            
            frame = self.capture_frame()
            return frame is not None
            
        except Exception:
            return False
    
    def get_camera_info(self) -> dict:
        """Get information about the camera"""
        info = {
            "camera_id": self.camera_id,
            "is_open": self.cap is not None and self.cap.isOpened(),
            "is_streaming": self.is_streaming
        }
        
        if self.cap is not None and self.cap.isOpened():
            info["width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info["height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            info["fps"] = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        return info
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# Demo/test function
if __name__ == "__main__":
    print("Testing camera...")
    
    camera = CameraEngine()
    
    if camera.test_connection():
        print("✅ Camera test passed!")
        print(f"Camera info: {camera.get_camera_info()}")
        
        # Capture a test image
        img = camera.capture_pil_image()
        if img:
            print(f"Captured image size: {img.size}")
    else:
        print("❌ Camera test failed!")
    
    camera.close()
