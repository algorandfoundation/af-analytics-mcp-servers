import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from weekly_kpis_server import mcp 
import os 
from dotenv import load_dotenv 

load_dotenv ()

ACTIVE_DEVS_URL = os.getenv("ACTIVE_DEVS_URL")

class ActiveDevs():
    async def executre_active_devs(self, week: str) -> Any:
        response = requests.get(ACTIVE_DEVS_URL)
        active_devs = response.json()
        return active_devs[week]
    

@mcp.tool()
async def get_active_devs(week: Optional[str] = None):
    active_devs = ActiveDevs()
    n_devs = await active_devs.executre_active_devs(week)

    return n_devs