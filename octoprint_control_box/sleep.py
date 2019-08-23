from rule import LambdaAction
import time

def SleepAction(sleep_time):
    return LambdaAction("Sleep %ss" % sleep_time, lambda: time.sleep(sleep_time))
