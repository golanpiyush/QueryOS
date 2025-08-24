"""
QueryOS Error Handling
"""
import sys
import traceback
from datetime import datetime
from config.settings import debug_print, info_print

class ErrorHandler:
    """Handle and log errors throughout the application"""
    
    @staticmethod
    def handle_voice_error(error):
        """Handle voice recognition errors"""
        error_type = type(error).__name__
        
        if "WaitTimeoutError" in error_type:
            debug_print("⏱️ No speech detected")
            return None
        elif "UnknownValueError" in error_type:
            debug_print("❓ Could not understand audio")
            return None
        elif "RequestError" in error_type:
            info_print(f"❌ Speech recognition error: {error}")
            return None
        else:
            debug_print(f"❌ Voice error: {error}")
            return None
    
    @staticmethod
    def handle_file_error(error, file_path=None):
        """Handle file operation errors"""
        error_type = type(error).__name__
        
        if "PermissionError" in error_type:
            debug_print(f"🔒 Permission denied: {file_path}")
            return False
        elif "FileNotFoundError" in error_type:
            debug_print(f"📄 File not found: {file_path}")
            return False
        elif "UnicodeDecodeError" in error_type:
            debug_print(f"📄 Cannot decode file (binary?): {file_path}")
            return False
        else:
            debug_print(f"❌ File error: {error}")
            return False
    
    @staticmethod
    def handle_search_error(error, location=None):
        """Handle search operation errors"""
        error_type = type(error).__name__
        
        if "PermissionError" in error_type:
            debug_print(f"🔒 Cannot access: {location}")
            return False
        elif "OSError" in error_type:
            debug_print(f"💾 OS error in: {location}")
            return False
        else:
            debug_print(f"❌ Search error: {error}")
            return False
    
    @staticmethod
    def handle_ai_error(error):
        """Handle AI API errors"""
        debug_print(f"🤖 AI parsing error: {error}")
        return {"filename": "", "action": "find"}
    
    @staticmethod
    def handle_system_error(error):
        """Handle system/subprocess errors"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        if "CalledProcessError" in error_type:
            if "explorer" in error_msg.lower():
                debug_print(f"❌ Explorer command failed - trying alternative method")
            else:
                info_print(f"❌ System command failed: {error}")
        elif "FileNotFoundError" in error_type:
            debug_print(f"❌ System file not found: {error}")
        elif "PermissionError" in error_type:
            debug_print(f"🔒 Permission denied for system operation: {error}")
        else:
            debug_print(f"❌ System error: {error}")
    
    @staticmethod
    def handle_fatal_error(error):
        """Handle fatal application errors"""
        info_print(f"❌ Fatal error: {error}")
        if debug_print == print:  # If debug mode is on
            traceback.print_exc()
        sys.exit(1)
    
    @staticmethod
    def log_error(error, context="Unknown"):
        """Log error with timestamp and context"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        debug_print(f"[{timestamp}] ERROR in {context}: {error}")
    
    @staticmethod
    def validate_windows_system():
        """Validate that we're running on Windows"""
        import os
        if os.name != 'nt':
            info_print("❌ QueryOS is designed for Windows systems only.")
            sys.exit(1)
    
    @staticmethod
    def handle_keyboard_interrupt():
        """Handle user interruption gracefully"""
        info_print("\n👋 Goodbye!")
        sys.exit(0)