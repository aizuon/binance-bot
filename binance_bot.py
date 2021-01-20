import argparse
import atexit
from time import sleep

from trader import Trader
from trade_logger import Logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, nargs='+', help="Symbol(s) to trade", default=["BTCUSDT"])
    parser.add_argument("--amount", type=float, help="Quantity of asset to trade", default=argparse.SUPPRESS)
    parser.add_argument("--key", type=str, help="API key", required=True)
    parser.add_argument("--secret", type=str, help="API secret", required=True)
    opt = parser.parse_args()

    Logger.init()
    atexit.register(Logger.cleanup)
    atexit.register(Trader.cleanup)

    try:
        for symbol in opt.symbol:
            setattr(opt, "current_symbol", symbol)
            trader = Trader(opt)

            trader.start()

        while True:
            sleep(1)
    except Exception:
        Logger.exception("Exception caught")
        exit(1)
