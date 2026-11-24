import pyaudio
import numpy as np
import threading
from collections import deque
import whisper
import time

class AudioMonitor:
    def __init__(self, config):
        self.config = config['detection']['audio_monitoring']
        self.sample_rate = self.config['sample_rate']
        self.chunk_size = 512  # 32ms chunks for low latency
        self.energy_threshold = self.config['energy_threshold']
        self.zcr_threshold = self.config['zcr_threshold']
        self.running = False
        self.audio_buffer = deque(maxlen=15)  # 480ms buffer
        self.alert_system = None
        self.alert_logger = None
        self.on_voice_detected = None
        
        # Audio alert cooldown to prevent warning flooding
        self.last_voice_alert_time = 0
        self.voice_alert_cooldown = 10.0  # seconds
        
        if self.config['whisper_enabled']:
            self.whisper_model = whisper.load_model(self.config['whisper_model'])
        
    def start(self):
        """Start audio monitoring thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop audio monitoring"""
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1)
            
    def _run(self):
        """Main audio processing loop with robust error handling"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
        except Exception as e:
            print(f"[AudioMonitor] ERROR: Could not open microphone device: {e}")
            print("[AudioMonitor] Voice detection disabled because no recording device was found.")
            self.running = False
            return
            
        try:
            while self.running:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio = np.frombuffer(data, dtype=np.int16)
                    self.audio_buffer.append(audio)
                    
                    if self._is_voice(audio):
                        self._handle_voice_detection()
                except Exception as e:
                    print(f"[AudioMonitor] Error processing audio frame: {e}")
                    time.sleep(0.1)
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            try:
                p.terminate()
            except:
                pass
    
    def _is_voice(self, audio):
        """Ultra-fast voice detection"""
        audio_norm = audio / 32768.0
        
        # 1. Energy detection
        energy = np.mean(audio_norm**2)
        if energy < self.energy_threshold:
            return False
            
        # 2. Zero-crossing rate
        zcr = np.mean(np.abs(np.diff(np.sign(audio_norm))))
        if zcr > self.zcr_threshold:
            return False
            
        return True
    
    def _handle_voice_detection(self):
        """Process detected voice with cooldown control"""
        current_time = time.time()
        if current_time - self.last_voice_alert_time < self.voice_alert_cooldown:
            return
        self.last_voice_alert_time = current_time
        
        if self.alert_system:
            self.alert_system.speak_alert("VOICE_DETECTED")
            
        if self.alert_logger:
            self.alert_logger.log_alert("VOICE_DETECTED", "Voice activity detected")
            
        if self.on_voice_detected:
            try:
                self.on_voice_detected("Voice activity detected")
            except Exception as e:
                print(f"[AudioMonitor] Error calling on_voice_detected callback: {e}")
            
        if self.config['whisper_enabled']:
            self._process_with_whisper()
    
    def _process_with_whisper(self):
        """Optional Whisper processing"""
        try:
            audio = np.concatenate(self.audio_buffer)
            result = self.whisper_model.transcribe(
                audio.astype(np.float32) / 32768.0,
                fp16=False,
                language='en'
            )
            
            text = result['text'].strip().lower()
            if any(word in text for word in ['help', 'answer', 'whisper']):
                if self.alert_system:
                    self.alert_system.speak_alert("SPEECH_VIOLATION")
                if self.on_voice_detected:
                    try:
                        self.on_voice_detected(f"Speech violation: '{text}'")
                    except Exception as e:
                        print(f"[AudioMonitor] Error calling on_voice_detected: {e}")
                    
        except Exception as e:
            if self.alert_logger:
                self.alert_logger.log_alert("WHISPER_ERROR", str(e))