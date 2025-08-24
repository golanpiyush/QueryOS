"""
QueryOS AI Query Parser
"""
import json
import re
from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, AI_MODEL, debug_print
from errors.error_handler import ErrorHandler

class QueryParser:
    """Parse natural language queries using AI"""
    
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
- "content_keywords": keywords that might be in the file content
- "drive": specific drive letter if mentioned (C, D, E, etc.)
- "date_range": if date mentioned (recent, today, this week, etc.)
- "action": what to do with the file (open, show, find, etc.)

Examples:
"Find me apimain.py" -> {"filename": "apimain.py", "file_type": "py", "action": "find"}
"Find Excel file with budget from June 2023" -> {"filename": "", "file_type": "xlsx", "content_keywords": ["budget"], "date_range": "June 2023", "action": "find"}
"In D drive find config.json and open it" -> {"filename": "config.json", "file_type": "json", "drive": "D", "action": "open"}
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
                debug_print(f"📋 Parsed parameters: {parsed_params}")
                return parsed_params
            else:
                # Fallback parsing
                debug_print("🔄 Using fallback parsing")
                return self._fallback_parse(query)
                
        except Exception as e:
            ErrorHandler.handle_ai_error(e)
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str):
        """Fallback query parsing when AI fails"""
        query_lower = query.lower()
        params = {"action": "find"}
        
        # Clean up common typos in the query
        query_cleaned = self._clean_typos(query)
        
        # Extract filename patterns
        if '.' in query_cleaned:
            words = query_cleaned.split()
            for word in words:
                if '.' in word and not word.startswith('.'):
                    params["filename"] = word
                    # Extract file extension
                    if '.' in word:
                        ext = word.split('.')[-1].lower()
                        params["file_type"] = ext
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
            common_words = ['find', 'search', 'look', 'for', 'me', 'file', 'the', 'a', 'an', 'in', 'on', 'with']
            words = [word for word in query_cleaned.split() if word.lower() not in common_words]
            if words:
                params["filename"] = ' '.join(words)
        
        debug_print(f"🔄 Fallback parsed: {params}")
        return params
    
    def _clean_typos(self, query: str):
        """Clean common typos in search queries"""
        # Common typo corrections
        typo_corrections = {
            'immpossible': 'impossible',
            'jurrasic': 'jurassic', 
            'missio': 'mission',
            'rebith': 'rebirth',
            'reconing': 'reckoning',
            'huoston': 'houston',
            'houstn': 'houston'
        }
        
        query_lower = query.lower()
        for typo, correction in typo_corrections.items():
            query_lower = query_lower.replace(typo, correction)
        
        return query_lower