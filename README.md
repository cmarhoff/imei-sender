# IMEI Sender

GTK-App to enter, validate and transmit an IMEI to the EG25-G-Module in the PinePhone Pro via AT-command, by ChatGPT.

## 🔧 Requirements

- Python 3
- GTK 3 (`python3-gi`, `gir1.2-gtk-3.0`)
  sudo apt install python3 python3-gi gir1.2-gtk-3.0 minicom

## 🚀 Installation & Execution  

```bash
git clone https://github.com/cmarhoff/imei-sender.git
cd imei-sender
chmod +x install.sh
./install.sh

Warning: an active ModemManager will inhibit a normal user from using the modem!

Start the app:

Via the application menu ("IMEI Sender")

Or directly:

./run.sh
