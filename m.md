Yes, it’s possible to get the **order book volume** by buy and sell sides using the **exchange’s API**, as most exchanges provide **order book data** broken down by buy and sell orders (bids and asks). The order book shows the current buy and sell orders at various price levels, which can give insights into **market depth, liquidity**, and potential **support/resistance levels**.
Here’s how to access the order book data, including the buy (bid) and sell (ask) volumes, and how you might use it in a trading bot.

---

### **1. Fetching Order Book Data via API**

Most exchanges, like **Binance, Bybit, and Kraken**, provide endpoints for accessing order book data. This data typically includes:

- **Price**: The price level of each order.
- **Volume**: The quantity of the asset available to buy or sell at that price level.
  For example, with **Binance API**, you can use the `depth` endpoint to get the order book.

#### **Example: Fetching Order Book Data from Binance**

To get the top order book levels from Binance, you can use the `depth` endpoint, which provides both **bid (buy) and ask (sell) volumes**:

```python
from binance.client import Client
# Initialize Binance client with your API keys
api_key = “YOUR_API_KEY”
api_secret = “YOUR_API_SECRET”
client = Client(api_key, api_secret)
def get_order_book(symbol, limit=10):
    “”"
    Fetches order book data for a given trading pair.
    Parameters:
        symbol (str): Trading pair symbol, e.g., ‘ETHUSDT’.
        limit (int): Number of levels to fetch from the order book (default is 10).
    Returns:
        dict: Order book data with bids and asks.
    “”"
    try:
        order_book = client.get_order_book(symbol=symbol, limit=limit)
        return order_book
    except Exception as e:
        print(f”Error fetching order book: {e}“)
        return None
```

### **Understanding Order Book Data**

The returned `order_book` data will contain:

- **Bids**: A list of buy orders (price and quantity) arranged from highest to lowest price.
- **Asks**: A list of sell orders (price and quantity) arranged from lowest to highest price.
  Each entry in `bids` and `asks` represents:
- **[Price, Quantity]**

#### Example Output

For an example symbol like `ETHUSDT`, the response for a 10-level order book might look like this:

```json
{
  “bids”: [
    [“2000.00", “1.5”],  # Buy order: price $2000, quantity 1.5 ETH
    [“1999.50", “0.8”],
    ...
  ],
  “asks”: [
    [“2000.50”, “1.2"],  # Sell order: price $2000.50, quantity 1.2 ETH
    [“2001.00”, “0.6"],
    ...
  ]
}
```

### **2. Summing Buy and Sell Volumes**

To get the **total buy and sell volume** at the top `N` levels in the order book:

```python
def get_buy_sell_volumes(order_book, levels=10):
    “”"
    Sums up buy (bid) and sell (ask) volumes at the specified number of levels.
    Parameters:
        order_book (dict): Order book data from the exchange.
        levels (int): Number of top levels to calculate volumes for.
    Returns:
        tuple: Total buy volume and total sell volume.
    “”"
    buy_volume = sum(float(bid[1]) for bid in order_book[‘bids’][:levels])
    sell_volume = sum(float(ask[1]) for ask in order_book[‘asks’][:levels])
    return buy_volume, sell_volume
```

#### Example Usage

```python
symbol = “ETHUSDT”
order_book = get_order_book(symbol, limit=10)
buy_volume, sell_volume = get_buy_sell_volumes(order_book, levels=10)
print(f”Top 10 Buy Volume: {buy_volume}“)
print(f”Top 10 Sell Volume: {sell_volume}“)
```

This will output the total **buy volume** and **sell volume** at the top 10 levels in the order book.

### **3. Using Buy/Sell Volumes for Trading Decisions**

The buy and sell volumes can give insights into **market sentiment and potential price direction**:

- **High Buy Volume**: If buy volume exceeds sell volume at the top levels, it might indicate strong buying interest and potential support, which could lead to upward pressure on price.
- **High Sell Volume**: If sell volume exceeds buy volume, it might indicate selling pressure and potential resistance, signaling downward pressure.
  In a trading bot, you could use this data to:
- **Confirm Trades**: Enter long positions when buy volume is significantly higher than sell volume, or short positions when sell volume dominates.
- **Identify Reversal Points**: High sell volume near a recent high could indicate a reversal, while high buy volume near a recent low could signal a potential bounce.

### **4. Example: Using Order Book Volumes in a Bot’s Trade Confirmation**

Here’s a simplified example of how you might integrate buy and sell volume checks into your bot’s trading logic:

```python
def confirm_trade_with_order_book(symbol, limit=10, volume_threshold=1.5):
    “”"
    Confirms trade direction based on buy and sell order book volumes.
    Parameters:
        symbol (str): Trading pair symbol.
        limit (int): Number of levels to check in the order book.
        volume_threshold (float): Ratio threshold between buy and sell volumes.
    Returns:
        str: ‘BUY’, ‘SELL’, or None if no clear direction.
    “”"
    order_book = get_order_book(symbol, limit=limit)
    if not order_book:
        return None
    buy_volume, sell_volume = get_buy_sell_volumes(order_book, levels=limit)
    # Example logic: Check if buy volume is significantly higher than sell volume
    if buy_volume / sell_volume > volume_threshold:
        return “BUY”  # Indicates stronger buy-side interest
    elif sell_volume / buy_volume > volume_threshold:
        return “SELL”  # Indicates stronger sell-side interest
    else:
        return None  # No clear confirmation
```

In this function:

- We check the ratio between **buy and sell volumes**.
- If the **buy volume is 1.5 times the sell volume**, we interpret it as strong buy interest and consider a **BUY** signal.
- Conversely, if the **sell volume is 1.5 times the buy volume**, we consider a **SELL** signal.
  This approach helps confirm trade direction based on real-time order book dynamics.

---

### **Additional Considerations**

1. **Frequency of Order Book Checks**:
   - Fetching the order book frequently is essential for accuracy but can also consume API rate limits. Balance frequency with rate limits to avoid reaching API caps.
2. **Depth of Analysis**:
   - Checking more levels (e.g., top 20 or 50 levels) provides a broader view of market sentiment but may dilute immediate price action signals. Adjust levels based on the trading strategy.
3. **Combining with Other Indicators**:
   - Use order book volume analysis with indicators like **RSI, Bollinger Bands,** or **MACD** to get a clearer overall picture of market direction.
     Using order book volume analysis effectively can provide a **short-term edge** by understanding immediate market dynamics, helping you optimize trade entries and exits in an automated strategy. Let me know if you’d like further help with integrating order book data or using it alongside other indicators!

## Parameters

```python
params = {
    'symbol': 'BTC/USDT:USDT',
    'timeframe': '300',
    'margin_mode': 'isolated',  # 'cross'
    'leverage': 1,
    'average_type': 'SMA',  # 'SMA', 'EMA', 'WMA', 'DCM'
    'envelopes': [0.07],
    'use_longs': True,
    'use_shorts': True,
    'bollinger_band_period': 20,
    'bollinger_band_deviation': 2.0,
    'rsi_period': 7,
    'rsi_overbought_level': 70,
    'rsi_oversold_level': 30,
    'atr_period': 14,
    'stop_loss_multiplier': 1.5,
    'moving_average_period': 50,
    ###############################
    'exchange': 'binance',
    'credentials': {
        'apiKey': '8cbf3e501e15b49e2f3743f63ea99b8ecb6317f00bd2d018e9d84708bfa3d528',
        'secret': '50aaa177085727d8074035e0b4e44d6c1c8a099274182cc1f6c4c34479e9cc5b',
        'enableRateLimit': True
    },
    'order_size': 2000
}

```
