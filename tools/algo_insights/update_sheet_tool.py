from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import gspread 
import pandas as pd 
from tools.algo_insights.report_tool import get_report
from algo_insights_server import mcp
import os
from dotenv import load_dotenv 

load_dotenv ()

@mcp.tool()
async def update_sheet_individual(month: Optional[str] = None):
    """
    Update Google Sheet using individual cell updates
    Less efficient but more granular control
    """
    df = await get_report(month)

    # Format as "Summary Table Mar - Apr"
    month_name = lambda d: d.strftime("%b")

    date_columns = [df.columns[1], df.columns[2]]
    date_columns_sorted = sorted(date_columns, key=pd.to_datetime)
    prev_month_end, curr_month_end = date_columns_sorted
    sa = gspread.service_account(filename='/Users/marc/Documents/paul/credentials/insights-credentials.json') 

    sh = sa.open('ALGORAND INSIGHTS REPORT DATA') 
    
    prev_month_name = month_name(datetime.strptime(prev_month_end, "%Y-%m-%d"))
    curr_month_name = month_name(datetime.strptime(curr_month_end, "%Y-%m-%d"))
    new_sheet_name = f"Summary Table {prev_month_name} - {curr_month_name}"
    # Create new sheet
    new_sheet = sh.add_worksheet(title=new_sheet_name, rows=1000, cols=26)

    # Define the mapping of queries to their row positions
    row_mapping = {
        'circulating_supply': 6,
        'fees_collected': 8,
        'payouts_paid': 10,
        'total_fee_sink_balance': 12,
        'inflation_amount': 14,
        'inflation': 16,
        'online_stake': 18,
        'online_accounts': 22,
        'monthly_transactions': 26,
        'monthly_wallets': 28,
        'monthly_active_users': 30,
        'nodes':32,
        'tvl_usd': 36,
        'tvl_algo': 38,
        'rwa_tvl': 40,
        'stables_mcap': 42,
        'contracts_deployed': 44,
        'asa_created': 46,
    }
    
    metric_mapping = {
        'circulating_supply': 'Circulating Supply (ALGO)',
        'fees_collected': 'Fees Collected (ALGO)',
        'payouts_paid': 'Payouts Paid (ALGO)',
        'total_fee_sink_balance': 'Total Fee Sink Balance (ALGO)',
        'inflation_amount': 'Tokens Issued (ALGO)',
        'inflation': 'Annualized Token Issuance',
        'monthly_transactions': 'Total Transactions',
        'monthly_wallets': 'Total Wallets',
        'monthly_active_users': 'Monthly Active Users',
        'online_accounts': 'Online Accounts',
        'online_stake': 'Online Stake (ALGO)',
        'nodes': 'Nodes',
        'tvl_usd': 'TVL (USD)',
        'tvl_algo': 'TVL (ALGO)',
        'rwa_tvl': 'RWA TVL (USD)',
        'stables_mcap': 'Total Stablecoins MCap (USD)',
        'contracts_deployed': 'Contracts Deployed',
        'asa_created': 'New Assets Created'
    }

    data_sources_msg = "Data Sources: Nodely DW, Defillama, Coingecko"
    mau_definition = "MAU is any wallet which sent at least 1 txn in a month"
    paul_attribution = "This report has been made by Paul under the supervision of AF BI team"

    worksheet = sh.worksheet(new_sheet_name)
    worksheet.update_acell('F3', prev_month_end)
    worksheet.update_acell('G3', month)
    worksheet.update_acell('E3', 'Metric')
    worksheet.update_acell('H3', f'MoM change:\n{prev_month_name} - {curr_month_name}')
    worksheet.update_acell('D5', 'Tokenomics')
    worksheet.update_acell('E20', 'AF Stake (ALGO)')
    worksheet.update_acell('D25', 'Network')
    worksheet.update_acell('D35', 'Ecosystem')
    worksheet.update_acell('D49', 'Social')
    worksheet.update_acell('E50', 'X - AlgoFoundation')
    worksheet.update_acell('E52', 'YT - AlgoFoundation')
    worksheet.update_acell('E54', 'IG - AlgoFoundation')
    
    worksheet.update_acell('D57', data_sources_msg)
    worksheet.update_acell('D58', mau_definition)
    worksheet.update_acell('D59', paul_attribution)
        
    for _, row in df.iterrows():
        query = row['query']
        if query in row_mapping:
            row_num = row_mapping[query]
            metric = metric_mapping[query]
            worksheet.update_acell(f'E{row_num}', metric)
            worksheet.update_acell(f'F{row_num}', row[prev_month_end])
            worksheet.update_acell(f'G{row_num}', row[curr_month_end])
            worksheet.update_acell(f'H{row_num}', row['change'])

