
import octoprint.printer.standard
from rule import Chainable

# Connection needs to block until the printer is fully started, hence we do not
# use the event but rather intercept the call to the PrinterInterface.
class _RuleIntercepterPrinter(octoprint.printer.standard.Printer):
    """A PrinterInterface intercepting connection."""
    def __init__(self, action, components):
        super(_RuleIntercepterPrinter, self).__init__(
            components["file_manager"],
            components["analysis_queue"],
            components["printer_profile_manager"])
        self._action = action
    
    def connect(self, port=None, baudrate=None, profile=None, *args, **kwargs):
        self._action.execute()
        # TODO: show it is trying to connect
        super(_RuleIntercepterPrinter, self).connect(port, baudrate, profile, *args, **kwargs)

class PrinterFactory():
    def __init__(self):
        self._action = Chainable("When Connecting")

    ##~~ Printer Factory hook
    def printer_factory_hook(self, components, *args, **kwargs):
        return _RuleIntercepterPrinter(self._action, components)

    def trigger(self):
        return self._action
