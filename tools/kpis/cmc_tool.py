from typing import Dict, List, Any, Tuple, Optional
import requests
from weekly_kpis_server import mcp
from bs4 import BeautifulSoup

class CMCRanking():
    async def execute_cmc_historic_ranking(self, date: Optional[str] = None):
        """Scrape top 100 cryptocurrency names for a given date from CoinMarketCap historical data."""
        date =  date.replace("-","")
        url = f"https://coinmarketcap.com/historical/{date}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve data for {date}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Select both top 20 and remaining 80 coins
        top_20_rows = soup.select("tr.cmc-table-row")
        remaining_80_rows = soup.select("tr.sc-9db05dbd-1.iWrTcJ.cmc-table-row")

        all_rows = top_20_rows + remaining_80_rows  # Combine both lists

        top_100 = []
        for index, row in enumerate(all_rows[:100]):  # Ensure exactly top 100
            name_tag = row.select_one("a.cmc-link")

            if name_tag:
                if index < 20 and 'title' in name_tag.attrs:  # First 20: Use title
                    full_name = name_tag['title'].strip()
                else:  # Remaining 80: Use text
                    full_name = name_tag.text.strip()
                
                top_100.append(full_name)
        ranking = top_100.index('Algorand')+1
        return ranking

    
@mcp.tool()
async def get_cmc_ranking(date: Optional[str] = None):
    tvl = CMCRanking()
    return await tvl.execute_cmc_historic_ranking(date)
