"""
QueryOS Input Handling
"""
from config.settings import debug_print, info_print
from errors.error_handler import ErrorHandler

class InputHandler:
    """Handle all user input processing"""
    
    def __init__(self):
        self.voice_mode = False
    
    def get_user_input(self, prompt="🔍 Search query (or 'help'): ", voice_handler=None):
        """Get input from user (text or voice)"""
        try:
            if self.voice_mode and voice_handler and voice_handler.is_available():
                debug_print("🎤 Voice mode active - say your command...")
                query = voice_handler.listen_for_voice()
                return query
            else:
                return input(prompt).strip()
        except KeyboardInterrupt:
            ErrorHandler.handle_keyboard_interrupt()
        except Exception as e:
            ErrorHandler.log_error(e, "InputHandler.get_user_input")
            return ""
    
    def process_special_commands(self, query, voice_handler=None):
        """Process special system commands"""
        if not query:
            return "continue"
        
        query_lower = query.lower()
        
        if query_lower in ['quit', 'exit', 'bye']:
            info_print("👋 Goodbye!")
            return "exit"
        
        elif query_lower == 'voice':
            if voice_handler and voice_handler.is_available():
                self.voice_mode = True
                if voice_handler.tts_engine:
                    voice_handler.speak("Voice mode activated")
                else:
                    info_print("🎤 Voice mode activated")
            else:
                info_print("❌ Voice features not available")
            return "continue"
        
        elif query_lower == 'text':
            self.voice_mode = False
            info_print("📝 Text mode activated")
            return "continue"
        
        elif query_lower == 'drives':
            from utils.file_searcher import FileSearcher
            searcher = FileSearcher()
            drives = searcher.get_available_drives()
            info_print(f"💾 Available drives: {drives}")
            if voice_handler and voice_handler.tts_engine:
                voice_handler.speak(f"Available drives: {', '.join(drives)}")
            return "continue"
        
        elif query_lower in ['help', '?']:
            self.show_help()
            return "continue"
        
        return "process"
    
    def show_help(self):
        """Display help information"""
        if debug_print == print:  # Debug mode
            info_print("\n📖 QueryOS Help:")
            info_print("Available commands:")
            info_print("  • 'voice' - Switch to voice mode")
            info_print("  • 'text' - Switch to text mode") 
            info_print("  • 'drives' - Show available drives")
            info_print("  • 'quit' or 'exit' - Exit application")
            info_print("\nSearch examples:")
            info_print("  • 'find me apimain.py'")
            info_print("  • 'in D drive find config.json and open it'")
            info_print("  • 'find Excel file with budget from June 2023'")
            info_print("\nJust describe what you're looking for in natural language!")
        else:
            info_print("\n📖 Help:")
            info_print("Describe what file you're looking for.")
            info_print("Commands: voice, text, drives, quit")
    
    def get_file_selection(self, max_results):
        """Get file selection from user"""
        try:
            choice = input(f"\nSelect file (1-{max_results}) or 0 to cancel: ").strip()
            if choice and choice.isdigit():
                idx = int(choice)
                if idx == 0:
                    return None
                elif 1 <= idx <= max_results:
                    return idx - 1
            return None
        except (ValueError, KeyboardInterrupt):
            return None
    
    def get_action_choice(self):
        """Get action choice from user"""
        try:
            if debug_print == print:  # Debug mode
                info_print("\n🎯 Options:")
                info_print("1. Open file")
                info_print("2. Show in Explorer") 
                info_print("3. Continue searching")
                choice = input("Choose action (1-3): ").strip()
            else:
                choice = input("\nOpen file? (y/n/e for explorer): ").strip().lower()
                if choice == 'y':
                    return '1'
                elif choice == 'e':
                    return '2' 
                else:
                    return '3'
            return choice
        except (ValueError, KeyboardInterrupt):
            return '3'
    
    def is_voice_mode(self):
        """Check if currently in voice mode"""
        return self.voice_mode