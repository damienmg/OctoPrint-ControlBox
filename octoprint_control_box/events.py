from rule import Chainable

class _EventTrigger(Chainable):
    def __init__(self, parent, deleteOnExecute, name, event_name, *args):
        self._events = set(event_name)
        self._events.add(args)
        super(OneTimeTrigger, self).__init__(name + ("any of %s" % ", ".join(self._events)) if len(args) else event_name))
        self._parent = parent
        for event in self._events:
            if event not in self._parent.triggers:
                self._parent.triggers[event] = set()
            self._parent.triggers[event].add(self)
        self._deleteOnExecute = deleteOnExecute

    def on_event(self, event_name, event_payload):
        if event_name in self._events:
            self.execute()
            if self._deleteOnExecute:
                self._parent.triggers[event].remove(self)
    
    def __hash__(self):
        return hash(repr(self))

class EventsDispatcher(object):
    def __init__(self):
        self.triggers = dict()

    def trigger(self, event_name, *args):
        return _EventTrigger(self, False, "When ", event_name, args)

    def wait_for(self, event_name, *args):
        return _EventTrigger(self, True, "Wait for ", event_name, *args)

    def on_event(self, event_name, event_payload):
        if event_name in self._triggers:
            for t in self._triggers[event_name]:
                t.on_event(event_name, event_payload)
