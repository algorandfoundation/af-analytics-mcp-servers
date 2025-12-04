from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import requests
import pandas as pd 
from io import StringIO 
from utils.utils import fetch_all_algorand_stables, merge_stables_data, fetch_all_rwa, merge_rwa_data
from weekly_kpis_server import mcp


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

    async def execute_coingecko_api(self, date: Optional[str] = None):
        url = f'https://www.coingecko.com/price_charts/export/algorand/usd.csv'
        response = requests.get(url)
        price = pd.read_csv(StringIO(response.text))
        price["snapped_at"] = pd.to_datetime(price["snapped_at"])
        return price[price["snapped_at"]==date]['price'].values[0]
    
@mcp.tool()
async def get_defillama_tvl(date: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_defillama_api(date)

@mcp.tool()
async def get_coingecko_price(date: Optional[str] = None):
    tvl = TvlData()
    return await tvl.execute_coingecko_api(date)

