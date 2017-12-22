#!/bin/env python3

import json
import requests
import base64
import PIL.Image, PIL.ImageTk
import qrcode

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

class FundSender(Frame):
    def __init__(self):
        super().__init__()
        self.option_add("*Listbox.Font", "courier")
        self.pack(expand=True, fill='both')
        self._address_file_picker()
        #self._address_list()

    # TODO: query block explorer API
    def check_balances(self):
        pass 

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

    def _address_file_picker(self):

        # ------ file --------
        label = Label(self, text='Address file:')
        label.grid(sticky=W, row=0, column=0, padx=10, pady=5)

        # filename
        self.ui_filename = StringVar()
        filename = Entry(self, state='readonly', textvariable=self.ui_filename)
        filename.grid(sticky=E, row=0, column=1, padx=5, pady=5)

        fopen = Button(self, text='Open', command=self._open_address_file)
        fopen.grid(sticky=E, row=0, column=2, padx=10, pady=5)

        #Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 2, weight=1)

        # ------ QR code -------
        #self.qr_image = qrcode.make('1234567891234567891234567891234567890123456789')#.PIL.Image.new('1', (128,128), color=1)
        self.qr_image = PIL.ImageTk.PhotoImage(PIL.Image.new('1', (128,128), color=1))
        self.qr = StringVar()
        #im_label = Label(self, textvariable=self.qr)#, image=PIL.ImageTk.PhotoImage(self.qr_image))
        im_label = Label(self, image=self.qr_image)
        im_label.image = self.qr_image
        im_label.grid(sticky=N+E+S+W, row=0, column=3, padx=10, pady=10)
        self.qr.set('blah blah qr')

        Grid.columnconfigure(self, 3, weight=1)


        # ------ addresses -------
        fr = Frame(master=self)
        fr.grid(sticky=N+E+S+W, row=1, column=0, columnspan=5)
        Grid.rowconfigure(self, 1, weight=1)

        # tv_addresses
        self.tv_addresses = Treeview(fr)
        self.tv_addresses.pack(side=LEFT, expand=True, fill='both')

        sb = Scrollbar(fr)
        sb.pack(side=RIGHT, fill='y')

        self.tv_addresses.config(yscrollcommand=sb.set)
        sb.config(command=self.tv_addresses.yview)


if __name__ == '__main__':
    #test()
    top = FundSender()
    top.mainloop()



