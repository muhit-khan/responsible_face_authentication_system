import os
import json
import datetime
from cryptography.fernet import Fernet
import numpy as np
import cv2
from src.security.consent_manager import ConsentRecord
from src.core.constants import ENCRYPTION_KEY_LENGTH

class PrivacyManager:
    """Manage data privacy and encryption."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize encryption
        key_file = os.path.join(storage_path, '.key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        
        self.cipher_suite = Fernet(key)
        
    def encrypt_image(self, image_data: np.ndarray) -> bytes:
        """Encrypt image data."""
        _, buffer = cv2.imencode('.jpg', image_data)
        return self.cipher_suite.encrypt(buffer.tobytes())
        
    def decrypt_image(self, encrypted_data: bytes) -> np.ndarray:
        """Decrypt image data."""
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        nparr = np.frombuffer(decrypted_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
    def record_consent(self, consent: ConsentRecord):
        """Record user consent."""
        consent_file = os.path.join(
            self.storage_path, 
            f"consent_{consent.user_id}.json"
        )
        with open(consent_file, 'w') as f:
            json.dump(consent.__dict__, f)
            
    def schedule_deletion(self, user_id: str, file_path: str):
        """Schedule file for deletion."""
        schedule_file = os.path.join(self.storage_path, "deletion_schedule.json")
        deletion_date = datetime.datetime.now() + datetime.timedelta(days=30)
        
        schedule = []
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                schedule = json.load(f)
                
        schedule.append({
            "file_path": file_path,
            "deletion_date": deletion_date.isoformat(),
            "user_id": user_id
        })
        
        with open(schedule_file, 'w') as f:
            json.dump(schedule, f)