#! /usr/bin/env python3

import os
import sys
import socket
import pickle
import threading
import time
from builtins import print
from tkinter import *
from Crypto.Random import random

from APIs.logging import Log
from APIs.security import *
GUI_OBJ = None
byeFlag = 1;
userName=''
KEY = None

class GUI(object):
    def __init__(self, master, network_obj):
        global GUI_OBJ
        self.master = master
        self.network = network_obj
        self.txt_input = Text(self.master, width=60, height=5)
        self.txt_disp = Text(self.master, width=60, height=15, bg='light grey')
        self.txt_input.bind('<Return>', self.get_entry)
        self.txt_disp.configure(state='disabled')
        self.txt_input.focus()
        self.txt_disp.pack()
        self.txt_input.pack()
        self.flag = True
        GUI_OBJ = self

    def init_canvas(self):
        self.canvas = Canvas(root, width=730, height=600)
        self.canvas.pack(fill="both", expand=True)

    def init_frame(self):
        self.frame_left = Frame(self.canvas, height=400, width=200)
        self.frame_right = Frame(self.canvas, width=500)
        self.frame_right_chat_show = Frame(self.frame_right)
        self.frame_right_chat_input = Frame(self.frame_right, width=460)
        self.frame_right_chat_input_buttons = Frame(self.frame_right, width=40)

        self.frame_left.pack(fill=Y, side='left')
        self.frame_right.pack(fill=Y, side='left')
        self.frame_right_chat_show.pack(fill=X, side='top')
        self.frame_right_chat_input.pack(side='left')
        self.frame_right_chat_input_buttons.pack(side='left')


    def update(self, msg):

        msg = '\n' + msg
        self.txt_disp.configure(state='normal')
        self.txt_disp.insert(END, msg)
        self.txt_disp.see(END)
        self.txt_disp.configure(state='disabled')

    def get_entry(self, *arg):

        msg_snd = self.txt_input.get('1.0', END)
        msg_snd = msg_snd.strip('\n')
        self.network.send_msg(msg_snd)
        msg_snd = '<YOU> ' + msg_snd
        self.update(msg_snd)
        self.txt_input.delete('1.0', END)

    def get_msg(self, *arg):

        while True:
            msg_rcv = self.network.get_msg()
            if msg_rcv:
                msg_rcv = msg_rcv.strip('\n')
                print('-' * 60)
                print(msg_rcv)
                self.update(msg_rcv)


class Network():
    def __init__(self, thread_name, SRV_IP='', SRV_PORT=''):
        self.SRV_IP = SRV_IP
        self.SRV_PORT = int(SRV_PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.SRV_IP, self.SRV_PORT))
        self.KEY_FLAG = False
        self.priv_key = None
        self.pub_key = None
        self.custemor_pub_key =None
        self.custemor_priv_key =None
        self.certified_custemor_pub_key=None
        self.certified_pub_key =None
        self.ca_pub_key=None
        self.KEY = None
        self.nonce =None
        self.KEYNonce = None
		
    def gen_nonce(self):
        TOKEN_CHAR_LIST = "abcdefghij!@#$%"
        self.nonce = ''.join(random.sample(TOKEN_CHAR_LIST, 10))
        self.KEYNonce =hasher(self.nonce + self.KEY)


    def genRSA(self, *args):
        logging.log("Generating private and public key")
        self.priv_key, self.pub_key = RSA_.genRSA()
        self.custemor_priv_key , self.custemor_pub_key = RSA_.genRSA()
        logging.log("Keys generation completed.")
        logging.log(self.pub_key.exportKey())
        print("My Public Key " + str(self.pub_key))
        logging.log(self.priv_key.exportKey())
        print("My Private  Key " + str(self.priv_key))
    def getSharedKey(self):
        TOKEN_CHAR_LIST = "abcdefghij!@#$%"
        passphrase = ''.join(random.sample(TOKEN_CHAR_LIST, 10))
        shared_key = hasher(passphrase)
        print("shared_key" + str(shared_key) + str(type(shared_key)))
        print("custemor_pub_key : " + str(self.custemor_pub_key) + str(type(self.custemor_pub_key)))
        EnSharedKey = RSA_.encrypt(self.custemor_pub_key, shared_key)
        if EnSharedKey:
            return (shared_key, EnSharedKey)
        else:
            logging.log("Unable to encrypt shared key with RSA.", msg_type='ERROR')

    def readSocketAndOutput(self,s):
        global byeFlag
        while True:
            if byeFlag:
              #  try:
                INandWrite1=s.recv(20000)
                hashed,str1=pickle.loads(INandWrite1)
                print ("Encrypted massage : " + str(str1))
                str1= AES_.decrypt(self.KEYNonce.encode(), str1)
                print ("Delivered hash " + str(hashed))
                if hashed==hasher(str1) :
                    logging.log("We Have integrity")
                else :
                    logging.log("We Dont Have integrity")
                print("\r>>> " + str1 + "\n<<<", end="", flush=True)


    def readSTDINandWriteSocket(self,s):
        global byeFlag
        while True:
            if byeFlag:
                str2 = input("<<< ")
                INandWrite2=(hasher(str2),AES_.encrypt(self.KEYNonce.encode(), str2))
                INandWrite2 = pickle.dumps(INandWrite2)
                s.send(INandWrite2)


    def check_ca(self):
        MY = RSA_.decrypt(self.ca_pub_key, self.certified_custemor_pub_key)
        if hash(self.custemor_pub_key) == MY :
             print("success")
             return 1
        #return 1



    def CHAT(self,userName):
        ch = input("Connect[1] if you are Client wait[2] for peer connection. Enter choice:")
        flag_rec = 1
        if ch == "1":
            host = '127.0.0.1'
            port = 54362
            self.s.connect((host, port))
            share_pub = (userName,self.certified_pub_key, self.pub_key)
            share_pub = pickle.dumps(share_pub)
            print("Waiting for Sending...")
            self.s.send(share_pub)
            rec_pub1 = self.s.recv(1024)  # 4000
            if rec_pub1:
                self.nonce,EnSharedKey, custemor,self.certified_custemor_pub_key ,self.custemor_pub_key = pickle.loads(rec_pub1)
                if self.check_ca():
                    logging.log("pubic key is valid")
                self.KEY = RSA_.decrypt(self.priv_key, EnSharedKey)
                print("AES KEY" + str(self.KEY))
                print ("nonce :" + self.nonce)
                self.KEYNonce = hasher(self.nonce + self.KEY)
            threading.Thread(target=self.readSocketAndOutput, args=(self.s,)).start()
            threading.Thread(target=self.readSTDINandWriteSocket, args=(self.s,)).start()

        elif ch == "2":
            host = '127.0.0.1'
            port = 54362
            self.s.bind((host, port))
            print("Waiting for connection...")
            self.s.listen(2)
            print("Waiting for RECEVING...")


            while True:
                c, addr = self.s.accept()
                if flag_rec ==1 :
                    rec_pub2 = c.recv(1024)
                    if rec_pub2:
                        custemor, self.certified_custemor_pub_key, self.custemor_pub_key = pickle.loads(rec_pub2)
                        if self.check_ca():
                            logging.log("pubic key is valid")
                        if self.custemor_pub_key:
                            self.KEY, EnSharedKey = self.getSharedKey()
                            print("AES KEY" + str(self.KEY) )
                    self.gen_nonce()
					print ("nonce :" + self.nonce)
                    share_pub = (self.nonce,EnSharedKey,userName,self.certified_pub_key, self.pub_key)
                    share_pub = pickle.dumps(share_pub)
                    c.send(share_pub)

                    flag_rec =0
                threading.Thread(target=self.readSocketAndOutput, args=(c,)).start()
                threading.Thread(target=self.readSTDINandWriteSocket, args=(c,)).start()

        else:
            print("Incorrect choice")
            sys.exit()

    def initEncryption(self, userName):
        global KEY
        msg_send = (userName, self.pub_key)
        msg_send = pickle.dumps(msg_send)
        self.client.send(msg_send)
        logging.log("User name along with public key has been sent to the CA.")
        data = self.client.recv(4000)
        if data:
            self.ca_pub_key, self.certified_pub_key = pickle.loads(data)
            self.CHAT(userName)

    def get_msg(self):
        if KEY != None:
            msg_rcv = AES_.decrypt(KEY.encode(), self.client.recv(20000))
            return msg_rcv

    def send_msg(self, msg_snd):
        if KEY is None:

            self.initEncryption(msg_snd)
            return
        try:
            print(msg_snd)
            result = self.client.send(AES_.encrypt(KEY.encode(), msg_snd))
            print("Bytes sent: ", result)
        except Exception as e:
            print(e)
            GUI.update(GUI_OBJ, "Not connected to the server")


def connection_thread(*args):
    root = args[0]
    retry_count = 0
    gui_flag = False
    while True:
        try:
            network = Network('network_thread', '127.0.0.1', 4445)
            if gui_flag:
                gui.network = network
            if not gui_flag:
                gui = GUI(root, network)
            logging.log('Connected to the server')
            gui.update('Connected to the server')
            gui.update('Enter your name.')
            break
        except Exception as e:
            msg = "[Retry {}] {}".format(retry_count + 1, e)
            logging.log(msg)
            retry_count += 1
            if retry_count == 1:
                gui = GUI(root, None)
                gui.update("Failed to connect the server.\n" + \
                           "Started retrying.")
                gui.update("Retry connecting...")
                time.sleep(5)
                gui_flag = True
            elif 4 > retry_count:
                time.sleep(5)
                gui_flag = True
            elif retry_count == 5:
                gui.update("Retry limit exceeded.\n" + \
                           "Unable to connect the server.\n" + \
                           "Program will automatically exit after 5 sec.")
                time.sleep(5)
                gui_flag = True
                root.destroy()
    logging.log('New thread has been initialized to fetch data from the CA')
    rsa_thread = threading.Thread(target=network.genRSA, args=())
    rsa_thread.start()
    rsa_thread.join()
    threading._start_new_thread(gui.get_msg, ())


def main():
    root = Tk()
    root.title('CA_Certificate')

    threading._start_new_thread(connection_thread, (root,))
    logging.log('Connection thread has been called')

    root.mainloop()

    logging.log('exiting main thread.')
    logging.stop()


if __name__ == "__main__":
    logging = Log(f_name='client_chatroom_')
    logging.logging_flag = True
    logging.validate_file()
    main()