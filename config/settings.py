"""
QueryOS Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug mode - controls information display level
DEBUG_MODE = False  # Set to False for minimal UI

# OpenAI API Configuration (loaded from .env)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
AI_MODEL = os.getenv("AI_MODEL", "nousresearch/deephermes-3-llama-3-8b-preview:free")

# File type associations
FILE_TYPES = {
    'code': [
        '.py', '.pyw', '.ipynb',
        '.js', '.ts', '.jsx', '.tsx',
        '.html', '.htm', '.css', '.scss', '.sass', '.less',
        '.java', '.class', '.jar',
        '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.kts',
        '.cs', '.vb', '.pl', '.sh', '.bat', '.ps1', '.r', '.m', '.scala',
        '.sql'
    ],
    'documents': [
        '.txt', '.pdf',
        '.docx', '.doc', '.rtf', '.odt',
        '.ppt', '.pptx', '.odp',
        '.md', '.tex'
    ],
    'data': [
        '.xlsx', '.xls', '.csv', '.tsv',
        '.json', '.xml', '.yaml', '.yml',
        '.sql', '.db', '.sqlite', '.parquet'
    ],
    'images': [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.svg', '.ico', '.tif', '.tiff', '.webp', '.heic'
    ],
    'media': [
        # video
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg',
        # audio
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'
    ],
    'archives': [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'
    ],
    'executables': [
        '.exe', '.msi', '.apk', '.app', '.deb', '.rpm', '.dmg', '.bin'
    ],
    'configs': [
        '.ini', '.cfg', '.conf', '.env', '.toml', '.properties'
    ]
}


# Priority search paths
PRIORITY_PATHS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
]

# Search limits
MAX_SEARCH_RESULTS = 50
MAX_DISPLAY_RESULTS = 20
MAX_FILE_SIZE_DISPLAY = 1024 * 1024  # 1MB
MAX_DISPLAY_LINES = 50

# Voice settings
VOICE_TIMEOUT = 5
VOICE_PHRASE_LIMIT = 10
TTS_RATE = 180

# UI Messages
MESSAGES = {
    'welcome': "🔍 QueryOS - AI Desktop Search Assistant initialized!",
    'voice_enabled': "🎤 Voice recognition enabled",
    'drives_ready': "📁 Ready to search across all drives",
    'voice_unavailable': "Voice features unavailable. Install: pip install speechrecognition pyttsx3 pyaudio"
}

# Debug output control
def debug_print(message):
    """Print message only if debug mode is enabled"""
    if DEBUG_MODE:
        print(message)

def info_print(message):
    """Always print important messages"""
    print(message)
