try:
    from dry_run import DRY_RUN
except:
    DRY_RUN = None

from rule import LambdaCondition, LambdaAction
import logging

if DRY_RUN is None:
    import RPi.GPIO as GPIO
else:
    class _GPIO:
        """A fake GPIO object to do dry run action"""
        BCM = "BCM"
        OUT = "OUT"
        HIGH = True
        LOW = False

        def __init__(self):
            self._logger = logging.getLogger("octoprint.plugins.ControlBox")

        def setmode(self, mode):
            self._logger.info("[DRY_RUN] GPIO.setmode(%s)" % mode)

        def _set_gpio(self, gpio, value=None):
            if "gpio" not in DRY_RUN:
                DRY_RUN["gpio"] = {}
            if value is None:
                del DRY_RUN["gpio"][gpio]
            else:
                DRY_RUN["gpio"][gpio] = value

        def cleanup(self, gpio):
            self._logger.info("[DRY_RUN] GPIO.cleanup(%s)" % gpio)
            if isinstance(gpio, int) or isinstance(gpio, long):
                self._set_gpio(gpio)
            elif isinstance(gpio, list) or isinstance(gpio, tuple):
                for g in gpio:
                    self._set_gpio(g)
            else:
                raise('Runtime error')
        
        def setup(self, gpio, mode):
            self._logger.info("[DRY_RUN] GPIO.setup(%s, %s)" % (gpio, mode))
            if isinstance(gpio, int) or isinstance(gpio, long):
                self._set_gpio(gpio, 0)
            elif isinstance(gpio, list) or isinstance(gpio, tuple):
                for g in gpio:
                    self._set_gpio(g, 0)
            else:
                raise('Runtime error')

        def input(self, gpio):
            self._logger.info("[DRY_RUN] GPIO.input(%s)" % gpio)
            if "gpio" not in DRY_RUN:
                return False
            return DRY_RUN["gpio"][gpio]

        def output(self, gpio, value):
            self._logger.info("[DRY_RUN] GPIO.output(%s, %s)" % (gpio, value))
            self._set_gpio(gpio, GPIO.HIGH if value else GPIO.LOW)

    GPIO = _GPIO()
            
class GPIOSwitchesDictionary:
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.ControlBox")
        self._gpio = dict()

    def setup(self):
        GPIO.setmode(GPIO.BCM)

    def set_names(self, new_gpio):
        old_gpios = set(self._gpio.values())
        new_gpios = set(new_gpio.values())
        GPIO.cleanup(list(old_gpios-new_gpios))
        GPIO.setup(list(new_gpios-old_gpios), GPIO.OUT)
        self._gpio = new_gpio

    def shutdown(self):
        for gpio in self._gpio.values():
            GPIO.cleanup(gpio)
    
    def condition(self, gpio_name):
        return LambdaCondition("GPIO Pin %s" % gpio_name, lambda: self.is_on(gpio_name))

    def action(self, gpio_name, is_on=True):
        return LambdaAction("Set GPIO Pin %s to %s" % (gpio_name, is_on),
                lambda: self.set_gpio(gpio_name, is_on))

    def is_on(self, gpio_name):
        if gpio_name not in self._gpio:
            self._logger.warning("GPIO pin named '%s' not found" % gpio_name)
            return False
        return GPIO.input(self._gpio[gpio_name])

    def names(self):
        return self._gpio.keys()

    def set_gpio(self, gpio_name, is_on=True):
        if gpio_name not in self._gpio:
            return False
        if isinstance(gpio_name, list) or isinstance(gpio_name, tuple):
            GPIO.output([self._gpio[n] for n in gpio_name], GPIO.HIGH if is_on else GPIO.LOW)
        else:
            GPIO.output(self._gpio[gpio_name], GPIO.HIGH if is_on else GPIO.LOW)
        return True
