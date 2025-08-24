"""
Enhanced QueryOS Voice Recognition and Text-to-Speech Handler
Uses multiple recognition engines for better accuracy without hardcoded terms
"""
from enum import Enum
import time
import threading
import tempfile
import os
from typing import Optional, List
from config.settings import VOICE_TIMEOUT, VOICE_PHRASE_LIMIT, TTS_RATE, debug_print
from errors.error_handler import ErrorHandler

# Try to import multiple recognition libraries
ENGINES_AVAILABLE = {}

# Voice Engine Priority Configuration
class VoiceEngine(Enum):
    """Voice recognition engines in priority order"""
    AZURE = "azure.cognitiveservices.speech"
    WHISPER = "openai_whisper"
    GOOGLE = "speech_recognition.google"
    BING = "speech_recognition.bing"
    SPHINX = "speech_recognition.sphinx"

    
try:
    import speech_recognition as sr
    ENGINES_AVAILABLE['speechrecognition'] = True
except ImportError:
    sr = None
    ENGINES_AVAILABLE['speechrecognition'] = False

try:
    import openai_whisper as whisper # pyright: ignore[reportMissingImports]
    ENGINES_AVAILABLE['whisper'] = True
except ImportError:
    try:
        import whisper
        ENGINES_AVAILABLE['whisper'] = True
    except ImportError:
        whisper = None
        ENGINES_AVAILABLE['whisper'] = False

try:
    import azure.cognitiveservices.speech as speechsdk
    ENGINES_AVAILABLE['azure'] = True
except ImportError:
    speechsdk = None
    ENGINES_AVAILABLE['azure'] = False

try:
    import pyttsx3
    ENGINES_AVAILABLE['tts'] = True
except ImportError:
    pyttsx3 = None
    ENGINES_AVAILABLE['tts'] = False

class VoiceHandler:
    """Enhanced voice handler with multiple recognition engines"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.whisper_model = None
        self.azure_recognizer = None
        self.available = False
        self._tts_lock = threading.Lock()
        self.recognition_engines = []
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize all available recognition engines"""
        engines_ready = []
        
        # Initialize SpeechRecognition (Google, Bing, etc.)
        if ENGINES_AVAILABLE['speechrecognition']:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self._configure_speechrecognition()
                self.recognition_engines.extend(['google', 'bing', 'sphinx'])
                engines_ready.append("SpeechRecognition")
            except Exception as e:
                debug_print(f"❌ SpeechRecognition init failed: {e}")
        
        # Initialize Whisper (OpenAI's model - very accurate)
        if ENGINES_AVAILABLE['whisper']:
            try:
                debug_print("🔄 Loading Whisper model (this may take a moment)...")
                self.whisper_model = whisper.load_model("base")
                self.recognition_engines.append('whisper')
                engines_ready.append("OpenAI Whisper")
            except Exception as e:
                debug_print(f"❌ Whisper init failed: {e}")
        
        # Initialize Azure Speech (if credentials available)
        if ENGINES_AVAILABLE['azure']:
            try:
                # Check for Azure credentials in environment
                speech_key = os.getenv('AZURE_SPEECH_KEY')
                service_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
                
                if speech_key:
                    speech_config = speechsdk.SpeechConfig(
                        subscription=speech_key, 
                        region=service_region
                    )
                    speech_config.speech_recognition_language = "en-US"
                    
                    audio_config = speechsdk.audio.AudioConfig(
                        use_default_microphone=True
                    )
                    
                    self.azure_recognizer = speechsdk.SpeechRecognizer(
                        speech_config=speech_config,
                        audio_config=audio_config
                    )
                    
                    self.recognition_engines.append('azure')
                    engines_ready.append("Azure Speech")
                else:
                    debug_print("💡 Azure Speech available but no credentials found")
            except Exception as e:
                debug_print(f"❌ Azure Speech init failed: {e}")
        
        # Initialize TTS
        if ENGINES_AVAILABLE['tts']:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                engines_ready.append("TTS")
            except Exception as e:
                debug_print(f"❌ TTS init failed: {e}")
        
        self.available = len(self.recognition_engines) > 0
        
        if self.available:
            debug_print(f"✅ Voice engines ready: {', '.join(engines_ready)}")
            debug_print(f"🎤 Recognition engines: {self.recognition_engines}")
        else:
            debug_print("❌ No voice recognition engines available")
            self._show_installation_help()
    
    def _configure_speechrecognition(self):
        """Configure SpeechRecognition settings"""
        if not self.recognizer:
            return
        
        try:
            # Calibrate microphone
            debug_print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Configure recognition parameters for better accuracy
            self.recognizer.energy_threshold = 4000  # Higher threshold for cleaner audio
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5
            
            debug_print("✅ SpeechRecognition configured")
            
        except Exception as e:
            debug_print(f"⚠️ SpeechRecognition config warning: {e}")
    
    def _configure_tts(self):
        """Configure text-to-speech settings"""
        if not self.tts_engine:
            return
        
        try:
            # Get and set voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Find best English voice
                english_voice = None
                for voice in voices:
                    if any(lang in voice.id.lower() for lang in ['en-us', 'en-gb', 'english']):
                        english_voice = voice
                        break
                
                if english_voice:
                    self.tts_engine.setProperty('voice', english_voice.id)
                    debug_print(f"🔊 Using voice: {english_voice.name}")
            
            # Set speech rate
            self.tts_engine.setProperty('rate', TTS_RATE)
            self.tts_engine.setProperty('volume', 0.8)
            
        except Exception as e:
            debug_print(f"⚠️ TTS config warning: {e}")
    
    def listen_for_voice(self) -> Optional[str]:
        """Listen for voice input using multiple engines for best results"""
        if not self.available:
            debug_print("❌ Voice recognition not available")
            return None
        
        debug_print("🎤 Listening... (speak clearly)")
        
        # Try each recognition engine in order of preference
        results = []
        audio_data = None
        
        # Capture audio first
        if self.recognizer and self.microphone:
            try:
                with self.microphone as source:
                    audio_data = self.recognizer.listen(
                        source,
                        timeout=VOICE_TIMEOUT,
                        phrase_time_limit=VOICE_PHRASE_LIMIT
                    )
                debug_print("🔄 Audio captured, processing...")
            except Exception as e:
                debug_print(f"❌ Audio capture failed: {e}")
                return None
        
        # Try Whisper first (most accurate for technical terms)
        if 'whisper' in self.recognition_engines and audio_data:
            result = self._try_whisper_recognition(audio_data)
            if result:
                results.append(('whisper', result))
        
        # Try Azure Speech
        if 'azure' in self.recognition_engines:
            result = self._try_azure_recognition()
            if result:
                results.append(('azure', result))
        
        # Try Google Speech
        if 'google' in self.recognition_engines and audio_data:
            result = self._try_google_recognition(audio_data)
            if result:
                results.append(('google', result))
        
        # Try Bing Speech
        if 'bing' in self.recognition_engines and audio_data:
            result = self._try_bing_recognition(audio_data)
            if result:
                results.append(('bing', result))
        
        # Try offline Sphinx as fallback
        if 'sphinx' in self.recognition_engines and audio_data:
            result = self._try_sphinx_recognition(audio_data)
            if result:
                results.append(('sphinx', result))
        
        # Return best result
        if results:
            # Prefer Whisper or Azure results, then Google, then others
            engine_priority = ['whisper', 'azure', 'google', 'bing', 'sphinx']
            
            for engine in engine_priority:
                for result_engine, text in results:
                    if result_engine == engine:
                        debug_print(f"📝 Best result from {engine}: '{text}'")
                        return text.strip()
            
            # If no priority match, return first result
            engine, text = results[0]
            debug_print(f"📝 Using result from {engine}: '{text}'")
            return text.strip()
        
        debug_print("❌ No recognition results from any engine")
        return None
    
    def _try_whisper_recognition(self, audio_data) -> Optional[str]:
        """Try recognition with OpenAI Whisper"""
        if not self.whisper_model:
            return None
        
        try:
            # Convert audio to temporary WAV file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data.get_wav_data())
                tmp_file_path = tmp_file.name
            
            try:
                result = self.whisper_model.transcribe(tmp_file_path)
                text = result["text"].strip()
                if text:
                    return text
            finally:
                os.unlink(tmp_file_path)  # Clean up temp file
                
        except Exception as e:
            debug_print(f"⚠️ Whisper recognition failed: {e}")
        
        return None
    
    def _try_azure_recognition(self) -> Optional[str]:
        """Try recognition with Azure Speech"""
        if not self.azure_recognizer:
            return None
        
        try:
            result = self.azure_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text.strip()
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return None
            else:
                debug_print(f"Azure recognition failed: {result.reason}")
                
        except Exception as e:
            debug_print(f"⚠️ Azure recognition failed: {e}")
        
        return None
    
    def _try_google_recognition(self, audio_data) -> Optional[str]:
        """Try recognition with Google Speech"""
        if not self.recognizer:
            return None
        
        try:
            return self.recognizer.recognize_google(audio_data)
        except Exception as e:
            debug_print(f"⚠️ Google recognition failed: {e}")
        
        return None
    
    def _try_bing_recognition(self, audio_data) -> Optional[str]:
        """Try recognition with Bing Speech"""
        if not self.recognizer:
            return None
        
        try:
            # Note: Bing requires API key
            bing_key = os.getenv('BING_SPEECH_API_KEY')
            if bing_key:
                return self.recognizer.recognize_bing(audio_data, key=bing_key)
        except Exception as e:
            debug_print(f"⚠️ Bing recognition failed: {e}")
        
        return None
    
    def _try_sphinx_recognition(self, audio_data) -> Optional[str]:
        """Try recognition with offline Sphinx"""
        if not self.recognizer:
            return None
        
        try:
            return self.recognizer.recognize_sphinx(audio_data)
        except Exception as e:
            debug_print(f"⚠️ Sphinx recognition failed: {e}")
        
        return None
    
    def speak(self, text: str):
        """Text-to-speech output (non-blocking)"""
        if not text or not text.strip():
            return
        
        debug_print(f"🔊 Speaking: {text}")
        
        if self.tts_engine:
            # Run TTS in separate thread to avoid blocking
            tts_thread = threading.Thread(target=self._speak_sync, args=(text,))
            tts_thread.daemon = True
            tts_thread.start()
    
    def _speak_sync(self, text: str):
        """Synchronous TTS (for threading)"""
        try:
            with self._tts_lock:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        except Exception as e:
            ErrorHandler.log_error(e, "EnhancedVoiceHandler._speak_sync")
    
    def is_available(self) -> bool:
        """Check if voice features are available"""
        return self.available
    
    def get_available_engines(self) -> List[str]:
        """Get list of available recognition engines"""
        return self.recognition_engines.copy()
    
    def test_voice_system(self) -> bool:
        """Test the voice system"""
        if not self.available:
            debug_print("❌ Voice system not available for testing")
            return False
        
        debug_print("🧪 Testing voice system...")
        debug_print(f"🎤 Available engines: {self.recognition_engines}")
        
        # Test TTS
        if self.tts_engine:
            self.speak("Voice system ready for testing")
        
        # Test recognition
        debug_print("🎤 Say something to test recognition...")
        result = self.listen_for_voice()
        
        if result:
            debug_print(f"✅ Voice system working! Recognized: '{result}'")
            return True
        else:
            debug_print("⚠️ Voice recognition test failed")
            return False
    
    def _show_installation_help(self):
        """Show help for installing voice recognition libraries"""
        debug_print("\n💡 To enable better voice recognition, install:")
        debug_print("   pip install openai-whisper  # Best accuracy")
        debug_print("   pip install azure-cognitiveservices-speech  # Enterprise grade")
        debug_print("   pip install speechrecognition pyttsx3 pyaudio  # Basic support")
        debug_print("\n🔑 For Azure Speech, set environment variables:")
        debug_print("   set AZURE_SPEECH_KEY=your_key")
        debug_print("   set AZURE_SPEECH_REGION=your_region")
    
    def cleanup(self):
        """Clean up voice resources"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()
            if hasattr(self, 'whisper_model'):
                del self.whisper_model
        except Exception as e:
            debug_print(f"⚠️ Cleanup warning: {e}")