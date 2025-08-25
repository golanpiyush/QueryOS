"""
QueryOS AI Query Parser with Folder Detection
"""
import json
import re
from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, AI_MODEL, debug_print
from errors.error_handler import ErrorHandler

class QueryParser:
    """Parse natural language queries using AI with folder/file detection"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
    
    def parse_search_query(self, query: str):
        """Parse natural language search query using AI"""
        system_prompt = """You are a file search query parser. Parse the user's natural language query into structured search parameters.

Return a JSON object with these fields:
- "filename": partial or full filename to search for
- "file_type": file extension or type (py, txt, xlsx, etc.)
- "search_type": "files", "folders", or "both" based on what user wants
- "content_keywords": keywords that might be in the file content
- "drive": specific drive letter if mentioned (C, D, E, etc.)
- "date_range": if date mentioned (recent, today, this week, etc.)
- "action": what to do with the file (open, show, find, etc.)

Important search_type rules:
- Use "folders" when user says: folder, folders, directory, directories, dir
- Use "files" when user specifically mentions: file, files, document, script
- Use "both" when unclear or when user doesn't specify

Examples:
"find me gay folder" -> {"filename": "gay", "search_type": "folders", "file_type": "", "action": "find"}
"Find me apimain.py" -> {"filename": "apimain.py", "file_type": "py", "search_type": "files", "action": "find"}
"show me project directories" -> {"filename": "project", "search_type": "folders", "file_type": "", "action": "show"}
"Find Excel file with budget from June 2023" -> {"filename": "", "file_type": "xlsx", "search_type": "files", "content_keywords": ["budget"], "date_range": "June 2023", "action": "find"}
"In D drive find config.json and open it" -> {"filename": "config.json", "file_type": "json", "search_type": "files", "drive": "D", "action": "open"}
"look for Documents folder" -> {"filename": "Documents", "search_type": "folders", "file_type": "", "action": "find"}
"""
        
        try:
            completion = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            
            response = completion.choices[0].message.content
            debug_print(f"🤖 AI Response: {response}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_params = json.loads(json_match.group())
                
                # Ensure search_type is set using fallback detection
                if 'search_type' not in parsed_params or not parsed_params['search_type']:
                    parsed_params['search_type'] = self._detect_search_type(query)
                
                debug_print(f"📋 Parsed parameters: {parsed_params}")
                return parsed_params
            else:
                # Fallback parsing
                debug_print("🔄 Using fallback parsing")
                return self._fallback_parse(query)
                
        except Exception as e:
            ErrorHandler.handle_ai_error(e)
            return self._fallback_parse(query)
    
    def _detect_search_type(self, query: str) -> str:
        """Detect if user is searching for files, folders, or both"""
        query_lower = query.lower()
        
        # Keywords that indicate folder search
        folder_keywords = [
            'folder', 'folders', 'directory', 'directories', 'dir',
            'in folder', 'inside folder', 'within folder', 'folder called',
            'folder named', 'folder with'
        ]
        
        # Keywords that indicate file search
        file_keywords = [
            'file', 'files', 'document', 'documents', 'script', 'scripts',
            '.py', '.txt', '.json', '.xml', '.html', '.css', '.js',
            '.xlsx', '.csv', '.pdf', '.docx', '.mp4', '.mp3'
        ]
        
        # Check for folder keywords first (more specific)
        if any(keyword in query_lower for keyword in folder_keywords):
            return 'folders'
        
        # Check for file extensions or explicit file keywords
        elif any(keyword in query_lower for keyword in file_keywords):
            return 'files'
        
        # Check for file extensions with dots
        elif re.search(r'\.\w{2,4}\b', query):
            return 'files'
        
        # Default to both if not specified
        else:
            return 'both'
    
    def _fallback_parse(self, query: str):
        """Enhanced fallback query parsing when AI fails"""
        query_lower = query.lower()
        params = {"action": "find"}
        
        # Detect search type using local method
        params["search_type"] = self._detect_search_type(query)
        
        # Clean up common typos in the query
        query_cleaned = self._clean_typos(query)
        
        # Extract filename patterns
        if '.' in query_cleaned:
            words = query_cleaned.split()
            for word in words:
                if '.' in word and not word.startswith('.'):
                    params["filename"] = word.split('.')[0]  # Get filename without extension
                    # Extract file extension
                    ext = word.split('.')[-1].lower()
                    params["file_type"] = ext
                    params["search_type"] = "files"  # Override if we found a file extension
                    break
        
        # Extract drive letters
        drive_match = re.search(r'\b([A-Z]):\s*drive\b', query, re.IGNORECASE)
        if drive_match:
            params["drive"] = drive_match.group(1).upper()
        
        # Extract action keywords
        if any(word in query_lower for word in ['open', 'launch', 'run']):
            params["action"] = "open"
        elif any(word in query_lower for word in ['show', 'display', 'view']):
            params["action"] = "show"
        
        # If no specific filename found, use the cleaned query as search term
        if "filename" not in params:
            # Remove common words but keep the typo-corrected terms
            common_words = ['find', 'search', 'look', 'for', 'me', 'file', 'files', 
                          'folder', 'folders', 'the', 'a', 'an', 'in', 'on', 'with', 
                          'called', 'named', 'directory', 'directories']
            words = [word for word in query_cleaned.split() if word.lower() not in common_words]
            if words:
                params["filename"] = ' '.join(words)
        
        # Set default empty values
        params.setdefault("file_type", "")
        params.setdefault("content_keywords", [])
        params.setdefault("drive", "")
        params.setdefault("date_range", "")
        
        debug_print(f"🔄 Fallback parsed: {params}")
        return params
    
    def _clean_typos(self, query: str):
        """Clean common typos in search queries"""
        # Common typo corrections
        typo_corrections = {
            'fies' : 'file',
            'screipt': 'script',
            'docuemnts': 'documents',
            'dowloads': 'downloads',
            'dekstop': 'desktop',
            'picutres': 'pictures',
            'musci': 'music',
            'vieos': 'videos',
            'fodler': 'folder',
            'floder': 'folder',
            'flie': 'file',
            'cofig': 'config',
            'conifg': 'config'
        }
        
        query_lower = query.lower()
        for typo, correction in typo_corrections.items():
            query_lower = query_lower.replace(typo, correction)
        
        return query_lower
    
    def enhance_search_params(self, params: dict, query: str) -> dict:
        """Enhance search parameters with additional context"""
        query_lower = query.lower()
        
        # Add common file type associations
        filename = params.get("filename", "").lower()
        if filename and not params.get("file_type"):
            # Common filename patterns
            file_associations = {
                'config': ['json', 'ini', 'cfg', 'conf'],
                'readme': ['txt', 'md'],
                'index': ['html', 'htm', 'php'],
                'main': ['py', 'js', 'java', 'cpp'],
                'test': ['py', 'js', 'java'],
                'package': ['json'],
                'requirements': ['txt'],
                'dockerfile': [''],
                'makefile': ['']
            }
            
            for pattern, extensions in file_associations.items():
                if pattern in filename:
                    if extensions and extensions[0]:
                        params["file_type"] = extensions[0]
                        params["search_type"] = "files"
                    break
        
        # Enhance content keywords based on context
        content_hints = {
            'budget': ['budget', 'financial', 'expense', 'cost'],
            'report': ['report', 'summary', 'analysis'],
            'presentation': ['slide', 'powerpoint', 'present'],
            'photo': ['image', 'picture', 'jpg', 'png'],
            'music': ['audio', 'song', 'mp3', 'music'],
            'video': ['movie', 'clip', 'mp4', 'video']
        }
        
        for keyword, related in content_hints.items():
            if keyword in query_lower:
                existing_keywords = params.get("content_keywords", [])
                params["content_keywords"] = list(set(existing_keywords + related))
                break
        
        return params