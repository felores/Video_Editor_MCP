import os
import logging
import time
import asyncio
import re
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("video_editor")

temp_output_path = "C:\\Users\\kush3\\video_editor\\temp"
current_time = int(time.time())

# Initialize FastMCP
mcp = FastMCP("video_editor")

@mcp.tool()
def export_path() -> str:
    """Get export path for video processing"""
    return f"{temp_output_path}\\{current_time}.mp4"

@mcp.tool()
async def execute_command(command: str, ctx: Context) -> str:
    """Execute FFmpeg command with progress tracking"""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        ctx.info(f"Starting: {command}")
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
            raise Exception(f"Failed: {stderr.decode()}")
            
        return "Success"
        
    except Exception as e:
        await ctx.report_progress(100, str(e), error=True)
        raise
