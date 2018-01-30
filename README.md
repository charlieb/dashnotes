Dependencies
============

SendFunds
---------
- pacman -S python-pip tk xsel
- pip install qrcode pillow requests clipboard pycoin
- Requires https://github.com/charlieb/pycoin version until https://github.com/richardkiss/pycoin/pull/265 is merged

Genkeypairs
-----------
- pip install pillow pycoin qrcode
- pacman -S rng-tools
- cp 99-TrueRNG.rules /etc/udev/rules.d
- echo 'RNGD_OPTS="-o /dev/random -r /dev/TrueRNG"' > /etc/conf.d/rngd
- systemctl start rngd
- systemctl enable rngd
