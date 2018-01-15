#!/bin/env python3

import json
import requests
import base64
import PIL.Image, PIL.ImageTk
import qrcode
import clipboard
import urllib as url

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

def getbalance_bc(addr):
    try:
        with url.request.urlopen('https://api.blockcypher.com/v1/dash/main/addrs/' + addr) as response:
            addr_data = json.loads(response.read())
    except url.error.HTTPError as e:
        if e.code == 400: # not found
            addr_data = {'balance' : 0}
        else:
            raise
    print(addr_data)
    return addr_data
    
def getbalance(addr):
    try:
        with url.request.urlopen('https://explorer.dash.org/chain/Dash/q/addressbalance/' + addr) as response:
            addr_data = response.read().decode()
    except url.error.HTTPError as e:
        if e.code == 400: # not found
            addr_data = '0.0'
        else:
            raise
    print(addr_data)
    return addr_data

def test():
    getbalance('Xm29AommZxPX6ahLkfYTSHnsMKXCLHMDyL')

#######################################
# UI
#######################################
from tkinter import *
from tkinter.font import Font
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
        self.balance = 0.000
        self.address_filename = ''
        self.option_add("*Listbox.Font", "courier")
        self.pack(expand=True, fill='both')
        self._address_file_picker()
        self.update_balances()

    def update_balances(self):
        self.balance = float(getbalance(self.address))
        self._amt_per_address_changed()
        self._update_tv_addresses()

    def _send_funds(self):
        send_funds('', self.addresses, float(self.amt_per_address.get()))

    def _addr_to_clipboard(self):
        clipboard.copy(self.address)

    def _get_address_data(self):
        self.address_data = {a : getbalance(a) for a in self.addresses}
        print(self.address_data)

    def _update_tv_addresses(self):
        self._get_address_data()
        for item in self.tv_addresses.get_children():
            data = self.address_data[self.tv_addresses.item(item)['text']]
            self.tv_addresses.item(item, values=[data])


    def _open_address_file(self):
        self.address_file = askopenfilename(initialdir='.',
                filetypes=(('Address File', '*.adr'), ('All Files', '*')),
                title='Choose Address File')

        with open(self.address_file, 'r') as addr_file:
            self.addresses = [a.strip() for a in addr_file.readlines()]

        self.lb_address_file.set(self.address_file)

        self.tv_addresses.delete(*self.tv_addresses.get_children())
        for r in self.addresses:
            self.tv_addresses.insert('', END, text=r)

        self._update_tv_addresses()

    def _amt_per_address_changed(self, *_):
        send = float(self.amt_per_address.get()) * len(self.addresses) - self.balance
        if send < 0: send = 0

        self.lb_balance.set('Balance: %0.5f\tNeeded: %0.5f\tSend %0.5f'%(
                             self.balance, float(self.amt_per_address.get()) * len(self.addresses),
                             send))

    def _address_file_picker(self):

        #       0      1      2  
        #    +------+------+
        # 0  | file | open |
        #    +------+------+
        # 1  | amt  | Dash |
        #    +------+------+
        # 2  |bal need send|
        #    +-------------+
        #    |             |
        # 3  |      QR     |
        #    |             |
        #    +-------------+
        # 4  | addr    |cpy|         
        #    |-------------+
        # 5  | Addr search |
        #    +-------------+
        # 6  | Addrs list  |
        #
        # ------ file --------
        self.lb_address_file = StringVar()
        self.lb_address_file.set('No Address File')
        label = Label(self, textvariable=self.lb_address_file)
        label.grid(row=0, column=0, padx=5, pady=5)

        # open button
        fopen = Button(self, text='Open', command=self._open_address_file)
        fopen.grid(sticky=W, row=0, column=1, padx=5, pady=5)

        # ------ amt -------
        self.amt_per_address = StringVar()
        self.amt_per_address.set('0.00')
        # change event is taken care of with a trace on the textvariable setup
        # below
        sb_amt = Spinbox(self, textvariable=self.amt_per_address, from_=0.000, to=1000, increment=0.001, width=10, format='%6.5f')
        sb_amt.grid(row=1, column=0, padx=5, pady=5)
        
        # ------ Dash ------
        naddrs = Label(self, text='DASH per address')
        naddrs.grid(row=1, column=1, pady=5, sticky=W)


        # ------ balance
        self.lb_balance = StringVar()
        self._amt_per_address_changed()
        bal = Label(self, textvariable=self.lb_balance)
        bal.grid(row=2, column=0, padx=5, pady=5, columnspan=2)


        # ------ QR code -------
        fr = Frame(self)
        fr.grid(row=3, column=0, columnspan=2)
        # TODO: generate once and load from file thereafter
        #self.addr = 'XqsjzGLmTcXZGH6aMVJ4YToQ8FnzTcEaTk'
        self.address = 'XwLpYiL77cPtPfj6t9VLCCgKERSccEoaKS'
        self.qr_image = PIL.ImageTk.PhotoImage(make_qr_im(self.address))
        im_label = Label(fr, compound=TOP, image=self.qr_image)
        im_label.image = self.qr_image
        im_label.grid(row=0, column=0, sticky=S, columnspan=2)

        # ------- addr -------
        self.qr = StringVar()
        self.qr.set(split_addr(self.address))
        qr_label = Label(fr, textvariable=self.qr)
        qr_label.grid(row=1, column=0, padx=5)

        # ------ cpy ---------
        cb_clip = Button(fr, text='Copy', width=4, command=self._addr_to_clipboard)
        cb_clip.grid(row=1, column=1, padx=0, sticky=W)
        
        # ------ all columns in place so configure them to auto-size
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 2, weight=1)

        # ------ send
        self.cb_send = Button(fr, text='SEND', command=self._send_funds)
        self.cb_send.grid(row=6, column=0, columnspan=3)
        Grid.rowconfigure(self, 6, weight=1)

        # ------ addresses -------
        fr = Frame(master=self)
        fr.grid(sticky=N+E+S+W, row=7, column=0, columnspan=3)
        Grid.rowconfigure(self, 7, weight=1)

        # tv_addresses
        style = Style()
        style.configure('Treeview', font=('Consolas', 10))
        consolas = Font(family='Consolas', size=10)
        font_w = consolas.measure('m')
        self.tv_addresses = Treeview(fr, show='tree headings', columns=['Balance'])
        self.tv_addresses.column('#0', width=38*font_w, anchor=W, stretch=0)
        self.tv_addresses.heading('Balance', text='Balance')
        self.tv_addresses.column('Balance', anchor=E)
        self.tv_addresses.heading('#0', text='Address')
        self.tv_addresses.pack(side=LEFT, expand=True, fill='both')

        sb = Scrollbar(fr)
        sb.pack(side=RIGHT, fill='y')

        self.tv_addresses.config(yscrollcommand=sb.set)
        sb.config(command=self.tv_addresses.yview)

        # Some events after all variables have been initialised
        self.amt_per_address.trace('w', self._amt_per_address_changed)

if __name__ == '__main__':
    test()
    top = FundSender()
    top.mainloop()



