# IMEI Sender

GTK-App to enter, validate and transmit an IMEI to the EG25-G-Module in the PinePhone Pro via AT-comman, by ChatGPT.

## 🔧 Requirements

- Python 3
- GTK 3 (`python3-gi`, `gir1.2-gtk-3.0`)
- access rights to `/dev/ttyUSB2`

## 🚀 Installation & Execution  

```bash
git clone https://github.com/cmarhoff/imei-sender.git
cd imei-sender
chmod +x run.sh
./run.sh
