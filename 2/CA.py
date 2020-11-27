#! /usr/bin/env python3

import os
import sys
import socket

import pickle
import threading
import time
from datetime import datetime


from APIs.logging import Log
from APIs.logging import Color
from APIs.security import *
from Crypto.Random import random


TERMINATE = False
CLI_HASH = {}
KEY = ''
CA = RSA_()
CA.CA_priv_key, CA.CA_pub_key = RSA_.genRSA()

print("CA Public Key : " + str(CA.CA_pub_key))
print("CA Private Key" + str(CA.CA_priv_key))

class Server():
    def __init__(self):
        self.HOST_IP = '0.0.0.0'
        self.HOST_PORT = '4445'
        self.MAX_USR_ACCPT = '100'

    def show_help(self):
        msg = '''
        AVAILABLE COMMANDS:
        \h          Print these information
        \sd         Show default configuration
        \sc         Show current configuration
        \su        Show active users
        \sf         Shutdown server '''
        print(msg)

    def show_config(self, type_='default'):
        if type_ in ('active', 'ACTIVE'):
            msg = '''
            Active configuration of the server :
            HOST IP = ''' + self.HOST_IP + '''
            HOST PORT = ''' + self.HOST_PORT + '''
            MAX USER ALLOWED = ''' + self.MAX_USR_ACCPT
            logging.log('Showing Active server configuration')
            print(msg)
        else:
            msg = '''
            Default configuration of the server:
            HOST IP = 0.0.0.0
            HOST PORT = 4444
            MAX USER ALLOWED = 100'''
            print(msg)

    def set_usr_config(self, parameters):
        if parameters:
            if sys.argv[1] in ('-h', '--help'):
                self.show_help()
            try:
                self.HOST_IP = sys.argv[1]
                self.HOST_PORT = sys.argv[2]
                self.MAX_USR_ACCPT = sys.argv[3]
            except:
                print('USAGE:\nscript ip_address port_number max_usr_accpt')
                sys.exit(0)
        else:
            self.HOST_IP = input('Enter host IP : ')
            self.HOST_PORT = input('Enter host PORT : ')
            self.MAX_USR_ACCPT = input('Enter max number of users server would accept : ')

    def update_active_users(self):
        self.user_list = []
        for cli_obj in CLI_HASH.values():
            self.user_list.append(cli_obj.userName)


    def srv_prompt(self):
        global TERMINATE
        print("for help plase use this command '\h'")
        while True:
            opt = input(Color.PURPLE + '\nenter command $ ' + Color.ENDC)
            if opt == '\h':
                self.show_help()
            elif opt == '\sd':
                self.show_config(type_='default')
            elif opt == '\sc':
                self.show_config(type_='active')
            elif opt == '\su':
                self.update_active_users()
                logging.log(self.user_list)
                print(self.user_list)
            elif opt == '\sf':
                print(Color.WARNING +
                      'WARNING: All users will be disconnected with out any notification!!' +
                      Color.ENDC)
                opt = input('Do you really want to close server?[Y/N] ')
                if opt == 'Y':
                    logging.log('Shuting down server...')
                    print('Shuting down server...')
                    TERMINATE = True
                    sys.exit(0)
                else:
                    logging.log('Aborted.')
                    print('Aborted.')
                    pass
            elif opt == '':
                pass
            else:
                print('COMMAND NOT FOUND!!')

    def init_clients(self):
        global CLI_HASH
        while not TERMINATE:
            try:
                self.server.settimeout(1)
                conn, addr = self.server.accept()
            except socket.timeout:
                pass
            except Exception as e:
                raise e
            else:
                logging.log(
                    'A connection from [{}.{}] has been received.'.format(
                        addr[0], addr[1]))

                cli_obj = Client(conn, addr, self)

                CLI_HASH[conn] = cli_obj

                threading._start_new_thread(cli_obj.run, ('',))
        try:
            print('Server has stopped listening on opened socket.')
            msg = "Sorry! We are unable to serve at this moment."
            for cli_socket in CLI_HASH.keys():
                try:
                    cli_socket.send(msg.encode())
                except:
                    cli_socket.close()
                    CLI_HASH.pop(cli_socket)
        except:
            pass

    def init(self):
        logging.log('Initializing server')
        if len(sys.argv) == 1:
            self.show_config(type_='default')
            opt = input('Set these default config?[Y/n] ')
            if opt == '':
                opt = 'Y'
            if opt in ('Y', 'y', 'yes', 'Yes', 'YES'):
                print("Setting up default configurations...")
            else:
                self.set_usr_config(parameters=False)
        else:
            self.set_usr_config(parameters=True)


        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server.bind((self.HOST_IP, int(self.HOST_PORT)))
            self.server.listen(int(self.MAX_USR_ACCPT))
        except:
            print('Unable to bind HOST IP and PORT.')
            sys.exit('EMERGENCY')
        print('\nServer is listening at {}:{}'.format(self.HOST_IP, self.HOST_PORT))
        print('Server is configured to accept %s clients.' % (str(self.MAX_USR_ACCPT)))

        thread_cli = threading.Thread(target=self.init_clients, args=())
        thread_cli.start()
        self.srv_prompt()

        for thread in (thread_cli):
            thread.join()
        print('Server and Client threads are exited.')


class Client():
    def __init__(self, conn, addr, srv_obj):
        self.srv_obj = srv_obj
        self.conn = conn
        self.addr = addr
        self.userName = '-N/A-'
        self.PUBLIC_KEY = None
        self.KEY = ''

    def validate_user(self):
        pass

    def features(self, msg):
        if msg == '@getonline':
            self._loop_break_flag = True
            self.conn.send(
                AES_.encrypt(self.KEY, str(self.srv_obj.user_list)))

        if msg.split()[0][1:] in self.srv_obj.user_list:
            self._loop_break_flag = True
            for _conn in CLI_HASH:
                if CLI_HASH[_conn].userName == msg.split()[0][1:]:
                    try:
                        self.IND_SOCK = _conn
                    except Exception as e:
                        logging.log(msg_type='EXCEPTION', msg=e)

    def getSharedKey(self):
        TOKEN_CHAR_LIST = "abcdefghij!@#$%"
        passphrase = ''.join(random.sample(TOKEN_CHAR_LIST, 10))
        shared_key = hasher(passphrase)

        print ( "shared_key" + str(shared_key) + str(type(shared_key))  )
        EnSharedKey = RSA_.encrypt(self.PUBLIC_KEY, shared_key)
        if EnSharedKey:
            return (shared_key, EnSharedKey)
        else:
            logging.log("Unable to encrypt shared key with RSA.", msg_type='ERROR')

    def certifying_client_key(self):
        TOKEN_CHAR_LIST = "abcdefghij!@#$%"
        passphrase = ''.join(random.sample(TOKEN_CHAR_LIST, 10))
        shared_key = hasher(passphrase)
        CertifiedKey = hasher(str(self.PUBLIC_KEY))
        print (" hash of your Key : " + str(CertifiedKey))
        if CertifiedKey:
            return (CertifiedKey)
        else:
            logging.log("Unable to certify key.", msg_type='ERROR')

    def run(self, *args):
        data = self.conn.recv(4000)


        if data:
            self.userName, self.PUBLIC_KEY = pickle.loads(data)


        if self.PUBLIC_KEY :
            CertifiedKey = self.certifying_client_key()

            CertifiedKey2 = (CA.CA_pub_key,CertifiedKey)
            CertifiedKey2 = pickle.dumps(CertifiedKey2)
            self.conn.send(CertifiedKey2)
            print ("hey "+ str( self.userName) + "! your cretified Key is \n" + str(CertifiedKey2))


        while True:
            try:
                self._loop_break_flag = False
                msg = self.conn.recv(20000)
                msg = AES_.decrypt(self.KEY, msg)

                if msg:
                    if msg.split()[0][0] == '@':
                        self.srv_obj.update_active_users()
                        self.features(msg)

                    if not self._loop_break_flag:
                        log_msg = "<" + self.userName + "@" + self.addr[0] + "> " + msg
                        logging.log(msg_type='CHAT', msg=log_msg)

                else:
                    pass
            except Exception as e:
                logging.log(msg_type='EXCEPTION', msg='[{}] {}'.format(self.userName, e))


if __name__ == "__main__":
    try:

        logging = Log(f_name='server_chatroom_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        logging.logging_flag = False #TRUE
        logging.silent_flag = True #False
        logging.validate_file()
        server = Server()
        server.init()
    except SystemExit as e:
        if e.code != 'EMERGENCY':
            raise  # Normal exit, let unittest catch it
        else:
            print(sys.exc_info())
            print('Something went wrong!!')
            os._exit(1)
    except:
        raise Exception
        print('Something went wrong!!')
        time.sleep(1)
        os._exit(1)