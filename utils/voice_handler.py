"""
QueryOS Voice Recognition and Text-to-Speech Handler
"""
from config.settings import VOICE_TIMEOUT, VOICE_PHRASE_LIMIT, TTS_RATE, debug_print
from errors.error_handler import ErrorHandler

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    sr = None
    pyttsx3 = None

class VoiceHandler:
    """Handle voice recognition and text-to-speech"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.available = False
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.tts_engine = pyttsx3.init()
                self.setup_voice()
                self.available = True
                debug_print("🎤 Voice recognition enabled")
            except Exception as e:
                ErrorHandler.log_error(e, "VoiceHandler.__init__")
                self.available = False
        else:
            debug_print("Voice features unavailable. Install: pip install speechrecognition pyttsx3 pyaudio")
    
    def setup_voice(self):
        """Configure voice recognition and text-to-speech"""
        if not self.available:
            return
        
        try:
            # Configure TTS
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_engine.setProperty('rate', TTS_RATE)
            
            # Calibrate microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                
        except Exception as e:
            ErrorHandler.log_error(e, "VoiceHandler.setup_voice")
            self.available = False
    
    def speak(self, text: str):
        """Text-to-speech output"""
        if self.available and self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                ErrorHandler.log_error(e, "VoiceHandler.speak")
        debug_print(f"🔊 {text}")
    
    def listen_for_voice(self):
        """Listen for voice input"""
        if not self.available:
            return None
        
        try:
            with self.microphone as source:
                debug_print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(
                    source, 
                    timeout=VOICE_TIMEOUT, 
                    phrase_time_limit=VOICE_PHRASE_LIMIT
                )
            
            debug_print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            debug_print(f"📝 Heard: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return ErrorHandler.handle_voice_error(sr.WaitTimeoutError())
        except sr.UnknownValueError:
            return ErrorHandler.handle_voice_error(sr.UnknownValueError())
        except sr.RequestError as e:
            return ErrorHandler.handle_voice_error(e)
        except Exception as e:
            ErrorHandler.log_error(e, "VoiceHandler.listen_for_voice")
            return None
    
    def is_available(self):
        """Check if voice features are available"""
        return self.available