import cv2
import numpy as np
import mediapipe as mp
import logging
from typing import Tuple, Dict, Any
from src.core.constants import *

class ImagePreprocessor:
    """Handle image preprocessing and quality checks."""
    
    def __init__(self):
        self.face_detector = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=MIN_FACE_CONFIDENCE
        )

    def check_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Check image quality metrics."""
        brightness = np.mean(image)
        contrast = np.std(image)
        
        results = self.face_detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        has_face = results.detections is not None and len(results.detections) > 0
        
        return {
            "brightness": brightness,
            "contrast": contrast,
            "has_face": has_face,
            "resolution": min(image.shape[:2])
        }

    def preprocess_image(self, image_path: str) -> Tuple[np.ndarray, bool, Dict[str, Any]]:
        """Preprocess image and check quality."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")
                
            quality_metrics = self.check_image_quality(image)
            
            quality_pass = (
                quality_metrics["has_face"] and
                quality_metrics["brightness"] > MIN_BRIGHTNESS and
                quality_metrics["contrast"] > MIN_CONTRAST and
                quality_metrics["resolution"] >= MIN_RESOLUTION
            )
            
            return image, quality_pass, quality_metrics
            
        except Exception as e:
            logging.error(f"Error in image preprocessing: {str(e)}")
            raise