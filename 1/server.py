from Tkinter import *
from socket import *
from threading import *
from ScrolledText import*
L2I = dict(zip("abcdefghijklmnopqrstuvwxyz",range(26)))
I2L = dict(zip(range(26),"abcdefghijklmnopqrstuvwxyz"))
key = 5
class Receive():
  def __init__(self, server, gettext):
    self.server = server
    self.gettext = gettext
    while 1:
      try:
        ciphertext = self.server.recv(1024)
	print("received cipher massage :" + ciphertext);
	#decrypt
	text = ""
	for c in ciphertext.lower():
    		if c.isalpha(): text += I2L[ (L2I[c] - key)%26 ]
    		else: text += c
			#Close
	if text =="good bye" :
		print("Good Bye!! see you later:)")
		self.server.close()
		quit()
        if not text: break
        self.gettext.configure(state=NORMAL)
        self.gettext.insert(END,'client >> %s\n'%text)
        self.gettext.configure(state=DISABLED)
        self.gettext.see(END)
      except:
        break	
class App(Thread):
#Socket
  server = socket()
  server.bind(('localhost', input("Port: ")))
  server.listen(5)
  client,addr = server.accept()
  def __init__(self, master):
    Thread.__init__(self)
    frame = Frame(master)
    frame.pack()
    self.gettext = ScrolledText(frame, height=10,width=100, state=NORMAL)
    self.gettext.pack()
    sframe = Frame(frame)
    sframe.pack(anchor='w')
    self.pro = Label(sframe, text="Server>>");
    self.sendtext = Entry(sframe,width=80)
    self.sendtext.focus_set()
    self.sendtext.bind(sequence="<Return>", func=self.Send)
    self.pro.pack(side=LEFT)
    self.sendtext.pack(side=LEFT)
    self.gettext.insert(END,'Welcome to Chat\n')
    self.gettext.configure(state=DISABLED)
  def Send(self, args):
    self.gettext.configure(state=NORMAL)
    plaintext = self.sendtext.get()
    # encrypt
    text = ""
    for c in plaintext.lower():
    	if c.isalpha(): text += I2L[ (L2I[c] + key)%26 ]
    	else: text += c
    print("cipher text sent :" + text)
    self.server.close()
    if text=="": text=" "
    self.gettext.insert(END,'Me >> %s \n'%plaintext)
    self.sendtext.delete(0,END)
    self.client.send(text)
    self.sendtext.focus_set()
    self.gettext.configure(state=DISABLED)
    self.gettext.see(END)
  def run(self):
    Receive(self.client, self.gettext)
root = Tk()
root.title('Server Chat')
app = App(root).start()
root.mainloop()
