import requests
from typing import Dict, List, Any, Tuple, Optional
from weekly_kpis_server import mcp 
import os 
from dotenv import load_dotenv 

load_dotenv ()

USER = os.getenv("NODELY_API_USER")
PASS = os.getenv("NODELY_API_PASS")


class Nodes: 

    async def get_nodes(self, month: str) -> Any:
        url = f"https://algoanalytics.api.nodely.io/v1/env/network/nodes/{month}"

        response = requests.get(url, auth=(USER, PASS))
        result = response.json()['unique_ips']
        return result
    
@mcp.tool()
async def execute_get_nodes(month: str) -> Any:
    api = Nodes()
    return await api.get_nodes(month)
    