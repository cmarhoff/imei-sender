#!/usr/bin/env python3
import gi
import os
import glob
import time
import select
from validate import is_valid_imei

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

class IMEIWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="IMEI Sender")
        self.set_border_width(20)
        self.set_default_size(450, 250)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(pixbuf)

        grid = Gtk.Grid(column_spacing=12, row_spacing=12, margin=10)
        self.add(grid)

        # IMEI input
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter IMEI (15 digits)")
        self.entry.set_hexpand(True)
        self.entry.connect("changed", self.on_entry_changed)
        imei_label = Gtk.Label(label="IMEI:")
        imei_label.set_markup("<b>IMEI:</b>")
        imei_label.set_halign(Gtk.Align.START)
        grid.attach(imei_label, 0, 0, 1, 1)
        grid.attach(self.entry, 1, 0, 2, 1)

        # Paste button
        paste_button = Gtk.Button(label="📋 Paste")
        paste_button.connect("clicked", self.on_paste_clicked)
        grid.attach(paste_button, 3, 0, 1, 1)

        # Port selection
        port_label = Gtk.Label(label="Port:")
        port_label.set_markup("<b>Port:</b>")
        port_label.set_halign(Gtk.Align.START)
        self.port_combo = Gtk.ComboBoxText()
        self.refresh_ports()
        grid.attach(port_label, 0, 1, 1, 1)
        grid.attach(self.port_combo, 1, 1, 3, 1)

        # Send button
        self.button = Gtk.Button(label="Send IMEI")
        self.button.get_style_context().add_class("suggested-action")
        self.button.connect("clicked", self.on_send_clicked)
        grid.attach(self.button, 0, 2, 4, 1)

        # Status label
        self.status = Gtk.Label(label="")
        self.status.set_line_wrap(True)
        grid.attach(self.status, 0, 3, 4, 1)

        # History dropdown
        history_label = Gtk.Label(label="History:")
        history_label.set_markup("<b>History:</b>")
        history_label.set_halign(Gtk.Align.START)
        self.history = Gtk.ComboBoxText()
        self.history.set_entry_text_column(0)
        self.load_history()
        self.history.connect("changed", self.on_history_changed)
        grid.attach(history_label, 0, 4, 1, 1)
        grid.attach(self.history, 1, 4, 3, 1)

    def refresh_ports(self):
        ports = glob.glob("/dev/ttyUSB*")
        n = 0
        for port in ports:
            self.port_combo.append_text(port)
            if n<2:
                n += 1
        if ports:
            self.port_combo.set_active(n)

    def load_history(self):
        self.history_file = os.path.expanduser("~/.imei_history")
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                for line in f:
                    imei = line.strip()
                    if imei:
                        self.history.append_text(imei)

    def save_to_history(self, imei):
        with open(self.history_file, "a") as f:
            f.write(imei + "\n")

    def on_history_changed(self, combo):
        imei = combo.get_active_text()
        if imei:
            self.entry.set_text(imei)

    def on_entry_changed(self, widget):
        imei = self.entry.get_text().strip()
        if is_valid_imei(imei):
            self.status.set_markup('<span foreground="green">Valid IMEI</span>')
        else:
            self.status.set_markup('<span foreground="red">Invalid IMEI</span>')

    def on_paste_clicked(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text()
        if text:
            self.entry.set_text(text.strip())

    def on_send_clicked(self, widget):
        imei = self.entry.get_text().strip()
        if not is_valid_imei(imei):
            self.status.set_markup('<span foreground="red">Invalid IMEI!</span>')
            return

        port = self.port_combo.get_active_text()
        if not port:
            self.status.set_markup('<span foreground="red">No serial port selected!</span>')
            return

        # Confirm dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Send this IMEI to the modem?",
        )
        dialog.format_secondary_text(f"IMEI: {imei}\nPort: {port}")
        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.OK:
            return

        at_command = f'AT+EGMR=1,7,"{imei}"\r\n'
        try:
            fd = os.open(port, os.O_RDWR | os.O_NONBLOCK)
            os.write(fd, at_command.encode())

            buffer = b""
            timeout = 2  # seconds
            start = time.time()

            while True:
                rlist, _, _ = select.select([fd], [], [], timeout)
                if rlist:
                    chunk = os.read(fd, 100)
                    buffer += chunk
                    if b"OK" in buffer or b"ERROR" in buffer:
                        break
                elif time.time() - start > timeout:
                    break

            os.close(fd)
            aanswer = buffer.decode('utf-8', errors='replace').strip()
            if "OK" in aanswer:
                self.status.set_markup(f"<span foreground='green'>IMEI sent successfully</span>")
                self.save_to_history(imei)
            else:
                self.status.set_markup(f"<span foreground='red'>IMEI sent, status: {aanswer}</span>")
        except OSError as e:
            self.status.set_markup(f"<span foreground='red'>OS error: {e}</span>")

if __name__ == "__main__":
    win = IMEIWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
