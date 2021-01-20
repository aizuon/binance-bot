import datetime as dt
import math
from decimal import Decimal
import asyncio
import requests

import pandas as pd
from binance.client import Client
from ta.trend import ema_indicator
from beepy import beep

from trade_logger import Logger


class Trader(object):
    __date_open = "date_open"
    __open = "open"
    __high = "high"
    __low = "low"
    __close = "close"
    __volume = "volume"
    __date_close = "date_close"
    __volume_asset = "volume_asset"
    __trades = "trades"
    __volume_asset_buy = "volume_asset_buy"
    __volume_asset_sell = "volume_asset_sell"
    __ignore = "ignore"

    __buy_string = "Buy"
    __sell_string = "Sell"

    __client = None

    __symbols = []

    __comission = 0.001
    __safety_factor = 0.1

    def __init__(self, opt):
        super().__init__()

        if Trader.__client is None:
            Trader.__client = Client(opt.key, opt.secret)
            Logger.info("Started")

        if opt.current_symbol in Trader.__symbols:
            raise Exception("Symbol already added")

        Trader.__symbols.append(opt.current_symbol)
        self.__symbol_idx = len(Trader.__symbols) - 1

        self.__last_hour = None
        self.__daily_ema = 0
        self.__bought_price = 0
        self.__have_quantity = 0
        self.est_profit_total = 0

        self.__normal_tick = 5
        self.__hour_tick = 10

        self.__buy_signals = 0
        self.__sell_signals = 0
        self.__buy_threshold = 3 * 60 // self.__normal_tick
        self.__sell_threshold = 2 * 60 // self.__normal_tick
        self.__notification_modulo_buy = self.__buy_threshold // 10
        self.__notification_modulo_sell = self.__sell_threshold // 10
        self.__notification_sound = "coin"

        symbol_info = Trader.__client.get_symbol_info(Trader.__symbols[self.__symbol_idx])
        if symbol_info is None:
            raise Exception(f"Symbol {Trader.__symbols[self.__symbol_idx]} not found")

        filters = symbol_info["filters"]

        min_filter = [f for f in filters if f["filterType"] == "MIN_NOTIONAL"]
        if len(min_filter) == 1:
            min_notional = float(min_filter[0]["minNotional"])
            if hasattr(opt, "amount"):
                if opt.amount * (1 - Trader.__comission) < min_notional:
                    raise Exception(f"Specified amount is less than minimum trade asset for symbol {Trader.__symbols[self.__symbol_idx]}")
                elif opt.amount * (1 - (Trader.__safety_factor +Trader.__comission)) < min_notional:
                    raise Exception(f"Specified amount with safety factor is less than minimum trade asset for symbol {Trader.__symbols[self.__symbol_idx]}")
                else:
                    self.__buy_amount_currency = opt.amount
            else:
                self.__buy_amount_currency = (min_notional + (min_notional * (Trader.__safety_factor - Trader.__comission))) # (1 + (Trader.__safety_factor - commission)) causes fpe
        else:
            if hasattr(opt, "amount"):
                self.__buy_amount_currency = opt.amount
            else:
                raise Exception(f"Trade asset amount isnt set and min filter doesnt exist for symbol {Trader.__symbols[self.__symbol_idx]}")
        
        lot_filter = [f for f in filters if f["filterType"] == "LOT_SIZE"]
        if len(lot_filter) == 1:
            self.__precision = int(round(-math.log(float(lot_filter[0]["stepSize"]), 10), 0))
        else:
            self.__precision = 6

        Logger.info(f"Working for {Trader.__symbols[self.__symbol_idx]} pair with {self.__buy_amount_currency} assets")

    async def loop(self):
            now = dt.datetime.now()
            if self.__last_hour != now.hour:
                await asyncio.sleep(self.__hour_tick)

                day_prices = self.__get_past_candles(Client.KLINE_INTERVAL_1HOUR, 48)
                day_prices_close = day_prices[Trader.__close]
                if len(day_prices_close.array) != 48:
                    return
                self.__daily_ema = float(ema_indicator(day_prices_close, 24).array[-2])
                Logger.debug(f"{Trader.__symbols[self.__symbol_idx]} Current Price: {day_prices_close.array[-1]}, Daily EMA: {self.__daily_ema}")

                self.__last_hour = now.hour
            else:
                await asyncio.sleep(self.__normal_tick)

                last_prices = self.__get_past_candles(Client.KLINE_INTERVAL_1HOUR, 2)
                last_prices_close = last_prices[Trader.__close]
                if len(last_prices_close.array) != 2:
                    return
                current_price = float(last_prices_close.array[1])
                last_price = float(last_prices_close.array[0])

                if last_price < self.__daily_ema and current_price > self.__daily_ema:
                    self.__reset_and_log_sell_signal(last_price, current_price)
                    if self.__have_quantity == 0:
                        self.__increment_and_log_buy_signal(last_price, current_price)
                elif current_price < self.__daily_ema:
                    self.__reset_and_log_buy_signal(last_price, current_price)
                    if self.__have_quantity != 0:
                        self.__increment_and_log_sell_signal(last_price, current_price)

                if self.__buy_signals >= self.__buy_threshold:
                    Logger.debug(f"Buying {Trader.__symbols[self.__symbol_idx]}")

                    quantity = round(Decimal((self.__buy_amount_currency - (Trader.__comission * self.__buy_amount_currency)) / current_price), self.__precision) # (1 - commission) causes fpe
                    try:
                        Trader.__client.create_order(symbol=Trader.__symbols[self.__symbol_idx], side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=quantity)
                    except requests.exceptions.ReadTimeout:
                        Logger.error(f"Timeout buying {Trader.__symbols[self.__symbol_idx]}")
                        return

                    Logger.buy(Trader.__symbols[self.__symbol_idx], current_price, quantity)
                    beep(sound=self.__notification_sound)

                    self.__bought_price = current_price
                    self.__have_quantity = quantity

                    self.__buy_signals = 0
                elif self.__sell_signals >= self.__sell_threshold:
                    Logger.debug(f"Selling {Trader.__symbols[self.__symbol_idx]}")

                    try:
                        Trader.__client.create_order(symbol=Trader.__symbols[self.__symbol_idx], side=Client.SIDE_SELL, type=Client.ORDER_TYPE_MARKET, quantity=self.__have_quantity)
                    except requests.exceptions.ReadTimeout:
                        Logger.error(f"Timeout selling {Trader.__symbols[self.__symbol_idx]}")
                        return

                    price_diff = (current_price - self.__bought_price)
                    est_profit_percent = (((price_diff / self.__bought_price) * 100) - Trader.__comission)
                    est_profit = ((price_diff * self.__have_quantity) * (1 - Trader.__comission))
                    self.est_profit_total += est_profit
                    Logger.sell(Trader.__symbols[self.__symbol_idx], current_price, self.__have_quantity, est_profit_percent, est_profit, self.est_profit_total)
                    beep(sound=self.__notification_sound)

                    self.__bought_price = 0
                    self.__have_quantity = 0

                    self.__sell_signals = 0

    def __reset_and_log_buy_signal(self, last_price, current_price):
        self.__log_reset_signal(Trader.__buy_string, last_price, current_price, self.__buy_signals, self.__buy_threshold)

        self.__buy_signals = 0

    def __reset_and_log_sell_signal(self, last_price, current_price):
        self.__log_reset_signal(Trader.__sell_string, last_price, current_price, self.__sell_signals, self.__sell_threshold)

        self.__sell_signals = 0

    def __log_reset_signal(self, signal, last_price, current_price, signal_count, signal_threshold):
        if signal_count != 0:
            Logger.debug(f"{Trader.__symbols[self.__symbol_idx]} {signal} Signal Reset {signal_count}/{signal_threshold} => Last Price: {last_price}, Current Price: {current_price}, Daily EMA: {self.__daily_ema}")
            beep(sound=self.__notification_sound)

    def __increment_and_log_buy_signal(self, last_price, current_price):
        self.__buy_signals += 1

        self.__log_signal(Trader.__buy_string, last_price, current_price, self.__buy_signals, self.__buy_threshold, self.__notification_modulo_buy)

    def __increment_and_log_sell_signal(self, last_price, current_price):
        self.__sell_signals += 1

        self.__log_signal(Trader.__sell_string, last_price, current_price, self.__sell_signals, self.__sell_threshold, self.__notification_modulo_sell)

    def __log_signal(self, signal, last_price, current_price, signal_count, signal_threshold, signal_notification_modulo):
        if signal_count == 1 or signal_count == signal_threshold or signal_count % signal_notification_modulo == 0:
            Logger.debug(f"{Trader.__symbols[self.__symbol_idx]} {signal} Signal {signal_count}/{signal_threshold}  => Last Price: {last_price}, Current Price: {current_price}, Daily EMA: {self.__daily_ema}")
            beep(sound=self.__notification_sound)

    def __get_past_candles(self, internal, n):
        try:
            data = Trader.__client.get_historical_klines(Trader.__symbols[self.__symbol_idx], internal, f"{n} hours ago UTC")
            candles = pd.DataFrame(data, columns=[Trader.__date_open, Trader.__open, Trader.__high, Trader.__low, Trader.__close, Trader.__volume, Trader.__date_close, Trader.__volume_asset, Trader.__trades, Trader.__volume_asset_buy, Trader.__volume_asset_sell, Trader.__ignore])
        except requests.exceptions.ReadTimeout:
            Logger.error(f"Timeout getting candles for symbol {Trader.__symbols[self.__symbol_idx]}")
            candles = pd.DataFrame(columns=[Trader.__date_open, Trader.__open, Trader.__high, Trader.__low, Trader.__close, Trader.__volume, Trader.__date_close, Trader.__volume_asset, Trader.__trades, Trader.__volume_asset_buy, Trader.__volume_asset_sell, Trader.__ignore])
        
        candles.set_index(Trader.__date_open, inplace=True)

        return candles