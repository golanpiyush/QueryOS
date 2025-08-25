"""
Simplified QueryOS Voice Recognition and Text-to-Speech Handler
Uses only speech_recognition and pyttsx3 for simplicity
"""
import time
import threading
from typing import Optional
from config.settings import VOICE_TIMEOUT, VOICE_PHRASE_LIMIT, TTS_RATE, debug_print
from errors.error_handler import ErrorHandler

# Try to import required libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    TTS_AVAILABLE = False

class VoiceHandler:
    """Simplified voice handler using only pyttsx3 and speech_recognition"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.available = False
        self._tts_lock = threading.Lock()
        
        self._initialize()
    
    def _initialize(self):
        """Initialize speech recognition and TTS"""
        success_count = 0
        
        # Initialize Speech Recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self._configure_recognition()
                success_count += 1
                debug_print("✅ Speech Recognition initialized")
            except Exception as e:
                debug_print(f"❌ Speech Recognition init failed: {e}")
        else:
            debug_print("❌ speech_recognition library not available")
        
        # Initialize TTS
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                success_count += 1
                debug_print("✅ Text-to-Speech initialized")
            except Exception as e:
                debug_print(f"❌ TTS init failed: {e}")
        else:
            debug_print("❌ pyttsx3 library not available")
        
        self.available = (self.recognizer is not None)
        
        if self.available:
            debug_print("🎤 Voice system ready")
        else:
            debug_print("❌ Voice system not available")
            self._show_installation_help()
    
    def _configure_recognition(self):
        """Configure speech recognition settings"""
        if not self.recognizer or not self.microphone:
            return
        
        try:
            # Calibrate microphone for ambient noise
            debug_print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Configure recognition parameters
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5
            
            debug_print("✅ Microphone calibrated")
            
        except Exception as e:
            debug_print(f"⚠️ Microphone calibration warning: {e}")
    
    def _configure_tts(self):
        """Configure text-to-speech settings"""
        if not self.tts_engine:
            return
        
        try:
            # Set speech rate
            self.tts_engine.setProperty('rate', TTS_RATE)
            self.tts_engine.setProperty('volume', 0.8)
            
            # Try to find and set English voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                english_voice = None
                for voice in voices:
                    if any(lang in voice.id.lower() for lang in ['en-us', 'en-gb', 'english']):
                        english_voice = voice
                        break
                
                if english_voice:
                    self.tts_engine.setProperty('voice', english_voice.id)
                    debug_print(f"🔊 Using voice: {english_voice.name}")
            
        except Exception as e:
            debug_print(f"⚠️ TTS configuration warning: {e}")
    
    def listen_for_voice(self) -> Optional[str]:
        """Listen for voice input and convert to text"""
        if not self.available:
            debug_print("❌ Voice recognition not available")
            return None
        
        try:
            debug_print("🎤 Listening... (speak clearly)")
            
            # Listen for audio
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=VOICE_TIMEOUT,
                    phrase_time_limit=VOICE_PHRASE_LIMIT
                )
            
            debug_print("🔄 Processing speech...")
            
            # Try to recognize speech using Google's free service
            try:
                text = self.recognizer.recognize_google(audio)
                debug_print(f"📝 Recognized: '{text}'")
                return text.strip()
            
            except sr.UnknownValueError:
                debug_print("❌ Could not understand audio")
                return None
            
            except sr.RequestError as e:
                debug_print(f"❌ Speech recognition service error: {e}")
                
                # Try offline recognition as fallback
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    debug_print(f"📝 Offline recognition: '{text}'")
                    return text.strip()
                except:
                    debug_print("❌ Offline recognition also failed")
                    return None
        
        except sr.WaitTimeoutError:
            debug_print("⏰ Listening timeout - no speech detected")
            return None
        
        except Exception as e:
            debug_print(f"❌ Voice recognition error: {e}")
            ErrorHandler.log_error(e, "VoiceHandler.listen_for_voice")
            return None
    
    def speak(self, text: str):
        """Convert text to speech (non-blocking)"""
        if not text or not text.strip():
            return
        
        if not self.tts_engine:
            debug_print("❌ TTS not available")
            return
        
        debug_print(f"🔊 Speaking: {text}")
        
        # Run TTS in separate thread to avoid blocking
        tts_thread = threading.Thread(target=self._speak_sync, args=(text,))
        tts_thread.daemon = True
        tts_thread.start()
    
    def _speak_sync(self, text: str):
        """Synchronous TTS implementation (for threading)"""
        try:
            with self._tts_lock:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        except Exception as e:
            debug_print(f"❌ TTS error: {e}")
            ErrorHandler.log_error(e, "VoiceHandler._speak_sync")
    
    def is_available(self) -> bool:
        """Check if voice recognition is available"""
        return self.available
    
    def test_voice_system(self) -> bool:
        """Test the voice system"""
        if not self.available:
            debug_print("❌ Voice system not available for testing")
            return False
        
        debug_print("🧪 Testing voice system...")
        
        # Test TTS
        if self.tts_engine:
            self.speak("Voice system ready for testing")
            time.sleep(1)  # Give TTS time to start
        
        # Test recognition
        debug_print("🎤 Say something to test recognition (you have 5 seconds)...")
        result = self.listen_for_voice()
        
        if result:
            debug_print(f"✅ Voice system working! You said: '{result}'")
            self.speak(f"I heard you say: {result}")
            return True
        else:
            debug_print("⚠️ Voice recognition test failed")
            self.speak("Voice recognition test failed")
            return False
    
    def _show_installation_help(self):
        """Show installation instructions"""
        debug_print("\n💡 To enable voice features, install:")
        debug_print("   pip install speechrecognition")
        debug_print("   pip install pyttsx3")
        debug_print("   pip install pyaudio")
        debug_print("\n🔧 If you get PyAudio errors on Windows:")
        debug_print("   pip install pipwin")
        debug_print("   pipwin install pyaudio")
    
    def cleanup(self):
        """Clean up voice resources"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()
        except Exception as e:
            debug_print(f"⚠️ Cleanup warning: {e}")