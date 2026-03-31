import websockets
import asyncio
from datetime import datetime, timezone, timedelta
import time
import json
import asyncio

# # Set start and end times for the data range in milliseconds
# start_time = int(datetime(2023, 12, 1, tzinfo=timezone.utc).timestamp() * 1000)
# end_time = int(datetime(2024, 1, 3, tzinfo=timezone.utc).timestamp() * 1000)

# # Binance API endpoint
# url = "https://api.binance.com/api/v3/aggTrades"
# symbol = "BTCUSDT"
# limit = 1000  # Max limit per API call

# # Initialize CSV writing
# csv_file = "binance_3s_ohlcv.csv"
# with open(csv_file, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])

#     # Loop through time range and fetch data in chunks
#     current_start_time = start_time
#     while current_start_time < end_time:
#         params = {
#             "symbol": symbol,
#             "startTime": current_start_time,
#             "endTime": min(current_start_time + 60 * 60 * 1000, end_time),  # Fetch up to 1 hour of data at a time
#             "limit": limit
#         }

#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             data = response.json()
            
#             if not data:
#                 # If no data is returned, move the current_start_time forward
#                 current_start_time += 60 * 60 * 1000  # Move by 1 hour
#                 continue

#             ohlcv_3s_data = []  # To store the 3-second aggregated data
#             current_interval_start = None
#             open_price = high_price = low_price = close_price = None
#             volume = 0

#             for trade in data:
#                 trade_time = trade['T'] // 1000  # Convert milliseconds to seconds
#                 price = float(trade['p'])
#                 qty = float(trade['q'])

#                 # Calculate the start of the 3-second interval
#                 interval_start = (trade_time // 3) * 3  # Round down to nearest 3-second interval

#                 # Initialize a new interval if needed
#                 if current_interval_start is None:
#                     current_interval_start = interval_start
#                     open_price = high_price = low_price = close_price = price
#                     volume = qty
#                 elif interval_start != current_interval_start:
#                     # End of the current interval; save OHLCV data
#                     ohlcv_3s_data.append([
#                         datetime.utcfromtimestamp(current_interval_start).strftime('%Y-%m-%d %H:%M:%S'),
#                         open_price,
#                         high_price,
#                         low_price,
#                         close_price,
#                         volume
#                     ])

#                     # Reset for the next interval
#                     current_interval_start = interval_start
#                     open_price = high_price = low_price = close_price = price
#                     volume = qty
#                 else:
#                     # Update values within the same interval
#                     high_price = max(high_price, price)
#                     low_price = min(low_price, price)
#                     close_price = price
#                     volume += qty

#             # Write any remaining data for the last interval
#             if current_interval_start is not None:
#                 ohlcv_3s_data.append([
#                     datetime.utcfromtimestamp(current_interval_start).strftime('%Y-%m-%d %H:%M:%S'),
#                     open_price,
#                     high_price,
#                     low_price,
#                     close_price,
#                     volume
#                 ])

#             # Write aggregated data to CSV
#             for row in ohlcv_3s_data:
#                 writer.writerow(row)

#             # Move start time to the timestamp of the last trade to continue fetching
#             current_start_time = data[-1]['T'] + 1  # Increment by 1 millisecond to avoid overlap
#         else:
#             print("Failed to fetch data:", response.status_code, response.text)
#             break

#         # Respect rate limits by sleeping if necessary
#         time.sleep(1)  # Adjust the sleep time as needed to avoid hitting API rate limits

# print(f"Data successfully saved to {csv_file}")


import ccxt
import time
import csv

import pandas as pd
import uuid
from datetime import datetime

# Initialize the Bybit exchange object
exchange = ccxt.bybit({
    'apiKey': "Of0vXWPStKwGqgym9G",
    'secret': "hlKJSw6PB9z4dIoGCxiRXSgfZUSvmaKm588Q",
})


def convert_to_milliseconds(date_string):
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    timestamp = int(dt.timestamp() * 1000)  # Convert to milliseconds
    return timestamp
# Fetch the trade history for ETH/USDT
def fetch_trade_history(symbol="ETH/USDT:USDT"):
    try:
        # You can adjust the since and limit parameters as needed
        # Fetch the most recent trades
        since = convert_to_milliseconds("2024-11-29 12:00:00")
        trades = exchange.fetch_my_trades(symbol, since=since,limit=100)  # 'limit' can be adjusted to your needs
        return trades
    except Exception as e:
        print(f"Error fetching trade history: {e}")
        return None

# Calculate Net Profit and save every net profit after each trade
def calculate_net_profit(trade_history):
    total_buy_cost = 0
    total_sell_revenue = 0
    net_profit = 0

    for trade in trade_history:
        price = float(trade['price'])
        amount = float(trade['amount'])
        
        # Track buy and sell trades
        if trade['side'] == 'buy':
            total_buy_cost += price * amount
        elif trade['side'] == 'sell':
            total_sell_revenue += price * amount

    # Calculate net profit: revenue from sells - cost from buys
    net_profit = total_sell_revenue - total_buy_cost
    return net_profit

# Save the trade history to a CSV file
def save_to_csv(trade_history, filename="eth_usdt_trade_history.csv"):
    # Specify the column headers
    headers = ["Trade ID", "Symbol", "Price", "Amount", "Side", "Timestamp"]
    
    # Open the file in write mode, create if doesn't exist
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(headers)
        
        # Write each trade record
        for trade in trade_history:
            # Convert timestamp to human-readable format
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(trade['timestamp'] / 1000))
            row = [
                trade['id'],
                trade['symbol'],
                trade['price'],
                trade['amount'],
                trade['side'],
                timestamp
            ]
            writer.writerow(row)
    print(f"Trade history saved to {filename}")

# Fetch trade history for ETH/USDT
trade_history = fetch_trade_history()

if trade_history:
    # Save the trade history to CSV
    save_to_csv(trade_history)
    
    # Calculate net profit
    net_profit = calculate_net_profit(trade_history)
    print(f"Net Profit: {net_profit:.2f} USDT")
else:
    print("No trade history found.")
    
    
df = pd.read_csv("ETH-USDT-USDT_trades_info.csv")
# df = pd.DataFrame(data)

# Define a function to generate the required format
def transform_trade(row):
    # Generate a unique Trade ID using UUID
    trade_id = str(uuid.uuid4())

    # Determine the trade side (buy/sell) based on the open reason
    if "Open long" in row['open_reason']:
        side = "buy"
        price = row['open_price']
    elif "Open short" in row['open_reason']:
        side = "sell"
        price = row['open_price']

    # Convert open and close times to the required format (e.g., "MM/DD/YYYY HH:MM")
    timestamp = datetime.strptime(row['open_time'], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %H:%M")
    timestamp_end = datetime.strptime(row['close_time'], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %H:%M")

    return {
        "Trade ID": trade_id,
        "Symbol": "ETH/USDT:USDT",
        "Price": price,
        "Amount": row['amount'],
        "Side": side,
        "Timestamp": timestamp,
        "Timestamp_end": timestamp_end
    }

# Apply transformation function to each row in the DataFrame
transformed_data = df.apply(transform_trade, axis=1)

# Convert the transformed data to a new DataFrame
transformed_df = pd.DataFrame(transformed_data.tolist())

# Save the result to CSV
transformed_df.to_csv("transformed_trade_history_with_end.csv", index=False)

# Show the transformed DataFrame
print(transformed_df)