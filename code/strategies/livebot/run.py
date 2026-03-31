import os
import sys
import json
import ta
from datetime import datetime
import asyncio
import websockets
import json
import time
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utilities.livebot.exchanges import Exchanges
from strategies.strategy import Strategy

# Resolve config/state paths relative to repo root (not current working directory)
REPO_ROOT = Path(__file__).resolve().parents[3]
base_path = str(REPO_ROOT) + os.sep
params_path = str(REPO_ROOT / "params.json")

def read_tracker_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

params = read_tracker_file(params_path)

tracker_file = base_path + f"tracker_{params['symbol'].replace('/', '-').replace(':', '-')}.json"
tracker_file_txt = base_path + f"tracker_{params['symbol'].replace('/', '-').replace(':', '-')}.txt"
break_point_price_file = base_path + f"break_point_price_{params['symbol'].replace('/', '-').replace(':', '-')}.json"

# --- AUTHENTICATION ---
print(f"\n{datetime.now().strftime('%H:%M:%S')}: >>> starting execution for {params['symbol']}")
exchange = Exchanges(params['exchange'], params.get('credentials'))

data = exchange.fetch_recent_ohlcv(params['symbol'], params['timeframe'], 100).iloc[:-1]
strategy = Strategy(params, data)

# --- TRACKER FILE ---
if not os.path.exists(tracker_file):
    with open(tracker_file, 'w') as file:
        json.dump({"status": "ok_to_trade", "last_side": None, "stop_loss_ids": []}, file)
        
if not os.path.exists(tracker_file_txt):
    with open(tracker_file_txt, 'w') as file:
        json.dump({'start': 'start'}, file)
        file.write('\n')
        
if not os.path.exists(break_point_price_file):
    with open(break_point_price_file, 'w') as file:
        json.dump({'break_point_price_long': 0, 'break_point_price_short': 0, 'trigger_price': 0, 'order_num': 0}, file)

def update_tracker_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def update_tracker_file_txt(file_path, data):
    with open(file_path, 'a') as file:
        json.dump(data, file)
        file.write('\n')
        
def read_break_point_price(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def update_break_point_price(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

start_trading = False
stop_loss_price = 0
position_opened = False

# --- CANCEL OPEN ORDERS ---
orders = exchange.fetch_open_orders(params['symbol'])
for order in orders:
    exchange.cancel_order(order['id'], params['symbol'])
trigger_orders = exchange.fetch_open_trigger_orders(params['symbol'])
long_orders_left = 0
short_orders_left = 0
for order in trigger_orders:
    if order['side'] == 'buy' and order['info']['tradeSide'] == 'open':
        long_orders_left += 1
    elif order['side'] == 'sell' and order['info']['tradeSide'] == 'open':
        short_orders_left += 1
    exchange.cancel_trigger_order(order['id'], params['symbol'])
print(f"{datetime.now().strftime('%H:%M:%S')}: orders cancelled, {long_orders_left} longs left, {short_orders_left} shorts left")

data = strategy.populate_indicators()
row = data.iloc[-1] 

# --- CHECKS IF STOP LOSS WAS TRIGGERED ---
closed_orders = exchange.fetch_closed_trigger_orders(params['symbol'])
tracker_info = read_tracker_file(tracker_file)
if len(closed_orders) > 0 and closed_orders[-1]['id'] in tracker_info['stop_loss_ids']:
    update_tracker_file(tracker_file, {
        "last_side": closed_orders[-1]['info']['side'],
        "status": "stop_loss_triggered",
        "stop_loss_ids": [],
    })
    print(f"{datetime.now().strftime('%H:%M:%S')}: /!\\ stop loss was triggered")


# --- CHECK FOR MULTIPLE OPEN POSITIONS AND CLOSE THE EARLIEST ONE ---
positions = exchange.fetch_open_positions(params['symbol'])
if positions:
    sorted_positions = sorted(positions, key=lambda x: x['timestamp'], reverse=True)
    latest_position = sorted_positions[0]
    for pos in sorted_positions[1:]:
        exchange.flash_close_position(pos['symbol'], side=pos['side'])
        print(f"{datetime.now().strftime('%H:%M:%S')}: double position case, closing the {pos['side']}.")


# --- CHECKS IF A POSITION IS OPEN ---
position = exchange.fetch_open_positions(params['symbol'])
print(position)
open_position = True if len(position) > 0 else False
if open_position:
    position = position[0]
    print(f"{datetime.now().strftime('%H:%M:%S')}: {position['side']} position of {round(position['contracts'] * position['contractSize'],2)} ~ {round(position['contracts'] * position['contractSize'] * position['markPrice'],2)} USDT is running")


# --- CHECKS IF CLOSE ALL SHOULD TRIGGER ---
if 'price_jump_pct' in params and open_position:
    if position['side'] == 'long':
        if float(row['close']) < float(position['info']['entryPrice']) * (1 - params['price_jump_pct']):
            exchange.flash_close_position(params['symbol'])
            update_tracker_file(tracker_file, {
                "last_side": "long",
                "status": "close_all_triggered",
                "stop_loss_ids": [],
            })
            print(f"{datetime.now().strftime('%H:%M:%S')}: /!\\ close all was triggered")

    elif position['side'] == 'short':
        if float(row['close']) > float(position['info']['entryPrice']) * (1 + params['price_jump_pct']):
            exchange.flash_close_position(params['symbol'])
            update_tracker_file(tracker_file, {
                "last_side": "short",
                "status": "close_all_triggered",
                "stop_loss_ids": [],
            })
            print(f"{datetime.now().strftime('%H:%M:%S')}: /!\\ close all was triggered")


price = read_break_point_price(break_point_price_file)
break_point_price_short = float(price['break_point_price_short'])
break_point_price_long = float(price['break_point_price_long'])
trigger_price = float(price['trigger_price'])
order_num = int(price['order_num'])
now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")


# --- OK TO TRADE CHECK ---
tracker_info = read_tracker_file(tracker_file)
print(f"{datetime.now().strftime('%H:%M:%S')}: okay to trade check, status was {tracker_info['status']}")
last_price = float(row['close'])
resume_price = row['average'] 
if position:
    if ('long' == position['side'] and last_price >= resume_price) or ('short' == position['side'] and last_price <= resume_price):
        print("POSITION is OK")
    if ('long' == position['side'] and last_price < resume_price) or ('short' == position['side'] and last_price > resume_price):
        print("POSITION is BAD")
if tracker_info['status'] != "ok_to_trade":
    if ('long' == tracker_info['last_side'] or 'BUY' == tracker_info['last_side'] and last_price >= resume_price) or (
            'short' == tracker_info['last_side'] or 'SELL' == tracker_info['last_side'] and last_price <= resume_price):
        update_tracker_file(tracker_file, {"status": "ok_to_trade", "last_side": tracker_info['last_side']})
        print(f"{datetime.now().strftime('%H:%M:%S')}: status is now ok_to_trade")
    else:
        print(f"{datetime.now().strftime('%H:%M:%S')}: <<< status is still {tracker_info['status']}")
        sys.exit()


# --- SET POSITION MODE, MARGIN MODE, LEVERAGE ---
if not open_position:
    exchange.set_margin_mode(params['symbol'], margin_mode=params['margin_mode'])
    exchange.set_leverage(params['symbol'], margin_mode=params['margin_mode'], leverage=params['leverage'])


# --- IF OPEN POSITION CHANGE TP AND SL ---
if open_position:
    print("position_opened")

else:
    
    long_ok, break_point_price_long = strategy.enter_trading_weight("long", row, 0, break_point_price_long)
    short_ok, break_point_price_short = strategy.enter_trading_weight("short", row, 0, break_point_price_short)
    start_trading = long_ok or short_ok
    info = {
        "status": "ok_to_trade",
        "last_side": tracker_info['last_side'],
        "stop_loss_ids": [],
    }

def cancel_position(entry_price, row, price, side, amount, order_num):
    position_opened = True
    # entry_price = float(position['info']['entryPrice'])
    close_side, stop_loss_price, order_num = strategy.calc_sl_livebot(side, row, entry_price, trigger_price, order_num)

    # amount = position['contracts'] * position['contractSize']

    end = False
    if close_side == "buy":
        if stop_loss_price < price:
           end = True
    elif close_side == "sell":
        if stop_loss_price > price:
            end = True

    if end:
        position_opened = False
        exchange.place_market_order(
            symbol=params['symbol'],
            side=close_side,
            amount=amount,
            reduce=True
        )
    
    # info = {
    #     "status": "ok_to_trade",
    #     "last_side": position['side'],
    #     "stop_loss_ids": [],
    # }
    # print(f"{datetime.now().strftime('%H:%M:%S')}: placed close {position['side']} orders: exit price , sl price {stop_loss_price}")
    return position_opened
# --- FETCHING AND COMPUTING BALANCE ---
# balance = params['balance_fraction'] * params['leverage'] * exchange.fetch_balance()['USDT']['total']
trading_balance = params['initial_balance'] / params['leverage']
balance = trading_balance if exchange.fetch_balance()['USDT']['total'] > trading_balance else sys.exit()
print(f"{datetime.now().strftime('%H:%M:%S')}: the trading balance is {balance}")

# --- PLACE ORDERS DEPENDING ON HOW MANY BANDS HAVE ALREADY BEEN HIT ---

range_longs = range(1)
range_shorts = range(1)

if start_trading:
    if open_position:    
        long_ok = False
        short_ok = False
        range_longs = range(len(params['envelopes']) - long_orders_left, len(params['envelopes']))
        range_shorts = range(len(params['envelopes']) - short_orders_left, len(params['envelopes']))
    else:
        range_longs = range(len(params['envelopes']))
        range_shorts = range(len(params['envelopes']))
else:
    long_ok = False
    short_ok = False

if not params['use_longs']:
    long_ok = False

if not params['use_shorts']:
    short_ok = False

print(start_trading, long_ok, short_ok)

if True:
    for i in range_longs:
        amount = balance / len(params['envelopes']) / row[f'bollinger_band_low_{i + 1}']
        min_amount = exchange.fetch_min_amount_tradable(params['symbol'])
        if amount >= min_amount:
            
            # entry           
            created_position = exchange.place_market_order(
                symbol=params['symbol'],
                side='buy',
                amount=amount
            )
            
            entry_price = float(created_position['info']['avgPrice'])
            
            stop_loss_price = strategy.calculate_long_sl_price(entry_price, row['atr'])
            order_num = 2
            position_opened = True
            
            # sl
            # sl_order = exchange.place_trigger_market_order(
            #     symbol=params['symbol'],
            #     side='sell',
            #     amount=amount,
            #     trigger_price=entry_price,
            #     reduce=True,
            #     print_error=True
            # )
            
            url = "wss://stream.binancefuture.com/ws/btcusdt@trade"
            
            
            async def bybit_websocket():
                # Connect to Bybit's public WebSocket endpoint for linear futures
                url = "wss://stream.bybit.com/v5/public/linear"
                # url = "wss://stream.binancefuture.com/ws/btcusdt@trade"
                async with websockets.connect(url) as websocket:
                    subscribe_message = {
                        "op": "subscribe",
                        "args": ["tickers.BTCUSDT"]
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    last_print_time = time.time()
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        
                        # Extract and display the price every 5 seconds
                        if isinstance(data, dict) and "p" in data:  # 'p' is the field for price in Binance trade data
                            price = data["p"]
                            current_time = time.time()
                            if current_time - last_print_time >= 5:
                                data = exchange.fetch_recent_ohlcv(params['symbol'], params['timeframe'], 100).iloc[:-1]
                                strategy = Strategy(params, data)
                                data = strategy.populate_indicators()
                                row = data.iloc[-1] 
                                print(f"Real-Time Price (every 5s): {price}")
                                position_opened = cancel_position(entry_price, row, float(price), "long", amount, order_num)
                                print(position_opened)
                                if not position_opened:
                                    break
                                last_print_time = current_time

                    await websocket.close()

            # Run the WebSocket client
            asyncio.run(bybit_websocket())

            # info["stop_loss_ids"].append(sl_order['id'])
            print(f"{datetime.now().strftime('%H:%M:%S')}: placed sl long trigger market order of {amount}")
        else:
            print(f"{datetime.now().strftime('%H:%M:%S')}: /!\\ long orders not placed for envelope {i+1}, amount {amount} smaller than minimum requirement {min_amount}")

if start_trading and short_ok:
    for i in range_shorts:
        amount = balance / len(params['envelopes']) / row[f'bollinger_band_high_{i + 1}']
        min_amount = exchange.fetch_min_amount_tradable(params['symbol'])
        if amount >= min_amount:
            # entry     
            created_position = exchange.place_market_order(
                symbol=params['symbol'],
                side='sell',
                amount=amount
            )
            
            price = float(created_position['info']['avgPrice'])
            
            stop_loss_price = strategy.calculate_short_sl_price(price, row['atr'])
            order_num = 2
            position_opened = True
            
            # sl
            sl_order = exchange.place_trigger_market_order(
                symbol=params['symbol'],
                side='buy',
                amount=amount,
                trigger_price=price,
                reduce=True,
                print_error=True
            )
            # info["stop_loss_ids"].append(sl_order['id'])
            print(f"{datetime.now().strftime('%H:%M:%S')}: placed sl short trigger market order of {amount}")
        else:
            print(f"{datetime.now().strftime('%H:%M:%S')}: /!\\ short orders not placed for envelope {i+1}, amount {amount} smaller than minimum requirement {min_amount}")
            
update_tracker_file(tracker_file, info)
update_tracker_file_txt(tracker_file_txt, {'time': formatted_time, 'close': row['close'], 'atr': row['atr'], 'BB_l': row[f'bollinger_band_low_1'], 'BB_h': row[f'bollinger_band_high_1'], 'rsi': row['rsi'], 'break_point_price_long': break_point_price_long, 'break_point_price_short': break_point_price_short, 'trigger_price': stop_loss_price, 'position_opened': position_opened})
update_break_point_price(break_point_price_file, {
    'break_point_price_short': break_point_price_short,
    'break_point_price_long': break_point_price_long,
    'trigger_price': stop_loss_price,
    'order_num': order_num
})

print(f"{datetime.now().strftime('%H:%M:%S')}: <<< all done")
