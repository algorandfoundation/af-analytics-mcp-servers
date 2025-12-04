import clickhouse_connect
from typing import Dict, List, Any, Tuple, Optional
from weekly_kpis_server import mcp 
import os 
from dotenv import load_dotenv 

load_dotenv ()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

class ClickhouseQueries: 

    async def execute_query(self, query: str) -> Any:
        client = clickhouse_connect.get_client(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            secure=False
        )
        result = client.query(query)
        return result
    
@mcp.tool()
async def execute_query_tool(query: str) -> Any:
    db = ClickhouseQueries()
    return await db.execute_query(query)
    