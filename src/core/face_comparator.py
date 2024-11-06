import logging
import time
from deepface import DeepFace
from typing import Dict, Any
from src.core.image_processor import ImagePreprocessor
from src.security.privacy_manager import PrivacyManager
from src.monitoring.model_monitor import ModelMonitor
from src.core.constants import FACE_MODELS, DETECTION_BACKENDS

def compare_photos_with_explanations(
    reference_image_path: str, 
    live_image_path: str, 
    user_id: str,
    privacy_manager: PrivacyManager,
    model_monitor: ModelMonitor
) -> Dict[str, Any]:
    """Compare photos with detailed explanations."""
    try:
        start_time = time.time()
        preprocessor = ImagePreprocessor()
        modelName=FACE_MODELS[2]
        detectorBackend=DETECTION_BACKENDS[0]
        
        # Preprocess images
        ref_image, ref_quality, ref_metrics = preprocessor.preprocess_image(reference_image_path)
        live_image, live_quality, live_metrics = preprocessor.preprocess_image(live_image_path)

        if not (ref_quality and live_quality):
            return {"error": "Image quality requirements not met"}

        # Analyze faces
        ref_analysis = DeepFace.analyze(
            img_path=reference_image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            detector_backend=detectorBackend
        )
        
        live_analysis = DeepFace.analyze(
            img_path=live_image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            detector_backend=detectorBackend
        )

        # Verify faces
        result = DeepFace.verify(
            img1_path=reference_image_path,
            img2_path=live_image_path,
            model_name=modelName,
            detector_backend=detectorBackend,
        )

        # Calculate metrics
        similarity_score = 1 - result.get("distance", 0)
        age_diff = abs(ref_analysis[0].get("age", 0) - live_analysis[0].get("age", 0))
        confidence_percentage = round(similarity_score * 100, 2)
        threshold_percentage = round((1 - result.get("threshold", 0)) * 100, 2)

        # Generate detailed explanation
        detailed_explanation = (
            f"The images are {'matching' if result.get('verified', False) else 'not matching'} "
            f"because the facial features show {'strong' if result.get('verified', False) else 'weak'} "
            f"similarity with a confidence score of {confidence_percentage}%. This is evidenced by: "
            f"the estimated ages are {'very close' if age_diff <= 5 else 'different'} "
            f"(difference of {age_diff} years). "
            f"The similarity score ({confidence_percentage}%) "
            f"{'significantly exceeds' if result.get('verified', False) else 'does not exceed'} "
            f"the required threshold of {threshold_percentage}%."
        )

        # Prepare enhanced explanation
        explanation = {
            "verification_result": {
                "match": result.get("verified", False),
                "confidence": confidence_percentage,
                "threshold": threshold_percentage,
                "processing_time": time.time() - start_time,
                "detailed_explanation": detailed_explanation
            },
            "analysis": {
                "reference_image": {
                    "age": ref_analysis[0].get("age"),
                    "gender": ref_analysis[0].get("dominant_gender"),
                    "emotion": ref_analysis[0].get("dominant_emotion"),
                    "quality": ref_metrics
                },
                "live_image": {
                    "age": live_analysis[0].get("age"),
                    "gender": live_analysis[0].get("dominant_gender"),
                    "emotion": live_analysis[0].get("dominant_emotion"),
                    "quality": live_metrics
                }
            },
            "technical_details": {
                "model": modelName,
                "detector": detectorBackend,
                "distance_metric": result.get("distance_metric", "cosine"),
                "raw_distance": result.get("distance", 0),
            }
        }

        # Track performance
        model_monitor.track_performance(explanation)

        return explanation

    except Exception as e:
        logging.error(f"Error in photo comparison: {str(e)}")
        return {"error": str(e)}