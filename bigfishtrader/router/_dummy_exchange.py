from bigfishtrader.engine.handler import Handler
from bigfishtrader.event import FillEvent, RecallEvent, EVENTS
from bigfishtrader.router.base import AbstractRouter


class DummyExchange(AbstractRouter):
    """
    DummyExchange if a simulation of a real exchange.
    It handles OrderEvent(ORDER,LIMIT,STOP) and
    generate FillEvent which then be put into the event_queue
    """

    def __init__(self, event_queue, data, exchange_name=None, **ticker_information):
        """
        :param event_queue:
        :param exchange_name:
        :param ticker_information: ticker={'lever':10000,'deposit_rate':0.02}
        :return:
        """
        super(DummyExchange, self).__init__()
        self.event_queue = event_queue
        self.ticker_info = ticker_information
        self.exchange_name = exchange_name
        self._data = data
        self.orders = {}
        self._handlers = {
            "on_bar": Handler(self.on_bar, EVENTS.BAR, topic="", priority=100),
            "on_order": Handler(self.on_order, EVENTS.ORDER, topic="", priority=0),
            "on_time": Handler(self.on_time, EVENTS.TIME, priority=200),
            "on_order_instance": Handler(self.on_order_instance, EVENTS.ORDER, topic='this_bar')
        }
        self.handle_order = {
            EVENTS.ORDER: self._fill_order,
            EVENTS.LIMIT: self._fill_limit,
            EVENTS.STOP: self._fill_stop
        }

    @staticmethod
    def calculate_commission(order, price):
        return 1

    @staticmethod
    def calculate_slippage(order, price):
        return 0

    def _put_fill(self, order, price, timestamp):
        fill = FillEvent(
            timestamp, order.ticker,
            order.action, order.quantity,
            price + self.calculate_slippage(order, price),
            self.calculate_commission(order, price),
            local_id=order.local_id, position_id=order.local_id,
            topic=order.topic, **self.ticker_info.get(order.ticker, {})
        )
        self.orders.pop(order.local_id, None)
        self.event_queue.put(fill)

    def on_cancel(self, event, kwargs=None):
        """
        When a CancelEvent arrives, remove the orders that satisfy the event's condition
        :param event:
        :return:
        """
        for order in self.orders.values():
            if order.match(event.conditions):
                self.orders.pop(order.loacl_id, None)

    def _fill_order(self, order, bar):
        self._put_fill(order, bar.open, bar.name)

    def _fill_limit(self, order, bar):
        if order.action:
            self._limit_open(order, bar)
        else:
            self._stop_open(order, bar)

    def _fill_stop(self, order, bar):
        if order.action:
            self._stop_open(order, bar)
        else:
            self._limit_open(order, bar)

    def _limit_open(self, order, bar):

        if order.quantity > 0 and bar.low < order.price:
            price = order.price if bar.open >= order.price else bar.open
            self._put_fill(order, price, bar.name)
        elif order.quantity < 0 and bar.high > order.price:
            price = order.price if bar.open <= order.price else bar.open
            self._put_fill(order, price, bar.name)

    def _stop_open(self, order, bar):
        if order.quantity > 0 and bar.high > order.price:
            price = order.price if bar.open <= order.price else bar.open
            self._put_fill(order, price, bar.name)
        elif order.quantity < 0 and bar.low < order.price:
            price = order.price if bar.open >= order.price else bar.open
            self._put_fill(order, price, bar.name)

    def on_order(self, event, kwargs=None):
        """
        When an order arrives put it into self.orders
        :param event:
        :param kwargs:
        :return:
        """
        self.orders[event.local_id] = event
        self.event_queue.put(
            RecallEvent(event.time, event)
        )

    def on_bar(self, bar_event, kwargs=None):
        """
        :param bar_event:
        :param kwargs:
        :return:
        """
        for order in self.orders.values():
            self.handle_order[order.order_type](order, bar_event)

    def on_time(self, event, kwargs=None):
        for _id, order in self.orders.copy().items():
            self.handle_order[order.order_type](order, self._data.current(order.ticker))

    def on_order_instance(self, event, kwargs=None):
        if event.order_type == EVENTS.ORDER:
            current = self._data.current(event.ticker)
            self.event_queue.put(
                RecallEvent(event.time, event)
            )
            self._put_fill(event, current.close, current.name)
        else:
            self.on_order(event, kwargs)

    def get_orders(self):
        return dict(map(
            lambda (_id, order): (
                _id,
                {'ticker': order.ticker, 'quantity': order.quantity,
                 'type': order.order_type, 'action': order.action}
            ),
            self.orders.items()
        ))