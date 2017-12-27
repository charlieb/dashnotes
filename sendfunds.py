#!/bin/env python3

import json
import requests
import base64
import PIL.Image, PIL.ImageTk
import qrcode
import clipboard

req_id = 0
def request(method, params=[]):
    global req_id
    url = "http://localhost:9998/"
    #TODO: read out of the config file, obviously!
    rpc_user = 'haXLL1he3CFzzEHQjhUt3OXCFnOAKTSh56i'
    rpc_pass = 'xGN/DzVnvLDD5Cmcke0V+O4WmEoo771k68MA'
    auth = base64.b64encode((rpc_user + ':' + rpc_pass).encode('utf8')).decode('utf8')
    headers = {'Host': '127.0.0.1:9998',
               'Authorization': 'Basic ' + auth,
               'content-type': 'application/json'}

    body = {
        "method": method,
        "params": params,
        "id": req_id,
    }
    body = json.dumps(body)
    print(body)

    response = requests.post(url, data=body, headers=headers).json()

    # Each request must have a different id
    req_id += 1

    print(response)
    return response['result']

def send_funds(from_acct, to_addrs, amt_per_address):
    balance = request('getbalance', [from_acct])
    if len(to_addrs) * amt_per_address > balance:
        print('Insufficient Funds: you have %f, you need %f to send %f to %d wallets'%(
            balance, len(to_addrs) * amt_per_address, amt_per_address, len(to_addrs)))
    reqs = {a:amt_per_address for a in to_addrs}
    res = request('sendmany', [from_acct, reqs])
    print(res)

def test():
    with open('addresses', 'r') as addr_file:
        to_addrs = addr_file.readlines()

    send_funds('', to_addrs, 0.0002)

#######################################
# UI
#######################################
from tkinter import *
from tkinter.ttk import * 
from tkinter.filedialog import askopenfilename

def make_qr_im(data):
    qr = qrcode.QRCode(
        #version=1,
        #error_correction=qrcode.constants.ERROR_CORRECT_L,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=None)
    return qr.make_image()

def split_addr(addr):
    addr = addr[:5] + ' ' + ' '.join(addr[i:i+4] for i in range(5, len(addr)-1, 4)) + addr[-1]
    addr = addr[0:20] + '\n' + addr[21:]
    return addr
    

class FundSender(Frame):
    def __init__(self):
        super().__init__()
        self.addresses = []
        self.option_add("*Listbox.Font", "courier")
        self.pack(expand=True, fill='both')
        self._address_file_picker()
        #self._address_list()

    # TODO: query block explorer API
    def check_balances(self):
        pass 

    def _addr_to_clipboard(self):
        print(self.addr)
        clipboard.copy(self.addr)

    def _open_address_file(self):
        filename = askopenfilename(initialdir='.',
                filetypes=(('Address File', '*.adr'), ('All Files', '*')),
                title='Choose Address File')

        with open(filename, 'r') as addr_file:
            self.addresses = addr_file.readlines()

        self.filename.set(filename)

        self.tv_addresses.delete(*self.tv_addresses.get_children())
        for r in self.addresses:
            self.tv_addresses.insert('', END, text=r.strip())

    def _amt_per_address_changed(self, *_):
        self.total.set('= %0.3f DASH total'%(float(self.amt_per_address.get()) * len(self.addresses)))

    def _address_file_picker(self):

        #       0      1      2     3    4
        #    +------+------+-----+----------+
        # 0  | lbl  | file | opn |          |
        #    +------+------+-----+   QR     |
        # 1  | amt  | Dash |tot  |          |
        #    +------+------+-----+----------+
        # 2  |total |-bal  | send| addr |cpy|
        #    +------+------+-----+----------+
        # 3  |   Address searchbox          |
        #    +------------------------------+
        # 4  |   Addresses listbox          |
        #
        # ------ file --------
        label = Label(self, text='Address file:')
        label.grid(sticky=W, row=0, column=0, padx=10, pady=5)

        # filename
        self.filename = StringVar()
        filename = Entry(self, state='readonly', textvariable=self.filename)
        filename.grid(sticky=E, row=0, column=1, padx=5, pady=5)

        # open button
        fopen = Button(self, text='Open', command=self._open_address_file)
        fopen.grid(sticky=E, row=0, column=2, padx=10, pady=5)


        # ------ QR code -------
        # TODO: generate once and load from file thereafter
        self.addr = 'XqsjzGLmTcXZGH6aMVJ4YToQ8FnzTcEaTk'
        self.qr_image = PIL.ImageTk.PhotoImage(make_qr_im(self.addr))
        im_label = Label(self, compound=TOP, image=self.qr_image)
        im_label.image = self.qr_image
        im_label.grid(row=0, column=3, padx=10, columnspan=2, rowspan=2, sticky=S)

        # ------- addr -------
        self.qr = StringVar()
        self.qr.set(split_addr(self.addr))
        qr_label = Label(self, textvariable=self.qr)
        qr_label.grid(row=2, column=3, padx=10, sticky=N)

        # ------ cpy ---------
        cb_clip = Button(self, text='Copy', command=self._addr_to_clipboard)
        cb_clip.grid(row=2, column=4, padx=10, sticky=W)
        
        # ------ amt -------
        self.amt_per_address = StringVar()
        self.amt_per_address.set('0.00')
        # change event is taken care of with a trace on the textvariable setup
        # below
        sb_amt = Spinbox(self, textvariable=self.amt_per_address, from_=0.000, to=1000, increment=0.001, width=10)
        sb_amt.grid(row=1, column=0, padx=10)
        
        # ------ Dash ------
        naddrs = Label(self, text='DASH per address')
        naddrs.grid(row=1, column=1, sticky=W)

        # ----- tot -------
        self.total = StringVar()
        self.total.set('= %s DASH total'%self.amt_per_address.get())
        total = Label(self, textvariable=self.total)
        total.grid(row=1, column=2, sticky=W)

        # ------
        self.balance = StringVar()
        self.balance.set('Current Balance: %0.3f'%(0.0001))
        bal = Label(self, textvariable=self.balance)
        bal.grid(row=2, column=0, padx=10, columnspan=2)

        # ----- 
        self.outstanding = StringVar()
        self.outstanding.set('Please send: %0.3f to address'%(0.0001))
        bal = Label(self, textvariable=self.outstanding)
        bal.grid(row=2, column=2, padx=10)

        # ------ all columns in place so configure them to auto-size
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 2, weight=1)
        Grid.columnconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 4, weight=1)

        # ------ addresses -------
        fr = Frame(master=self)
        fr.grid(sticky=N+E+S+W, row=4, column=0, columnspan=5)
        Grid.rowconfigure(self, 1, weight=1)

        # tv_addresses
        self.tv_addresses = Treeview(fr)
        self.tv_addresses.pack(side=LEFT, expand=True, fill='both')

        sb = Scrollbar(fr)
        sb.pack(side=RIGHT, fill='y')

        self.tv_addresses.config(yscrollcommand=sb.set)
        sb.config(command=self.tv_addresses.yview)

        # Some events after all variables have been initialised
        self.amt_per_address.trace('w', self._amt_per_address_changed)

if __name__ == '__main__':
    #test()
    top = FundSender()
    top.mainloop()



