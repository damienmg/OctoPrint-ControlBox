try:
    from dry_run import DRY_RUN
except:
    DRY_RUN = None

from rule import LambdaCondition, LambdaAction
import subprocess

class WebcamController:
    def __init__(self):
        self.controller = None

    def condition(self):
        return LambdaCondition("Webcam is turned on", lambda: self.is_on())

    def action(self, is_on=True):
        return LambdaAction("Switch webcam " + "on" if is_on else "off",
                lambda: self.switch(is_on))

    def is_on(self):
        if not self.controller:
            return False
        if DRY_RUN is not None:
            return "webcam" in DRY_RUN and DRY_RUN["webcam"]
        try:
            result = subprocess.check_output([self.controller, "status"])
            return "running" in result
        except:
            return False

    def switch(self, is_on=True):
        if not self.controller:
            return False
        if DRY_RUN is not None:
            DRY_RUN["webcam"] = is_on
            return True
        try:
            result = subprocess.check_output([self.controller, "start" if is_on else "stop"])
            return ("started" if is_on else "stopped") in result
        except:
            return False
