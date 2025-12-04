import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from weekly_kpis_server import mcp 
import os 
from dotenv import load_dotenv 

load_dotenv ()

PROJECT_ID = os.getenv("PROJECT_ID")

class AlgokitDownloads():
    async def execute_algokit_query(self, query: str) -> Any:
        credentials = service_account.Credentials.from_service_account_file(filename='/Users/marc/Documents/paul/credentials/insights-credentials.json')
        client = bigquery.Client(
            credentials = credentials, 
            project = PROJECT_ID)

        query_job = client.query(query)
        rows = query_job.result() 
        results = [dict(row) for row in rows]
        return results[0]['python_downloads']
    
    async def execute_npm_algokit(self, date: Optional[str] = None):
        # Calculate week range (Monday to Sunday)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        days_since_monday = date_obj.weekday()
        week_start = date_obj - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        start_date = week_start.strftime("%Y-%m-%d")
        end_date = week_end.strftime("%Y-%m-%d")

        # Get downloads for that specific week
        package_name = "@algorandfoundation/algokit-utils"
        encoded_package = package_name.replace("/", "%2F").replace("@", "%40")
        url = f"https://api.npmjs.org/downloads/point/{start_date}:{end_date}/{encoded_package}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['downloads']
    

@mcp.tool()
async def get_algokit_downloads(query: str, date: Optional[str] = None):
    algokit = AlgokitDownloads()
    python = await algokit.execute_algokit_query(query)
    node = await algokit.execute_npm_algokit(date)

    return python, node