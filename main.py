import os
import json 
import logging
from datetime import datetime
from src.core.face_comparator import compare_photos_with_explanations
from src.security.privacy_manager import PrivacyManager
from src.monitoring.model_monitor import ModelMonitor
from src.security.consent_manager import ConsentRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point for the face authentication system."""
    try:
        # Initialize components
        privacy_manager = PrivacyManager('./data/secure_storage')
        model_monitor = ModelMonitor('facial_comparison_v1')
        
        # Record consent
        consent = ConsentRecord(
            user_id="user123",
            consent_date=datetime.now().isoformat(), 
            purpose="identity_verification",
            retention_period=30,
            data_types=['facial_images', 'facial_features']
        )
        privacy_manager.record_consent(consent)
        
        # Example image paths
        reference_path = './data/photos/img-1.jpg'
        live_path = './data/photos/methu.jpg'
        
        # Validate paths
        if not all(os.path.exists(path) for path in [reference_path, live_path]):
            logging.error("Image files not found")
            return
            
        # Perform comparison
        result = compare_photos_with_explanations(
            reference_path,
            live_path,
            'user123',
            privacy_manager,
            model_monitor
        )
        
        # Print results
        print("\n\nResponsible Face Authentication System")
        print("---------------------------------------\n\n")
        print(json.dumps(result, indent=4))
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()