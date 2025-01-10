import os
import re
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

class VideoEditorError(Exception):
    """Base exception for video editor errors"""
    pass

class InvalidInputError(VideoEditorError):
    """Invalid input parameters"""
    pass

class SecurityError(VideoEditorError):
    """Security-related errors"""
    pass

def is_safe_path(path: Union[str, Path], base_dir: Union[str, Path]) -> bool:
    """
    Validate if the path is safe and within allowed directory
    
    Args:
        path: The path to validate
        base_dir: The base directory that should contain the path
        
    Returns:
        bool: True if path is safe, False otherwise
    """
    try:
        resolved_path = os.path.realpath(str(path))
        base_path = os.path.realpath(str(base_dir))
        return os.path.commonpath([resolved_path, base_path]) == base_path
    except (TypeError, ValueError):
        return False

def validate_timestamp(timestamp: str) -> bool:
    """
    Validate timestamp format (HH:MM:SS.ms)
    
    Args:
        timestamp: The timestamp string to validate
        
    Returns:
        bool: True if timestamp is valid, False otherwise
    """
    pattern = r'^(\d+:)?[0-5]?\d:[0-5]\d(\.\d+)?$'
    return bool(re.match(pattern, timestamp))

def validate_video_file(path: Union[str, Path]) -> Optional[Path]:
    """
    Validate video file path and format
    
    Args:
        path: Path to the video file
        
    Returns:
        Path: Validated path object if valid
        
    Raises:
        InvalidInputError: If file is invalid
    """
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise InvalidInputError("File does not exist")
            
        if not path_obj.suffix.lower() in ('.mp4', '.avi', '.mov', '.mkv', '.webm'):
            raise InvalidInputError("Unsupported file format")
            
        return path_obj
    except Exception as e:
        logger.error(f"Error validating video file: {e}")
        raise InvalidInputError(f"Invalid video file: {e}")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove path separators and null bytes
    filename = os.path.basename(filename)
    # Remove any null bytes
    filename = filename.replace('\0', '')
    # Additional sanitization can be added here
    return filename 