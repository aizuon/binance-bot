import argparse
import atexit

from trader import Trader
from trade_logger import Logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, help="Symbol to trade", default="BTCUSDT")
    parser.add_argument("--amount", type=float, help="Quantity of assets to trade", default=argparse.SUPPRESS)
    parser.add_argument("--key", type=str, help="API key", required=True)
    parser.add_argument("--secret", type=str, help="API secret", required=True)
    opt = parser.parse_args()

    Logger.init()
    atexit.register(Logger.cleanup)

    try:
        trader = Trader(opt)

        trader.loop()
    except Exception as e:
        Logger.exception("Exception caught")
        exit(1)
