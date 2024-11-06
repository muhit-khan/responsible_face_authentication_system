# Face authentication system configuration
SETTINGS = {
    "face_detection": {
        "model": "Facenet512",
        "detector": "OpenCV",
        "min_confidence": 0.7
    },
    "privacy": {
        "retention_days": 30,
        "storage_path": "./data/secure_storage",
        "encryption_enabled": True
    },
    "monitoring": {
        "drift_threshold": 0.1,
        "calibration_days": 7,
        "log_path": "./data/monitoring"
    },
    "quality": {
        "min_brightness": 40,
        "min_contrast": 20,
        "min_resolution": 224
    }
}