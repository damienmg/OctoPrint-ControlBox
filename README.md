# OctoPrint-ControlBox

**TODO:** Describe what your plugin does.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/damienmg/OctoPrint-ControlBox/archive/master.zip

**TODO:** Describe how to install your plugin, if more needs to be done than just installing it via pip or through
the plugin manager.

- Add permission to udev, added `SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0666"` (see https://unix.stackexchange.com/questions/44308/understanding-udev-rules-and-permissions-in-libusb). TODO: verify security of that (is it safe in all cases?)

## Configuration

**TODO:** Describe your plugin's configuration options (if any).
