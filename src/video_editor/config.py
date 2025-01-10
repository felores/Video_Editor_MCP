import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
WORKSPACE_DIR = Path(os.getenv('VIDEO_EDITOR_WORKSPACE', Path.home() / '.video_editor'))
TEMP_DIR = WORKSPACE_DIR / 'temp'
INPUT_DIR = WORKSPACE_DIR / 'input'
OUTPUT_DIR = WORKSPACE_DIR / 'output'

# Create necessary directories
for directory in (WORKSPACE_DIR, TEMP_DIR, INPUT_DIR, OUTPUT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# FFmpeg settings
FFMPEG_TIMEOUT = int(os.getenv('FFMPEG_TIMEOUT', '3600'))  # 1 hour default timeout
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', str(1024 * 1024 * 1024)))  # 1GB default

# Security settings
ALLOWED_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.webm')
MAX_FILENAME_LENGTH = 255 