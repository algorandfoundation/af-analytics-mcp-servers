from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from tools.kpis.tvl_tool import get_defillama_tvl, get_coingecko_price
from tools.kpis.on_chain_tool import execute_query_tool
from tools.kpis.nodes_tool import execute_get_nodes
from tools.kpis.cmc_tool import get_cmc_ranking
from tools.kpis.algokit import get_algokit_downloads
from tools.kpis.active_devs import get_active_devs
from weekly_kpis_server import mcp 
import pandas as pd 
import yaml

@mcp.tool()
async def get_tvl_report(week: Optional[str] = None):
    # Set default month to current month if not provided
    if not week:
        week = datetime.now().strftime("%Y-%m-%d")

    defillama_tvl_usd_curr = await get_defillama_tvl(week)
    coingecko_price_curr = await get_coingecko_price(week)
    ranking = await get_cmc_ranking(week)
    defillama_tvl_algo_curr = defillama_tvl_usd_curr / coingecko_price_curr

    rows = [
        {"query": "cmc_ranking", week: ranking},
        {"query": "tvl_usd", week: defillama_tvl_usd_curr},
        {"query": "tvl_algo", week: defillama_tvl_algo_curr}
    ]
    df = pd.DataFrame(rows)

    return df

@mcp.tool()
async def get_kpis_report(week: Optional[str] = None) -> Any:
    # Predefined queries from the documentation
    with open('docs/kpis/queries.yaml', 'r') as f:
        QUERIES = yaml.safe_load(f)
    # Set default month to current month if not provided
    if not week:
        week = datetime.now().strftime("%Y-%m-%d")
    data = []
    
    for query_name, query_info in QUERIES.items():        
        query_sql = query_info["sql"]
        query_sql = query_sql.replace("WEEK", f"'{week}'")
        if query_name == 'algokit_downloads':
            continue
        result = await execute_query_tool(query_sql)
        
        # Convert result to dict with date as keys
        row = {"query": query_name}
        for date, value in result.result_rows:
            row[date] = value
        data.append(row)

    nodes = await execute_get_nodes(week)
    row = {'query': 'nodes', week: nodes}
    data.append(row)
        
    df = pd.DataFrame(data)

    algokit_sql = QUERIES['algokit_downloads']['sql']
    algokit_sql = algokit_sql.replace("WEEK", f"'{week}'")
    py_downloads, npm_downloads = await get_algokit_downloads(algokit_sql, week)
    active_devs = await get_active_devs(week)
    
    downloads = [
        {'query': 'algokit_downloads', week: py_downloads+npm_downloads},
        {'query': 'algokit_python', week: py_downloads},
        {'query': 'algokit_ts', week: npm_downloads},
        {'query': 'active_devs', week: active_devs}
    ]
    downloads_df = pd.DataFrame(downloads)

    tvl = await get_tvl_report(week)
    df = pd.concat([df, tvl, downloads_df], ignore_index=True)

    return df

