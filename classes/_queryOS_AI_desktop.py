"""
QueryOS Main AIDesktopSearch Class
"""
from config.settings import MESSAGES, debug_print, info_print
from errors.error_handler import ErrorHandler
from utils.voice_handler import VoiceHandler
from utils.file_searcher import FileSearcher
from utils.query_parser import QueryParser
from user.user_interface import UserInterface
from inputs.input_handler import InputHandler

class QueryOS_AI:
    """Main AI Desktop Search class"""
    
    def __init__(self):
        # Initialize components
        self.voice_handler = VoiceHandler()
        self.file_searcher = FileSearcher()
        self.query_parser = QueryParser()
        self.ui = UserInterface()
        self.input_handler = InputHandler()
        
        # Display initialization messages
        info_print(MESSAGES['welcome'])
        
        if self.voice_handler.is_available():
            info_print(MESSAGES['voice_enabled'])
        else:
            self.ui.show_no_voice_warning()
        
        info_print(MESSAGES['drives_ready'])
    
    def process_search_command(self, query: str):
        """Process a search command"""
        # Parse the query
        search_params = self.query_parser.parse_search_query(query)
        
        # Display processing info
        self.ui.display_search_processing(query, search_params)
        
        # Search for files
        results = self.file_searcher.search_files(search_params)
        
        # Display results
        if not self.ui.display_search_results(results):
            if self.voice_handler.is_available():
                # self.voice_handler.speak("No files found matching your criteria")
                pass
            return
        
        # Handle results based on count and user preferences
        self._handle_search_results(results, search_params)
        
        # Voice feedback
        # if self.voice_handler.is_available():
        #     self.voice_handler.speak(f"Found {len(results)} files matching your search")
    
    def _handle_search_results(self, results, search_params):
        """Handle search results based on count and parameters"""
        if len(results) == 1 or search_params.get('filename'):
            # Single result or specific filename - show content and handle action
            selected_file = results[0]
            debug_print(f"\n📖 Displaying content of: {selected_file}")
            
            # Extract keywords for highlighting
            keywords = self._extract_keywords(search_params)
            
            # Display file content
            self.ui.display_file_content(selected_file, keywords)
            
            # Handle action
            action = search_params.get('action', 'find')
            if action == 'open':
                self.ui.open_file_with_default_app(selected_file)
            else:
                # Ask user what to do
                choice = self.input_handler.get_action_choice()
                self.ui.handle_file_action(selected_file, choice)
        else:
            # Multiple results - let user choose
            self._handle_multiple_results(results)
    
    def _extract_keywords(self, search_params):
        """Extract keywords for highlighting from search parameters"""
        keywords = []
        
        if search_params.get('content_keywords'):
            keywords.extend(search_params['content_keywords'])
        
        if search_params.get('filename'):
            # Split filename into words for highlighting
            filename_words = search_params['filename'].split()
            keywords.extend(filename_words)
        
        return [k for k in keywords if k and len(k) > 2]  # Filter out short keywords
    
    def _handle_multiple_results(self, results):
        """Handle multiple search results"""
        try:
            choice_idx = self.input_handler.get_file_selection(len(results))
            
            if choice_idx is not None:
                selected_file = results[choice_idx]
                self.ui.display_file_content(selected_file)
                
                action_choice = self.input_handler.get_action_choice()
                self.ui.handle_file_action(selected_file, action_choice)
            else:
                debug_print("❌ No file selected")
                
        except Exception as e:
            ErrorHandler.log_error(e, "AIDesktopSearch._handle_multiple_results")
    
    def run(self):
        """Main application loop"""
        # Show welcome message
        self.ui.show_welcome_message()
        
        while True:
            try:
                # Get user input
                query = self.input_handler.get_user_input(voice_handler=self.voice_handler)
                
                if not query:
                    continue
                
                # Process special commands
                command_result = self.input_handler.process_special_commands(query, self.voice_handler)
                
                if command_result == "exit":
                    break
                elif command_result == "continue":
                    continue
                elif command_result == "process":
                    # Process search command
                    self.process_search_command(query)
                
            except KeyboardInterrupt:
                ErrorHandler.handle_keyboard_interrupt()
            except Exception as e:
                ErrorHandler.log_error(e, "AIDesktopSearch.run")
                info_print("❌ An error occurred. Please try again.")
        
        info_print("👋 Thanks for using QueryOS!")