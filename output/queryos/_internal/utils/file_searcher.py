"""
QueryOS File Searcher
"""
import os
import time
from pathlib import Path
from typing import List, Dict
from config.settings import FILE_TYPES, PRIORITY_PATHS, MAX_SEARCH_RESULTS, MAX_DISPLAY_RESULTS, debug_print
from errors.error_handler import ErrorHandler

class FileSearcher:
    """Handle file searching operations"""
    
    def __init__(self):
        self.file_types = FILE_TYPES
        self.priority_paths = PRIORITY_PATHS
    
    def get_available_drives(self) -> List[str]:
        """Get list of available drives on Windows"""
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append(letter)
        return drives
    
    def search_files(self, search_params: Dict) -> List[Path]:
        """Search for files based on parsed parameters"""
        results = []
        drives_to_search = self._determine_search_drives(search_params)
        
        filename_pattern = search_params.get('filename', '').lower()
        file_type = search_params.get('file_type', '').lower()
        
        debug_print(f"🔍 Searching drives: {drives_to_search}")
        debug_print(f"📝 Looking for: {filename_pattern} (type: {file_type})")
        
        for drive in drives_to_search:
            try:
                self._search_in_directory(drive, filename_pattern, file_type, results)
                if len(results) >= MAX_SEARCH_RESULTS:
                    break
            except Exception as e:
                if not ErrorHandler.handle_search_error(e, drive):
                    continue
        
        # Sort results by relevance
        results.sort(key=lambda x: self._calculate_relevance(x, search_params), reverse=True)
        
        return results[:MAX_DISPLAY_RESULTS]
    
    def _determine_search_drives(self, search_params: Dict) -> List[str]:
        """Determine which drives to search based on parameters"""
        if search_params.get('drive'):
            drive_letter = search_params['drive'].upper()
            available_drives = self.get_available_drives()
            if drive_letter in available_drives:
                return [f"{drive_letter}:\\"]
        
        # Search all available drives
        return [f"{d}:\\" for d in self.get_available_drives()]
    
    def _search_in_directory(self, directory: str, filename_pattern: str, file_type: str, results: List[Path]):
        """Recursively search in directory with better error handling"""
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories and hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'System Volume Information', 
                    '$RECYCLE.BIN', 
                    'Windows',
                    'Program Files',
                    'Program Files (x86)',
                    'ProgramData',
                    'AppData'  # Skip most AppData to avoid clutter
                ]]
                
                # Special case: if searching specifically in AppData, allow it
                if 'appdata' in directory.lower():
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                        'System Volume Information', 
                        '$RECYCLE.BIN'
                    ]]
                
                for file in files:
                    try:
                        if self._matches_criteria(file, filename_pattern, file_type):
                            file_path = Path(root) / file
                            # Verify the file actually exists and is accessible
                            if file_path.exists():
                                results.append(file_path)
                                
                                if len(results) >= MAX_SEARCH_RESULTS:
                                    return
                    except (PermissionError, OSError):
                        continue  # Skip inaccessible files
                            
        except (PermissionError, OSError) as e:
            ErrorHandler.handle_search_error(e, directory)
        except Exception as e:
            ErrorHandler.log_error(e, f"FileSearcher._search_in_directory({directory})")
    
    def _matches_criteria(self, filename: str, pattern: str, file_type: str) -> bool:
        """Check if file matches search criteria with fuzzy matching"""
        filename_lower = filename.lower()
        
        # Check filename pattern with fuzzy matching
        if pattern:
            # If pattern contains spaces, treat as multiple keywords
            if ' ' in pattern:
                keywords = pattern.split()
                if not all(self._fuzzy_match(keyword, filename_lower) for keyword in keywords):
                    return False
            else:
                if not self._fuzzy_match(pattern, filename_lower):
                    return False
        
        # Check file type
        if file_type:
            if not filename_lower.endswith(f'.{file_type}'):
                return False
        
        return True
    
    def _fuzzy_match(self, pattern: str, text: str) -> bool:
        """Fuzzy matching that handles typos and partial matches"""
        pattern_lower = pattern.lower()
        text_lower = text.lower()
        
        # Exact match
        if pattern_lower in text_lower:
            return True
        
        # Handle common typos and variations
        # Remove duplicated characters (e.g., "immpossible" -> "impossible")
        pattern_dedupe = self._remove_duplicate_chars(pattern_lower)
        if pattern_dedupe in text_lower:
            return True
        
        # Check if most characters match (Levenshtein-like)
        if len(pattern_lower) > 3:
            return self._similarity_match(pattern_lower, text_lower, threshold=0.8)
        
        return False
    
    def _remove_duplicate_chars(self, text: str) -> str:
        """Remove consecutive duplicate characters"""
        result = []
        prev_char = None
        for char in text:
            if char != prev_char:
                result.append(char)
            prev_char = char
        return ''.join(result)
    
    def _similarity_match(self, pattern: str, text: str, threshold: float = 0.8) -> bool:
        """Check if pattern has enough similarity with any part of text"""
        pattern_len = len(pattern)
        
        # Check all substrings of text with same length as pattern
        for i in range(len(text) - pattern_len + 1):
            substring = text[i:i + pattern_len]
            
            # Calculate character match ratio
            matches = sum(1 for a, b in zip(pattern, substring) if a == b)
            similarity = matches / pattern_len
            
            if similarity >= threshold:
                return True
        
        return False
    
    def _calculate_relevance(self, file_path: Path, search_params: Dict) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        filename = file_path.name.lower()
        search_filename = search_params.get('filename', '').lower()
        
        # Exact filename match
        if search_filename and search_filename == filename:
            score += 10.0
        
        # Partial filename match
        if search_filename and search_filename in filename:
            score += 5.0
            # Bonus for matches at start of filename
            if filename.startswith(search_filename):
                score += 2.0
        
        # File type match
        if search_params.get('file_type') and filename.endswith(f".{search_params['file_type']}"):
            score += 3.0
        
        # Priority location bonus
        file_str = str(file_path).lower()
        for priority_path in self.priority_paths:
            if file_str.startswith(priority_path.lower()):
                score += 2.0
                break
        
        # Recent file bonus
        try:
            mtime = file_path.stat().st_mtime
            days_old = (time.time() - mtime) / (24 * 3600)
            if days_old < 1:  # Less than a day old
                score += 2.0
            elif days_old < 7:  # Less than a week old
                score += 1.0
            elif days_old < 30:  # Less than a month old
                score += 0.5
        except Exception:
            pass
        
        # File size considerations (prefer smaller files for code, larger for documents)
        try:
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            # Code files - prefer reasonable sizes
            if file_ext in self.file_types.get('code', []):
                if 1000 < file_size < 100000:  # 1KB to 100KB
                    score += 0.5
            
            # Document files - size doesn't matter as much
            elif file_ext in self.file_types.get('documents', []):
                score += 0.1
                
        except Exception:
            pass
        
        return score
    
    def get_file_type_category(self, file_path: Path) -> str:
        """Get the category of file based on extension"""
        file_ext = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if file_ext in extensions:
                return category
        
        return 'other'