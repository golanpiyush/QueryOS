"""
QueryOS Spinner - Loading Animation
"""
import sys
import time
import threading
import random

class Spinner:
    """Animated spinner for showing loading/searching progress"""
    
    # Different spinner animations
    spinners = [
        ["⡿", "⣟", "⣯", "⣷", "⣾", "⣽", "⣻", "⢿"],  # Braille dots
        ["⠄", "⠆", "⠇", "⠋", "⠙", "⠸", "⠰", "⠠"],  # Clock-like
        ["✶", "✸", "✹", "✺", "✹", "✷"],             # Stars
        ["◐", "◓", "◑", "◒"],                        # Quarter circles
        ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],  # Bars
        ["🔍", "🔎"]                                   # Search icons
    ]
    
    def __init__(self, text="Loading", delay=0.1, color="cyan"):
        """
        Initialize spinner
        
        Args:
            text (str): Text to display with spinner
            delay (float): Animation delay between frames
            color (str): Color of the spinner (cyan, green, yellow, red, magenta)
        """
        self.text = text
        self.busy = False
        self.delay = delay
        self.color = color
        self.spinner_generator = self.spinning_cursor()
        self.thread = None
        
        # Color codes
        self.colors = {
            'cyan': '\u001b[36;1m',
            'green': '\u001b[32;1m', 
            'yellow': '\u001b[33;1m',
            'red': '\u001b[31;1m',
            'magenta': '\u001b[35;1m',
            'blue': '\u001b[34;1m',
            'reset': '\u001b[0m'
        }
    
    def spinning_cursor(self):
        """Generate spinner frames"""
        spinner_set = random.choice(self.spinners)
        while True:
            for char in spinner_set:
                yield char
    
    def spinner_task(self):
        """Run the spinner animation"""
        color_code = self.colors.get(self.color, self.colors['cyan'])
        sys.stdout.write(color_code)
        
        while self.busy:
            # Clear line and write spinner with text
            sys.stdout.write(f"\r{self.text} {next(self.spinner_generator)}")
            sys.stdout.flush()
            time.sleep(self.delay)
        
        # Clear the line when done
        sys.stdout.write(f"\r{' ' * (len(self.text) + 3)}\r")
        sys.stdout.write(self.colors['reset'])
        sys.stdout.flush()
    
    def start(self):
        """Start the spinner"""
        if not self.busy:
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the spinner"""
        if self.busy:
            self.busy = False
            if self.thread:
                self.thread.join(timeout=0.5)
    
    def update_text(self, new_text):
        """Update spinner text while running"""
        self.text = new_text
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exception, value, tb):
        """Context manager exit"""
        self.stop()
        if exception is not None:
            return False


# Usage examples and helper functions
class SearchSpinner(Spinner):
    """Specialized spinner for search operations"""
    
    def __init__(self, query="", **kwargs):
        search_text = f"🔍 Searching for '{query}'" if query else "🔍 Searching"
        super().__init__(text=search_text, **kwargs)


class LoadingSpinner(Spinner):
    """Specialized spinner for loading operations"""
    
    def __init__(self, operation="", **kwargs):
        loading_text = f"⏳ Loading {operation}" if operation else "⏳ Loading"
        super().__init__(text=loading_text, **kwargs)


# Convenience function for quick spinner usage
def show_spinner(text="Processing", duration=None, color="cyan"):
    """
    Show a spinner for a specific duration
    
    Args:
        text (str): Text to display
        duration (float): Duration in seconds (None for manual control)
        color (str): Spinner color
    
    Returns:
        Spinner: The spinner instance for manual control if duration is None
    """
    spinner = Spinner(text=text, color=color)
    
    if duration:
        spinner.start()
        time.sleep(duration)
        spinner.stop()
    else:
        return spinner


# if __name__ == "__main__":
#     """Testing the spinner functionality"""
    
#     print("Testing different spinner types...\n")
    
#     # Test 1: Basic spinner with context manager
#     with Spinner("Processing data", color="green"):
#         time.sleep(3)
    
#     print("✅ Basic spinner test completed\n")
    
#     # Test 2: Search spinner
#     with SearchSpinner("config files"):
#         time.sleep(2)
    
#     print("✅ Search spinner test completed\n")
    
#     # Test 3: Loading spinner
#     with LoadingSpinner("file system"):
#         time.sleep(2)
    
#     print("✅ Loading spinner test completed\n")
    
#     # Test 4: Manual control
#     spinner = Spinner("Manual control test", color="magenta")
#     spinner.start()
#     time.sleep(2)
#     spinner.update_text("Updated text")
#     time.sleep(2)
#     spinner.stop()
    
#     print("✅ All tests completed!")