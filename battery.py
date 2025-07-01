import logging
import socket
import threading
import time
from os import path

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Battery(plugins.Plugin):
    __author__ = "pragma8123@gmail.com"
    __version__ = "0.1.2"
    __license__ = "GPL3"
    __description__ = (
        "A battery status indicator plugin primarily for pisugar batteries."
    )

    def __init__(self):
        self.options = dict()
        self.percent = "-"
        self.charging = False
        self.stop = False
        self.sock = None
        self.check_thread = threading.Thread(target=self._battery_status_checker)
        self.check_thread.daemon = True
        self.check_thread.start()

    def _battery_status_checker(self):
        while True:
            time.sleep(3)

            if self.stop:
                return

            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if not path.exists("/tmp/pisugar-server.sock"):
                logging.warning(
                    "[battery] pisugar server does not seem to be installed."
                )
                self.sock = None
                continue
            try:
                self.sock.connect("/tmp/pisugar-server.sock")
            except socket.error as e:
                logging.error(f"[battery] error connecting to pisugar: {e}")
                self.sock = None
                continue

            # get battery percentage
            try:
                self.sock.send("get battery".encode())
                data = self.sock.recv(128).decode()
                battery_exact = data.split(" ")[1].strip()
                self.percent = int(float(battery_exact))
            except socket.error as e:
                logging.error(f"[battery] error getting data from pisugar: {e}")

            # get battery charging status
            try:
                self.sock.send("get battery_power_plugged".encode())
                data = self.sock.recv(128).decode()
                self.charging = data.split(" ")[1].strip() == "true"
            except socket.error as e:
                logging.error(f"[battery] error getting data from pisugar: {e}")

            self.sock.close()
            self.sock = None

    def on_loaded(self):
        logging.info("[battery] plugin loaded.")

    def on_unload(self, ui):
        ui.remove_element("battery")
        self.stop = True
        logging.info("[battery] plugin unloaded.")

    def on_ui_setup(self, ui):
        ui.add_element(
            "bat",
            LabeledValue(
                color=BLACK,
                label="CHG" if self.charging else "BAT",
                value="-",
                position=(ui.width() / 2 + 16, 0),
                label_font=fonts.Bold,
                text_font=fonts.Medium,
            ),
        )

    def on_ui_update(self, ui):
        if "bat" not in ui._state._state:
            return

        ui.set("bat", f"{self.percent}%")
        ui._state._state["bat"].label = "CHG" if self.charging else "BAT"
