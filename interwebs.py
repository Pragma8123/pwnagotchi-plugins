import logging
import threading
import time

import requests

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Example(plugins.Plugin):
    __author__ = "pragma8123@gmail.com"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "An internet status plugin that doesn't suck."

    def __init__(self):
        self.options = dict()
        self.internet = False
        self.wan_ip = ""
        self.stop = False
        self.connection_thread = threading.Thread(target=self._internet_check)
        self.connection_thread.daemon = True
        self.connection_thread.start()

    def _is_internet_available(self):
        try:
            with requests.get(
                "https://api.ipify.org?format=json", timeout=3
            ) as response:
                with response.json() as body:
                    if self.wan_ip != body["ip"]:
                        self.wan_ip = body["ip"]
                        logging.debug(f"[interwebs] New WAN IP: {self.wan_ip}")
                    return True
        except Exception as e:
            return False

    def _internet_check(self):
        while True:
            if self.stop:
                return
            self.internet = self._is_internet_available()
            time.sleep(3)

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info("[interwebs] plugin loaded!")

    # called before the plugin is unloaded
    def on_unload(self, ui):
        ui.remove_element("internet")
        self.stop = True
        self.connection_thread.join()
        logging.info("[interwebs] plugin unloaded!")

    # called to set up the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        ui.add_element(
            "internet",
            LabeledValue(
                color=BLACK,
                label="WWW",
                value="D",
                position=(ui.width() / 2 + 25, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    # called when the ui is updated
    def on_ui_update(self, ui):
        val = "D"
        if self.internet:
            val = "C"
        ui.set("internet", val)
