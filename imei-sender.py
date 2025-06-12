#!/usr/bin/env python3
import gi
import subprocess
from validate import is_valid_imei

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class IMEIWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="IMEI Sender")
        self.set_border_width(10)
        self.set_default_size(300, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter IMEI (15 digits)")
        box.pack_start(self.entry, True, True, 0)

        self.button = Gtk.Button(label="Send")
        self.button.connect("clicked", self.on_send_clicked)
        box.pack_start(self.button, True, True, 0)

        self.status = Gtk.Label(label="")
        box.pack_start(self.status, True, True, 0)

    def on_send_clicked(self, widget):
        imei = self.entry.get_text().strip()
        if not is_valid_imei(imei):
            self.status.set_text("Invalid IMEI!")
            return

        try:
            command = f'echo -e "AT+EGMR=1,7,\\"{imei}\\"\r" > /dev/ttyUSB2'
            subprocess.run(command, shell=True, check=True)
            self.status.set_text("IMEI sent.")
        except Exception as e:
            self.status.set_text(f"Error: {e}")

if __name__ == "__main__":
    win = IMEIWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
