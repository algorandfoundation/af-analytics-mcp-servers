from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import requests
import pandas as pd 
from io import StringIO 
from utils.utils import fetch_all_algorand_stables, merge_stables_data, fetch_all_rwa, merge_rwa_data
from algo_insights_server import mcp


class TvlData():
    async def execute_defillama_api(self, date: Optional[str] = None):
        url = f'https://api.llama.fi/simpleChainDataset/algorand?pool2=true&staking=true&borrowed=true&doublecounted=true&liquidstaking=true&vesting=true&govtokens=true'
        response = requests.get(url) 
        tvl = pd.read_csv(StringIO(response.text))
        tvl = tvl.melt(id_vars='Protocol')
        tvl['variable'] = pd.to_datetime(tvl['variable'], format="%d/%m/%Y")
        total_tvl = tvl[tvl['Protocol']=='Total']
        total_tvl['variable'] = pd.to_datetime(total_tvl['variable'], format="%d/%m/%Y")
        return total_tvl[total_tvl['variable']==date]['value'].values[0]

    async def execute_coingecko_api(self, date: Optional[str] = None, field: Optional[str] = None):
        url = f'https://www.coingecko.com/price_charts/export/algorand/usd.csv'
        response = requests.get(url)
        price = pd.read_csv(StringIO(response.text))
        price["snapped_at"] = pd.to_datetime(price["snapped_at"])
        # Ensure 'date' is a datetime object
        if field == 'price':
            filtered = price[price["snapped_at"] == date]
            return filtered['price'].values[0]
        elif field == 'market_cap':
            filtered = price[price["snapped_at"] == date]
            return filtered['market_cap'].values[0]

    async def execute_stables_tvl(self, date: Optional[str] = None):
        stables_data = fetch_all_algorand_stables()
        stables_mcap = merge_stables_data(stables_data)
        return stables_mcap[stables_mcap['date']==date]['total_mcap'].values[0]

    async def execute_rwa_tvl(self, date: Optional[str] = None):
        rwa_data = fetch_all_rwa()
        rwa_tvl = merge_rwa_data(rwa_data)
        return rwa_tvl[rwa_tvl['date']==date]['total_tvl'].values[0]
    
@mcp.tool()
async def get_defillama_tvl(date: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_defillama_api(date)

@mcp.tool()
async def get_coingecko_price(date: Optional[str] = None, field: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_coingecko_api(date, field)

@mcp.tool()
async def get_stables_tvl(date: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_stables_tvl(date)

@mcp.tool()
async def get_rwa_tvl(date: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_rwa_tvl(date)