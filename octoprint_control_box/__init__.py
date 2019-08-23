# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from . import gpio,events,printer,sleep,usb_power,webcam

# Scenarii:
#   TODO turn off after extruder temp is under X for Y s
#   TODO Lighting & Camera: turn on lighting along with camera and automate turning on/off camera (integration with octolapse)
#   TODO Fan: Turn on fan when temp > 45C, turn off when temp <= 40C

class ControlBoxPlugin(octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SimpleApiPlugin,
                       octoprint.plugin.ShutdownPlugin,
                       octoprint.plugin.EventHandlerPlugin,
                       octoprint.plugin.StartupPlugin):
    """Plugin class, see file descripion about the behavior of this plugin."""
    def __init__(self):
        self._gpio = gpio.GPIOSwitchesDictionary()
        self._webcam = webcam.WebcamController()
        self.printer_factory = printer.PrinterFactory()
        self._events = events.EventsDispatcher()
        self._triggers = [
			# TODO: turn on camera lights?
			self.printer_factory.trigger().chain(
				# Turn on the printer when trying to connect as well as the webcam.
				usb_power.SwitchUSBPower()
				).chain(
					self._webcam.action()
				).chain(
					self._gpio.action("Printer")
				).chain(
					sleep.SleepAction(5)),  # TODO: make this time configurable
			# Disconnecting: Turn off: camera, printer, lights & usb
			self._events.trigger("Disconnecting").chain(
				self._webcam.action(False)
				).chain(
					self._gpio.action("Printer", False)
				).chain(
					self._gpio.action("Light", False)
				).chain(
					usb_power.SwitchUSBPower(False)
				),
		]

    ##~ Events
    def on_event(self, event_name, event_payload):
        self._events.on_event(event_name, event_payload)

    ##~~ ShutdownPlugin mixin
    def on_shutdown(self):
        self._gpio.shutdown()

    ##-- Template hooks
    def get_template_configs(self):
        return [dict(type="settings",custom_bindings=False),dict(type="controls",custom_bindings=False)]

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(
            GPIO = dict(
                Printer = dict(
					gpio=26,
					protected=True,
                ),
                Fan = dict(
					gpio=5,
					protected=False,
                ),
                Light = dict(
					gpio=13,
					protected=False,
                ),
            ),
            WebcamController = "/home/octoprint/scripts/webcam",
            # TODO: make rules settable
            # FanTemperatorThreshold = 55,
            # MaxHotendTempBeforeShutdown = 50,
            # MinutesBeforeShutdown = 10,
            # CoupleLightWithPrinting = True,
            # CoupleCameraWithPrinter = True,
            # CouplePrinterWithConnect = True,
            # CoupleUSBWithConnect = True,
        )

    def get(self, name):
        val = self._settings.get([name])
        return val if val is not None else self.get_settings_defaults()[name]

    def on_settings_save(self, data):
        self._gpio.set_names({k: v["gpio"] for k, v in self.get("GPIO").iteritems()})
        self._webcam.controller = self.get("WebcamController")

    def on_after_startup(self):
        self._gpio.setup()
        self.on_settings_save(None)

    ##~~ AssetPlugin mixin
    def get_assets(self):
        return dict(
            js=["js/control_box.js"],
        )

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            control_box=dict(
                displayName="ControlBox Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="damienmg",
                repo="OctoPrint-ControlBox",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/damienmg/OctoPrint-ControlBox/archive/{target_version}.zip"
            )
        )

    ##~~ SimpleApiPlugin mixin
    def get_api_commands(self):
        return dict(
            usb_power=["status"],
            webcam=["status"],
            gpio=["name", "status"],
        )
    
    def is_api_admin_only(self):
        return True

    def on_api_command(self, command, data):
        if command == "usb_power":
            usb_power.Switch(data["status"].lower() == "on")
        elif command == "webcam":
            self._webcam.switch(data["status"].lower() == "on")
        elif command == "gpio":
            self._gpio.set_gpio(data["name"], data["status"].lower() == "on")

    def on_api_get(self, request):
        import flask
        return flask.jsonify(
            usb_power=usb_power.IsOn(),
            webcam=self._webcam.is_on(),
            gpio={k: {
					"status": self._gpio.is_on(k),
					"protected": p["protected"]
				} for k,p in self.get("GPIO").iteritems()},
        )

__plugin_name__ = "ControlBox Plugin"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ControlBoxPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.printer.factory": __plugin_implementation__.printer_factory.printer_factory_hook
    }

