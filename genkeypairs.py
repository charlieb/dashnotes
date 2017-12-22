#!/bin/env python3

import qrcode
import sys
from pycoin.cmds import ku
from pycoin.key.BIP32Node import BIP32Node

def keypair():
    # ku -n DASH create 
    # wif = private key
    # Dash Address = public address
    key = BIP32Node.from_master_secret(ku.get_entropy(), 'DASH')
    pub = key.address(use_uncompressed=False)
    priv = key.wif(use_uncompressed=False)
    print(priv)
    print(pub)
    return pub, priv

def make_qr_im(data):
    qr = qrcode.QRCode(
        #version=1,
        #error_correction=qrcode.constants.ERROR_CORRECT_L,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=None)
    return qr.make_image()


def main():
    pub, priv = keypair()

    make_qr_im(pub).show()
    make_qr_im(priv).show()

if __name__ == '__main__':
    main()

    


