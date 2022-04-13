################################################################################
###                                 Imports                                  ###
################################################################################
from Crust import Crust
import socket
import threading
import os
import time
import sys

################################################################################
###                             Helper Functions                             ###
################################################################################
def client_rx(conn, fin):
	"""
	PURPOSE: handles receiving data from a client
	ARGS:
		conn (socket): socket to client
		fin (file-like object): file like object to write to
	RETURNS: none
	NOTES: to be run in a separate thread
	"""
	while True:
		#wait for input from client
		data = conn.recv(1024)
		if data == b'':
			#Socket died
			break

		fin.write(data.decode("ascii"))
		fin.flush()

################################################################################
def client_tx(conn, fout):
	"""
	PURPOSE: handles transmitting data to client
	ARGS:
		conn (socket): socket to client
		fout (file-like object): file like object to read from
	RETURNS: none
	NOTES: to be run in a separate thread
	"""
	while True:
		c = fout.read(1)
		conn.send(c.encode("ascii"))

################################################################################
###                                  Main                                    ###
################################################################################
#Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 30000))
sock.listen(5)
print("Starting server...")
print("Kill with 'ctrl-c' or 'ctrl-break'")

#Listen for connections
my_threads = []
while True:
	#Wait for connection
	print("Waiting for client...")
	clientsock, addr = sock.accept()

	#Create a new shell
	r, w = os.pipe()
	shell_fin_r = os.fdopen(r, 'r')
	shell_fin_w = os.fdopen(w, 'w')
	r, w = os.pipe()
	shell_fout_r = os.fdopen(r, 'r')
	shell_fout_w = os.fdopen(w, 'w')
	#write fout and ferr to the same place for now
	crust = Crust(shell_fin_r, shell_fout_w, shell_fout_w)
	#start thread to handle transmitting output to client
	tx_thread = threading.Thread(target=client_tx, args=(clientsock, shell_fout_r), daemon=True)
	tx_thread.start()
	#start thread to handle receiving input from client and passing to the shell
	rx_thread = threading.Thread(target=client_rx, args=(clientsock, shell_fin_w), daemon=True)
	rx_thread.start()
	#run shell
	print("Running shell...")
	crust.run()

################################################################################
###                               End of File                                ###
################################################################################