# Supported models and backends
FACE_MODELS = [
    "VGG-Face", 
    "Facenet", 
    "Facenet512", 
    "OpenFace", 
    "DeepFace", 
    "DeepID", 
    "ArcFace", 
    "Dlib", 
    "SFace",
    "GhostFaceNet",
]

DETECTION_BACKENDS = [
    'opencv', 
    'ssd', 
    'dlib', 
    'mtcnn', 
    'fastmtcnn',
    'retinaface', 
    'mediapipe',
    'yolov8',
    'yunet',
    'centerface',
]

# Quality thresholds
MIN_BRIGHTNESS = 40
MIN_CONTRAST = 20
MIN_RESOLUTION = 224
MIN_FACE_CONFIDENCE = 0.5

# Privacy settings
RETENTION_DAYS = 30
ENCRYPTION_KEY_LENGTH = 32