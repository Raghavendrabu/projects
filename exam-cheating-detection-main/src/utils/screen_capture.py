import cv2
import numpy as np
from mss import mss
from datetime import datetime
import os
import threading
import time

class ScreenRecorder:
    def __init__(self, config):
        self.config = config['screen']
        self.monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # Default values
        self.writer = None
        self.filename = None
        self.frame_count = 0
        self.recording_path = os.path.abspath(config['video']['recording_path'])
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = None
        
    def _initialize_sct(self):
        """Initialize MSS in the thread where it will be used"""
        self.sct = mss()
        monitors = self.sct.monitors
        if len(monitors) > self.config['monitor_index'] + 1:  # +1 because monitor 0 is all screens
            self.monitor = monitors[self.config['monitor_index'] + 1]
        else:
            self.monitor = monitors[1]  # Default to first monitor
        
    def start_recording(self):
        if not os.path.exists(self.recording_path):
            os.makedirs(self.recording_path)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(self.recording_path, f"screen_{timestamp}.mp4")
        
        # Initialize SCT to get monitor dimensions
        self._initialize_sct()
        
        # Try H264 (avc1) first for HTML5 native browser playability, fallback to mp4v if unavailable
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            self.writer = cv2.VideoWriter(
                self.filename,
                fourcc,
                self.config['fps'],
                (self.monitor['width'], self.monitor['height'])
            )
            if not self.writer.isOpened():
                raise Exception("avc1 writer failed to open")
            print("🎥 ScreenRecorder: Successfully initialized using 'avc1' (H.264) codec.")
        except Exception as e:
            print(f"⚠️ ScreenRecorder: 'avc1' (H.264) codec failed: {e}. Falling back to 'mp4v'...")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(
                self.filename,
                fourcc,
                self.config['fps'],
                (self.monitor['width'], self.monitor['height'])
            )
        
        # Start capture thread
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()
        
    def _capture_loop(self):
        """Main capture loop running in separate thread with robust Pillow fallback"""
        self._initialize_sct()  # Initialize MSS in this thread
        fallback_to_pillow = False
        
        while not self.stop_event.is_set():
            try:
                frame = None
                with self.lock:
                    if not fallback_to_pillow:
                        try:
                            screenshot = self.sct.grab(self.monitor)
                            frame = np.array(screenshot)
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        except Exception as mss_err:
                            print(f"[ScreenRecorder] MSS capture error: {mss_err}. Falling back to Pillow.")
                            fallback_to_pillow = True
                            
                    if fallback_to_pillow:
                        # Fallback using Pillow ImageGrab (perfectly reliable on Windows)
                        from PIL import ImageGrab
                        screenshot = ImageGrab.grab()
                        frame = np.array(screenshot)
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        
                    if frame is not None and self.writer:
                        # Ensure dimensions match monitor resolution
                        if frame.shape[1] != self.monitor['width'] or frame.shape[0] != self.monitor['height']:
                            frame = cv2.resize(frame, (self.monitor['width'], self.monitor['height']))
                        self.writer.write(frame)
                        self.frame_count += 1
            except Exception as loop_err:
                print(f"[ScreenRecorder] Capture loop warning: {loop_err}")
                
            time.sleep(1.0 / self.config['fps'])
    
    def stop_recording(self):
        """Stop recording and clean up"""
        self.stop_event.set()
        if self.thread:
            self.thread.join()
            self.thread = None
            
        if self.writer:
            self.writer.release()
            self.writer = None
            
        return {
            'filename': self.filename,
            'frame_count': self.frame_count,
            'duration': self.frame_count / self.config['fps']
        }