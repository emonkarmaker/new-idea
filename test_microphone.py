"""
Microphone Test Utility
Test your microphone setup before using the main application
"""

import sounddevice as sd
import numpy as np
import time

def list_audio_devices():
    """List all available audio input devices"""
    print("\n" + "="*60)
    print("AVAILABLE AUDIO DEVICES")
    print("="*60)
    devices = sd.query_devices()
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"\nDevice {i}: {device['name']}")
            print(f"  - Input Channels: {device['max_input_channels']}")
            print(f"  - Sample Rate: {device['default_samplerate']} Hz")
            print(f"  - Host API: {sd.query_hostapis(device['hostapi'])['name']}")
    
    print("\n" + "="*60)

def test_microphone(device_id=None, duration=5):
    """Test microphone input levels"""
    print("\n" + "="*60)
    print(f"MICROPHONE TEST - {duration} seconds")
    print("="*60)
    print("\nSpeak into your microphone...")
    print("Watch for the audio level bars below.\n")
    
    RATE = 16000
    CHANNELS = 1
    
    def callback(indata, frames, time_info, status):
        if status:
            print(f"Status: {status}")
        
        # Calculate audio level
        level = np.abs(indata).mean()
        energy = np.sqrt(np.mean(indata**2))
        
        # Visual representation
        bars = int(min(level * 1000, 10))
        visual = "█" * bars + "░" * (10 - bars)
        
        print(f"\rLevel: {visual} | RMS: {energy:.4f} | Mean: {level:.4f}", end="", flush=True)
    
    try:
        if device_id is not None:
            stream = sd.InputStream(
                callback=callback,
                channels=CHANNELS,
                samplerate=RATE,
                device=device_id
            )
        else:
            stream = sd.InputStream(
                callback=callback,
                channels=CHANNELS,
                samplerate=RATE
            )
        
        with stream:
            time.sleep(duration)
        
        print("\n\n✓ Microphone test complete!")
        print("\nInterpretation:")
        print("  - RMS > 0.03: Good voice level")
        print("  - RMS 0.01-0.03: Acceptable, but speak louder or move closer")
        print("  - RMS < 0.01: Too quiet, increase microphone gain or get closer")
        print("  - Bars should show 5-8 bars when speaking")
        
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if microphone is connected")
        print("  2. Check microphone permissions in system settings")
        print("  3. Try a different device ID")

def test_vad_threshold():
    """Test Voice Activity Detection with current settings"""
    print("\n" + "="*60)
    print("VOICE ACTIVITY DETECTION TEST")
    print("="*60)
    print("\nThis will test if your voice crosses the VAD threshold.")
    print("Speak a few Arabic words or verses...\n")
    
    RATE = 16000
    CHANNELS = 1
    ENERGY_THRESHOLD = 0.03
    ZCR_THRESHOLD = 0.1
    
    speech_detected_count = 0
    total_chunks = 0
    
    def calculate_zcr(audio_chunk):
        """Calculate Zero Crossing Rate"""
        signs = np.sign(audio_chunk)
        zcr = np.sum(np.abs(np.diff(signs))) / (2 * len(audio_chunk))
        return zcr
    
    def callback(indata, frames, time_info, status):
        nonlocal speech_detected_count, total_chunks
        
        total_chunks += 1
        chunk = indata.flatten()
        
        # Normalize
        if np.max(np.abs(chunk)) > 0:
            chunk = chunk / np.max(np.abs(chunk))
        
        # Calculate features
        energy = np.sqrt(np.mean(chunk**2))
        zcr = calculate_zcr(chunk)
        
        # Speech detection
        is_speech = (energy > ENERGY_THRESHOLD) and (zcr > ZCR_THRESHOLD)
        
        if is_speech:
            speech_detected_count += 1
            status_icon = "✓ SPEECH"
            color = "🟢"
        else:
            status_icon = "✗ Silence"
            color = "⚪"
        
        print(f"\r{color} {status_icon} | Energy: {energy:.4f} (>{ENERGY_THRESHOLD}) | ZCR: {zcr:.4f} (>{ZCR_THRESHOLD})", end="", flush=True)
    
    try:
        stream = sd.InputStream(
            callback=callback,
            channels=CHANNELS,
            samplerate=RATE,
            blocksize=int(RATE * 0.1)
        )
        
        with stream:
            time.sleep(10)
        
        detection_rate = (speech_detected_count / total_chunks) * 100
        
        print(f"\n\n✓ VAD Test Complete!")
        print(f"\nResults:")
        print(f"  - Total chunks: {total_chunks}")
        print(f"  - Speech detected: {speech_detected_count} chunks")
        print(f"  - Detection rate: {detection_rate:.1f}%")
        print(f"\nInterpretation:")
        if detection_rate > 50:
            print(f"  ✓ EXCELLENT - Voice is clearly detected")
        elif detection_rate > 30:
            print(f"  ⚠ GOOD - Voice detected but may need adjustment")
        elif detection_rate > 10:
            print(f"  ⚠ FAIR - Increase microphone volume or move closer")
        else:
            print(f"  ❌ POOR - Voice not detected well, check setup")
        
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("AUDIO SETUP TEST UTILITY")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. List available audio devices")
        print("  2. Test microphone (5 seconds)")
        print("  3. Test Voice Activity Detection (10 seconds)")
        print("  4. Test specific device")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            list_audio_devices()
        
        elif choice == "2":
            test_microphone(duration=5)
        
        elif choice == "3":
            test_vad_threshold()
        
        elif choice == "4":
            list_audio_devices()
            device_id = input("\nEnter device ID to test: ").strip()
            try:
                device_id = int(device_id)
                test_microphone(device_id=device_id, duration=5)
            except ValueError:
                print("Invalid device ID")
        
        elif choice == "5":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option, try again")

if __name__ == "__main__":
    main()
