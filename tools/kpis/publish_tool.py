from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import gspread 
import pandas as pd 
from tools.kpis.weekly_kpi_tool import get_kpis_report
from weekly_kpis_server import mcp
import os
from dotenv import load_dotenv 

load_dotenv ()

@mcp.tool()
async def publish_kpis(week: Optional[str] = None, sheet: Optional[str] = None):
    """
    Update Google Sheet using individual cell updates
    Less efficient but more granular control
    """
    df = await get_kpis_report(week)
    print('I got the df')
    sa = gspread.service_account(filename='/Users/marc/Documents/paul/credentials/insights-credentials.json') 
    print('I got the sa')
    sh = sa.open('KPIS Marketing') 
    source_sheet = sh.worksheet(sheet)

    values = source_sheet.get_all_values()

    # Find the last row with data (skip empty rows at the end)
    last_row_index = len(values)
    for i in range(len(values) - 1, -1, -1):
        if any(cell.strip() for cell in values[i]):  # Check if row has any non-empty cells
            last_row_index = i + 1  # +1 because sheets are 1-indexed
            break

    # Get the latest row data
    if last_row_index > 0:
        latest_row_data = values[last_row_index - 1]  # -1 because list is 0-indexed
        print(f"Latest row ({last_row_index}): {latest_row_data}")
    else:
        latest_row_data = []
        print("No data found in the sheet")

    week_dt = datetime.strptime(week, '%Y-%m-%d')  
    week_dt = datetime.date(week_dt).isoformat()  
    if sheet == "Financials & OnChain":
        new_row = [week_dt, df[df['query'] == 'cmc_ranking'][week].values[0], df[df['query'] == 'weekly_transactions'][week].values[0],
                   df[df['query'] == 'weekly_wallets'][week].values[0], df[df['query'] == 'weekly_active_users'][week].values[0], 'pera1', 
                   'pera2', df[df['query'] == 'tvl_usd'][week].values[0], df[df['query'] == 'tvl_algo'][week].values[0],
                   df[df['query'] == 'online_stake'][week].values[0], df[df['query'] == 'online_accounts'][week].values[0],
                   df[df['query'] == 'nodes'][week].values[0]
                   ]
        next_row_index = last_row_index + 1
        source_sheet.insert_row(new_row, next_row_index)
        print(f"New row inserted at index {next_row_index}, {new_row}")
        return 
    elif sheet == "Algokit":
        new_row = [week, df[df['query'] == 'algokit_downloads'][week].values[0], 
                   df[df['query'] == 'algokit_python'][week].values[0], df[df['query'] == 'algokit_ts'][week].values[0],
                   df[df['query'] == 'active_devs'][week].values[0]]
        next_row_index = last_row_index + 1
        source_sheet.insert_row(new_row, next_row_index)
        print(f"New row inserted at index {next_row_index}, {new_row}")
        return df

