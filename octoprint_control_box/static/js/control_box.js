/*
 * View model for OctoPrint-ControlBox
 *
 * Author: Damien Martin-Guillerez
 * License: Apache 2.0
 */
$(function() {
    function Control_boxViewModel(parameters) {
        var self = this;


        // assign the injected parameters.
        self.printerStateViewModel = parameters[0];

        self.setButtonActive = function(name, value) {
            if (value) {
                $('.' + name + '-button').addClass('active');
            } else {
                $('.' + name + '-button').removeClass('active');
            }
        }
        self.getControlValues = function() {
            $.ajax({
                url: API_BASEURL + "plugin/control_box",
                type: "GET",
                dataType: "json",
                success: function(response) {
                    Object.entries(response).forEach(
                        entry => {
                            if (entry[0] == "gpio") {
                                Object.entries(entry[1]).forEach(
                                    e => self.setButtonActive(e[0], e[1].status));
                            } else {
                                self.setButtonActive(entry[0], entry[1]);
                            }
                        }
                    )
                }
            })
        }
        self.switchPower = function(cmd, name) {
            $.ajax({
                url: API_BASEURL + "plugin/control_box",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({"command": cmd, "name": name, "status": $("." + name + "-button").hasClass('active') ? "off" : "on"}),
                contentType: "application/json",
                complete: function(response) {
                    self.getControlValues();
                }
            })
        }
        self.onEventConnected = function(_payload) {
            self.getControlValues();
        }
        self.onEventDisconnected = function(_payload) {
            self.getControlValues();
        }
        self.getAdditionalControls = function() {
            var buttons = {
                usb_power: {title: "USB", command: "usb", protected: true},
                webcam: {title: "WebCam", command: "webcam"},
            };
            $.ajax({
                url: API_BASEURL + "plugin/control_box",
                type: "GET",
                dataType: "json",
                success: function(response) {
                    Object.entries(response["gpio"]).forEach(
                        e => buttons[e[0]] = {title: e[0], command: "gpio", protected: e[1]["protected"]}
                    );
                },
                async: false
            });
            var transform = function(entry) {
                return {
                    additionalClasses: entry[0] + "-button",
                    enabled: entry[1].protected ? function() { return !self.printerStateViewModel.isPrinting(); } : true,
                    type: "javascript",
                    javascript: function() { self.switchPower(entry[1].command, entry[0]); },
                    name: entry[1].title,
                    confirm: "Do you want to switch power of " + entry[1].title + "?"
                };
            };
            return [
                { name: "Power", type: "section", layout: "horizontal", children:
                    Object.entries(buttons).map(transform)
                }
            ];
        };
        self.onAllBound = function(_allViewModels) {
            self.getControlValues();
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Control_boxViewModel,
        dependencies: [ "printerStateViewModel" /*, "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_control_box, #tab_plugin_control_box, ...
        elements: [ /* ... */ ]
    });
});
