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
        self.consent_file = os.path.join(storage_path, 'consents.json')
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize consent file if not exists
        if not os.path.exists(self.consent_file):
            with open(self.consent_file, 'w') as f:
                json.dump({"consents": []}, f)
        
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
        """Record user consent in single JSON file."""
        try:
            with open(self.consent_file, 'r') as f:
                data = json.load(f)
            
            consent_dict = {
                "user_id": consent.user_id,
                "consent_date": consent.consent_date,
                "purpose": consent.purpose,
                "retention_period": consent.retention_period,
                "data_types": consent.data_types,
                "revoked": consent.revoked
            }
            
            # Update existing consent or add new one
            consents = data["consents"]
            updated = False
            for i, existing in enumerate(consents):
                if existing["user_id"] == consent.user_id:
                    consents[i] = consent_dict
                    updated = True
                    break
                    
            if not updated:
                consents.append(consent_dict)
                
            # Save updated consents
            with open(self.consent_file, 'w') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            raise RuntimeError(f"Failed to record consent: {str(e)}")

    def get_all_consents(self):
        """Retrieve all consent records."""
        try:
            with open(self.consent_file, 'r') as f:
                data = json.load(f)
            return data["consents"]
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve consents: {str(e)}")

    def get_user_consent(self, user_id: str):
        """Get consent record for specific user."""
        consents = self.get_all_consents()
        return next((c for c in consents if c["user_id"] == user_id), None)

    def revoke_consent(self, user_id: str):
        """Revoke user's consent."""
        try:
            with open(self.consent_file, 'r') as f:
                data = json.load(f)
            
            updated = False
            for consent in data["consents"]:
                if consent["user_id"] == user_id:
                    consent["revoked"] = True
                    updated = True
                    break
                    
            if updated:
                with open(self.consent_file, 'w') as f:
                    json.dump(data, f, indent=4)
            
            return updated
        except Exception as e:
            raise RuntimeError(f"Failed to revoke consent: {str(e)}")

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