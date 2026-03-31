import ccxt
import time
import pandas as pd
from typing import Any, Optional, Dict, List

EXCHANGES: Dict[str, Dict[str, Any]] = {
    # "bitget": {
    #     "exchange_object": ccxt.bitget(config={'enableRateLimit': True}),
    #     "limit_size_request": 200,
    # },
    "binanceusdm": {
        "exchange_object": ccxt.binanceusdm(config={'enableRateLimit': True}),
        "limit_size_request": 1000,  # Based on Binance Futures max limit
    },
    "binance": {
        "exchange_object": ccxt.binance(config={'enableRateLimit': True}),
        "limit_size_request": 1000,
    },
    "bybit": {
        "exchange_object": ccxt.bybit(config={'enableRateLimit': True}),
        "limit_size_request": 200,
    },
    "kucoin": {
        "exchange_object": ccxt.kucoin(config={'enableRateLimit': True}),
        "limit_size_request": 1500,
    },
    "huobi": {
        "exchange_object": ccxt.huobi(config={'enableRateLimit': True}),
        "limit_size_request": 2000,
    },
    "kraken": {
        "exchange_object": ccxt.kraken(config={'enableRateLimit': True}),
        "limit_size_request": 720,
    },
    "okx": {
        "exchange_object": ccxt.okx(config={'enableRateLimit': True}),
        "limit_size_request": 1000,
    }
}

class Exchanges():
    def __init__(self, exchange, api_setup: Optional[Dict[str, Any]] = None) -> None:

        if api_setup == None:
            self.select_exchange(exchange, api_setup)
            self.exchange = exchange
        else:
            # Allow callers to control sandbox mode explicitly.
            # Note: CCXT no longer supports futures sandbox for some exchanges (e.g. binanceusdm).
            sandbox = bool(api_setup.pop("sandbox", False))

            api_setup.setdefault("options", {"defaultType": "future"})
            self.select_exchange(exchange, api_setup)
            self.exchange = exchange
            if sandbox:
                try:
                    self.session.set_sandbox_mode(True)
                except Exception:
                    # If the exchange does not support sandbox, keep running in live mode.
                    pass
            
        self.markets = self.session.load_markets()

    def select_exchange(self, exchange, api_setup):
        if exchange == 'binance':
            self.session = ccxt.binance(api_setup)
        elif exchange == 'binanceusdm':
            self.session = ccxt.binanceusdm(api_setup)
        elif exchange == 'bybit':
            self.session = ccxt.bybit(api_setup)
        elif exchange == 'kucoin':
            self.session = ccxt.kucoin(api_setup)
        elif exchange == 'huobi':
            self.session = ccxt.huobi(api_setup)
        elif exchange == 'kraken':
            self.session = ccxt.kraken(api_setup)
        elif exchange == 'okx':
            self.session = ccxt.okx(api_setup)
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")
    
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        try:
            return self.session.fetch_ticker(symbol)
        except Exception as e:
            raise Exception(f"Failed to fetch ticker for {symbol}: {e}")

    def fetch_min_amount_tradable(self, symbol: str) -> float:
        try:
            return self.markets[symbol]['limits']['amount']['min']
        except Exception as e:
            raise Exception(f"Failed to fetch minimum amount tradable: {e}")        
        
    def amount_to_precision(self, symbol: str, amount: float) -> str:
        try:
            return self.session.amount_to_precision(symbol, amount)
        except Exception as e:
            raise Exception(f"Failed to convert amount {amount} {symbol} to precision", e)

    def price_to_precision(self, symbol: str, price: float) -> str:
        try:
            return self.session.price_to_precision(symbol, price)
        except Exception as e:
            raise Exception(f"Failed to convert price {price} to precision for {symbol}", e)

    def fetch_balance(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        try:
            return self.session.fetch_balance(params)
        except Exception as e:
            raise Exception(f"Failed to fetch balance: {e}")

    def fetch_order(self, id: str, symbol: str) -> Dict[str, Any]:
        try:
            return self.session.fetch_order(id, symbol)
        except Exception as e:
            raise Exception(f"Failed to fetch order {id} info for {symbol}: {e}")

    def fetch_open_orders(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            return self.session.fetch_open_orders(symbol)
        except Exception as e:
            raise Exception(f"Failed to fetch open orders: {e}")

    def fetch_open_trigger_orders(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            return self.session.fetch_open_orders(symbol, params={'stop': True})
        except Exception as e:
            raise Exception(f"Failed to fetch open trigger orders: {e}")

    def fetch_closed_trigger_orders(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            return self.session.fetch_closed_orders(symbol, params={'stop': True})
        except Exception as e:
            raise Exception(f"Failed to fetch closed trigger orders: {e}")

    def cancel_order(self, id: str, symbol: str) -> Dict[str, Any]:
        try:
            return self.session.cancel_order(id, symbol)
        except Exception as e:
            raise Exception(f"Failed to cancel the {symbol} order {id}", e)

    def cancel_trigger_order(self, id: str, symbol: str) -> Dict[str, Any]:
        try:
            return self.session.cancel_order(id, symbol, params={'stop': True})
        except Exception as e:
            raise Exception(f"Failed to cancel the {symbol} trigger order {id}", e)

    def fetch_open_positions(self, symbol: str) -> List[Dict[str, Any]]:
        try:
            positions = self.session.fetch_positions([symbol], params={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'})
            print(positions)
            real_positions = []
            for position in positions:
                if float(position['contracts']) > 0:
                    real_positions.append(position)
            return real_positions
        except Exception as e:
            raise Exception(f"Failed to fetch open positions: {e}")

    def flash_close_position(self, symbol: str, side: Optional[str] = None) -> Dict[str, Any]:
        try:
            return self.session.close_position(symbol, side=side)
        except Exception as e:
            raise Exception(f"Failed to fetch closed order for {symbol}", e)

    def set_margin_mode(self, symbol: str, margin_mode: str = 'isolated') -> None:
        try:
            self.session.set_margin_mode(
                margin_mode,
                symbol,
                params={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'},
            )
        except Exception as e:
            raise Exception(f"Failed to set margin mode: {e}")

    def set_leverage(self, symbol: str, margin_mode: str = 'isolated', leverage: int = 1) -> None:
        try:
            if margin_mode == 'isolated':
                self.session.set_leverage(
                    leverage,
                    symbol,
                    params={
                        'productType': 'USDT-FUTURES',
                        'marginCoin': 'USDT',
                        'holdSide': 'long',
                    },
                )
                self.session.set_leverage(
                    leverage,
                    symbol,
                    params={
                        'productType': 'USDT-FUTURES',
                        'marginCoin': 'USDT',
                        'holdSide': 'short',
                    },
                )
            else:
                self.session.set_leverage(
                    leverage,
                    symbol,
                    params={'productType': 'USDT-FUTURES', 'marginCoin': 'USDT'},
                )
        except Exception as e:
            raise Exception(f"Failed to set leverage: {e}")

    def fetch_recent_ohlcv(self, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
        exchange_fetch_limit = EXCHANGES[self.exchange]['limit_size_request']

        # Accept both:
        # - CCXT timeframes like "1m", "15m", "1h"
        # - Legacy numeric seconds like "60", "900", "3600"
        if isinstance(timeframe, str) and timeframe.isdigit():
            seconds = int(timeframe)
            if seconds % 3600 == 0:
                ccxt_timeframe = f"{seconds // 3600}h"
            elif seconds % 60 == 0:
                ccxt_timeframe = f"{seconds // 60}m"
            else:
                raise ValueError(f"Unsupported numeric timeframe (seconds): {timeframe}")
            timeframe_to_milliseconds = seconds * 1000
        else:
            ccxt_timeframe = str(timeframe)
            timeframe_to_milliseconds = int(self.session.parse_timeframe(ccxt_timeframe) * 1000)

        end_timestamp = int(time.time() * 1000)
        start_timestamp = end_timestamp - (limit * timeframe_to_milliseconds)
        current_timestamp = start_timestamp

        ohlcv_data = []
        while current_timestamp < end_timestamp:
            request_end_timestamp = min(current_timestamp + (exchange_fetch_limit * timeframe_to_milliseconds),
                                        end_timestamp)
            try:
                fetched_data = self.session.fetch_ohlcv(
                    symbol,
                    ccxt_timeframe,
                    params={
                        "startTime": str(current_timestamp),
                        "endTime": str(request_end_timestamp),
                        "limit": exchange_fetch_limit,
                    }
                )
                ohlcv_data.extend(fetched_data)
            except Exception as e:
                raise Exception(f"Failed to fetch OHLCV data for {symbol} in timeframe {timeframe}: {e}")

            current_timestamp += (exchange_fetch_limit * timeframe_to_milliseconds) + 1

        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        return df

    def place_market_order(self, symbol: str, side: str, amount: float, reduce: bool = False) -> Dict[str, Any]:
        try:
            params = {
                'reduceOnly': reduce,
            }
            amount = self.amount_to_precision(symbol, amount)
            return self.session.create_order(symbol, 'market', side, amount, params=params)

        except Exception as e:
            raise Exception(f"Failed to place market order of {amount} {symbol}: {e}")

    def place_limit_order(self, symbol: str, side: str, amount: float, price: float, reduce: bool = False) -> Dict[str, Any]:
        try:
            params = {
                'reduceOnly': reduce,
            }
            amount = self.amount_to_precision(symbol, amount)
            price = self.price_to_precision(symbol, price)
            return self.session.create_order(symbol, 'limit', side, amount, price, params=params)

        except Exception as e:
            raise Exception(f"Failed to place limit order of {amount} {symbol} at price {price}: {e}")

    def place_trigger_market_order(self, symbol: str, side: str, amount: float, trigger_price: float, reduce: bool = False, print_error: bool = False) -> Optional[Dict[str, Any]]:
        try:
            amount = self.amount_to_precision(symbol, amount)
            trigger_price = self.price_to_precision(symbol, trigger_price)
            params = {
                'reduceOnly': reduce,
                'triggerPrice': trigger_price,
            }
            return self.session.create_order(symbol, 'market', side, amount, params=params)
        except Exception as err:
            if print_error:
                print(err)
                return None
            else:
                raise err

    def place_trigger_limit_order(self, symbol: str, side: str, amount: float, trigger_price: float, price: float, reduce: bool = False, print_error: bool = False) -> Optional[Dict[str, Any]]:
        try:
            amount = self.amount_to_precision(symbol, amount)
            trigger_price = self.price_to_precision(symbol, trigger_price)
            price = self.price_to_precision(symbol, price)
            params = {
                'reduceOnly': reduce,
                'triggerPrice': trigger_price,
            }
            return self.session.create_order(symbol, 'limit', side, amount, price, params=params)
        except Exception as err:
            if print_error:
                print(err)
                return None
            else:
                raise err
