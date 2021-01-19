import logging


class Logger(object):
    __logger = None

    @staticmethod
    def init():
        Logger.__logger = logging.getLogger("TradeLogger")
        Logger.__logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        fh = logging.FileHandler("log.txt")
        fh.setFormatter(formatter)
        Logger.__logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        Logger.__logger.addHandler(ch)

    @staticmethod
    def __throw_if_uninitialized():
         if Logger.__logger is None:
             raise Exception("Logger isnt initialized")

    @staticmethod
    def cleanup():
        Logger.__throw_if_uninitialized()
        logging.shutdown()

    @staticmethod
    def debug(msg):
        Logger.__throw_if_uninitialized()
        Logger.__logger.debug(msg)

    @staticmethod
    def info(msg):
        Logger.__throw_if_uninitialized()
        Logger.__logger.info(msg)

    @staticmethod
    def error(msg):
        Logger.__throw_if_uninitialized()
        Logger.__logger.error(msg)

    @staticmethod
    def exception(msg):
        Logger.__throw_if_uninitialized()
        Logger.__logger.exception(msg)

    @staticmethod
    def buy(price, amount):
        Logger.__throw_if_uninitialized()
        Logger.__logger.info(f"BUY => Price: {price}, Amount: {amount}")

    @staticmethod
    def sell(price, amount, est_profit_percent, est_profit, est_profit_total):
        Logger.__throw_if_uninitialized()
        Logger.__logger.info(f"SELL => Price: {price}, Amount: {amount}, Estimated Profit Percent: {est_profit_percent}%, Estimated Profit: {est_profit}, Estimated Profit Total: {est_profit_total}")
