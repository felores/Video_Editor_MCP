import os
import json
import logging
from datetime import datetime, timedelta
from collections.abc import Sequence
from functools import lru_cache
from typing import Any

import httpx
import asyncio
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import subprocess
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("video_editor")

current_path:str


temp_output_path="temp"
current_time = int(time.time())


def import_video(path:str):
    current_path=path


# def split(timestmap:str):
#     command="ffmpeg -i "+ f"{current_path}"
def trim (timestamp_start:str, timestamp_end: str):
    command=f"ffmpeg -i {current_path}" + f"-ss {timestamp_start} -to {timestamp_end} " + f"-c copy {temp_output_path}//{current_time}.mp4"  
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result


def preview():
    command=f"ffplay -i {current_path}" 
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result

def export(file_name:str, path: str):
    command=f"ffmpeg -i {current_path}" + f"-c copy {path}//{file_name}.mp4"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result



def speed (speed):
    command=f"ffmpeg -i {current_path}" + f"-ss {timestamp_start} -to {timestamp_end} " + f"-c copy {temp_output_path}//{current_time}.mp4"  








    



        

app = Server("video_editor")

# @app.list_resources()
# async def list_resources() -> list[Resource]:
#     """ Lists saved notes"""
#     return [
#         Resource(
#             uri=AnyUrl(f"notes://{note_name}"),
#             name=note_name,
#             # mimeType="application/json",
#             # description=f"Notes stored in {note_name}"
#         )
#         for note_name in notes
        
#     ]

# @app.read_resource()
# async def read_resource(uri: AnyUrl) -> str:
#     """Read the content of the note"""
#     note_name
#     if str(uri).startswith("notes://"):
#         note_name = str(uri).split("/")[-1]
#     else:
#         raise ValueError(f"Unknown resource: {uri}")

#     content=read_note(note_name=note_name)

# Resource implementation ...

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available note tools."""
    return [
        Tool(
            name="import",
            description="Import the video to edit",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the video to be editted. "
                    },
                },
                "required": ["path"]
            }
            
        ),
        # Tool(
        #     name="split",
        #     description="Split the video at a particular timestamp",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "timestamp": {
        #                 "type": "string",
        #                 "description": "Timestamp at which the video needs to be splitted. "
        #             },
        #         },
        #         "required": ["timestamp"]
        #     }
            
        # ),
        Tool(
            name="trim",
            description="Removes unwanted portions from the beginning or the end",
            inputSchema={
                "type": "object",
                "properties": {
                    "timestamp_start": {
                        "type": "string",
                        "description": "Name of the Note to be removed"
                    },
                    "timestamp_end": {
                        "type": "string",
                        "description": "Name of the Note to be removed"
                    },

                },
                "required": [""]
            }
        ),
        Tool(
            name="preview",
            description="Previews the Editted Video",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [""]
            }
        ),
        Tool(
            name="export",
            description="Export the final video",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The Path where the final video is to be exported"
                    },
                    "file_name":{
                        "type": "string",
                        "description": "The Name of the Final Video"
                    },
                },
                "required": ["file_name"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name:str,  arguments: dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for video editor"""

    if not isinstance(arguments, dict):
        raise ValueError("Arguments must be a dictionary.")

    if name=="import":
        if "path" not in arguments:
            raise ValueError("Path is Required for editing the video")

        import_video(path=arguments["path"])
        return [
            TextContent(
                type="text",
                text=f"The Video at {arguments["path"]} has been imported Successfully"
            )
        ]

    # elif name=="split":
    #     if "timestamp" not in arguments:
    #         raise ValueError("TimeStamp is Required for splitting video")

    #     split(timestamp=arguments["timestamp"])
    #     return [
    #         TextContent(
    #             type="text",
    #             text=f"Note {arguments["note_name"]} Saved Successfully"
    #         )
    #     ]
    
    elif name=="trim":
        if "timestamp_start" not in arguments and "timestamp_end" not in arguments:
            raise ValueError("Atleast one of Timestamp Start or Timestamp End is required for Trimming Video")
        
        trim(timestamp_start=arguments["timestamp_start"], timestamp_end=arguments["timestamp_end"])
        return [
            TextContent(
                type="text",
                text=f"Note {arguments["note_name"]} Removed Successfully"
            )
        ]
    
    elif name=="preview":

        result=preview()
        return [
            TextContent(
                type="text",
                text= result.stdout
            )
        ]
    
    elif name=="export":
        result:str
        if "file_name" not in arguments:
            raise ValueError("File Name is required for Exporting Video")
        else :
            if "path" in arguments:
                result=export(file_name=arguments["file_name"], path=arguments["path"])
            else :
                result=export(file_name=arguments["file_name"],path="")

        return [
            TextContent(
                type="text",
                text= result.stdout
            )
        ]
    

    else: raise ValueError(f"Unknown tool: {name}")

    
    
async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
