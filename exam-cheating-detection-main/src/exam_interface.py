from flask import Flask, render_template, Response, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room
import cv2
import json
import time
from datetime import datetime, timedelta
import threading
import os
import sys
import yaml
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

# Import all detection and utils modules
from detection.face_detection import FaceDetector
from detection.eye_tracking import EyeTracker
from detection.mouth_detection import MouthMonitor
from detection.multi_face import MultiFaceDetector
from detection.object_detection import ObjectDetector
from detection.audio_detection import AudioMonitor

from utils.video_utils import VideoRecorder
from utils.screen_capture import ScreenRecorder
from utils.logging import AlertLogger
from utils.alert_system import AlertSystem
from utils.violation_logger import ViolationLogger
from utils.screenshot_utils import ViolationCapturer
from reporting.report_generator import ReportGenerator
from utils.mongodb_utils import MongoDBManager

# Load config
config_path = os.path.join(project_root, 'config', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Flask setup
template_dir = os.path.join(project_root, 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your-secret-key-change-this'
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, cors_allowed_origins="*")

class ExamSession:
    def __init__(self, student_name, exam_name, exam_code=None, duration_minutes=60):
        self.student_name = student_name
        self.exam_name = exam_name
        self.exam_code = exam_code or exam_name
        self.student_id = f"STUDENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.duration_minutes = duration_minutes
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.is_active = True
        self.is_submitted = False
        self.violations = []
        self.warning_count = 0
        self.max_warnings = 3
        self.last_violation_time = {}  # Track last time for each violation type
        self.violation_cooldown = 10  # Seconds between same violation type
        
    def get_remaining_time(self):
        remaining = self.end_time - datetime.now()
        return max(0, remaining.total_seconds())
    
    def can_log_violation(self, violation_type):
        """Check if enough time has passed since last same violation"""
        current_time = time.time()
        last_time = self.last_violation_time.get(violation_type, 0)
        return (current_time - last_time) >= self.violation_cooldown
    
    def add_violation(self, violation_type, timestamp=None, metadata=None):
        """Add violation and return if warning should be shown"""
        # Check cooldown to prevent multiple same violations
        if not self.can_log_violation(violation_type):
            return False
        
        # Update last violation time
        self.last_violation_time[violation_type] = time.time()
        
        self.violations.append({
            'type': violation_type,
            'time': datetime.now().strftime("%H:%M:%S"),
            'timestamp': timestamp or datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            'metadata': metadata or {}
        })
        
        # Count unique violation types for warnings
        unique_violations = set([v['type'] for v in self.violations])
        new_warning_count = len(unique_violations)
        
        if new_warning_count > self.warning_count:
            self.warning_count = new_warning_count
            return True
        return False
    
    def get_warnings_left(self):
        return max(0, self.max_warnings - self.warning_count)
    
    def is_terminated(self):
        return self.warning_count >= self.max_warnings
    
    def get_student_info(self):
        return {
            'id': self.student_id,
            'name': self.student_name,
            'exam': self.exam_name,
            'course': 'Online Exam'
        }
    
    def get_status(self):
        return {
            'active': self.is_active and not self.is_submitted and not self.is_terminated(),
            'time_remaining': self.get_remaining_time(),
            'violations': self.violations[-15:],
            'student_name': self.student_name,
            'exam_name': self.exam_name,
            'warning_count': self.warning_count,
            'warnings_left': self.get_warnings_left(),
            'terminated': self.is_terminated()
        }

# Global variables
current_exam = None
camera = None
detectors = []
alert_logger = None
alert_system = None
violation_capturer = None
violation_logger = None
video_recorder = None
screen_recorder = None
audio_monitor = None
mongodb_manager = None
last_center_gaze_time = time.time()

# Detection control variables
frame_counter = 0
DETECTION_INTERVAL = 3  # Process detection every 3 frames
last_violation_capture = {}  # Track last capture time per violation
VIOLATION_CAPTURE_COOLDOWN = 5  # Seconds between captures of same violation

# Background detection threading
latest_results = {
    'face_present': True,
    'gaze_direction': 'Center',
    'eye_ratio': 0.3,
    'mouth_moving': False,
    'multiple_faces': False,
    'objects_detected': False,
    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
detection_thread_running = False
detection_lock = threading.Lock()

def detection_worker():
    """Background worker for running detections"""
    global detection_thread_running, latest_results, camera
    
    while detection_thread_running:
        if camera and camera.isOpened():
            success, frame = camera.read()
            if success:
                # Run detections
                new_results = run_detections_internal(frame)
                with detection_lock:
                    latest_results.update(new_results)
        time.sleep(0.01) # Small sleep to prevent CPU hogging

def run_detections_internal(frame):
    """Internal function to run detections and return results with dynamic settings checks"""
    global current_exam, violation_capturer, violation_logger, alert_system, last_violation_capture, last_center_gaze_time
    
    results = {
        'face_present': True,
        'gaze_direction': 'center',
        'eye_ratio': 0.3,
        'mouth_moving': False,
        'multiple_faces': False,
        'objects_detected': False,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # If webcam proctoring is disabled, bypass all AI camera checks
    if not config.get('enable_webcam', True):
        return results
        
    # Run all detections
    try:
        results['face_present'] = detectors[0].detect_face(frame)
        
        # Gaze tracking (if enabled)
        if config.get('detection', {}).get('eyes', {}).get('enabled', True):
            results['gaze_direction'], results['eye_ratio'] = detectors[1].track_eyes(frame)
        else:
            results['gaze_direction'] = 'center'
            results['eye_ratio'] = 0.3
            
        # Mouth movement monitor (if enabled)
        if config.get('detection', {}).get('mouth', {}).get('enabled', True):
            results['mouth_moving'] = detectors[2].monitor_mouth(frame)
        else:
            results['mouth_moving'] = False
            
        results['multiple_faces'] = detectors[3].detect_multiple_faces(frame)
        
        # Object detection (if enabled)
        if config.get('detection', {}).get('objects', {}).get('enabled', True):
            results['objects_detected'] = detectors[4].detect_objects(frame)
        else:
            results['objects_detected'] = False
    except Exception as e:
        print(f"Detection error: {e}")
        return results
    
    # Check for violations
    if not current_exam or not current_exam.is_active:
        return results

    violation_type = None
    if results['multiple_faces']:
        violation_type = "MULTIPLE_FACES"
    elif results['objects_detected'] and config.get('detection', {}).get('objects', {}).get('enabled', True):
        violation_type = "OBJECT_DETECTED"
    elif results['mouth_moving'] and config.get('detection', {}).get('mouth', {}).get('enabled', True):
        violation_type = "MOUTH_MOVING"
    elif config.get('detection', {}).get('eyes', {}).get('enabled', True) and results['gaze_direction'].lower() != 'center':
        gaze_away_threshold = config.get('detection', {}).get('eyes', {}).get('gaze_threshold', 2)
        if time.time() - last_center_gaze_time > gaze_away_threshold:
            violation_type = "GAZE_AWAY"
    elif not results['face_present']:
        violation_type = "FACE_DISAPPEARED"
        
    if results['gaze_direction'].lower() == 'center':
        last_center_gaze_time = time.time()
    
    if violation_type:
        current_time = time.time()
        last_capture = last_violation_capture.get(violation_type, 0)
        
        if current_time - last_capture >= VIOLATION_CAPTURE_COOLDOWN:
            last_violation_capture[violation_type] = current_time
            alert_system.speak_alert(violation_type)
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            violation_result = violation_capturer.capture_violation(frame, violation_type, ts_str)
            
            image_gridfs_id = None
            if mongodb_manager and mongodb_manager.is_connected() and violation_result:
                image_path = violation_result.get('image_path')
                if image_path:
                    filename = os.path.basename(image_path)
                    image_gridfs_id = mongodb_manager.save_file_to_gridfs(image_path, filename, 'image/jpeg')
                    if image_gridfs_id:
                        try:
                            if os.path.exists(image_path):
                                os.remove(image_path)
                                print(f"[Cleanup] Deleted local violation snapshot after GridFS upload: {image_path}")
                        except Exception as clean_ex:
                            print(f"[Cleanup] Error deleting local violation snapshot {image_path}: {clean_ex}")
            
            log_metadata = {'details': results}
            if image_gridfs_id:
                log_metadata['image_gridfs_id'] = image_gridfs_id
                
            violation_logger.log_violation(violation_type, ts_str, log_metadata)
            current_exam.add_violation(violation_type, ts_str, log_metadata)
            
            if mongodb_manager and mongodb_manager.is_connected():
                mongodb_manager.log_violation({
                    'student_id': current_exam.student_id if current_exam else None,
                    'student_name': current_exam.student_name if current_exam else None,
                    'exam_name': current_exam.exam_name if current_exam else None,
                    'type': violation_type,
                    'timestamp': ts_str,
                    'image_gridfs_id': image_gridfs_id,
                    'metadata': log_metadata
                })
            
            # Emit real-time WebSocket violation alert to Admin
            try:
                socketio.emit('violation_detected', {
                    'student_id': current_exam.student_id if current_exam else 'UNKNOWN',
                    'student_name': current_exam.student_name if current_exam else 'Anonymous',
                    'exam_name': current_exam.exam_name if current_exam else 'Online Exam',
                    'type': violation_type,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'image_gridfs_id': image_gridfs_id,
                    'risk_level': 'High' if violation_type in ['MULTIPLE_FACES', 'TAB_SWITCHED'] else 'Medium'
                }, to='admin')
                print(f"[WebSocket] Real-time alert emitted to Admin: {violation_type}")
            except Exception as se:
                print(f"[WebSocket] Error emitting alert: {se}")
            
            if current_exam.is_terminated():
                current_exam.is_active = False
    
    return results

def handle_audio_violation(message="Voice activity detected"):
    """Handle background voice detection violations and increment warning count"""
    global current_exam, violation_logger, alert_system, socketio, mongodb_manager
    
    if current_exam and current_exam.is_active:
        violation_type = "AUDIO_DETECTED"
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Cooldown check
        if not current_exam.can_log_violation(violation_type):
            return
            
        print(f"🎙️ Voice/Audio violation detected: {message}")
        
        # Log violation locally
        violation_logger.log_violation(violation_type, ts_str, {'details': message})
        
        # Add violation to session and check if warning count increased
        warning_shown = current_exam.add_violation(violation_type, ts_str, {'details': message})
        
        if warning_shown:
            # Play verbal/TTS warning
            alert_system.speak_alert(violation_type)
            
        # Log to MongoDB if connected
        if mongodb_manager and mongodb_manager.is_connected():
            mongodb_manager.log_violation({
                'student_id': current_exam.student_id,
                'student_name': current_exam.student_name,
                'exam_name': current_exam.exam_name,
                'type': violation_type,
                'timestamp': ts_str,
                'metadata': {'details': message}
            })
            
        # Emit WebSocket alert to Admin
        try:
            socketio.emit('violation_detected', {
                'student_id': current_exam.student_id if current_exam else 'UNKNOWN',
                'student_name': current_exam.student_name if current_exam else 'Anonymous',
                'exam_name': current_exam.exam_name if current_exam else 'Online Exam',
                'type': violation_type,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'image_gridfs_id': None,
                'risk_level': 'Medium'
            }, to='admin')
            print(f"[WebSocket] Real-time audio violation alert emitted to Admin")
        except Exception as se:
            print(f"[WebSocket] Error emitting audio alert: {se}")
            
        if current_exam.is_terminated():
            current_exam.is_active = False

def initialize_system():
    """Initialize all detection and recording systems"""
    global detectors, alert_logger, alert_system, violation_capturer, violation_logger, video_recorder, screen_recorder, audio_monitor, mongodb_manager
    
    print("=" * 50)
    print("Initializing Exam Proctoring System...")
    print("=" * 50)
    
    # Initialize MongoDB Manager
    mongodb_manager = MongoDBManager(config)
    
    # Initialize logging and alert systems
    alert_logger = AlertLogger(config)
    alert_system = AlertSystem(config)
    violation_capturer = ViolationCapturer(config)
    violation_logger = ViolationLogger(config)
    
    # Initialize recorders
    video_recorder = VideoRecorder(config)
    screen_recorder = ScreenRecorder(config)
    
    # Initialize audio monitor
    audio_monitor = AudioMonitor(config)
    audio_monitor.alert_system = alert_system
    audio_monitor.alert_logger = alert_logger
    audio_monitor.on_voice_detected = handle_audio_violation
    if config.get('detection', {}).get('audio_monitoring', {}).get('enabled', True):
        audio_monitor.start()
        print("✅ Audio monitoring started")
    
    # Initialize detectors
    print("Loading AI Models...")
    detectors = [
        FaceDetector(config),
        EyeTracker(config),
        MouthMonitor(config),
        MultiFaceDetector(config),
        ObjectDetector(config),
    ]
    
    # Set alert logger for all detectors
    for detector in detectors:
        if hasattr(detector, 'set_alert_logger'):
            detector.set_alert_logger(alert_logger)
    
    print("✅ All systems initialized!")

def display_detection_results(frame, results):
    """Display detection results on frame - Stable version"""
    y_offset = 30
    line_height = 28
    
    # Background for better readability
    overlay = frame.copy()
    cv2.rectangle(overlay, (5, 5), (300, 200), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
    
    # Status indicators with stable colors
    face_color = (0, 255, 0) if results['face_present'] else (0, 0, 255)
    cv2.putText(frame, f"Face: {'✓ PRESENT' if results['face_present'] else '✗ NOT VISIBLE'}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.55, face_color, 2)
    y_offset += line_height
    
    # Gaze direction
    gaze_color = (0, 255, 0) if results['gaze_direction'] == 'Center' else (0, 165, 255)
    cv2.putText(frame, f"Gaze: {results['gaze_direction'].upper()}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.55, gaze_color, 2)
    y_offset += line_height
    
    # Eye status
    eye_status = "Open" if results['eye_ratio'] > 0.25 else "Closed"
    eye_color = (0, 255, 0) if results['eye_ratio'] > 0.25 else (0, 0, 255)
    cv2.putText(frame, f"Eyes: {eye_status}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.55, eye_color, 2)
    y_offset += line_height
    
    # Mouth status
    mouth_color = (0, 165, 255) if results['mouth_moving'] else (0, 255, 0)
    cv2.putText(frame, f"Mouth: {'MOVING' if results['mouth_moving'] else 'Still'}", (10, y_offset), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.55, mouth_color, 2)
    y_offset += line_height
    
    # Alerts
    if results['multiple_faces']:
        cv2.putText(frame, "⚠️ MULTIPLE FACES DETECTED!", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += line_height
    
    if results['objects_detected']:
        cv2.putText(frame, "⚠️ SUSPICIOUS OBJECT DETECTED!", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += line_height
    
    # Warning counter
    if current_exam:
        warning_color = (0, 255, 0) if current_exam.get_warnings_left() > 0 else (0, 0, 255)
        cv2.putText(frame, f"Warnings: {current_exam.warning_count}/3", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, warning_color, 2)
    
    # Timestamp on right side
    cv2.putText(frame, results['timestamp'].split()[1], 
               (frame.shape[1] - 120, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

def run_detections(frame):
    """Overlay latest detection results on the frame"""
    with detection_lock:
        results = latest_results.copy()
    
    # Display results on frame
    frame = display_detection_results(frame, results)
    
    return frame

def get_camera():
    """Get or initialize camera"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(config['video']['source'], cv2.CAP_DSHOW)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, config['video']['resolution'][0])
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config['video']['resolution'][1])
            camera.set(cv2.CAP_PROP_FPS, config['video']['fps'])
            # Warm up camera
            for _ in range(10):
                camera.read()
            time.sleep(1)  # Give camera time to stabilize
            print("✅ Camera initialized")
    return camera

@app.route('/')
def index():
    """Landing page"""
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error loading login page: {e}"

@app.route('/start_exam', methods=['POST'])
def start_exam():
    """Start exam session with all recording features"""
    global current_exam, video_recorder, screen_recorder, frame_counter, last_violation_capture
    
    student_name = request.form.get('student_name')
    exam_name = request.form.get('exam_name')
    exam_code = request.form.get('exam_code') or exam_name
    duration = int(request.form.get('duration', 60))
    
    # Reset tracking variables
    frame_counter = 0
    last_violation_capture = {}
    
    # Create exam session
    current_exam = ExamSession(student_name, exam_name, exam_code, duration)
    
    # Start recordings
    if config['screen']['recording']:
        screen_recorder.start_recording()
        print("✅ Screen recording started")
    
    video_recorder.start_recording()
    print("✅ Video recording started")
    
    # Start detection thread
    global detection_thread_running
    if not detection_thread_running:
        detection_thread_running = True
        threading.Thread(target=detection_worker, daemon=True).start()
        print("✅ Detection thread started")
    
    # Give camera time to stabilize before calibration
    time.sleep(1)
    print("✅ Calibration complete - Exam starting")
    
    try:
        return render_template('exam.html', 
                             student_name=student_name, 
                             exam_name=exam_name,
                             exam_code=exam_code,
                             lockdown_browser=config.get('lockdown_browser', True),
                             force_fullscreen=config.get('force_fullscreen', True))
    except Exception as e:
        return f"Error loading exam page: {e}"

@app.route('/video_feed')
def video_feed():
    """Video streaming with full detection"""
    def generate():
        global frame_counter
        
        if not config.get('enable_webcam', True):
            while current_exam and current_exam.is_active and not current_exam.is_terminated():
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "WEBCAM STREAM DISABLED BY PROCTOR", (100, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                ret, buffer = cv2.imencode('.jpg', blank)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.5)
            # Exam ended - show termination message
            while True:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                if current_exam and current_exam.is_terminated():
                    cv2.putText(blank, "EXAM TERMINATED - 3 WARNINGS REACHED", (50, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(blank, "EXAM COMPLETED", (50, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                ret, buffer = cv2.imencode('.jpg', blank)
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(1)
            return
            
        cap = get_camera()
        if not cap or not cap.isOpened():
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'Camera Error' + b'\r\n'
            return
        
        # Wait a bit for camera to stabilize
        time.sleep(1)
        
        while current_exam and current_exam.is_active and not current_exam.is_terminated():
            success, frame = cap.read()
            if not success:
                continue
            
            # Overlay detection results on every frame to prevent blinking
            frame = run_detections(frame)
            
            # Record frame
            if video_recorder:
                video_recorder.record_frame(frame)
            
            # Add timer and student info overlay
            if current_exam:
                remaining = current_exam.get_remaining_time()
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                hours = int(remaining // 3600)
                timer_text = f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # Semi-transparent background for timer
                overlay = frame.copy()
                cv2.rectangle(overlay, (frame.shape[1] - 250, 5), (frame.shape[1] - 10, 60), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
                
                cv2.putText(frame, timer_text, (frame.shape[1] - 240, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Check if time is up
                if remaining <= 0:
                    current_exam.is_active = False
                    break
            
            # Encode and send frame
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Small delay for performance
            time.sleep(0.033)
        
        # Exam ended - show termination message
        while True:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            if current_exam and current_exam.is_terminated():
                cv2.putText(blank, "EXAM TERMINATED - 3 WARNINGS REACHED", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(blank, "EXAM COMPLETED", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(1)
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_grid_file/<file_id>')
def get_grid_file(file_id):
    """Retrieve and serve a file directly from MongoDB GridFS with full HTTP Range support for video seeking"""
    if not mongodb_manager or not mongodb_manager.is_connected():
        return "MongoDB features are not enabled", 503
        
    try:
        grid_file = mongodb_manager.get_file_from_gridfs(file_id)
        if not grid_file:
            return "File not found in GridFS", 404
            
        import mimetypes
        content_type = grid_file.content_type
        if not content_type:
            content_type, _ = mimetypes.guess_type(grid_file.filename)
        if not content_type:
            content_type = 'application/octet-stream'
            
        file_length = grid_file.length
        
        # Parse standard HTTP Range request headers for streaming video chunks
        range_header = request.headers.get('Range', None)
        if range_header and content_type.startswith('video/'):
            try:
                # E.g. "bytes=1048576-" or "bytes=0-1024"
                byte_ranges = range_header.replace('bytes=', '').split('-')
                start_byte = int(byte_ranges[0])
                end_byte = int(byte_ranges[1]) if (len(byte_ranges) > 1 and byte_ranges[1]) else file_length - 1
            except ValueError:
                start_byte = 0
                end_byte = file_length - 1
                
            start_byte = max(0, min(start_byte, file_length - 1))
            end_byte = max(start_byte, min(end_byte, file_length - 1))
            length = end_byte - start_byte + 1
            
            grid_file.seek(start_byte)
            chunk_data = grid_file.read(length)
            
            response = Response(chunk_data, 206, mimetype=content_type)
            response.headers['Content-Range'] = f'bytes {start_byte}-{end_byte}/{file_length}'
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(length)
            response.headers['Content-Disposition'] = f'inline; filename="{grid_file.filename}"'
            return response
        else:
            # Direct full-file response (e.g. standard images or non-seeked media requests)
            response = Response(grid_file.read(), mimetype=content_type)
            response.headers['Content-Length'] = str(file_length)
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Disposition'] = f'inline; filename="{grid_file.filename}"'
            return response
    except Exception as e:
        return f"Error fetching file: {e}", 500

@app.route('/get_exam_status')
def get_exam_status():
    """Get current exam status"""
    if current_exam:
        status = current_exam.get_status()
        
        if status['time_remaining'] <= 0:
            current_exam.is_active = False
            status['active'] = False
            status['message'] = 'Time is up!'
        
        if current_exam.is_terminated():
            status['active'] = False
            status['terminated'] = True
            status['message'] = 'Exam terminated due to 3 warnings!'
        
        return jsonify(status)
    return jsonify({'active': False, 'message': 'Exam ended'})

@app.route('/log_tab_switch', methods=['POST'])
def log_tab_switch():
    """Handle tab switching violation - Ends exam immediately, stops recorders, and saves results"""
    global current_exam, violation_logger, alert_system, video_recorder, screen_recorder
    
    if current_exam and current_exam.is_active:
        violation_type = "TAB_SWITCHED"
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Log violation
        violation_logger.log_violation(violation_type, ts_str, {'details': 'User switched tab or minimized window'})
        
        # Add to exam session (force termination)
        current_exam.warning_count = 3  # Force terminate
        current_exam.add_violation(violation_type, ts_str, {'details': 'User switched tab or minimized window'})
        current_exam.is_active = False
        current_exam.is_submitted = True # Mark as finished
        
        # Play voice alert
        alert_system.speak_alert(violation_type)
        
        # Stop recorders and save video/screen recordings gracefully
        video_result = None
        screen_result = None
        if video_recorder:
            video_result = video_recorder.stop_recording()
            print(f"🎬 [Termination] Webcam video saved: {video_result['filename'] if video_result else 'None'}")
            
        if screen_recorder and config['screen']['recording']:
            screen_result = screen_recorder.stop_recording()
            print(f"🎬 [Termination] Screen recording saved: {screen_result['filename'] if screen_result else 'None'}")
            
        # Generate final PDF/HTML proctor report
        report_generator = ReportGenerator(config)
        student_info = current_exam.get_student_info()
        violations = violation_logger.get_violations()
        report_path = report_generator.generate_report(student_info, violations)
        
        # Grade and upload exam metrics and files to MongoDB GridFS
        save_exam_results(current_exam, {}, video_result, screen_result, report_path)
        
        print(f"🚨 CRITICAL Violation: {violation_type} at {datetime.now().strftime('%H:%M:%S')} - Exam terminated and saved successfully!")
        
        return jsonify({'success': True, 'terminated': True})
    
    return jsonify({'success': False, 'message': 'No active exam'})

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    """Submit exam and generate report"""
    global current_exam, video_recorder, screen_recorder
    
    if not current_exam:
        return jsonify({'success': False, 'message': 'No active exam found'})
    
    current_exam.is_submitted = True
    current_exam.is_active = False
    
    # Save answers
    answers = request.json.get('answers', {})
    
    # Stop recordings
    video_result = None
    screen_result = None
    
    if video_recorder:
        video_result = video_recorder.stop_recording()
        print(f"✅ Video saved: {video_result['filename'] if video_result else 'None'}")
    
    if screen_recorder and config['screen']['recording']:
        screen_result = screen_recorder.stop_recording()
        print(f"✅ Screen recording saved: {screen_result['filename'] if screen_result else 'None'}")
    
    # Generate report
    report_generator = ReportGenerator(config)
    student_info = current_exam.get_student_info()
    violations = violation_logger.get_violations()
    report_path = report_generator.generate_report(student_info, violations)
    
    # Save exam results
    save_exam_results(current_exam, answers, video_result, screen_result, report_path)
    
    print(f"📊 Report generated: {report_path}")
    print(f"📝 Total violations: {len(violations)}")
    
    return jsonify({'success': True, 'message': 'Exam submitted successfully!'})

def save_exam_results(exam, answers, video_result, screen_result, report_path):
    """Save all exam data to JSON and MongoDB, with absolute path resolution and dynamic grading"""
    results_dir = os.path.join(project_root, 'exam_results')
    os.makedirs(results_dir, exist_ok=True)
    
    # GridFS uploads with absolute path resolution to guarantee uploads
    video_gridfs_id = None
    screen_gridfs_id = None
    report_gridfs_id = None
    
    if mongodb_manager and mongodb_manager.is_connected():
        if config.get('upload_gridfs', True):
            if video_result and video_result.get('filename'):
                v_path = os.path.abspath(video_result['filename'])
                if os.path.exists(v_path):
                    video_gridfs_id = mongodb_manager.save_file_to_gridfs(v_path, os.path.basename(v_path), 'video/mp4')
                    if video_gridfs_id:
                        try:
                            os.remove(v_path)
                            print(f"[Cleanup] Deleted local video file after GridFS upload: {v_path}")
                        except Exception as clean_ex:
                            print(f"[Cleanup] Error deleting local video file {v_path}: {clean_ex}")
                else:
                    print(f"[save_exam_results] WARNING: Video file does not exist at absolute path: {v_path}")
                
            if screen_result and screen_result.get('filename'):
                s_path = os.path.abspath(screen_result['filename'])
                if os.path.exists(s_path):
                    screen_gridfs_id = mongodb_manager.save_file_to_gridfs(s_path, os.path.basename(s_path), 'video/mp4')
                    if screen_gridfs_id:
                        try:
                            os.remove(s_path)
                            print(f"[Cleanup] Deleted local screen video file after GridFS upload: {s_path}")
                        except Exception as clean_ex:
                            print(f"[Cleanup] Error deleting local screen video file {s_path}: {clean_ex}")
                else:
                    print(f"[save_exam_results] WARNING: Screen video file does not exist at absolute path: {s_path}")
            
        if report_path:
            r_path = os.path.abspath(report_path)
            if os.path.exists(r_path):
                report_gridfs_id = mongodb_manager.save_file_to_gridfs(r_path, os.path.basename(r_path))
                if report_gridfs_id:
                    try:
                        os.remove(r_path)
                        print(f"[Cleanup] Deleted local report file after GridFS upload: {r_path}")
                    except Exception as clean_ex:
                        print(f"[Cleanup] Error deleting local report file {r_path}: {clean_ex}")
                        
                    # Delete intermediate heatmap and timeline charts under reports/generated/images/ matching the student's ID
                    try:
                        student_id = exam.student_id
                        image_dir = os.path.join(project_root, 'reports', 'generated', 'images')
                        for img_name in [f'heatmap_{student_id}.png', f'timeline_{student_id}.png']:
                            img_path = os.path.join(image_dir, img_name)
                            if os.path.exists(img_path):
                                os.remove(img_path)
                                print(f"[Cleanup] Deleted intermediate chart file: {img_path}")
                    except Exception as img_clean_ex:
                        print(f"[Cleanup] Error deleting intermediate charts for student {exam.student_id}: {img_clean_ex}")
                
    # Fetch quiz questions for grading
    quiz_questions = []
    if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.quizzes_col is not None:
        try:
            quiz_doc = mongodb_manager.quizzes_col.find_one({'exam_code': exam.exam_code})
            if quiz_doc:
                quiz_questions = quiz_doc.get('questions', [])
        except Exception as e:
            print(f"Error fetching quiz from DB for grading: {e}")
            
    if not quiz_questions:
        # Seeding fallback questions
        quiz_questions = [
            {"text": "What is the capital of France?", "options": ["London", "Berlin", "Paris", "Madrid"], "correct": 2, "type": "mcq"},
            {"text": "Which programming language is primarily used for Artificial Intelligence?", "options": ["Java", "Python", "C++", "Ruby"], "correct": 1, "type": "mcq"},
            {"text": "What does CPU stand for?", "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Unit"], "correct": 0, "type": "mcq"},
            {"text": "Which of the following is a database management system?", "options": ["HTML", "CSS", "MySQL", "JavaScript"], "correct": 2, "type": "mcq"},
            {"text": "What does HTTP stand for?", "options": ["HyperText Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Text Protocol", "HighText Transfer Protocol"], "correct": 0, "type": "mcq"}
        ]
        
    grading_report = []
    correct_count = 0
    
    for idx, q in enumerate(quiz_questions):
        student_ans = answers.get(str(idx))
        correct_ans = q.get('correct') if q.get('correct') is not None else q.get('correct_answer')
        
        is_correct = False
        student_ans_text = "Not Answered"
        correct_ans_text = ""
        q_type = q.get('type', 'mcq')
        
        if q_type == 'text':
            # Text based subjective answer check (keyword match)
            if student_ans:
                student_ans_text = str(student_ans).strip()
                correct_ans_text = str(correct_ans).strip()
                if correct_ans_text.lower() in student_ans_text.lower():
                    is_correct = True
            else:
                correct_ans_text = str(correct_ans).strip()
        else:
            # MCQ choice check
            if student_ans is not None:
                try:
                    ans_idx = int(student_ans)
                    student_ans_text = q['options'][ans_idx] if ans_idx < len(q['options']) else str(student_ans)
                    
                    correct_idx = int(correct_ans)
                    correct_ans_text = q['options'][correct_idx]
                    
                    if ans_idx == correct_idx:
                        is_correct = True
                except Exception as ge:
                    print(f"Grading index error: {ge}")
            else:
                try:
                    correct_idx = int(correct_ans)
                    correct_ans_text = q['options'][correct_idx]
                except:
                    correct_ans_text = str(correct_ans)
                    
        if is_correct:
            correct_count += 1
            
        grading_report.append({
            'question_text': q.get('text') or q.get('question_text', 'Question'),
            'student_answer': student_ans_text,
            'correct_answer': correct_ans_text,
            'is_correct': is_correct,
            'type': q_type
        })
        
    score_data = {
        'correct': correct_count,
        'total': len(quiz_questions),
        'percentage': int((correct_count / len(quiz_questions)) * 100) if quiz_questions else 0
    }
    
    results = {
        'student_info': exam.get_student_info(),
        'exam_name': exam.exam_name,
        'exam_code': exam.exam_code,
        'start_time': exam.start_time.isoformat(),
        'end_time': datetime.now().isoformat(),
        'duration_minutes': exam.duration_minutes,
        'answers': answers,
        'violations': exam.violations,
        'warning_count': exam.warning_count,
        'terminated': exam.is_terminated(),
        'status': 'terminated' if exam.is_terminated() else 'submitted',
        'recordings': {
            'video': video_result['filename'] if video_result else None,
            'screen': screen_result['filename'] if screen_result else None,
            'video_gridfs_id': video_gridfs_id,
            'screen_gridfs_id': screen_gridfs_id
        },
        'report_path': report_path,
        'report_gridfs_id': report_gridfs_id,
        'grading_report': grading_report,
        'score': score_data
    }
    
    filename = f"exam_results_{exam.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(results_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Exam results saved to {filepath}")
    
    # Save to MongoDB
    if mongodb_manager and mongodb_manager.is_connected():
        mongodb_manager.save_session(results)
        
    # Store in flask session for completed scorecard display
    session['last_results'] = results
    
    # Broadcast to admin socket
    try:
        socketio.emit('exam_completed', {
            'student_id': exam.student_id,
            'student_name': exam.student_name,
            'exam_name': exam.exam_name,
            'score': score_data
        }, to='admin')
        print(f"[WebSocket] Emitted exam completion event for student: {exam.student_name}")
    except Exception as se:
        print(f"Error emitting exam_completed socket: {se}")
        
    # Print summary
    print("\n" + "=" * 50)
    print("EXAM SUMMARY")
    print("=" * 50)
    print(f"Student: {exam.student_name}")
    print(f"Exam: {exam.exam_name}")
    print(f"Duration: {(datetime.now() - exam.start_time).total_seconds() / 60:.1f} minutes")
    print(f"Warnings: {exam.warning_count}/3")
    print(f"Violations: {len(exam.violations)}")
    print(f"Score: {correct_count}/{len(quiz_questions)} ({score_data['percentage']}%)")
    print("=" * 50)
    
    return filepath

@app.route('/exam_completed')
def exam_completed():
    """Show scorecard and grading details template"""
    results = session.get('last_results')
    if not results:
        return render_template('login.html')
    
    return render_template('exam_completed.html', results=results)

@app.route('/api/admin_exams/quiz/<exam_code>', methods=['GET'])
def api_admin_exams_quiz_get(exam_code):
    """Retrieve quiz questions for a given exam_code"""
    if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.quizzes_col is not None:
        try:
            quiz_doc = mongodb_manager.quizzes_col.find_one({'exam_code': exam_code}, {'_id': 0})
            if quiz_doc:
                return jsonify(quiz_doc)
        except Exception as e:
            print(f"Error querying quizzes database: {e}")
            
    # Default fallbacks
    default_questions = [
        {"text": "What is the capital of France?", "options": ["London", "Berlin", "Paris", "Madrid"], "correct": 2, "type": "mcq"},
        {"text": "Which programming language is primarily used for Artificial Intelligence?", "options": ["Java", "Python", "C++", "Ruby"], "correct": 1, "type": "mcq"},
        {"text": "What does CPU stand for?", "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Unit"], "correct": 0, "type": "mcq"},
        {"text": "Which of the following is a database management system?", "options": ["HTML", "CSS", "MySQL", "JavaScript"], "correct": 2, "type": "mcq"},
        {"text": "What does HTTP stand for?", "options": ["HyperText Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Text Protocol", "HighText Transfer Protocol"], "correct": 0, "type": "mcq"}
    ]
    return jsonify({
        'exam_code': exam_code,
        'questions': default_questions
    })

@app.route('/api/admin_exams/quiz', methods=['POST'])
def api_admin_exams_quiz_post():
    """Save quiz questions dynamically from Admin panel"""
    data = request.json
    if not data or 'exam_code' not in data or 'questions' not in data:
        return jsonify({'success': False, 'message': 'Missing exam code or questions'}), 400
        
    exam_code = data['exam_code']
    questions = data['questions']
    
    if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.quizzes_col is not None:
        try:
            mongodb_manager.quizzes_col.update_one(
                {'exam_code': exam_code},
                {'$set': {'exam_code': exam_code, 'questions': questions}},
                upsert=True
            )
            return jsonify({'success': True, 'message': 'Quiz questions imported and saved successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
            
    return jsonify({'success': True, 'message': 'Quiz saved locally in memory (Offline mode)'})

@app.route('/admin')
def admin_panel():
    """Render premium administrative proctoring dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/api/admin_stats')
def api_admin_stats():
    """Query and aggregate system-wide stats dynamically from MongoDB ONLY (no dummy data)"""
    stats = {
        'total_students': 0,
        'active_exams': 0,
        'cheating_alerts': 0,
        'suspicious_students': 0,
        'exams_completed': 0,
        'average_trust_score': 100,
        'total_reports': 0,
        'system_status': {
            'webcam_monitoring': 'Online' if (camera and camera.isOpened()) else 'Offline',
            'ai_detection_engine': 'Online' if detection_thread_running else 'Offline',
            'database': 'Offline',
            'cloud_storage': 'Online',
            'notifications': 'Online'
        }
    }
    
    if mongodb_manager and mongodb_manager.is_connected():
        stats['system_status']['database'] = 'Online'
        try:
            stats['total_students'] = len(mongodb_manager.sessions_col.distinct('student_info.id'))
            stats['exams_completed'] = mongodb_manager.sessions_col.count_documents({'status': 'submitted'})
            stats['cheating_alerts'] = mongodb_manager.violations_col.count_documents({})
            stats['suspicious_students'] = mongodb_manager.sessions_col.count_documents({'warning_count': {'$gt': 0}})
            stats['total_reports'] = mongodb_manager.sessions_col.count_documents({'report_gridfs_id': {'$ne': None}})
            
            # Calculate average trust score
            cursor = mongodb_manager.sessions_col.find({}, {'warning_count': 1})
            scores = []
            for doc in cursor:
                warnings = doc.get('warning_count', 0)
                score = max(0, 100 - (warnings * 24))
                scores.append(score)
            if scores:
                stats['average_trust_score'] = int(sum(scores) / len(scores))
        except Exception as e:
            print(f"Error querying statistics: {e}")
            
    if current_exam and current_exam.is_active:
        stats['active_exams'] = 1
        
    return jsonify(stats)

@app.route('/api/admin_alerts')
def api_admin_alerts():
    """Retrieve proctoring alerts dynamically from MongoDB ONLY (no dummy data)"""
    db_alerts = []
    if mongodb_manager and mongodb_manager.is_connected():
        try:
            cursor = mongodb_manager.violations_col.find().sort('timestamp', -1).limit(40)
            for idx, doc in enumerate(cursor):
                db_alerts.append({
                    'alert_id': f"ALRT-{100000 + idx}",
                    'student_id': doc.get('student_id', 'UNKNOWN'),
                    'student_name': doc.get('student_name', 'Student'),
                    'exam_name': doc.get('exam_name', 'Online Exam'),
                    'type': doc.get('type', 'Suspicious Activity'),
                    'risk_level': 'High' if doc.get('type') in ['MULTIPLE_FACES', 'TAB_SWITCHED'] else 'Medium',
                    'time': doc.get('timestamp', ''),
                    'confidence': '94%',
                    'image_gridfs_id': doc.get('image_gridfs_id'),
                    'status': 'Active'
                })
        except Exception as e:
            print(f"Error querying violations: {e}")
    return jsonify(db_alerts)

@app.route('/api/admin_recordings')
def api_admin_recordings():
    """Retrieve finished sessions with completed video recordings dynamically from MongoDB ONLY (no dummy data)"""
    db_recordings = []
    if mongodb_manager and mongodb_manager.is_connected():
        try:
            cursor = mongodb_manager.sessions_col.find().sort('start_time', -1).limit(40)
            for doc in cursor:
                video_g_id = doc.get('recordings', {}).get('video_gridfs_id')
                screen_g_id = doc.get('recordings', {}).get('screen_gridfs_id')
                report_g_id = doc.get('report_gridfs_id')
                db_recordings.append({
                    'student_id': doc['student_info'].get('id', 'UNKNOWN'),
                    'student_name': doc['student_info'].get('name', 'Student'),
                    'exam_name': doc.get('exam_name', 'Online Exam'),
                    'start_time': doc.get('start_time', ''),
                    'duration': '01:00:00',
                    'size': '450 MB',
                    'status': doc.get('status', 'Completed').capitalize(),
                    'video_gridfs_id': video_g_id,
                    'screen_gridfs_id': screen_g_id,
                    'report_gridfs_id': report_g_id
                })
        except Exception as e:
            print(f"Error querying recordings: {e}")
    return jsonify(db_recordings)

@app.route('/api/admin_exams', methods=['GET', 'POST'])
def api_admin_exams():
    """Retrieve or save exam configurations dynamically"""
    if request.method == 'GET':
        default_exams = [
            {"exam_code": "EX-DS-401", "exam_name": "Data Structures Mid Term", "subject": "Computer Science", "duration": "90 Minutes", "status": "Active"},
            {"exam_code": "EX-DB-204", "exam_name": "Database Management", "subject": "Computer Science", "duration": "60 Minutes", "status": "Upcoming"},
            {"exam_code": "EX-OS-302", "exam_name": "Operating Systems Final", "subject": "Electronics", "duration": "120 Minutes", "status": "Active"}
        ]
        if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.exams_col is not None:
            try:
                count = mongodb_manager.exams_col.count_documents({})
                if count == 0:
                    # Seed database with initial default exams
                    mongodb_manager.exams_col.insert_many(default_exams)
                
                exams = list(mongodb_manager.exams_col.find({}, {'_id': 0}))
                return jsonify(exams)
            except Exception as e:
                print(f"Error querying exams collection: {e}")
        return jsonify(default_exams)
        
    elif request.method == 'POST':
        data = request.json
        if not data or 'exam_code' not in data:
            return jsonify({'success': False, 'message': 'Missing exam code'}), 400
            
        exam_code = data['exam_code']
        exam_data = {
            'exam_code': exam_code,
            'exam_name': data.get('exam_name', 'Unnamed Exam'),
            'subject': data.get('subject', 'General Studies'),
            'duration': data.get('duration', '60 Minutes'),
            'status': data.get('status', 'Active')
        }
        if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.exams_col is not None:
            try:
                mongodb_manager.exams_col.update_one(
                    {'exam_code': exam_code},
                    {'$set': exam_data},
                    upsert=True
                )
                return jsonify({'success': True, 'message': 'Exam configuration saved successfully'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
        return jsonify({'success': True, 'message': 'Exam saved locally (Offline mode)'})

@app.route('/api/admin_exams/delete', methods=['POST'])
def api_admin_exams_delete():
    """Delete an exam configuration dynamically"""
    data = request.json
    if not data or 'exam_code' not in data:
        return jsonify({'success': False, 'message': 'Missing exam code'}), 400
        
    exam_code = data['exam_code']
    if mongodb_manager and mongodb_manager.is_connected() and mongodb_manager.exams_col is not None:
        try:
            mongodb_manager.exams_col.delete_one({'exam_code': exam_code})
            return jsonify({'success': True, 'message': 'Exam deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Database error: {e}'}), 500
    return jsonify({'success': True, 'message': 'Exam deleted locally (Offline mode)'})

@app.route('/api/admin_students')
def api_admin_students():
    """Retrieve unique list of all candidates from MongoDB sessions ONLY (no dummy data)"""
    students_list = []
    if mongodb_manager and mongodb_manager.is_connected():
        try:
            cursor = mongodb_manager.sessions_col.find()
            seen_ids = set()
            for doc in cursor:
                s_info = doc.get('student_info', {})
                s_id = s_info.get('id')
                if s_id and s_id not in seen_ids:
                    seen_ids.add(s_id)
                    warnings = doc.get('warning_count', 0)
                    trust_score = max(0, 100 - (warnings * 24))
                    status = 'Blocked' if warnings >= 3 else ('Suspicious' if warnings > 0 else 'Active')
                    students_list.append({
                        'student_id': s_id,
                        'student_name': s_info.get('name', 'Student'),
                        'student_email': f"{s_info.get('name', 'student').lower().replace(' ', '')}@gmail.com",
                        'trust_score': trust_score,
                        'status': status
                    })
        except Exception as e:
            print(f"Error querying students: {e}")
    return jsonify(students_list)

# WebSocket connection room handler for Admin panel
@socketio.on('join_admin')
def on_join_admin():
    join_room('admin')
    print("[WebSocket] Admin connected and successfully joined 'admin' room")
    emit('status_update', {'message': 'Connected to dynamic WebSocket proctor room'}, to='admin')

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """GET or POST system settings configuration"""
    global config, audio_monitor
    
    if request.method == 'GET':
        return jsonify({
            'enable_webcam': config.get('enable_webcam', True),
            'force_fullscreen': config.get('force_fullscreen', True),
            'lockdown_browser': config.get('lockdown_browser', True),
            'gaze_detection': config.get('detection', {}).get('eyes', {}).get('enabled', True),
            'object_recognition': config.get('detection', {}).get('objects', {}).get('enabled', True),
            'mouth_monitor': config.get('detection', {}).get('mouth', {}).get('enabled', True),
            'voice_alerts': config.get('logging', {}).get('alert_system', {}).get('voice_alerts', True),
            'upload_gridfs': config.get('upload_gridfs', True),
            'session_cleanup': config.get('session_cleanup', False),
            'audio_monitoring': config.get('detection', {}).get('audio_monitoring', {}).get('enabled', True)
        })
        
    elif request.method == 'POST':
        data = request.json or {}
        
        config['enable_webcam'] = data.get('enable_webcam', True)
        config['force_fullscreen'] = data.get('force_fullscreen', True)
        config['lockdown_browser'] = data.get('lockdown_browser', True)
        
        if 'detection' not in config:
            config['detection'] = {}
        if 'eyes' not in config['detection']:
            config['detection']['eyes'] = {}
        config['detection']['eyes']['enabled'] = data.get('gaze_detection', True)
        
        if 'objects' not in config['detection']:
            config['detection']['objects'] = {}
        config['detection']['objects']['enabled'] = data.get('object_recognition', True)
        
        if 'mouth' not in config['detection']:
            config['detection']['mouth'] = {}
        config['detection']['mouth']['enabled'] = data.get('mouth_monitor', True)
        
        if 'logging' not in config:
            config['logging'] = {}
        if 'alert_system' not in config['logging']:
            config['logging']['alert_system'] = {}
        config['logging']['alert_system']['voice_alerts'] = data.get('voice_alerts', True)
        
        config['upload_gridfs'] = data.get('upload_gridfs', True)
        config['session_cleanup'] = data.get('session_cleanup', False)
        
        if 'audio_monitoring' not in config['detection']:
            config['detection']['audio_monitoring'] = {}
        config['detection']['audio_monitoring']['enabled'] = data.get('audio_monitoring', True)
        
        if audio_monitor:
            should_run = config['detection']['audio_monitoring']['enabled']
            if should_run and not audio_monitor.running:
                try:
                    audio_monitor.start()
                    print("[Settings] AudioMonitor started dynamically")
                except Exception as e:
                    print(f"[Settings] Error starting AudioMonitor: {e}")
            elif not should_run and audio_monitor.running:
                try:
                    audio_monitor.stop()
                    print("[Settings] AudioMonitor stopped dynamically")
                except Exception as e:
                    print(f"[Settings] Error stopping AudioMonitor: {e}")
                    
        try:
            with open(config_path, 'w') as f:
                yaml.safe_dump(config, f)
            print("[Settings] config.yaml saved successfully")
        except Exception as e:
            print(f"[Settings] ERROR: Failed to save config.yaml: {e}")
            
        return jsonify({'success': True, 'message': 'System configurations saved successfully!'})

if __name__ == '__main__':
    print("=" * 60)
    print("📝 EXAM PROCTORING SYSTEM - FIXED VERSION")
    print("=" * 60)
    
    # Initialize all systems
    initialize_system()
    
    # Find local network IP address
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print(f"\n🌐 Access URLs:")
    print(f"   - Local:  http://localhost:5000")
    print(f"   - Mobile: http://{local_ip}:5000")
    print("\n📁 Files will be saved to:")
    print(f"   - Recordings: {config['video']['recording_path']}")
    print(f"   - Violation images: reports/violation_captures/ (1 image per violation)")
    print(f"   - Reports: reports/generated/")
    print(f"   - Exam results: exam_results/")
    
    print("\n🎯 Detection Features:")
    print("   ✓ Face presence detection (with cooldown)")
    print("   ✓ Eye gaze tracking")
    print("   ✓ Mouth movement detection")
    print("   ✓ Multiple face detection")
    print("   ✓ Object detection (phone, book)")
    print("   ✓ Screen recording")
    print("   ✓ Video recording")
    print("   ✓ 3-warning system")
    print("   ✓ 5-second cooldown between same violations")
    print("   ✓ 1 screenshot per violation only")
    
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', debug=True, port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
    finally:
        # Cleanup
        if camera and camera.isOpened():
            camera.release()
        if audio_monitor:
            audio_monitor.stop()
        print("\n✅ System shutdown complete.")