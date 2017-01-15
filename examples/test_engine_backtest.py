# encoding: utf-8
try:
    from Queue import PriorityQueue
except ImportError:
    from queue import PriorityQueue

from datetime import datetime
from pymongo import MongoClient
import pandas as pd

import strategy
from bigfishtrader.portfolio.handlers import PortfolioHandler
from bigfishtrader.quotation.handlers import MongoHandler
from bigfishtrader.router.exchange import DummyExchange
from bigfishtrader.engine.core import Engine
from bigfishtrader.backtest.engine_backtest import EngineBackTest
from bigfishtrader.middleware.timer import CountTimer
from bigfishtrader.performance import WindowFactorPerformance
from bigfishtrader.data_support.mongo_data_support import MongoDataSupport
from bigfishtrader.portfolio.context import Context


def run_backtest(collection, ticker, start, end, period='D'):
    event_queue = PriorityQueue()
    portfolio_handler = PortfolioHandler(event_queue)
    data_support = MongoDataSupport(**{'.'.join([ticker, period]): collection})
    price_handler = MongoHandler(collection, ticker, event_queue, fetchall=True, data_support=data_support)
    router = DummyExchange(event_queue, price_handler)
    context = Context()
    context.ticker = ticker
    engine = Engine(event_queue=event_queue)
    timer = CountTimer()
    timer.register(engine)
    backtest = EngineBackTest(
        event_queue, engine, strategy,
        price_handler, portfolio_handler,
        router, data_support, context
    )
    portfolio = backtest.run(start, end)
    history = pd.DataFrame(portfolio.history)
    performance = WindowFactorPerformance()
    performance.set_equity(pd.Series(history["equity"].values, index=history["datetime"]))
    print(performance.ar_window_simple)
    print(performance.volatility_window_simple)
    print(performance.sharpe_ratio_window_simple)
    positions = pd.DataFrame(
        [position.show() for position in portfolio.closed_positions]
    )

    print(positions)
    print('Total_profit ', positions['profit'].sum())
    print("Count of BAR %s" % timer.bar_counts)
    print("AVHT of BAR: %f nanoseconds" % timer.avht_bar)
    print("Count of ORDER %s" % timer.order_counts)
    print("AVHT of ORDER: %f nanoseconds" % timer.avht_order)


if __name__ == '__main__':
    import time

    st = time.time()
    run_backtest(
        MongoClient("192.168.1.103", port=27018).Oanda['EUR_USD.D'],
        'EUR_USD', datetime(2014, 1, 1), datetime(2015, 12, 31)
    )
    print("Total spending time: %s seconds" % (time.time() - st))