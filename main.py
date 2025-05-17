from mcp.server.fastmcp import FastMCP
from cmfapi import cmfClient
import os
import tomli
from dotenv import load_dotenv
import uvicorn
from typing import List, Dict, Optional, Any
from pathlib import Path
import atexit
import signal
import sys
import logging

# Import modular components
from tools import pipeline, execution, artifact, additional
# from resources import common, discovery
# from prompts import guide

# Setup logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("cmf-mcp")

# Load environment variables from .env file
load_dotenv()

# Get version from pyproject.toml
def get_version() -> str:
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)
            return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomli.TOMLDecodeError):
        # Fallback version if we can't read from pyproject.toml
        return "0.0.0"

# Create MCP server
mcp = FastMCP(
    "cmf-mcp-server", 
    version=get_version(),
    instructions="You are a helpful assistant that can help with Common Metadata Framework (CMF) server tasks. You can show pipelines, artifacts, executions, and more on a Common Metadata Framework (CMF) server",
)

# Initialize cmf clients based on environment variables
cmf_clients = {}

# Initialize primary Pi-hole (required)
primary_url = os.getenv("CMF_BASE_URL")

if not primary_url:
    raise ValueError("Primary CMF configuration (CMF_BASE_URL) is required")

cmf_clients[primary_url] = cmfClient(primary_url)
print(f"CMF Client initialized for {primary_url}")

# Initialize optional cmf Clients (2-4)
for i in range(2, 5):
    url = os.getenv(f"CMF{i}_BASE_URL")
    if url:
        cmf_clients[url] = cmfClient(url)
        print(f"Additional CMF Client initialized for {url}")


# Flag to track if sessions have been closed
sessions_closed = False

# Function to close all cmf client sessions
def close_cmfAPIClient_sessions():
    global sessions_closed
    
    # Avoid closing sessions more than once
    if sessions_closed:
        return
    
    logger.info("Closing cmfapi client sessions...")
    for url, client in cmf_clients.items():
        try:
            client.close_session()
            logger.info(f"Successfully closed session for cmfapi Server: {url}")
        except Exception as e:
            logger.error(f"Error closing session for cmfapi Server {url}: {e}")
    
    sessions_closed = True


# Register cleanup handlers
atexit.register(close_cmfAPIClient_sessions)

def signal_handler(sig, frame):
    logger.info("Received shutdown signal, cleaning up...")
    close_cmfAPIClient_sessions()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Register resources, tools, and prompts
#Resources
# common.register_resources(mcp, cmf_clients, get_version)
# discovery.register_resources(mcp)
#Tools
pipeline.register_tools(mcp, cmf_clients)
execution.register_tools(mcp, cmf_clients)
artifact.register_tools(mcp, cmf_clients)
additional.register_tools(mcp, cmf_clients)
#Prompts
# guide.register_prompt(mcp)

def main():
    logger.info("Starting CMF MCP server...")
    mcp.run()

# Expose the MCP server over HTTP/SSE
app = mcp.sse_app()

if __name__ == "__main__":
    # Serve on 0.0.0.0:8000 so all can connect
    uvicorn.run(app, host="0.0.0.0", port=8000)