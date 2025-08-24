#!/usr/bin/env python3
"""
QueryOS - AI Desktop Search Assistant
Main executable file

Usage: python bin/queryos.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from errors.error_handler import ErrorHandler
from classes._queryOS_AI_desktop import QueryOS_AI

def main():
    """Main entry point for QueryOS"""
    # Validate Windows system
    ErrorHandler.validate_windows_system()
    
    try:
        # Initialize and run the application
        assistant = QueryOS_AI()
        assistant.run()
        
    except KeyboardInterrupt:
        ErrorHandler.handle_keyboard_interrupt()
    except Exception as e:
        ErrorHandler.handle_fatal_error(e)

if __name__ == "__main__":
    main()