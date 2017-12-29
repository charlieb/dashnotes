#!/bin/env python3

import qrcode
import sys
from pycoin.cmds import ku
from pycoin.key.BIP32Node import BIP32Node
from PIL import Image, ImageDraw


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

def test_keypair():
    pub, priv = keypair()
    make_qr_im(pub).show()
    make_qr_im(priv).show()

################################################
# IMAGES
################################################

dpi=300
page_size = [18*dpi, 12*dpi] # = 5400 x 3600 landscape
overprint = dpi / 16 # halfway between 1/8 and 1/16inch


# >>> w = 457.2 # 18 inches in mm
# >>> h =  304.8 # 12 inches in mm
# >>> int(w / 125) # 125 is the long side of a fiver
# 3 # we can fit 3
# >>> ((w/125) - int(w / 125)) * 125
# 82.19999999999999 # with 82mm to spare
# >>> (((w/125) - int(w / 125)) * 125) / (int(w/125) + 1)
# 20.549999999999997 # per fiver +1 for the fence post
#
# We can fit 4 short sides into the short side
# >>> (((h/65) - int(h/65)) * 65) / (int(h/65) + 1)
# 8.959999999999997 # per fiver +1 for the fence post

def paste_coords(im):
    '''Stacks 3 copies in in X and 4 in Y of im argument.
    Distributes leftover space between im copies.
    Returns list of 12 (x,y) tuples for the top-left coord of eaceh copy.'''
    (ix,iy) = im.size
    px = page_size[0]
    xcopies = int(px / ix)
    xspace = int((px % ix) / (xcopies + 1))
    x = [xspace + (xspace + ix) * j for j in range(xcopies)]

    py = page_size[1]
    ycopies = int(py / iy)
    yspace = int((py % iy) / (ycopies + 1))
    y = [yspace + (yspace + iy) * j for j in range(ycopies)]

    return [(i,j) for i in x for j in y]

def crop_marks(im, page):
    coords = paste_coords(im)
    xs = list(set(c[0] for c in coords))
    ys = list(set(c[1] for c in coords))

    xs = [x+overprint for x in xs] + [x+im.size[0]-overprint for x in xs]
    ys = [y+overprint for y in ys] + [y+im.size[1]-overprint for y in ys]

    draw = ImageDraw.Draw(page)
    for x in xs:
        draw.line((x, 0, x, min(ys) - overprint), fill=(0,0,0))
        draw.line((x, max(ys) + overprint, x, page.size[1]), fill=(0,0,0))
    for y in ys:
        draw.line((0, y, min(xs) - overprint, y), fill=(0,0,0))
        draw.line((max(xs) + overprint, y, page.size[0], y), fill=(0,0,0))


def main():
    sheet = Image.new('RGB', page_size, (255,255,255))
    #im = Image.new('RGB', (1476,768), (0,0,128))
    im = Image.open('back.png')
    # increase size of image to counteract overprint
    im.resize((int(c + overprint) for c in im.size), resample=Image.LANCZOS)
    for coord in paste_coords(im):
        sheet.paste(im, coord)
    crop_marks(im, sheet)
    sheet.show()
    print(sheet)
    sheet.save('test.png', 'PNG')
    sheet.save('test.pdf', 'PDF')
    

if __name__ == '__main__':
    main()

    


