"""
CMF MCP Execution tools
"""

from typing import List, Dict, Optional, Any
import time
import secrets
import threading
import json

def register_tools(mcp, cmf_clients):
    """Register execution related tools with the MCP server."""

    @mcp.tool(name="cmf_show_executions", description="Lists all Executions for a given pipeline in CMF server")
    def cmf_show_executions(pipeline: str, cmfClient_instances: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Show Pipelines in CMF Server(s)
        Select only one pipeline to show all the executions for it.
        
        Args:
            pipeline: Name of the pipeline to show executions for.
            cmfClient_instances: Optional list of cmfClient_instances to query. If None, query all configured cccAPI_instances.
        """
        result = []
        
        # Determine which ccc_instances to query
        targets = cmf_clients.keys() if cmfClient_instances is None else [p for p in cmfClient_instances if p in cmf_clients]
        
        for url in targets:
            client = cmf_clients[url]
            try:
                data = client.get_executions(pipeline)
                result.append({"cmfClient": url, "data": data})
                json.dumps(data, indent=4)
            except Exception as e:
                result.append({"cmfClient": url, "error": str(e)})
        
        return result
