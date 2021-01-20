import argparse
import atexit
import asyncio

from trader import Trader
from trade_logger import Logger


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, nargs='+', help="Symbol(s) to trade", default=["BTCUSDT"])
    parser.add_argument("--amount", type=float, help="Quantity of asset to trade", default=argparse.SUPPRESS)
    parser.add_argument("--key", type=str, help="API key", required=True)
    parser.add_argument("--secret", type=str, help="API secret", required=True)
    opt = parser.parse_args()

    Logger.init()
    atexit.register(Logger.cleanup)

    try:
        traders = []
        for symbol in opt.symbol:
            setattr(opt, "current_symbol", symbol)
            trader = Trader(opt)
            traders.append(trader)

        while True:
            await asyncio.gather(*[trader.loop() for trader in traders])
    except Exception:
        Logger.exception("Exception caught")
        exit(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        asyncio.set_event_loop(None)
        loop.close()