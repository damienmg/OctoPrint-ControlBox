from rule import Chainable

class EventsDispatcher():
    def __init__(self):
        self._triggers = dict()

    def trigger(self, event_name):
        if event_name not in self._triggers:
            self._triggers[event_name] = []
        result = Chainable("When %s" % event_name)
        self._triggers[event_name].append(result)
        return result

    def on_event(self, event_name, event_payload):
        if event_name in self._triggers:
            for t in self._triggers[event_name]:
                t.execute()
