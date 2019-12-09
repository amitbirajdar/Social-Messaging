import os
import json
import socket
import tkinter as tk
import threading

CONNECTION_PORT = 9311

class Serializable:

	def __init__(self):
		self.file = None

	def serialize(self, path, mode):
		try:
			self.file = open(path, mode)
		except:
			raise FileNotFoundError()
		if self.file:
			return self.file

class App(Serializable, threading.Thread):

	def __init__(self):
		Serializable.__init__(self)
		if os.path.isfile("user2.cfg"):
			self.data = self.load("user2.cfg")
		else:
			self.data = {
				"HOST": "127.0.0.1",
				"NICKNAME2": "Unknown User"
			}
		self.write("user2.cfg")
		threading.Thread.__init__(self)

		self.start() # starts a thread by calling run function

	def write(self, path):
		self.serialize(path, "w").write(json.dumps(self.data)) #json.dumps() converts python object into json string
		self.file.close()

	def load(self, path):
		json_data = open(path, "r")
		self.data = json.load(json_data) #json.load() converts json string into python dictionary
		json_data.close()
		return self.data

	def callback(self): #used for aynchronous handling
		self.root.quit()

	def center(self, win):
		win.update_idletasks()  # event callback to force screen update
		width = win.winfo_width()
		height = win.winfo_height()
		x = (win.winfo_screenwidth() // 2) - (width // 2) # // is used for floor division
		y = (win.winfo_screenheight() // 2) - (height // 2)
		win.geometry("{}x{}+{}+{}".format(width, height, x, y)) # x, y give coordinates of upperleft corner of window



	def run(self):
		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)
		self.root.title("Baby Whatsapp")
		self.root.grid()
		self.root.grid_columnconfigure(0, weight=1) # column resizing
		for n in range(7):
			self.root.grid_rowconfigure(n, weight=2)
		self.create_widgets()
		self.console.insert(tk.END, "Baby is Awake.\n")
		self.connected = False
		self.center(self.root)
		self.root.mainloop()

	def create_widgets(self):
		self.console = tk.Text(self.root, bg="#000", fg="#0F0", highlightcolor="#F00", highlightthickness=2)
		self.console.grid(column=0, row=0, padx=25, pady=10, sticky=tk.W+tk.E) # sticky enables the widget and cell to touch each other at specified compass direction

		self.msg_label = tk.Label(self.root, text="Message: ")
		self.msg_label.grid(column=0, row=1, pady=10, sticky=tk.W+tk.E)
		self.msg_area = tk.Text(self.root, height=6, width=58, bg="#000", fg="#0F0", highlightcolor="#F00", highlightthickness=2)
		self.msg_area.grid(column=0, row=2, padx=25, pady=10, sticky=tk.W+tk.E)
		self.msg_area.focus()
		self.send_button = tk.Button(self.root, text="Send", command=self.send) # command is function to call on event


		self.send_button.grid(column=0, row=3, padx=30, pady=10, sticky=tk.W)
		self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
		self.connect_button.grid(column=0, row=3, padx=130, pady=10, sticky=tk.W)
		self.quit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
		self.quit_button.grid(column=0, row=3, padx=230, pady=10, sticky=tk.W)

	def send(self, x=None):
		self.sock.sendall(bytes(json.dumps({   #sendall sends whole buffer instead of small no of bytes

			"data": self.msg_area.get("1.0", tk.END),
			"user": self.data["NICKNAME2"]
		}), "utf-8"))
		self.msg_area.delete('1.0',tk.END)

	def connect(self, x=None):
		if not self.connected:
			self.host = self.data["HOST"]
			self.console.insert(tk.END, "Connecting to {host}...\nApproaching Baby\n".format(host = self.host))

			try:
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.connect((self.host, CONNECTION_PORT))
				self.console.insert(tk.END, "Connection established.\nBaby is Laughing\n")
				self.connect_button.config(text="Disconnect")
				self.connected = True
			except Exception as e:
				self.console.insert(tk.END, "Error trying to connect to {host}: {msg}\nBaby is crying \n".format(host = self.host, msg = str(e)))
		else:
			self.sock.close()

			self.console.insert(tk.END, "Connection with {host} destroyed.\nBaby is asleep \n".format(host = self.host))
			self.connect_button.config(text="Connect")
			self.connected = False

if __name__ == '__main__':
	app = App()
	while 1:
		try:
			received = app.sock.recv(10000).decode("utf-8")
			app.console.insert(tk.END, "{msg}\n".format(msg = received))
			app.console.focus()


		except:
			pass
