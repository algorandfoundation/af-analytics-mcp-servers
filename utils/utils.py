import requests
import pandas as pd
import time
from datetime import datetime

def fetch_stables_data(coin_id, stable, stable_name):
    """
    Fetch stablecoin data from DeFiLlama API and return as DataFrame
    
    Inputs:
        - coin_id: the name of the crypto we are getting the data (e.g., 'algorand')
        - stable: the stablecoin ID number
        - stable_name: name of the stablecoin for identification
    
    Output:
        - DataFrame with the stablecoin data
    """
    # Construct the URL
    full_url = f'https://stablecoins.llama.fi/stablecoincharts/{coin_id}?stablecoin={stable}'
    
    try:
        # Download the data
        response = requests.get(full_url, headers={'User-agent': 'Price Scrapper'})
        
        if response.status_code == 429:
            print(f"Rate limited for {stable_name}. Waiting...")
            time.sleep(int(response.headers.get("Retry-After", 60)))
            response = requests.get(full_url, headers={'User-agent': 'Price Scrapper'})
        
        if response.status_code == 200:
            # Parse JSON directly into DataFrame
            data = response.json()
            df = pd.DataFrame(data)
            print(f"Successfully fetched {stable_name} data: {len(df)} records")
            return df
        else:
            print(f"Failed to fetch data for {stable_name}. Status code: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching {stable_name}: {e}")
        return pd.DataFrame()

def extract_pegged_usd_values(df):
    """
    Extract peggedUSD values from nested dictionary structure
    
    Args:
        df: DataFrame with potentially nested dictionary data
    
    Returns:
        DataFrame with peggedUSD values extracted
    """
    if df.empty:
        return df
        
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # For each column except the date column
    for col in result_df.columns:
        if col != 'date':  # Skip the date column
            # Extract the peggedUSD value for each row in the column
            result_df[col] = result_df[col].apply(
                lambda x: x.get('peggedUSD') if isinstance(x, dict) else x
            )
    
    return result_df

def convert_timestamps_in_df(df, date_column='date', format_string='%Y-%m-%d'):
    """
    Convert timestamp column to readable dates
    
    Args:
        df: DataFrame with timestamp column
        date_column: name of the date/timestamp column
        format_string: desired date format
    
    Returns:
        DataFrame with converted dates
    """
    if df.empty or date_column not in df.columns:
        return df
        
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], unit='s')
    return df_copy

def fetch_all_algorand_stables():
    """
    Fetch all Algorand stablecoin data and return as dictionary of DataFrames
    
    Returns:
        Dictionary with stablecoin names as keys and DataFrames as values
    """
    # Stablecoin definitions
    stables = {
        'usdt': 1, 
        'usdc': 2, 
        'eurd': 161,
        'stbl': 38, 
        'eurs': 51, 
        'monerium': 101
    }
    
    # Dictionary to store all dataframes
    stables_data = {}

    # Fetch data for each stablecoin
    for stable_name, stable_id in stables.items():
        df = fetch_stables_data('algorand', stable_id, stable_name)
        
        if not df.empty:
            # Extract peggedUSD values
            df_processed = extract_pegged_usd_values(df)
            
            # Convert timestamps to readable dates
            df_processed = convert_timestamps_in_df(df_processed)
            
            stables_data[stable_name] = df_processed
        else:
            stables_data[stable_name] = pd.DataFrame()
        
        # Small delay to be respectful to the API
        time.sleep(0.5)
    
    return stables_data

def merge_stables_data(stables_data):
    """
    Merge all stablecoin DataFrames on the 'date' column and add total_mcap column
    Only keeps totalCirculatingUSD columns for each stablecoin
    
    Args:
        stables_data: Dictionary of DataFrames from fetch_all_algorand_stables()
        
    Returns:
        DataFrame with all stablecoins merged on date with total_mcap column
    """
    # Filter out empty DataFrames
    valid_dfs = {name: df for name, df in stables_data.items() if not df.empty}
    
    if not valid_dfs:
        print("No valid data to merge")
        return pd.DataFrame()
    
    merged_dfs = []
    
    # Process each DataFrame to keep only date and totalCirculatingUSD columns
    for stable_name, df in valid_dfs.items():
        if not df.empty:
            # Create a copy with only date and totalCirculatingUSD columns
            if 'totalCirculatingUSD' in df.columns:
                df_subset = df[['date', 'totalCirculatingUSD']].copy()
                # Rename totalCirculatingUSD to include stablecoin name
                df_subset = df_subset.rename(columns={
                    'totalCirculatingUSD': f"{stable_name}_totalCirculatingUSD"
                })
                merged_dfs.append(df_subset)
                print(f"Added {stable_name}_totalCirculatingUSD: {len(df_subset)} records")
            else:
                print(f"Warning: {stable_name} doesn't have 'totalCirculatingUSD' column")
                print(f"Available columns: {list(df.columns)}")
    
    if not merged_dfs:
        print("No DataFrames with 'totalCirculatingUSD' column found")
        return pd.DataFrame()
    
    # Start with the first DataFrame
    merged_df = merged_dfs[0]
    
    # Merge with remaining DataFrames
    for df in merged_dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='date', how='outer')
    
    # Fill NaN values with 0 for calculation
    merged_df = merged_df.fillna(0)
    
    # Calculate total_mcap by summing all totalCirculatingUSD columns
    totalCirculatingUSD_columns = [col for col in merged_df.columns 
                                   if col.endswith('_totalCirculatingUSD')]
    
    if totalCirculatingUSD_columns:
        merged_df['total_mcap'] = merged_df[totalCirculatingUSD_columns].sum(axis=1)
    else:
        merged_df['total_mcap'] = 0
        print("Warning: No totalCirculatingUSD columns found for total_mcap calculation")
    
    # Sort by date for better readability
    merged_df = merged_df.sort_values('date').reset_index(drop=True)
    
    return merged_df

def fetch_rwa_data(protocol):
    """
    """
    # Construct the URL
    full_url = f'https://api.llama.fi/protocol/{protocol}'
    
    try:
        # Download the data
        response = requests.get(full_url, headers={'User-agent': 'Price Scrapper'})
        
        if response.status_code == 429:
            print(f"Rate limited for {protocol}. Waiting...")
            time.sleep(int(response.headers.get("Retry-After", 60)))
            response = requests.get(full_url, headers={'User-agent': 'Price Scrapper'})
        
        if response.status_code == 200:
            # Parse JSON directly into DataFrame
            data = response.json()['tvl']
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Failed to fetch data for {protocol}. Status code: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching {protocol}: {e}")
        return pd.DataFrame()
    
def fetch_all_rwa():
    """
    Fetch all Algorand stablecoin data and return as dictionary of DataFrames
    
    Returns:
        Dictionary with stablecoin names as keys and DataFrames as values
    """
    # RWA protocols

    protocols = {
        'lofty': 'lofty', 
        'asa_gold': 'asa.gold', 
        'meld': 'meld%20gold', 
        'vesta': 'vesta%20equity'
    }
    
    # Dictionary to store all dataframes
    rwa_data = {}

    # Fetch data for each stablecoin
    for protocol_name, protocol_id in protocols.items():
        df = fetch_rwa_data(protocol_id)
        
        if not df.empty:
            # Extract peggedUSD values
            df_processed = extract_pegged_usd_values(df)
            
            # Convert timestamps to readable dates
            df_processed = convert_timestamps_in_df(df_processed)
            
            rwa_data[protocol_name] = df_processed
        else:
            rwa_data[protocol_name] = pd.DataFrame()
        
        # Small delay to be respectful to the API
        time.sleep(0.5)
    
    return rwa_data    

def merge_rwa_data(rwa_data):
    """
    Merge all stablecoin DataFrames on the 'date' column and add total_mcap column
    Only keeps totalCirculatingUSD columns for each stablecoin
    
    Args:
        stables_data: Dictionary of DataFrames from fetch_all_algorand_stables()
        
    Returns:
        DataFrame with all stablecoins merged on date with total_mcap column
    """
    # Filter out empty DataFrames
    valid_dfs = {name: df for name, df in rwa_data.items() if not df.empty}
    
    if not valid_dfs:
        print("No valid data to merge")
        return pd.DataFrame()
    
    merged_dfs = []
    
    # Process each DataFrame to keep only date and totalCirculatingUSD columns
    for stable_name, df in valid_dfs.items():
        if not df.empty:
            # Create a copy with only date and totalCirculatingUSD columns
            if 'totalLiquidityUSD' in df.columns:
                df_subset = df[['date', 'totalLiquidityUSD']].copy()
                # Rename totalCirculatingUSD to include stablecoin name
                df_subset = df_subset.rename(columns={
                    'totalLiquidityUSD': f"{stable_name}_totalLiquidityUSD"
                })
                merged_dfs.append(df_subset)
                print(f"Added {stable_name}_totalLiquidityUSD: {len(df_subset)} records")
            else:
                print(f"Warning: {stable_name} doesn't have 'totalLiquidityUSD' column")
                print(f"Available columns: {list(df.columns)}")
    
    if not merged_dfs:
        print("No DataFrames with 'totalLiquidityUSD' column found")
        return pd.DataFrame()
    
    # Start with the first DataFrame
    merged_df = merged_dfs[0]
    
    # Merge with remaining DataFrames
    for df in merged_dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='date', how='outer')
    
    # Fill NaN values with 0 for calculation
    merged_df = merged_df.fillna(0)
    
    # Calculate total_mcap by summing all totalCirculatingUSD columns
    totalLiquidityUSD_columns = [col for col in merged_df.columns 
                                   if col.endswith('_totalLiquidityUSD')]
    
    if totalLiquidityUSD_columns:
        merged_df['total_tvl'] = merged_df[totalLiquidityUSD_columns].sum(axis=1)
    else:
        merged_df['total_tvl'] = 0
        print("Warning: No totalLiquidityUSD columns found for total_tvl calculation")
    
    # Sort by date for better readability
    merged_df = merged_df.sort_values('date').reset_index(drop=True)
    
    return merged_df
