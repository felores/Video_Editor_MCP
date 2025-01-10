import os
import logging
import time
import asyncio
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

from .security import (
    validate_timestamp,
    validate_video_file,
    sanitize_filename,
    is_safe_path,
    VideoEditorError,
    InvalidInputError,
    SecurityError
)
from . import config

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("video_editor")

# Initialize FastMCP
mcp = FastMCP("video_editor")

class VideoEditor:
    def __init__(self):
        self.current_video: Optional[Path] = None
        
    def import_video(self, path: str) -> Path:
        """Safely import a video file"""
        video_path = validate_video_file(path)
        if not is_safe_path(video_path, config.INPUT_DIR):
            raise SecurityError("Access denied: File must be in allowed input directory")
        self.current_video = video_path
        return video_path
        
    def get_output_path(self, filename: str) -> Path:
        """Generate safe output path"""
        safe_filename = sanitize_filename(filename)
        if len(safe_filename) > config.MAX_FILENAME_LENGTH:
            raise InvalidInputError("Filename too long")
        return config.OUTPUT_DIR / safe_filename

    async def execute_ffmpeg(self, args: list[str], ctx: Context) -> str:
        """Execute FFmpeg command safely"""
        try:
            if not self.current_video:
                raise InvalidInputError("No video imported")
                
            command = ["ffmpeg", "-i", str(self.current_video)] + args
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            ctx.info(f"Starting FFmpeg: {' '.join(command)}")
            frames_processed = 0
            
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                    
                text = line.decode().strip()
                ctx.info(text)
                
                if b"frame=" in line:
                    frames_processed += 1
                    if frames_processed % 30 == 0:
                        progress = min(95, frames_processed // 30)
                        await ctx.report_progress(progress, f"Frames processed: {frames_processed}")

            stdout, stderr = await process.communicate()
            await ctx.report_progress(100, "Complete")
            
            if process.returncode != 0:
                raise VideoEditorError(f"FFmpeg error: {stderr.decode()}")
                
            return "Success"
            
        except Exception as e:
            logger.error("FFmpeg execution failed", exc_info=e)
            await ctx.report_progress(100, str(e), error=True)
            raise

editor = VideoEditor()

@mcp.tool()
async def trim_video(timestamp_start: str, timestamp_end: str, ctx: Context) -> str:
    """Trim video safely"""
    if not validate_timestamp(timestamp_start) or not validate_timestamp(timestamp_end):
        raise InvalidInputError("Invalid timestamp format")
        
    output_file = editor.get_output_path(f"trim_{int(time.time())}.mp4")
    
    args = [
        "-ss", timestamp_start,
        "-to", timestamp_end,
        "-c", "copy",
        str(output_file)
    ]
    
    return await editor.execute_ffmpeg(args, ctx)

@mcp.tool()
async def import_video(path: str) -> str:
    """Import video safely"""
    try:
        video_path = editor.import_video(path)
        return f"Successfully imported video: {video_path.name}"
    except Exception as e:
        logger.error("Failed to import video", exc_info=e)
        raise

async def main():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options()
        )
