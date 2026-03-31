import sys
import pandas as pd
from datetime import datetime

from . import tools as ut
from strategies.strategy import Strategy


class Backtest:
    def __init__(self, params, ohlcv) -> None:
        self.params = params
        self.data = ohlcv.copy()
        # self.data_15 = ohlcv_15.copy()
        self.strategy = Strategy(self.params, self.data)

        self.data = self.strategy.populate_indicators()
        # self.set_trade_mode()
        self.good_to_trade = True
        self.position_was_closed = False
        self.n_bands_hit = 0
        self.num = 0
        self.order_price = 0
        self.break_point_price_short = 0
        self.break_point_price_long = 0
        self.trade_num = 0
        self.time = 0
        self.timethreshold = False
        self.rsi_high = 0
        self.rsi_low = 0

    # --- Positions ---
    def evaluate_orders(self, time, row):
        if not self.time == datetime.date(time):
            self.time = datetime.date(time)
        # if datetime.time(time).hour == 3 and self.timethreshold == False:
        #     self.timethreshold = True
        self.position_was_closed = False
        self.good_to_trade = True

        if self.position.side == "long":
            if self.rsi_high == 0 or self.rsi_high < self.data['rsi'].iloc[self.num - 2]:
                self.rsi_high = self.data['rsi'].iloc[self.num - 2]
                
            elif self.position.check_for_sl(row):
                self.close_trade(time, row['close'], "SL long")
                self.good_to_trade = False
                self.n_bands_hit = 0
                self.rsi_high = 0
                self.break_point_price_long = 0
                self.break_point_price_short = 0
                
            else:
                self.order_price = self.strategy.calc_sl_backtest(row, self.position, self.order_price, self.num)
            

        elif self.position.side == "short":
            if self.rsi_low == 0 or self.data['rsi'].iloc[self.num - 2]:
                self.rsi_low = self.data['rsi'].iloc[self.num - 2]
                
            elif self.position.check_for_sl(row) :
                self.close_trade(time, row['close'], "SL short")
                self.good_to_trade = False
                self.n_bands_hit = 0
                self.rsi_low = 0
                self.break_point_price_long = 0
                self.break_point_price_short = 0                
            
            else:
                self.order_price = self.strategy.calc_sl_backtest(row, self.position, self.order_price, self.num)
                    

        if self.good_to_trade and not self.position_was_closed:
            balance = self.balance
            for i in range(self.n_bands_hit, len(self.params["envelopes"])):
                
                price_long = price_short = row['close']
                atr = row['atr']

                check_long, self.break_point_price_long = self.strategy.check_entry_condition("long", row, i, self.break_point_price_long)
                check_short, self.break_point_price_short = self.strategy.check_entry_condition("short", row, i, self.break_point_price_short)
                start_trading = check_long or check_short

                if self.position.side != "short" and check_long:
                    side = "long"
                    price = price_long
                    sl_price_calc = self.strategy.calculate_long_sl_price
                elif self.position.side != "long" and check_short:
                    side = "short"
                    price = price_short
                    sl_price_calc = self.strategy.calculate_short_sl_price
                else:
                    continue


                if start_trading:
                    self.last_position_side = side

                    if 'position_size_percentage' in self.params: 
                        # initial_margin = balance * round(self.params['position_size_percentage'] / 100 / len(self.params["envelopes"]), 4)
                        if self.balance > 5000:
                            initial_margin = 5000
                        else:
                            raise ValueError(f"Low Balance  time: {time} balance: {self.balance}")  
                        
                    elif 'position_size_fixed_amount' in self.params:
                        initial_margin = round(self.params['position_size_fixed_amount'] / len(self.params["envelopes"]), 4)

                    self.balance -= initial_margin
                    self.n_bands_hit += 1
                    
                    if i == 0:
                        self.trade_num +=1
                        self.position.open(
                            time,
                            side,
                            initial_margin,
                            price,
                            f"Open {side} {i + 1}",
                            sl_price=sl_price_calc(price, atr),
                        )
                    else:
                        self.position.add(initial_margin, price, f"Open {side} {i + 1}")
                        self.position.sl_price = sl_price_calc(self.position.open_price, atr)


    def close_trade(self, time, price, reason):
        self.position.close(time, price, reason)
        open_balance = self.balance
        self.balance += self.position.initial_margin + self.position.net_pnl
        trade_info = self.position.info()
        trade_info["open_balance"] = open_balance
        trade_info["close_balance"] = self.balance
        del trade_info["tp_price"]
        self.trades_info.append(trade_info)

    # --- Backtest ---
    def run_backtest(self, open_fee_rate, close_fee_rate):
        self.initial_balance = self.params['initial_balance']
        self.balance = self.params['initial_balance']
        self.position = ut.Position(leverage=self.params['leverage'], open_fee_rate=open_fee_rate, close_fee_rate=close_fee_rate)
        self.equity_update_interval = pd.Timedelta(hours=24)

        self.previous_equity_update_time = datetime(1900, 1, 1)
        self.trades_info = []
        self.equity_record = []

        for time, row in self.data.iterrows():
            self.num += 1
            self.evaluate_orders(time, row)
            self.previous_equity_update_time = ut.update_equity_record(
                time,
                self.position,
                self.balance,
                row["close"],
                self.previous_equity_update_time,
                self.equity_update_interval,
                self.equity_record,
                self.trades_info
            )

        self.trades_info = pd.DataFrame(self.trades_info)
        self.equity_record = pd.DataFrame(self.equity_record).set_index("time")
        self.final_equity = round(self.equity_record.iloc[-1]["equity"], 2)

    # --- Save results ---
    def save_equity_record(self, path):
        self.equity_record.to_csv(path+'_equity_record.csv', header=True, index=True)

    def save_trades_info(self, path):
        self.trades_info.to_csv(path+'_trades_info.csv', header=True, index=True)
