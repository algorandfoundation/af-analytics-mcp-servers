from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from tools.algo_insights.tvl_tool import get_defillama_tvl, get_coingecko_price, get_rwa_tvl, get_stables_tvl
from tools.algo_insights.queries_tool import execute_query_tool
from tools.algo_insights.nodes_tool import execute_get_nodes
from algo_insights_server import mcp 
import pandas as pd 
import numpy as np
import yaml

@mcp.tool()
async def get_tvl_report(month: Optional[str] = None):
    # Set default month to current month if not provided
    if not month:
        month = datetime.now().strftime("%Y-%m-%d")
    
    # Parse the month
    try:
        year, month_num, day = map(int, month.split("-"))
        
        # Calculate previous month end date
        if month_num == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month_num - 1
            
        # Get the last day of previous month
        if prev_month == 12:
            next_month = 1
            next_year = prev_year + 1
        else:
            next_month = prev_month + 1
            next_year = prev_year
            
        # Calculate the end of previous month (last day of previous month)
        prev_month_end = f"{prev_year}-{prev_month:02d}-01"
        prev_month_end_date = datetime.strptime(f"{next_year}-{next_month:02d}-01", "%Y-%m-%d") - timedelta(days=1)
        prev_month_end = prev_month_end_date.strftime("%Y-%m-%d")
        
        # Current month end is the input date
        curr_month_end = month
    
    except ValueError:
        return f"Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2023-12-31)."
    data = []

    defillama_tvl_usd_curr = await get_defillama_tvl(curr_month_end)
    defillama_tvl_usd_prev = await get_defillama_tvl(prev_month_end)
    coingecko_price_curr = await get_coingecko_price(curr_month_end, 'price')
    coingecko_price_prev = await get_coingecko_price(prev_month_end, 'price')
    mcap_curr = await get_coingecko_price(curr_month_end, 'market_cap')
    mcap_prev = await get_coingecko_price(prev_month_end, 'market_cap') 
    defillama_tvl_algo_curr = defillama_tvl_usd_curr / coingecko_price_curr
    defillama_tvl_algo_prev = defillama_tvl_usd_prev / coingecko_price_prev
    circulating_supply_curr = mcap_curr / coingecko_price_curr
    circulating_supply_prev = mcap_prev / coingecko_price_prev

    # Calculate the inflation rate

    rwa_tvl_curr = await get_rwa_tvl(curr_month_end)
    rwa_tvl_prev = await get_rwa_tvl(prev_month_end)
    rows = [
        {"query": "tvl_usd", curr_month_end: defillama_tvl_usd_curr, prev_month_end: defillama_tvl_usd_prev},
        {"query": "tvl_algo", curr_month_end: defillama_tvl_algo_curr, prev_month_end: defillama_tvl_algo_prev},
        {"query": "rwa_tvl", curr_month_end: rwa_tvl_curr, prev_month_end: rwa_tvl_prev},
        {"query": "circulating_supply", curr_month_end: circulating_supply_curr, prev_month_end: circulating_supply_prev}
    ]
    df = pd.DataFrame(rows)
    df['change'] = df[curr_month_end]/df[prev_month_end] - 1
    
    return df

@mcp.tool()
async def get_stables_mcap(month: Optional[str] = None):
        # Set default month to current month if not provided
    if not month:
        month = datetime.now().strftime("%Y-%m-%d")
    
    # Parse the month
    try:
        year, month_num, day = map(int, month.split("-"))
        
        # Calculate previous month end date
        if month_num == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month_num - 1
            
        # Get the last day of previous month
        if prev_month == 12:
            next_month = 1
            next_year = prev_year + 1
        else:
            next_month = prev_month + 1
            next_year = prev_year
            
        # Calculate the end of previous month (last day of previous month)
        prev_month_end = f"{prev_year}-{prev_month:02d}-01"
        prev_month_end_date = datetime.strptime(f"{next_year}-{next_month:02d}-01", "%Y-%m-%d") - timedelta(days=1)
        prev_month_end = prev_month_end_date.strftime("%Y-%m-%d")
        
        # Current month end is the input date
        curr_month_end = month
    
    except ValueError:
        return f"Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2023-12-31)."
    
    stables_tvl_curr = await get_stables_tvl(curr_month_end)
    stables_tvl_prev = await get_stables_tvl(prev_month_end)

    rows = [
        {"query": "stables_mcap", curr_month_end: stables_tvl_curr, prev_month_end: stables_tvl_prev}
    ]
    df = pd.DataFrame(rows)
    df['change'] = df[curr_month_end]/df[prev_month_end] - 1
    
    return df


@mcp.tool()
async def get_report(month: Optional[str] = None) -> Any:
    # Predefined queries from the documentation
    with open('docs/algo_insights/queries.yaml', 'r') as f:
        QUERIES = yaml.safe_load(f)
    # Set default month to current month if not provided
    if not month:
        month = datetime.now().strftime("%Y-%m-%d")
    
    # Parse the month
    try:
        year, month_num, day = map(int, month.split("-"))
        
        # Calculate previous month end date
        if month_num == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month_num - 1
            
        # Get the last day of previous month
        if prev_month == 12:
            next_month = 1
            next_year = prev_year + 1
        else:
            next_month = prev_month + 1
            next_year = prev_year
            
        # Calculate the end of previous month (last day of previous month)
        prev_month_end = f"{prev_year}-{prev_month:02d}-01"
        prev_month_end_date = datetime.strptime(f"{next_year}-{next_month:02d}-01", "%Y-%m-%d") - timedelta(days=1)
        prev_month_end = prev_month_end_date.strftime("%Y-%m-%d")
        
        # Calculate the start of previous month (first day of previous month)
        prev_month_start = f"{prev_year}-{prev_month:02d}-01"
        
        # Calculate the start of current month (first day of current month)
        curr_month_start = f"{year}-{month_num:02d}-01"
        
        # Current month end is the input date
        curr_month_end = month
        
    except ValueError:
        return f"Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2023-12-31)."
    data = []
    

    for query_name, query_info in QUERIES.items():
        query_sql = query_info["sql"]
        print(query_sql)
        query_sql = query_sql.replace("START_1", f"'{prev_month_start}'")
        query_sql = query_sql.replace("START_2", f"'{curr_month_start}'")
        query_sql = query_sql.replace("PREV_MONTH", f"'{prev_month_end}'")
        query_sql = query_sql.replace("CURR_MONTH", f"'{curr_month_end}'")
        result = await execute_query_tool(query_sql)
        
        # Convert result to dict with date as keys
        row = {"query": query_name}
        for date, value in result.result_rows:
            row[date] = value
        data.append(row)

    curr_nodes = await execute_get_nodes(curr_month_end)
    prev_nodes = await execute_get_nodes(prev_month_end)

    row = {'query': 'nodes', curr_month_end: curr_nodes, prev_month_end: prev_nodes}
    data.append(row)

    df = pd.DataFrame(data)
    fee_sink_balance_curr = df[df['query'] == 'fee_sink_balance'][curr_month_end].values[0]
    fee_sink_balance_prev = df[df['query'] == 'fee_sink_balance'][prev_month_end].values[0]
    cumulative_fees_collected_curr = df[df['query'] == 'fees_collected_cumulative'][curr_month_end].values[0]
    cumulative_fees_collected_prev = df[df['query'] == 'fees_collected_cumulative'][prev_month_end].values[0]
    total_fee_sink_balance_curr = fee_sink_balance_curr + cumulative_fees_collected_curr 
    total_fee_sink_balance_prev = fee_sink_balance_prev + cumulative_fees_collected_prev
    
    initial_stake = 8326259584
    initial_balance = 5504018
    
    gross_issuance_curr = df[df['query']=='gross_issuance'][curr_month_end].values[0]
    gross_issuance_prev = df[df['query']=='gross_issuance'][prev_month_end].values[0]
    token_issuance_curr = (gross_issuance_curr + initial_balance) - total_fee_sink_balance_curr 
    token_issuance_prev = (gross_issuance_prev + initial_balance) - total_fee_sink_balance_prev
    inflation_rate_curr = token_issuance_curr / initial_stake
    inflation_rate_prev = token_issuance_prev / initial_stake
    inflation_rows = [
        {'query': 'total_fee_sink_balance', curr_month_end: total_fee_sink_balance_curr, prev_month_end: total_fee_sink_balance_prev},
        {'query': 'inflation_amount', curr_month_end: token_issuance_curr, prev_month_end: token_issuance_prev},
        {'query': 'inflation', curr_month_end: inflation_rate_curr, prev_month_end: inflation_rate_prev}
    ]

    balance_df = pd.DataFrame(inflation_rows)
    df = pd.concat([df, balance_df], ignore_index=True)

    df['change'] = np.where(
    df[prev_month_end] == 0,
    0,  
    df[curr_month_end] / df[prev_month_end] - 1 
    )

    df = df.replace([np.inf, -np.inf], 0).fillna(0)
    stables_mcap = await get_stables_mcap(month)
    tvl = await get_tvl_report(month)
    df = pd.concat([df, stables_mcap, tvl], ignore_index=True)

    
    inflation_df = pd.DataFrame(inflation_rows)
    inflation_df['change'] = np.where(
        inflation_df[prev_month_end] == 0,
        0,  
        inflation_df[curr_month_end] / inflation_df[prev_month_end] - 1 
    )
    df = pd.concat([df, inflation_df])

    return df

