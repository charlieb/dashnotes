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
### Source Dependencies
#### SendFunds
- python3
- pacman -S python-pip tk xsel
- pip install qrcode pillow requests clipboard pycoin
- Requires https://github.com/charlieb/pycoin version until https://github.com/richardkiss/pycoin/pull/271 is merged
- Add the location where you downloaded https://github.com/charlieb/pycoin to
  your PYTHONPATH

#### Genkeypairs
- python3
- pip install pillow pycoin qrcode
- pacman -S rng-tools
- cp 99-TrueRNG.rules /etc/udev/rules.d
- echo 'RNGD_OPTS="-o /dev/random -r /dev/TrueRNG"' > /etc/conf.d/rngd
- systemctl start rngd
- systemctl enable rngd

Sending Dash to Address List
============================
![Main UI](https://i.imgur.com/kI4Z8aT.png)
### Quick Overview
- Launch the program.
- Open the address list file.
- Select how much Dash to send to each address.
- The program will calculate the total needed (including transaction fees).
- Send that amount of Dash to the program's address, wait until the program
  shows the balance.
- Hit send.
- Wait until the address list shows the new balances.
## Detailed Instructions
- Start the program
  - On Windows dashnotes/sendfunds.exe
  - On Linux dashnotes/sendfunds
  - On MaxOS dashnotes/sendfunds.exe (?)
  - from source run python3 dashnotes/sendfunds.py
- Load the address list
  - You should have received a file containing a list of addresses, one per line
  - Select File -> Open from the main menu, navigate to your file and hit open
- Choose how much Dash to send to each card
  - Enter an amount of Dash in the "Dash per address" box.
- Send Dash to the program
  - The "Dash needed" readout should turn red and display an amount. This
    amount is the total needed by the program to send the the requested amount
    of Dash to each address.
  - Send that amount of Dash to the address on the right. You can use the QR
    code to send from a phone or hit the "copy" button to copy the address
    shown to the clipboard.
  - Once the necessary amount of Dash has been received the "Current Balance"
    display will show the amount sent and the "Dash needed" readout will turn
    green. This will also enable the "Send" button.
- Send Dash to the addresses
  - Hit the "Send" button.
  - A transaction will be generated and sent to the network.
  - The balances of the addresses are checked frequently so when the
    transaction is confirmed all the addresses will update to show the new
    balance.

Further Information
===================
### Reclaiming Unused Dash
If you send too much Dash to the program you can easily reclaim it.
- Select Address -> Show Private Key from the main menu.
- A window will open with the private key in "Wallet Import Format" (WIP).
- The private key can be readily imported into most Dash or multicoin wallets.
### Failed to Save Private Keys Message
When the program starts up it generates a new key and its address. It attempts
to save both to the location it is started from. If it fails to save the file
it will warn the user.

**If you send Dash to the program after seeing this message and then close the
program your Dash will be lost!**

Please move the program to a location on the disk where it can create files.

It is not recommended but the program can still be used. The program must be
used in a single session because once it is closed the private key generated 
at startup will be lost.

If you have to run the program after seeing this message it it recommended that you make a manual
copy of the private key by selecting Address -> Show Private Key from the main
menu and either capturing the QR code or using the copy button. This will allow
you to recover your funds in the event that the program closes.

