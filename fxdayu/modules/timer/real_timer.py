# encoding:utf-8
from fxdayu.context import ContextMixin
from fxdayu.event import TimeEvent, ScheduleEvent, EVENTS
from fxdayu.utils.api_support import api_method
from fxdayu.engine.handler import HandlerCompose
from datetime import datetime


class RealTimer(HandlerCompose, ContextMixin):
    def __init__(self, engine):
        super(RealTimer, self).__init__(engine)
        ContextMixin.__init__(self)

        self._ahead = []
        self._behind = []

    def init(self):
        super(RealTimer, self).init()
        self.data.subscribe('tick')
        self.data.listen(self.put_time)

    def put_time(self, time):
        try:
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")

            self.put_schedule(self._ahead, time)
            self.engine.put(TimeEvent(time, topic="bar.open"))
            self.engine.put(TimeEvent(time, topic="bar.close"))
            self.put_schedule(self._behind, time)

        except Exception as e:
            print(e)

    def link_context(self):
        self.environment['time_schedule'] = self.time_schedule

    @api_method
    def time_schedule(self, func, time_rule, ahead=True):
        if ahead:
            topic = 'ahead'+str(len(self._ahead))
            self.set_schedule(func, time_rule, topic, self._ahead)
        else:
            topic = 'behind'+str(len(self._ahead))
            self.set_schedule(func, time_rule, topic, self._behind)

    def set_schedule(self, func, time_rule, topic, l):
        def schedule(event, kwargs=None):
            func(self.context, self.data)
        self.engine.register(schedule, EVENTS.SCHEDULE, topic=topic)
        l.append((func, time_rule, topic))

    def put_schedule(self, l, time):
        for func, time_rule, topic in l:
            if time_rule(time):
                self.engine.put(ScheduleEvent(time, topic))
