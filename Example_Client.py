################################################################################
###                                 Imports                                  ###
################################################################################
import socket
import threading
import sys

################################################################################
###                             Helper Functions                             ###
################################################################################
def server_rx(conn):
	"""
	PURPOSE: handles receiving data from the server
	ARGS:
		conn (socket): socket to server
	RETURNS: none
	NOTES: to be run in a separate thread
	"""
	while True:
		#wait for input from client
		data = conn.recv(1024)
		if data == b'':
			#Socket died
			break

		sys.stdout.write(data.decode("ascii"))
		sys.stdout.flush()

################################################################################
###                                  Main                                    ###
################################################################################
#Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to server...")
sock.connect(("127.0.0.1", 30000))
print("Connected to server")
print("Kill with 'ctrl-c' or 'ctrl-break'")

rx_thread = threading.Thread(target=server_rx, args=(sock,), daemon=True)
rx_thread.start()

while True:
	#Get user input
	user_input = input() + "\n"

	sock.sendall(user_input.encode("ascii"))

	if user_input == "exit\n":
		break

################################################################################
###                               End of File                                ###
################################################################################