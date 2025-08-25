"""
QueryOS File Searcher with Spinner Integration
"""
import os
import time
from pathlib import Path
from typing import List, Dict
from config.settings import FILE_TYPES, PRIORITY_PATHS, MAX_SEARCH_RESULTS, MAX_DISPLAY_RESULTS, debug_print
from errors.error_handler import ErrorHandler
from .loading_spinners import Spinner, SearchSpinner

class FileSearcher:
    """Handle file and folder searching operations with visual progress indicators"""
    
    def __init__(self):
        self.file_types = FILE_TYPES
        self.priority_paths = PRIORITY_PATHS
    
    def get_available_drives(self) -> List[str]:
        """Get list of available drives on Windows with loading animation"""
        with Spinner("💾 Scanning available drives", color="yellow", delay=0.15):
            drives = []
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(letter)
            # Small delay to show the spinner briefly
            time.sleep(0.5)
        return drives
    
    def search_files(self, search_params: Dict) -> List[Path]:
        """Search for files and folders based on parsed parameters with spinner animation"""
        results = []
        drives_to_search = self._determine_search_drives(search_params)
        
        filename_pattern = search_params.get('filename', '').lower()
        file_type = search_params.get('file_type', '').lower()
        search_type = search_params.get('search_type', 'both')  # 'files', 'folders', or 'both'
        
        # Create search query string for spinner
        search_query = filename_pattern
        if file_type:
            search_query += f" ({file_type} files)"
        elif search_type == 'folders':
            search_query += " (folders)"
        
        debug_print(f"🔍 Searching drives: {drives_to_search}")
        debug_print(f"📝 Looking for: {filename_pattern} (type: {file_type}, search_type: {search_type})")
        
        # Use spinner during search operation
        spinner = SearchSpinner(search_query, color="green")
        spinner.start()
        
        try:
            for i, drive in enumerate(drives_to_search):
                try:
                    # Update spinner text to show current drive being searched
                    drive_letter = drive.split(':')[0]
                    progress = f"({i+1}/{len(drives_to_search)})"
                    spinner.update_text(f"🔍 Searching drive {drive_letter}: {progress} for '{search_query}'")
                    
                    self._search_in_directory(drive, filename_pattern, file_type, results, spinner, search_type)
                    
                    if len(results) >= MAX_SEARCH_RESULTS:
                        break
                        
                except Exception as e:
                    if not ErrorHandler.handle_search_error(e, drive):
                        continue
            
            # Update spinner to show processing results
            if results:
                spinner.update_text(f"📊 Processing {len(results)} results for '{search_query}'")
                time.sleep(0.8)  # Brief pause to show processing message
                
                # Sort results by relevance (folders first if searching for folders)
                results.sort(key=lambda x: self._calculate_relevance(x, search_params), reverse=True)
            else:
                spinner.update_text(f"❌ No results found for '{search_query}'")
                time.sleep(1.0)
                
        finally:
            spinner.stop()
        
        return results[:MAX_DISPLAY_RESULTS]
    
    def search_files_with_detailed_progress(self, search_params: Dict) -> List[Path]:
        """Alternative search method with more detailed progress updates"""
        results = []
        drives_to_search = self._determine_search_drives(search_params)
        
        filename_pattern = search_params.get('filename', '').lower()
        file_type = search_params.get('file_type', '').lower()
        search_type = search_params.get('search_type', 'both')
        
        search_query = filename_pattern
        if file_type:
            search_query += f" ({file_type} files)"
        elif search_type == 'folders':
            search_query += " (folders)"
        
        # Manual spinner control for detailed progress
        spinner = Spinner(f"🔍 Initializing search for '{search_query}'", color="cyan")
        spinner.start()
        
        try:
            total_files_scanned = 0
            
            for drive_idx, drive in enumerate(drives_to_search):
                try:
                    drive_letter = drive.split(':')[0]
                    spinner.update_text(f"🔍 [{drive_idx+1}/{len(drives_to_search)}] Scanning {drive_letter}: drive...")
                    
                    drive_results, files_scanned = self._search_in_directory_with_count(
                        drive, filename_pattern, file_type, results, spinner, search_type
                    )
                    
                    total_files_scanned += files_scanned
                    results.extend(drive_results)
                    
                    # Update with current progress
                    item_type = "folders" if search_type == 'folders' else "items"
                    spinner.update_text(
                        f"🔍 Found {len(results)} {item_type}, scanned {total_files_scanned} items"
                    )
                    
                    if len(results) >= MAX_SEARCH_RESULTS:
                        spinner.update_text(f"🔍 Reached max results limit ({MAX_SEARCH_RESULTS})")
                        time.sleep(0.5)
                        break
                        
                except Exception as e:
                    ErrorHandler.handle_search_error(e, drive)
                    continue
            
            # Final processing
            if results:
                spinner.update_text(f"📊 Ranking {len(results)} results by relevance...")
                time.sleep(0.5)
                results.sort(key=lambda x: self._calculate_relevance(x, search_params), reverse=True)
                
                spinner.update_text(f"✅ Search complete! Found {len(results)} matches")
                time.sleep(1.0)
            else:
                spinner.update_text(f"❌ No matches found after scanning {total_files_scanned} items")
                time.sleep(1.5)
                
        finally:
            spinner.stop()
        
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
    
    def _search_in_directory(self, directory: str, filename_pattern: str, file_type: str, 
                           results: List[Path], spinner: Spinner = None, search_type: str = 'both'):
        """Recursively search in directory with spinner updates for files and/or folders"""
        try:
            for root, dirs, files in os.walk(directory):
                # Update spinner with current directory being searched (if in debug mode)
                if spinner and debug_print == print:  # Only show detailed path in debug mode
                    current_dir = os.path.basename(root) or root
                    if len(current_dir) > 30:
                        current_dir = current_dir[:27] + "..."
                    spinner.update_text(f"🔍 Scanning: {current_dir}")
                
                # Search in folders/directories if requested
                if search_type in ['folders', 'both']:
                    for dir_name in dirs:
                        if self._matches_criteria(dir_name, filename_pattern, '', is_folder=True):
                            dir_path = Path(root) / dir_name
                            if dir_path.exists():
                                results.append(dir_path)
                                
                                # Update spinner when we find matches
                                if spinner and len(results) % 3 == 0:  # Update every 3 matches for folders
                                    folder_word = "folder" if len(results) == 1 else "folders"
                                    spinner.update_text(f"📁 Found {len(results)} {folder_word} so far...")
                                
                                if len(results) >= MAX_SEARCH_RESULTS:
                                    return
                
                # Skip system directories and hidden directories for further traversal
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
                
                # Search in files if requested
                if search_type in ['files', 'both']:
                    for file in files:
                        try:
                            if self._matches_criteria(file, filename_pattern, file_type, is_folder=False):
                                file_path = Path(root) / file
                                # Verify the file actually exists and is accessible
                                if file_path.exists():
                                    results.append(file_path)
                                    
                                    # Update spinner when we find matches
                                    if spinner and len(results) % 5 == 0:  # Update every 5 matches for files
                                        spinner.update_text(f"🔍 Found {len(results)} matches so far...")
                                    
                                    if len(results) >= MAX_SEARCH_RESULTS:
                                        return
                        except (PermissionError, OSError):
                            continue  # Skip inaccessible files
                            
        except (PermissionError, OSError) as e:
            ErrorHandler.handle_search_error(e, directory)
        except Exception as e:
            ErrorHandler.log_error(e, f"FileSearcher._search_in_directory({directory})")
    
    def _search_in_directory_with_count(self, directory: str, filename_pattern: str, 
                                      file_type: str, existing_results: List[Path], 
                                      spinner: Spinner = None, search_type: str = 'both') -> tuple:
        """Search with file count tracking"""
        results = []
        items_scanned = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                # Search folders if requested
                if search_type in ['folders', 'both']:
                    for dir_name in dirs:
                        items_scanned += 1
                        if self._matches_criteria(dir_name, filename_pattern, '', is_folder=True):
                            dir_path = Path(root) / dir_name
                            if dir_path.exists():
                                results.append(dir_path)
                                
                                if len(existing_results) + len(results) >= MAX_SEARCH_RESULTS:
                                    return results, items_scanned
                
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'System Volume Information', '$RECYCLE.BIN', 'Windows',
                    'Program Files', 'Program Files (x86)', 'ProgramData'
                ]]
                
                # Search files if requested
                if search_type in ['files', 'both']:
                    for file in files:
                        items_scanned += 1
                        
                        # Update spinner every 100 items scanned
                        if spinner and items_scanned % 100 == 0:
                            total_found = len(existing_results) + len(results)
                            spinner.update_text(f"🔍 Scanned {items_scanned} items, found {total_found} matches")
                        
                        try:
                            if self._matches_criteria(file, filename_pattern, file_type, is_folder=False):
                                file_path = Path(root) / file
                                if file_path.exists():
                                    results.append(file_path)
                                    
                                    if len(existing_results) + len(results) >= MAX_SEARCH_RESULTS:
                                        return results, items_scanned
                        except (PermissionError, OSError):
                            continue
                        
        except (PermissionError, OSError) as e:
            ErrorHandler.handle_search_error(e, directory)
        except Exception as e:
            ErrorHandler.log_error(e, f"FileSearcher._search_in_directory_with_count({directory})")
        
        return results, items_scanned
    
    def _matches_criteria(self, filename: str, pattern: str, file_type: str, is_folder: bool = False) -> bool:
        """Check if file or folder matches search criteria with fuzzy matching"""
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
        
        # Check file type (only applies to files, not folders)
        if file_type and not is_folder:
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
        """Calculate relevance score for search result (files and folders)"""
        score = 0.0
        filename = file_path.name.lower()
        search_filename = search_params.get('filename', '').lower()
        search_type = search_params.get('search_type', 'both')
        is_folder = file_path.is_dir()
        
        # Boost folders if specifically searching for folders
        if search_type == 'folders' and is_folder:
            score += 15.0  # High bonus for folders when searching for folders
        elif search_type == 'files' and not is_folder:
            score += 10.0  # High bonus for files when searching for files
        elif is_folder:
            score += 8.0   # Moderate bonus for folders in general search
        
        # Exact filename match
        if search_filename and search_filename == filename:
            score += 10.0
        
        # Partial filename match
        if search_filename and search_filename in filename:
            score += 5.0
            # Bonus for matches at start of filename
            if filename.startswith(search_filename):
                score += 2.0
        
        # File type match (only for files)
        if not is_folder and search_params.get('file_type') and filename.endswith(f".{search_params['file_type']}"):
            score += 3.0
        
        # Priority location bonus
        file_str = str(file_path).lower()
        for priority_path in self.priority_paths:
            if file_str.startswith(priority_path.lower()):
                score += 2.0
                break
        
        # Recent file/folder bonus
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
        
        # File size considerations (only for files)
        if not is_folder:
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