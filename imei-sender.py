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
        self.set_default_size(500, 320)

        icon_path = os.path.join(os.path.dirname(__file__), "icon.jpg")
        if os.path.exists(icon_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(pixbuf)

        self.grid = Gtk.Grid(column_spacing=12, row_spacing=12, margin=10)
        self.add(self.grid)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter IMEI (15 digits)")
        self.entry.set_hexpand(True)
        self.entry.connect("changed", self.on_entry_changed)
        imei_label = Gtk.Label(label="IMEI:")
        imei_label.set_markup("<b>IMEI:</b>")
        imei_label.set_halign(Gtk.Align.START)
        self.grid.attach(imei_label, 0, 0, 1, 1)
        self.grid.attach(self.entry, 1, 0, 3, 1)

        paste_button = Gtk.Button(label="📋 Paste")
        paste_button.connect("clicked", self.on_paste_clicked)
        self.grid.attach(paste_button, 1, 1, 1, 1)

        port_label = Gtk.Label(label="Port:")
        port_label.set_markup("<b>Port:</b>")
        port_label.set_halign(Gtk.Align.START)
        self.port_combo = Gtk.ComboBoxText()
        self.refresh_ports()
        self.grid.attach(port_label, 0, 2, 1, 1)
        self.grid.attach(self.port_combo, 1, 2, 3, 1)

        self.button = Gtk.Button(label="Send IMEI")
        self.button.get_style_context().add_class("suggested-action")
        self.button.connect("clicked", self.on_send_clicked)
        self.grid.attach(self.button, 0, 3, 4, 1)

        self.status = Gtk.Label(label="")
        self.status.set_line_wrap(True)
        self.grid.attach(self.status, 0, 4, 4, 1)

        history_label = Gtk.Label(label="History:")
        history_label.set_markup("<b>History:</b>")
        history_label.set_halign(Gtk.Align.START)
        self.history = Gtk.ComboBoxText()
        self.history.set_entry_text_column(0)
        self.load_history()
        self.history.connect("changed", self.on_history_changed)
        self.grid.attach(history_label, 0, 5, 1, 1)
        self.grid.attach(self.history, 1, 5, 3, 1)

        info_button = Gtk.Button(label="Info")
        info_button.connect("clicked", self.on_info_clicked)
        self.grid.attach(info_button, 0, 6, 1, 1)

        self.info_grid = Gtk.Grid(column_spacing=12, row_spacing=6, margin_top=6)
        self.grid.attach(self.info_grid, 0, 7, 3, 1)

    def refresh_ports(self):
        ports = glob.glob("/dev/ttyUSB*")
        n = 0
        for port in ports:
            self.port_combo.append_text(port)
            if n < 2:
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

    def send_at_command(self, port, command):
        try:
            fd = os.open(port, os.O_RDWR | os.O_NONBLOCK)
            os.write(fd, (command + "\r\n").encode())

            buffer = b""
            timeout = 2
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
            return buffer.decode("utf-8", errors="replace").strip()
        except OSError as e:
            return f"OS error: {e}"

    def on_send_clicked(self, widget):
        imei = self.entry.get_text().strip()
        if not is_valid_imei(imei):
            self.status.set_markup('<span foreground="red">Invalid IMEI!</span>')
            return

        port = self.port_combo.get_active_text()
        if not port:
            self.status.set_markup('<span foreground="red">No serial port selected!</span>')
            return

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

        reply = self.send_at_command(port, "ATE0")
        reply = self.send_at_command(port, f'AT+EGMR=1,7,"{imei}"')
        if "OK" in reply:
            self.status.set_markup("<span foreground='green'>IMEI sent successfully</span>")
            self.save_to_history(imei)
        else:
            self.status.set_markup(f"<span foreground='red'>IMEI sent, status: {reply}</span>")

    def on_info_clicked(self, widget):
        port = self.port_combo.get_active_text()
        if not port:
            self.status.set_markup('<span foreground="red">No serial port selected!</span>')
            return

        # Clear old info
        for child in self.info_grid.get_children():
            self.info_grid.remove(child)

        self.send_at_command(port, "ATE0")

        labels = ["IMEI", "Manufacturer", "Model", "Version"]
        commands = ["AT+GSN", "AT+GMI", "AT+GMM", "AT+GMR"]
        for i, cmd in enumerate(commands):
            result = self.send_at_command(port, cmd)
            clean = result.replace("OK", "").strip() if "OK" in result else "-"
            label = Gtk.Label(label=labels[i] + ":", xalign=0)
            value = Gtk.Label(label=clean, xalign=0)
            label.set_markup(f"<b>{labels[i]}:</b>")
            self.info_grid.attach(label, 0, i, 1, 1)
            self.info_grid.attach(value, 1, i, 1, 1)

        self.info_grid.show_all()

if __name__ == "__main__":
    win = IMEIWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
