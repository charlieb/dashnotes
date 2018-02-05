#!/bin/env python3

import PIL.Image, PIL.ImageTk
import qrcode
import clipboard
import urllib as url

from pycoin.cmds import ku
from pycoin.key.BIP32Node import BIP32Node
from pycoin.services import blockcypher
from pycoin.tx import tx_utils

import threading
import queue

duffs_per_dash = 10**8
def duff2dash(d): return float(d) / float(duffs_per_dash)
def dash2duff(d): return int(d * duffs_per_dash)

blockcypher_api_key = 'ee938bfdf0e949c3888b63940969e35c'
def send_funds(from_addr, payables, wif, fee):
    '''from_addr is a simple address in a string.
    payables is a list of tuples of (address, amount in duffs)
    wif is the wallet import format version of the private key for from_addr
    fee is the fee in duffs should be 100-200 duffs at time of writing.

    Amount at from_addr must = sum of amounts in tos + fee ot TX will not be valid.
    '''
    # Note: Requires https://github.com/charlieb/pycoin version until 
    # https://github.com/richardkiss/pycoin/pull/265 is merged

    bc = blockcypher.BlockcypherProvider(netcode='DASH', api_key=blockcypher_api_key)

    spendables = bc.spendables_for_address(from_addr)
    tx = tx_utils.create_tx(spendables, payables, fee=fee)
    tx_utils.sign_tx(tx, [wif])
    rtx = bc.broadcast_tx(tx)
    return rtx
    
def getbalance(addr):
    try:
        with url.request.urlopen('https://explorer.dash.org/chain/Dash/q/addressbalance/' + addr) as response:
            addr_data = response.read().decode()
    except url.error.HTTPError as e:
        if e.code == 400: # not found
            addr_data = '0.0'
        else:
            raise
    #print(addr_data)
    return addr_data

def new_keypair():
    # ku -n DASH create 
    # wif = private key
    # Dash Address = public address
    key = BIP32Node.from_master_secret(ku.get_entropy(), 'DASH')
    pub = key.address(use_uncompressed=False)
    priv = key.wif(use_uncompressed=False)
    return pub, priv

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

class FundSender(Tk):
    def __init__(self, balance_queues):
        super().__init__()
        self.title('Send to DashNotes')
        self.savefilename = 'FundSender.sav'
        try:
            with open(self.savefilename, 'r') as f:
                self.address, self.privkey = (line.strip() for line in f.readlines())
        except: #TODO only filenotfound exception
            self.address, self.privkey = new_keypair()
            try:
                with open(self.savefilename, 'w') as f:
                    f.write(self.address + '\n' + self.privkey)
            except:
                pass # TODO: WARN USER

        #print([self.address, self.privkey])

        self.balance_queues = balance_queues
        #self.addr = 'XqsjzGLmTcXZGH6aMVJ4YToQ8FnzTcEaTk'
        #self.address = 'XwLpYiL77cPtPfj6t9VLCCgKERSccEoaKS'

        self.addresses = []
        self.balance = 0.000
        self.fee = 226
        self.address_filename = ''
        self.option_add("*Listbox.Font", "courier")
        self._menu()
        self._address_UI_init()
        self._amt_per_address_changed()

        self.update_balances_completed = True
        self.update_balances_loop()
        self.receive_balances_loop()

        self.query_sent_repeat = False

    def receive_balances_loop(self):
        q = self.balance_queues['results']
        while not q.empty():
            bal = q.get()
            if bal is not None:
                if bal['address'] == self.address:
                    self.balance = float(bal['balance'])
                    self._amt_per_address_changed()
                elif bal['address'] in self.addresses:
                    self.tv_addresses.item(bal['address'], values=[bal['balance']])
                q.task_done()

        # wait 0.5 secs
        self.after(500, self.receive_balances_loop) 

    def update_balances_now(self):
        for addr in self.addresses:
            self.balance_queues['queries'].put(addr)
        self.balance_queues['queries'].put(self.address)
        self.update_balances_completed = False

    def update_balances_loop(self):
        if self.balance_queues['queries'].empty():
            if self.update_balances_completed:
                for addr in self.addresses:
                    self.balance_queues['queries'].put(addr)
                self.balance_queues['queries'].put(self.address)
                # update_balances_completed causes there to be 
                # an extra wait before queuing all the address
                # queries again. This means that we are not continuously
                # quertying for updated balances 
                self.update_balances_completed = False
            else:
                self.update_balances_completed = True
        
        # always wait 5 seconds before thinking about requeueing
        self.after(5000, self.update_balances_loop) 

    def _send_funds(self):
        self.query_sent_repeat = True
        send_funds(self.address, [(addr, int(float(self.amt_per_address.get()) * duffs_per_dash)) for addr in self.addresses], self.privkey, self.fee)
        self.update_balances_now()

    def _addr_to_clipboard(self):
        clipboard.copy(self.address)

    def _open_address_file(self):
        address_file = askopenfilename(initialdir='.',
                filetypes=(('Address File', '*.adr'), ('All Files', '*')),
                title='Choose Address File')

        if address_file == '': return

        self.address_file = address_file

        with open(self.address_file, 'r') as addr_file:
            self.addresses = [a.strip() for a in addr_file.readlines()]

        self.lb_address_file.set(self.address_file)

        self.tv_addresses.delete(*self.tv_addresses.get_children())
        for r in self.addresses:
            self.tv_addresses.insert('', END, text=r, iid=r)

        self.update_balances_now()

    def _amt_per_address_changed(self, *_):
        total = float(self.amt_per_address.get()) * len(self.addresses) + float(self.fee) / float(duffs_per_dash)
        need = total - self.balance
        if need < 0: need = 0

        self.lb_balance.set('    %0.8f Dash'%self.balance)
        self.lb_needed.set( '    %0.8f Dash'%duff2dash(need))

    def nop(self):
        pass

    def _menu(self):
        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self._open_address_file)
        filemenu.add_command(label="Save", command=self.nop)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        addressmenu = Menu(menubar, tearoff=0)
        addressmenu.add_command(label="Show Private Key", command=self.nop)
        addressmenu.add_command(label="Create New", command=self.nop)
        menubar.add_cascade(label="Address", menu=addressmenu)

        self.config(menu=menubar)

    def _address_UI_init(self):

        #       0      1      2  
        #    +------+------+
        # 0  | file | open |
        #    +---+--+------+
        # 1  |amt| Dash    |
        #    +---+---------+
        # 2  |bal need send|
        #    +-------------+
        #    |             |
        # 3  |      QR     |
        #    |             |
        #    +----+---+----+
        # 4  |addr|cpy|priv|         
        #    |----+---+----+
        # 5  | Addr search |
        #    +-------------+
        # 6  | Addrs list  |
        #
        # V2
        #            0        1
        #    +------------+--------+
        #    | menu                |
        #    +------------+--------+
        #  0 | amt Dashper|        |
        #  1 | balance    |  QR    |
        #  2 | NEEDED     |        |
        #  3 |    SEND    |addr cpy|
        #    +------------+--------+
        #  3 | Addr search?        |
        #    +---------------------+
        #  4 | Addrs list          |
        #
        #
        #

        # ====== Dash to send =======
        ds_frame = Frame(self)
        ## ------ amt -------
        Label(ds_frame, text='DASH per address:').grid(row=0, column=0)
        self.amt_per_address = StringVar()
        self.amt_per_address.set('0.00')
        Spinbox(ds_frame, textvariable=self.amt_per_address, from_=0.000, to=1000, increment=0.001, width=10, format='%6.8f').grid(row=0, column=1)

        ## ------ balance
        self.lb_balance = StringVar()
        Label(ds_frame, text='Current Balance:').grid(row=1, column=0)
        Label(ds_frame, textvariable=self.lb_balance).grid(row=1, column=1)

        self.lb_needed = StringVar()
        Label(ds_frame, text='DASH needed:').grid(row=2, column=0)
        Label(ds_frame, textvariable=self.lb_needed).grid(row=2, column=1)

        self._amt_per_address_changed()
        print(self.lb_needed.get())

        ds_frame.grid(row=0, column=0)

        # ====== QR code =======
        qr_frame = Frame(self)
        self.qr_image = PIL.ImageTk.PhotoImage(make_qr_im(self.address))
        im_label = Label(qr_frame, compound=BOTTOM, image=self.qr_image)
        im_label.image = self.qr_image
        im_label.grid(row=0, column=0, columnspan=3)

        ## ------- addr -------
        self.qr = StringVar()
        self.qr.set(split_addr(self.address))
        qr_label = Label(qr_frame, textvariable=self.qr)
        qr_label.grid(row=1, column=0, columnspan=2)

        ## ------ cpy ---------
        Button(qr_frame, text='Copy', width=4, command=self._addr_to_clipboard).grid(row=1, column=2, padx=5)
        qr_frame.grid(row=0, column=1)

        # ------ send
        Button(self, text='SEND', command=self._send_funds).grid(row=6, column=0, columnspan=3)
        
        # ------ Private ---------
        #cb_clip = Button(self, text='Private\nKey', width=5, command=self._addr_to_clipboard)
        #cb_clip.grid(row=5, column=2)

        # ------ all columns in place so configure them to auto-size
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 2, weight=1)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1)
        Grid.rowconfigure(self, 4, weight=1)

        return


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

from time import sleep
def remote_queries(queries, results):
    while True:
        address = queries.get(block=True)
        if address == 'QUIT': return
        balance = getbalance(address)
        results.put({'address': address, 'balance': balance})
        print(address, balance)
        queries.task_done()

if __name__ == '__main__':
    # Start remote query thread
    queues = {'queries': queue.Queue(), 'results': queue.Queue()}
    query_thread = threading.Thread(target=remote_queries, kwargs=queues)
    query_thread.start()

    top = FundSender(queues)
    top.mainloop()


    queues['queries'].put('QUIT')

    query_thread.join()



