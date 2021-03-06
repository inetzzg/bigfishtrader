from fxdayu.context import ContextMixin
from fxdayu.engine.handler import HandlerCompose, Handler
from fxdayu.event import EVENTS


class SelectorHandler(HandlerCompose, ContextMixin):
    def __init__(self, engine, context, environment, data, selector_admin, executor_admin):
        super(SelectorHandler, self).__init__(engine)
        ContextMixin.__init__(self)
        self.set_context(context)
        self.set_environment(environment)
        self.set_data(data)
        self._handlers['on_time'] = Handler(self.initialize, EVENTS.TIME, 'bar.open')
        self.selectors = []
        self.executors = []
        self.sa = selector_admin
        self.ea = executor_admin
        self.initialized = False

    def link_context(self):
        pass

    def initialize(self, event, kwargs=None):
        if not self.initialized:
            if self.sa is None:
                self.sa = self.sa(*self.selectors)
            if self.ea is None:
                self.ea = self.ea(*self.executors)
            self.initialized = True

        self._handlers['on_time'].unregister(self.engine)
        self.engine.register(self.on_time, EVENTS.TIME, 'bar.close')

    def on_time(self, event, kwargs=None):
        self.sa.on_time(event.time, self.context, self.data)
        self.ea.on_time(self.context, self.data, self.environment)
        self.send_order()

    def send_order(self):
        for code in self.context.portfolio.positions:
            if code not in self.context.selector_pool:
                self.environment['order_target'](code, 0)

        for code, pct in self.context.executor_pool.items():
            self.environment['order_target_percent'](code, pct)

