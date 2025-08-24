"""
QueryOS User Interface
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
from config.settings import debug_print, info_print, MAX_FILE_SIZE_DISPLAY, MAX_DISPLAY_LINES
from errors.error_handler import ErrorHandler

class UserInterface:
    """Handle all user interface operations"""
    
    def show_welcome_message(self):
        """Display welcome message"""
        if debug_print == print:  # Debug mode
            info_print("\n🚀 QueryOS - AI Desktop Search Assistant")
            info_print("Available commands:")
            info_print("  • 'voice' - Switch to voice mode")
            info_print("  • 'text' - Switch to text mode")
            info_print("  • 'drives' - Show available drives")
            info_print("  • 'quit' or 'exit' - Exit application")
            info_print("\nSearch examples:")
            info_print("  • 'find me apimain.py'")
            info_print("  • 'in D drive find config.json and open it'")
            info_print("  • 'find Excel file with budget from June 2023'")
        else:
            info_print("🚀 QueryOS - Ready to search")
    
    def display_search_processing(self, query, search_params):
        """Display search processing information"""
        debug_print(f"\n🔍 Processing: {query}")
        debug_print(f"📋 Search parameters: {search_params}")
    
    def display_search_progress(self, drives_to_search, filename_pattern, file_type):
        """Display search progress information"""
        debug_print(f"🔍 Searching drives: {drives_to_search}")
        debug_print(f"📝 Looking for: {filename_pattern} (type: {file_type})")
    
    def display_search_results(self, results):
        """Display search results"""
        if not results:
            message = "❌ No files found matching your criteria."
            info_print(message)
            return False
        
        info_print(f"\n✅ Found {len(results)} files:")
        for i, result in enumerate(results, 1):
            info_print(f"{i:2d}. {result}")
        
        return True
    
    def display_file_content(self, file_path: Path, highlight_terms=None):
        """Display file content with highlighting"""
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE_DISPLAY:
                info_print(f"📄 File too large to display: {file_path}")
                return False
            
            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                return False
            
            if debug_print == print:  # Debug mode - show full details
                info_print(f"\n📄 File: {file_path}")
                info_print(f"📊 Size: {file_size} bytes")
                info_print(f"📅 Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}")
                info_print("=" * 60)
                
                # Display content with line numbers
                lines = content.split('\n')[:MAX_DISPLAY_LINES]
                for i, line in enumerate(lines, 1):
                    display_line = self._highlight_line(line, highlight_terms)
                    info_print(f"{i:3d}: {display_line}")
                
                if len(content.split('\n')) > MAX_DISPLAY_LINES:
                    info_print(f"\n... ({len(content.split('\n')) - MAX_DISPLAY_LINES} more lines)")
                
                info_print("=" * 60)
            else:
                # Minimal mode - just show file found
                info_print(f"📄 Found: {file_path.name}")
            
            return True
            
        except Exception as e:
            ErrorHandler.handle_file_error(e, file_path)
            return False
    
    def _read_file_content(self, file_path: Path):
        """Read file content with proper encoding handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                ErrorHandler.handle_file_error(e, file_path)
                return None
        except Exception as e:
            ErrorHandler.handle_file_error(e, file_path)
            return None
    
    def _highlight_line(self, line, highlight_terms):
        """Apply simple highlighting to line"""
        if not highlight_terms:
            return line
        
        display_line = line
        for term in highlight_terms:
            if term and term.lower() in line.lower():
                # Simple highlighting with asterisks
                display_line = display_line.replace(term, f"***{term.upper()}***")
        
        return display_line
    
    def open_file_in_explorer(self, file_path: Path):
        """Open file location in Windows Explorer"""
        try:
            # Convert to absolute path and handle spaces/special characters properly
            abs_path = str(file_path.resolve())
            
            # Use subprocess with shell=True to handle paths with spaces
            command = f'explorer /select,"{abs_path}"'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                info_print(f"📂 Opened in Explorer: {file_path.name}")
                return True
            else:
                # Fallback: just open the parent directory
                parent_dir = str(file_path.parent.resolve())
                fallback_command = f'explorer "{parent_dir}"'
                subprocess.run(fallback_command, shell=True)
                info_print(f"📂 Opened parent folder: {file_path.parent}")
                return True
                
        except Exception as e:
            ErrorHandler.handle_system_error(e)
            return False
    
    def open_file_with_default_app(self, file_path: Path):
        """Open file with default application"""
        try:
            # Use absolute path and handle spaces properly
            abs_path = str(file_path.resolve())
            
            # Use os.startfile which handles paths with spaces better
            os.startfile(abs_path)
            info_print(f"🚀 Opened file: {file_path.name}")
            return True
        except Exception as e:
            ErrorHandler.handle_system_error(e)
            return False
    
    def handle_file_action(self, selected_file, action):
        """Handle file actions based on user choice"""
        if action == '1':  # Open file
            return self.open_file_with_default_app(selected_file)
        elif action == '2':  # Show in explorer
            return self.open_file_in_explorer(selected_file)
        else:
            return True  # Continue
    
    def show_no_voice_warning(self):
        """Show warning when voice features are unavailable"""
        debug_print("Voice features unavailable. Install: pip install speechrecognition pyttsx3 pyaudio")