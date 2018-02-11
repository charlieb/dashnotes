Installation
============

## Easy Bundles
Download and upzip the package for your platform
- [Windows](http://google.com)
- [Linux](http://google.com)
- [MacOS](http://google.com)

## Install from Source

### Download Source 
- git clone https://github.com/charlieb/dashnotes
- or [download a release version](https://github.com/charlieb/dashnotes/releases)
### Install Dependencies
#### SendFunds
- pacman -S python-pip tk xsel
- pip install qrcode pillow requests clipboard pycoin
- Requires https://github.com/charlieb/pycoin version until https://github.com/richardkiss/pycoin/pull/271 is merged

#### Genkeypairs
- pip install pillow pycoin qrcode
- pacman -S rng-tools
- cp 99-TrueRNG.rules /etc/udev/rules.d
- echo 'RNGD_OPTS="-o /dev/random -r /dev/TrueRNG"' > /etc/conf.d/rngd
- systemctl start rngd
- systemctl enable rngd

Sending Dash to Address List
============================

### From a bundle
- Unzip the bundles and launch:
  - On Windows dashnotes/sendfunds.exe
  - On Linux dashnotes/sendfunds
  - On MaxOS dashnotes/sendfunds.exe (?)
### From Source Install
- Add my pycoin branch to the PYTHONPATH 
- python dashnotes/sendfunds.py


![Main UI](https://i.imgur.com/kI4Z8aT.png)


