from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime
import tempfile
from werkzeug.utils import secure_filename
from src.security.privacy_manager import PrivacyManager 
from src.monitoring.model_monitor import ModelMonitor
from src.security.consent_manager import ConsentRecord
from src.core.face_comparator import compare_photos_with_explanations
from src.utils.helpers import load_config, export_model_card

app = Flask(__name__, 
    static_url_path='', 
    static_folder='server_documentation')
CORS(app)

# Initialize components
privacy_manager = PrivacyManager('./data/secure_storage')
model_monitor = ModelMonitor('facial_comparison_v1')
settings = load_config('./config/settings.py')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/compare', methods=['POST'])
def compare_faces():
    try:
        # Validate files
        if 'reference_image' not in request.files or 'live_image' not in request.files:
            return jsonify({'error': 'Missing image files'}), 400
            
        reference_image = request.files['reference_image']
        live_image = request.files['live_image']
        
        if not all(allowed_file(f.filename) for f in [reference_image, live_image]):
            return jsonify({'error': 'Invalid file type'}), 400

        # Get and validate consent data
        required_consent_fields = ['user_id', 'retention_period']  # Removed purpose and data_types
        consent_data = {}
        
        # Set default values
        consent_data['purpose'] = 'identity_verification'  # Default purpose
        consent_data['data_types'] = 'facial_images,facial_features'  # Default data types
        
        # Get required fields
        for field in required_consent_fields:
            value = request.form.get(field)
            if not value:
                return jsonify({'error': f'Missing required consent field: {field}'}), 400
            consent_data[field] = value

        # Override defaults if provided in request
        if request.form.get('purpose'):
            consent_data['purpose'] = request.form.get('purpose')
        if request.form.get('data_types'):
            consent_data['data_types'] = request.form.get('data_types')

        # Parse data types and retention period
        try:
            data_types = consent_data['data_types'].split(',')
            retention_period = int(consent_data['retention_period'])
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid data_types or retention_period format'}), 400

        # Record consent
        consent = ConsentRecord(
            user_id=consent_data['user_id'],
            consent_date=datetime.now().isoformat(),
            purpose=consent_data['purpose'],
            retention_period=retention_period,
            data_types=data_types
        )
        privacy_manager.record_consent(consent)

        # Create secure temporary files
        with tempfile.NamedTemporaryFile(delete=False) as ref_temp:
            reference_image.save(ref_temp.name)
        with tempfile.NamedTemporaryFile(delete=False) as live_temp:
            live_image.save(live_temp.name)

        try:
            # Perform comparison
            result = compare_photos_with_explanations(
                ref_temp.name,
                live_temp.name,
                consent.user_id,
                privacy_manager,
                model_monitor
            )
            
            return jsonify(result)

        finally:
            # Clean up temporary files
            os.unlink(ref_temp.name)
            os.unlink(live_temp.name)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def documentation():
    return send_from_directory('server_documentation', 'index.html')

@app.route('/monitoring/performance')
def performance_logs():
    """Display model performance monitoring data."""
    logs = []
    log_path = f"monitoring/{model_monitor.model_name}_performance.jsonl"
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            logs = [json.loads(line) for line in f]
    return jsonify({
        "logs": logs,
        "drift_status": model_monitor.detect_drift(),
        "calibration_needed": model_monitor.check_calibration()
    })

@app.route('/model/card')
def model_card():
    """Display model card with system details."""
    with open('docs/model_card.json', 'r') as f:
        card_data = json.load(f)
    return jsonify(card_data)

@app.route('/consent/logs')
def consent_logs():
    """Display consent records (with PII removed)."""
    consent_files = os.listdir('./data/secure_storage')
    consent_records = []
    for file in consent_files:
        if file.startswith('consent_'):
            with open(os.path.join('./data/secure_storage', file), 'r') as f:
                record = json.load(f)
                # Format user_id correctly
                original_id = record['user_id']
                record['user_id'] = f"user_{original_id}"  # Add user_ prefix without truncating
                consent_records.append(record)
    return jsonify({"records": consent_records})

@app.route('/system/settings')
def system_settings():
    """Display system configuration."""
    # Remove sensitive data
    safe_settings = settings.copy()
    if 'encryption' in safe_settings:
        del safe_settings['encryption']
    return jsonify(safe_settings)

@app.route('/system/health')
def system_health():
    """System health and monitoring status."""
    return jsonify({
        "status": "healthy",
        "model_status": {
            "drift_detected": model_monitor.detect_drift() is not None,
            "last_calibration": model_monitor.last_calibration.isoformat(),
            "performance_samples": len(model_monitor.performance_history)
        },
        "storage": {
            "consent_records": len(os.listdir('./data/secure_storage')),
            "monitoring_data": os.path.exists(f"monitoring/{model_monitor.model_name}_performance.jsonl")
        }
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)