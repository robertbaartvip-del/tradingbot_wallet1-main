import ta

class Strategy :
    def __init__(self, params, data) -> None:
        self.data = data
        self.params = params
        
    def BB(self, i):
        self.data[f'bollinger_band_high_{i + 1}'] = self.data["average"] + (self.data['std_dev'] * self.params['bollinger_band_deviation'])
        self.data[f'bollinger_band_low_{i + 1}'] = self.data["average"] - (self.data['std_dev'] * self.params['bollinger_band_deviation'])
        
        # if self.data['volume'].iloc[i] == "3684.66":
        #     raise ValueError(f"{self.data[f'bollinger_band_high_{i + 1}'].iloc[i]} {self.data[f'bollinger_band_low_{i + 1}'].iloc[i]}")
    def RSI(self):
        self.data['rsi'] = ta.momentum.rsi(self.data['close'], window=self.params['rsi_period'])
        self.data['rsi'].fillna(0, inplace=True)

    def ATR(self):
        self.data['atr'] = ta.volatility.average_true_range(self.data['high'], self.data['low'], self.data['close'], window=self.params['atr_period'])
    
    # def MA(self):
    #     self.data['ma'] = ta.trend.sma_indicator(self.data["close"], window=self.params["moving_average_period"]).shift(1)
        
    def KVO(self):
        kvo = ta.volume.KlingerVolumeOscillator(
            high=self.data["high"],
            low=self.data["low"],
            close=self.data["close"],
            volume=self.data["volume"],
            window_fast=self.params["kvo_fast"],
            window_slow=self.params["kvo_slow"],
            window_sign=self.params["kvo_signal"],
        )
        self.data["kvo"] = kvo.kvo()
        self.data["kvo_signal"] = kvo.kvo_signal()
    
    def StochRSI(self):
        stoch = ta.momentum.StochRSIIndicator(
            close=self.data["close"],
            window=self.params["stoch_rsi_rsi_period"],
            smooth1=self.params["stoch_rsi_k"],
            smooth2=self.params["stoch_rsi_d"],
        )
        self.data["stoch_rsi"] = stoch.stochrsi()
        # Use the smoothed %D as signal line
        self.data["stoch_rsi_signal"] = stoch.stochrsi_d()
        
    def calculate_long_sl_price(self, avg_open_price, atr):
        return avg_open_price - avg_open_price * 0.0025
    
    def calculate_short_sl_price(self, avg_open_price, atr):
        return avg_open_price + avg_open_price * 0.0025
        
    def populate_indicators(self):
        if "DCM" == self.params["average_type"]:
            ta_obj = ta.volatility.DonchianChannel(self.data["high"], self.data["low"], self.data["close"], window=self.params["bollinger_band_period"])
            self.data["average"] = ta_obj.donchian_channel_mband().shift(1)
        elif "SMA" == self.params["average_type"]:
            self.data["average"] = self.data['close'].rolling(window=self.params["bollinger_band_period"]).mean()
            self.data['std_dev'] = self.data['close'].rolling(window=self.params["bollinger_band_period"] ).std(ddof=0)
        elif "EMA" == self.params["average_type"]:
            self.data["average"] = ta.trend.ema_indicator(self.data["close"], window=self.params["bollinger_band_period"]).shift(1)
        elif "WMA" == self.params["average_type"]:
            self.data["average"] = ta.trend.wma_indicator(self.data["close"], window=self.params["bollinger_band_period"]).shift(1)
        else:
            raise ValueError(f"The average type {self.params['average_type']} is not supported")

        self.RSI()
        self.ATR()
        # self.MA()
        self.KVO()
        self.StochRSI()

        for i, e in enumerate(self.params["envelopes"]):
            self.BB(i)
        
        return self.data
            
    def check_entry_condition(self, side, row, i, break_point_price):
        if side == "long":
            if row['rsi'] >= self.params['rsi_oversold_level'] and break_point_price == 1:
                break_point_price = 2
            if (row['kvo'] > row['kvo_signal'] or row['stoch_rsi'] > row['stoch_rsi_signal']) and break_point_price == 2:
                break_point_price = 0
                return True, break_point_price
            # if row['close'] <= row[f'bollinger_band_low_{i + 1}'] and row['rsi'] < self.params['rsi_oversold_level']:
            if row['close']  <= row[f'bollinger_band_low_{i + 1}'] and row['rsi'] < self.params['rsi_oversold_level']:
            #     if break_point_price == 0:
            #         break_point_price = row['close']
            # elif row['rsi'] >=self.params['rsi_oversold_level']:
            #     if break_point_price <= row['close'] and not break_point_price == 0:
            #         break_point_price = 0
            #         return True, break_point_price
            #     else:
            #         break_point_price = 0
                break_point_price = 1
        
        elif side == "short":
            if row['rsi'] <= self.params['rsi_overbought_level'] and break_point_price == 1:
                break_point_price = 2
            if (row['kvo'] < row['kvo_signal'] or row['stoch_rsi'] < row['stoch_rsi_signal']) and break_point_price == 2:
                break_point_price = 0
                return True, break_point_price
            if row['close']  >= row[f'bollinger_band_high_{i + 1}'] and row['rsi'] > self.params['rsi_overbought_level']:
            #     if break_point_price == 0 :
            #         break_point_price = row['close']
            # elif row['rsi'] <= self.params['rsi_overbought_level']:
            #     if break_point_price >= row['close'] and not break_point_price == 0:                
            #         break_point_price = 0
            #         return True, break_point_price          
            #     else:
            #         break_point_price = 0
                break_point_price = 1
  
        return False, break_point_price
    
    def calc_sl_backtest(self, row, position, order_price, num):
        close = row['close']
        atr = row['atr']
        
        if position.side == 'long':
            if position.sl_price >= position.open_price:          
                if close >= order_price:
                    for i in range(1, 100):
                        if close - position.sl_price < position.open_price * 0.0005:
                            break
                        position.sl_price += position.open_price * 0.0005
                    order_price = close
                        
            elif position.open_price * 0.0025 <= close - position.open_price:
                position.sl_price = position.open_price + position.open_price * 0.0025
                for i in range(1, 100):
                    if close - position.sl_price < position.open_price * 0.0005:
                        break
                    position.sl_price += position.open_price * 0.0005
                order_price = close
        
        elif position.side == 'short':
            if position.sl_price <= position.open_price:
                if close <= order_price:
                    for i in range(1, 100):
                        if position.sl_price - close < position.open_price * 0.0005:
                            break
                        position.sl_price -= position.open_price * 0.0005
                    order_price = close
            elif position.open_price * 0.0025 <= position.open_price - close:
                position.sl_price = position.open_price - position.open_price * 0.0025
                for i in range(1, 100):
                    if position.sl_price - close < position.open_price * 0.0005:
                        break
                    position.sl_price -= position.open_price * 0.0005
                order_price = close
        
        return order_price
    
    def calc_sl_livebot(self, side, row, entry_price, trigger_price, order_num):
        order_num_change = False
        
        if side == 'long':
            close_side = 'sell'
            if not trigger_price == 0:
                stop_loss_price = trigger_price
            else:
                stop_loss_price = self.calculate_long_sl_price(entry_price, float(row['atr']))
                trigger_price = self.calculate_long_sl_price(entry_price, float(row['atr']))
                
            if trigger_price >= entry_price:
                if float(row['close']) >= float(self.data['close'].iloc[-order_num]):
                    stop_loss_price = float(row['close']) - float(row['atr']) * 0.5
                    order_num = 2
                    order_num_change = True
            elif float(row['atr']) * 0.5 <= float(row['close']) - entry_price:
                # stop_loss_price = entry_price
                stop_loss_price = float(row['close']) + float(row['atr']) * 0.5
                order_num = 2
                order_num_change = True
        elif side == 'short':
            close_side = 'buy'
            if not trigger_price == 0: 
                stop_loss_price = trigger_price
            else:
                stop_loss_price = self.calculate_short_sl_price(entry_price, float(row['atr']))
                trigger_price = self.calculate_short_sl_price(entry_price, float(row['atr']))
            stop_loss_price = trigger_price
            
            if trigger_price <= entry_price:
                if float(row['close']) <= float(self.data['close'].iloc[-order_num]):
                    stop_loss_price = float(row['close']) + float(row['atr']) * 0.5
                    order_num = 2
                    order_num_change = True
            elif float(row['atr']) * 0.5 <= entry_price - float(row['close']):
                # stop_loss_price = entry_price
                stop_loss_price = float(row['close']) + float(row['atr']) * 0.5
                order_num = 2
                order_num_change = True
                    
        if not order_num_change:
            order_num += 1
            
        return close_side, stop_loss_price, order_num
    