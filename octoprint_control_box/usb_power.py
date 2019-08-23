try:
    from dry_run import DRY_RUN
except:
    DRY_RUN = None
from rule import LambdaAction
if DRY_RUN is None:
    import usb.core

def _GetRaspberryPiRootHub():
    # Get hub on bus 1 address 2 == Raspberry Pi Root USB Hub.
    # TODO: Is this is always this one?
    return usb.core.find(
        bDeviceClass=usb.CLASS_HUB,
        custom_match=lambda d: d.bus == 1 and d.address == 2,
    )

def IsOn():
    if DRY_RUN is not None:
        return "usb" in DRY_RUN and DRY_RUN["usb"]
    # Get the device status.
    status = _GetRaspberryPiRootHub().ctrl_transfer(
        usb.TYPE_CLASS | usb.RECIP_OTHER | usb.ENDPOINT_IN,
        usb.REQ_GET_STATUS,
        wValue = 0,
        wIndex = 2,
        data_or_wLength = 4,
        timeout = 1000
    )
    return (status[1] & 0x1) != 0


def Switch(on=True):
    if DRY_RUN is not None:
        DRY_RUN["usb"] = on
        return True
    # Set the device power.
    _GetRaspberryPiRootHub().ctrl_transfer(
        usb.TYPE_CLASS | usb.RECIP_OTHER,
        usb.REQ_SET_FEATURE if on else usb.REQ_CLEAR_FEATURE,
        wValue = 8, # USB_PORT_FEAT_POWER
        wIndex = 2,
        data_or_wLength = None,
        timeout = 1000,
    )
    return True

def SwitchUSBPower(on=True):
    return LambdaAction("Switch USB power " + "on" if on else "off", lambda: Switch(on))
