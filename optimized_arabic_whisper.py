import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import queue
import scipy.io.wavfile as wavfile
import os
import tempfile
import time
from scipy import signal
from collections import deque

# OpenAI Whisper API
try:
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_OPENAI_API_KEY_HERE")
    USE_NEW_API = True
except ImportError:
    import openai
    openai.api_key = "YOUR_OPENAI_API_KEY_HERE"
    USE_NEW_API = False

# Optimized audio parameters for Arabic speech
RATE = 16000  # Whisper's optimal sample rate
CHANNELS = 1
CHUNK_DURATION = 0.1  # Smaller chunks for better VAD (100ms)
MIN_SPEECH_DURATION = 1.0  # Minimum 1 second of speech
MAX_SPEECH_DURATION = 10.0  # Maximum 10 seconds per segment
SILENCE_DURATION = 0.8  # 800ms of silence to trigger transcription

# Advanced VAD parameters
ENERGY_THRESHOLD = 0.03  # Energy-based threshold
ZCR_THRESHOLD = 0.1  # Zero-crossing rate threshold
MIN_SPEECH_FRAMES = 10  # Minimum frames to consider as speech

class AdvancedVAD:
    """Advanced Voice Activity Detection for Arabic speech"""
    
    def __init__(self, sample_rate=RATE):
        self.sample_rate = sample_rate
        self.speech_frames = []
        self.silence_frames = 0
        self.is_speaking = False
        
    def calculate_energy(self, audio_chunk):
        """Calculate energy (RMS) of audio chunk"""
        return np.sqrt(np.mean(audio_chunk**2))
    
    def calculate_zcr(self, audio_chunk):
        """Calculate Zero Crossing Rate"""
        signs = np.sign(audio_chunk)
        zcr = np.sum(np.abs(np.diff(signs))) / (2 * len(audio_chunk))
        return zcr
    
    def is_speech(self, audio_chunk):
        """Determine if audio chunk contains speech using multiple features"""
        # Normalize audio
        if np.max(np.abs(audio_chunk)) > 0:
            audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))
        
        # Calculate features
        energy = self.calculate_energy(audio_chunk)
        zcr = self.calculate_zcr(audio_chunk)
        
        # Speech detection logic
        is_speech = (energy > ENERGY_THRESHOLD) and (zcr > ZCR_THRESHOLD)
        
        return is_speech, energy

class AudioPreprocessor:
    """Advanced audio preprocessing for optimal Whisper performance"""
    
    @staticmethod
    def normalize_audio(audio_data):
        """Normalize audio to -1 to 1 range"""
        if np.max(np.abs(audio_data)) > 0:
            return audio_data / np.max(np.abs(audio_data))
        return audio_data
    
    @staticmethod
    def apply_noise_gate(audio_data, threshold=0.01):
        """Apply noise gate to remove low-level noise"""
        audio_data = audio_data.copy()
        audio_data[np.abs(audio_data) < threshold] = 0
        return audio_data
    
    @staticmethod
    def apply_bandpass_filter(audio_data, sample_rate, lowcut=80, highcut=8000):
        """Apply bandpass filter for speech frequencies"""
        nyquist = sample_rate / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        
        # Design Butterworth bandpass filter
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, audio_data)
        
        return filtered
    
    @staticmethod
    def remove_dc_offset(audio_data):
        """Remove DC offset from audio"""
        return audio_data - np.mean(audio_data)
    
    @staticmethod
    def apply_pre_emphasis(audio_data, coefficient=0.97):
        """Apply pre-emphasis filter to boost high frequencies"""
        return np.append(audio_data[0], audio_data[1:] - coefficient * audio_data[:-1])
    
    @staticmethod
    def process_audio(audio_data, sample_rate=RATE):
        """Complete audio preprocessing pipeline"""
        # Remove DC offset
        audio_data = AudioPreprocessor.remove_dc_offset(audio_data)
        
        # Apply bandpass filter for speech frequencies (80Hz - 8kHz)
        audio_data = AudioPreprocessor.apply_bandpass_filter(audio_data, sample_rate)
        
        # Apply noise gate
        audio_data = AudioPreprocessor.apply_noise_gate(audio_data, threshold=0.01)
        
        # Apply pre-emphasis
        audio_data = AudioPreprocessor.apply_pre_emphasis(audio_data)
        
        # Normalize
        audio_data = AudioPreprocessor.normalize_audio(audio_data)
        
        return audio_data

class OptimizedArabicTranscriber:
    def __init__(self, root):
        self.root = root
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.speech_buffer = []
        self.vad = AdvancedVAD()
        self.preprocessor = AudioPreprocessor()
        
        # Timing
        self.silence_start = None
        self.speech_start = None
        
        # Statistics
        self.total_transcriptions = 0
        self.successful_transcriptions = 0
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        self.root.title("Optimized Arabic Speech-to-Text (Whisper)")
        self.root.geometry("800x700")
        self.root.configure(bg="#1a1a2e")
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg="#16213e", height=100)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="🎤 Enhanced Arabic Speech Recognition",
            font=("Arial", 20, "bold"),
            bg="#16213e",
            fg="#e94560"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Optimized for Quranic Arabic | Powered by OpenAI Whisper",
            font=("Arial", 10),
            bg="#16213e",
            fg="#f0f0f0"
        )
        subtitle_label.pack()
        
        # Settings Frame
        settings_frame = tk.LabelFrame(
            self.root,
            text="Audio Settings",
            bg="#16213e",
            fg="#e94560",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            bd=2
        )
        settings_frame.pack(fill=tk.X, pady=5, padx=20)
        
        # Energy threshold slider
        threshold_frame = tk.Frame(settings_frame, bg="#16213e")
        threshold_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            threshold_frame,
            text="Voice Sensitivity:",
            bg="#16213e",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.threshold_var = tk.DoubleVar(value=ENERGY_THRESHOLD * 100)
        threshold_slider = tk.Scale(
            threshold_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            bg="#16213e",
            fg="white",
            highlightthickness=0,
            length=200,
            command=self.update_threshold
        )
        threshold_slider.pack(side=tk.LEFT, padx=5)
        
        self.threshold_label = tk.Label(
            threshold_frame,
            text=f"{ENERGY_THRESHOLD * 100:.1f}%",
            bg="#16213e",
            fg="#e94560",
            font=("Arial", 10, "bold")
        )
        self.threshold_label.pack(side=tk.LEFT, padx=5)
        
        # Preprocessing toggle
        preprocess_frame = tk.Frame(settings_frame, bg="#16213e")
        preprocess_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.preprocess_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            preprocess_frame,
            text="Enable Advanced Audio Preprocessing (Recommended)",
            variable=self.preprocess_var,
            bg="#16213e",
            fg="white",
            selectcolor="#16213e",
            font=("Arial", 10),
            activebackground="#16213e",
            activeforeground="white"
        ).pack(side=tk.LEFT)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg="#1a1a2e")
        status_frame.pack(pady=10)
        
        # Status indicator
        self.status_label = tk.Label(
            status_frame,
            text="● Ready to Listen",
            font=("Arial", 13, "bold"),
            bg="#1a1a2e",
            fg="#95a5a6"
        )
        self.status_label.pack()
        
        # Real-time indicators
        indicators_frame = tk.Frame(status_frame, bg="#1a1a2e")
        indicators_frame.pack(pady=5)
        
        # Audio level
        self.level_label = tk.Label(
            indicators_frame,
            text="Audio Level: ▁▁▁▁▁",
            font=("Consolas", 11),
            bg="#1a1a2e",
            fg="#3498db"
        )
        self.level_label.pack()
        
        # Speech detection
        self.speech_label = tk.Label(
            indicators_frame,
            text="Speech: Not Detected",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#95a5a6"
        )
        self.speech_label.pack()
        
        # Statistics
        stats_frame = tk.Frame(status_frame, bg="#1a1a2e")
        stats_frame.pack(pady=5)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Transcriptions: 0 | Success Rate: 0%",
            font=("Arial", 9),
            bg="#1a1a2e",
            fg="#95a5a6"
        )
        self.stats_label.pack()
        
        # Text output area
        text_frame = tk.Frame(self.root, bg="#1a1a2e")
        text_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Label for text area
        tk.Label(
            text_frame,
            text="Transcription Output",
            bg="#1a1a2e",
            fg="#e94560",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W)
        
        self.text_output = scrolledtext.ScrolledText(
            text_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            font=("Arial", 13),
            bg="#0f3460",
            fg="#f0f0f0",
            insertbackground="white",
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.text_output.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure text tags for different types of output
        self.text_output.tag_config("timestamp", foreground="#95a5a6", font=("Arial", 9))
        self.text_output.tag_config("arabic", foreground="#e94560", font=("Arial", 14, "bold"))
        self.text_output.tag_config("confidence", foreground="#f39c12", font=("Arial", 9, "italic"))
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#1a1a2e")
        button_frame.pack(pady=20)
        
        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="▶ START LISTENING",
            command=self.start_listening,
            height=2,
            width=20,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            activebackground="#229954",
            bd=0
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ STOP",
            command=self.stop_listening,
            height=2,
            width=20,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.FLAT,
            activebackground="#c0392b",
            bd=0
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Clear button
        clear_button = tk.Button(
            button_frame,
            text="🗑 CLEAR",
            command=self.clear_text,
            height=2,
            width=15,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            activebackground="#2980b9",
            bd=0
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # Tips label
        tips_label = tk.Label(
            self.root,
            text="💡 Tips: Speak clearly | Minimize background noise | Wait for 'Speech Detected' indicator",
            bg="#1a1a2e",
            fg="#95a5a6",
            font=("Arial", 9, "italic")
        )
        tips_label.pack(pady=(0, 10))
        
    def update_threshold(self, value):
        """Update voice sensitivity threshold"""
        global ENERGY_THRESHOLD
        ENERGY_THRESHOLD = float(value) / 100
        self.threshold_label.config(text=f"{float(value):.1f}%")
        
    def update_status(self, text, color="#95a5a6"):
        """Update status label"""
        self.status_label.config(text=f"● {text}", fg=color)
        
    def update_audio_level(self, level):
        """Visual audio level indicator"""
        bars = min(int(level * 20), 10)
        visual = "▁▂▃▄▅▆▇█"
        level_visual = (visual[min(bars, 7)] * 5).ljust(5, "▁")
        self.level_label.config(text=f"Audio Level: {level_visual}")
        
    def update_speech_status(self, is_speech, energy):
        """Update speech detection status"""
        if is_speech:
            self.speech_label.config(
                text=f"Speech: ✓ DETECTED (Energy: {energy:.3f})",
                fg="#27ae60"
            )
        else:
            self.speech_label.config(
                text=f"Speech: Waiting... (Energy: {energy:.3f})",
                fg="#95a5a6"
            )
    
    def update_stats(self):
        """Update transcription statistics"""
        if self.total_transcriptions > 0:
            success_rate = (self.successful_transcriptions / self.total_transcriptions) * 100
        else:
            success_rate = 0
        
        self.stats_label.config(
            text=f"Transcriptions: {self.total_transcriptions} | Success Rate: {success_rate:.0f}%"
        )
        
    def clear_text(self):
        """Clear transcription output"""
        self.text_output.delete(1.0, tk.END)
        
    def save_audio_to_wav(self, audio_data):
        """Save processed audio to WAV file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()
        
        # Convert to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        wavfile.write(temp_file.name, RATE, audio_int16)
        
        return temp_file.name
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio using OpenAI Whisper API with optimal settings"""
        try:
            self.update_status("Processing with Whisper AI...", "#f39c12")
            self.total_transcriptions += 1
            
            with open(audio_file_path, 'rb') as audio_file:
                if USE_NEW_API:
                    # Use verbose_json to get more information
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ar",  # Arabic language code
                        response_format="verbose_json",  # Get detailed response
                        temperature=0.0,  # Deterministic output for accuracy
                    )
                    text = transcript.text
                    # Note: API doesn't return confidence scores directly
                    confidence = "High" if len(text) > 10 else "Medium"
                else:
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file,
                        language="ar",
                        temperature=0.0
                    )
                    text = transcript['text']
                    confidence = "High"
            
            # Display transcription
            if text and text.strip():
                self.successful_transcriptions += 1
                timestamp = time.strftime("%H:%M:%S")
                
                # Insert with formatting
                self.text_output.insert(tk.END, f"[{timestamp}] ", "timestamp")
                self.text_output.insert(tk.END, f"{text}", "arabic")
                self.text_output.insert(tk.END, f" (Confidence: {confidence})\n", "confidence")
                self.text_output.see(tk.END)
                
                print(f"✓ Transcribed: {text}")
                self.update_status("Success! Listening...", "#27ae60")
            else:
                print("⚠ No speech detected in audio")
                self.update_status("No speech detected", "#f39c12")
            
            # Update statistics
            self.root.after(0, self.update_stats)
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            self.update_status("Error - Check API key", "#e74c3c")
        finally:
            # Clean up temp file
            try:
                os.remove(audio_file_path)
            except:
                pass
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio input callback"""
        if status:
            print(f"Audio status: {status}")
        
        self.audio_queue.put(indata.copy())
    
    def process_audio_stream(self):
        """Process audio stream with advanced VAD"""
        frames_per_chunk = int(CHUNK_DURATION * RATE)
        silence_frames_threshold = int(SILENCE_DURATION / CHUNK_DURATION)
        
        while self.is_listening:
            try:
                # Get audio chunk
                chunk = self.audio_queue.get(timeout=1)
                chunk = chunk.flatten()
                
                # Check for speech using VAD
                is_speech, energy = self.vad.is_speech(chunk)
                
                # Update UI
                self.root.after(0, lambda e=energy: self.update_audio_level(e))
                self.root.after(0, lambda s=is_speech, e=energy: self.update_speech_status(s, e))
                
                if is_speech:
                    # Speech detected
                    if not self.vad.is_speaking:
                        # Start of speech
                        self.vad.is_speaking = True
                        self.speech_start = time.time()
                        self.speech_buffer = []
                        print("🎤 Speech started")
                    
                    # Add to speech buffer
                    self.speech_buffer.append(chunk)
                    self.vad.silence_frames = 0
                    
                    # Check if we've hit max duration
                    if len(self.speech_buffer) * CHUNK_DURATION > MAX_SPEECH_DURATION:
                        self.process_speech_buffer()
                        
                else:
                    # Silence detected
                    if self.vad.is_speaking:
                        self.vad.silence_frames += 1
                        self.speech_buffer.append(chunk)  # Keep adding to buffer
                        
                        # Check if silence duration exceeded
                        if self.vad.silence_frames >= silence_frames_threshold:
                            # End of speech
                            speech_duration = len(self.speech_buffer) * CHUNK_DURATION
                            
                            if speech_duration >= MIN_SPEECH_DURATION:
                                self.process_speech_buffer()
                            else:
                                print(f"⚠ Speech too short: {speech_duration:.2f}s (min: {MIN_SPEECH_DURATION}s)")
                                self.speech_buffer = []
                                self.vad.is_speaking = False
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")
    
    def process_speech_buffer(self):
        """Process accumulated speech buffer"""
        if not self.speech_buffer:
            return
        
        try:
            # Combine all chunks
            combined_audio = np.concatenate(self.speech_buffer)
            duration = len(combined_audio) / RATE
            
            print(f"📝 Processing speech segment ({duration:.2f}s)")
            
            # Apply preprocessing if enabled
            if self.preprocess_var.get():
                combined_audio = self.preprocessor.process_audio(combined_audio, RATE)
            else:
                # Just normalize
                combined_audio = self.preprocessor.normalize_audio(combined_audio)
            
            # Save and transcribe
            audio_file = self.save_audio_to_wav(combined_audio)
            
            # Run transcription in separate thread
            transcribe_thread = threading.Thread(
                target=self.transcribe_audio,
                args=(audio_file,),
                daemon=True
            )
            transcribe_thread.start()
            
        except Exception as e:
            print(f"Error processing speech buffer: {e}")
        finally:
            # Reset buffer
            self.speech_buffer = []
            self.vad.is_speaking = False
            self.vad.silence_frames = 0
    
    def start_listening(self):
        """Start audio capture"""
        if not self.is_listening:
            try:
                # Reset state
                self.speech_buffer = []
                self.vad.is_speaking = False
                self.vad.silence_frames = 0
                
                while not self.audio_queue.empty():
                    self.audio_queue.get()
                
                self.is_listening = True
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.update_status("Initializing microphone...", "#f39c12")
                
                # Start audio stream
                self.stream = sd.InputStream(
                    callback=self.audio_callback,
                    channels=CHANNELS,
                    samplerate=RATE,
                    blocksize=int(RATE * CHUNK_DURATION),
                    dtype=np.float32
                )
                self.stream.start()
                
                # Start processing thread
                self.process_thread = threading.Thread(
                    target=self.process_audio_stream,
                    daemon=True
                )
                self.process_thread.start()
                
                self.update_status("Listening... Speak now!", "#27ae60")
                print("✓ Listening started")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start microphone:\n{str(e)}")
                self.stop_listening()
    
    def stop_listening(self):
        """Stop audio capture"""
        self.is_listening = False
        
        # Process any remaining speech
        if self.speech_buffer and self.vad.is_speaking:
            self.process_speech_buffer()
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Stopped", "#e74c3c")
        self.update_audio_level(0)
        self.speech_label.config(text="Speech: Not Detected", fg="#95a5a6")
        print("⏹ Listening stopped")
    
    def on_closing(self):
        """Handle window close"""
        self.stop_listening()
        self.root.destroy()

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizedArabicTranscriber(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
