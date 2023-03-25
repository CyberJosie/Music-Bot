# Music Bot

A CLI tool made in Python for downloading songs or videos from YouTube as MP3 files
onto your computer.

# Installation

## Auto Install (Linux Only)
```
git clone https://github.com/CyberJosie/Music-Bot
cd Music-Bot
pip3 install -r requirements.txt
sudo python3 install.py /opt
```

## Manual Install (Linux)
```
git clone https://github.com/CyberJosie/Music-Bot
cd Music-Bot
pip3 install -r requirements.txt
sudo cp -rfv ../Music-Bot /opt
```
Add this code into a file named `musicbot.sh` in `/opt`
```
#!/bin/bash
export args=""
export pypath=$(which python3)

for var in "$@"; do
    args="${args} $var "
done;

$pypath /opt/Music-Bot/musicbot.py $args
```

```
chmod +x /opt/Music-Bot/musicbot.sh
sudo ln -s /opt/Music-Bot/musicbot.sh /usr/local/bin/musicbot
```

# Usage
```
musicbot --help
```