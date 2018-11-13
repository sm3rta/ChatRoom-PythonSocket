import socket
import sys
from threading import Thread, Lock
from time import sleep
from logging import log

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverIP = "192.168.1.57"
# serverIP = "192.168.43.234"
port = 666

server.bind(("", port))
server.listen(100)

clients = dict()
clientsLock = Lock()

# clientsLock.acquire()


def userExists(receiverName):
	for connection, user in clients.items():
		if user == receiverName:
			clientsLock.release()
			return connection
	return False

def assertClientStatus():
	while True:
		sleep(1)
		deadClients = []
		clientsLock.acquire()

		for client in clients:
			try:
				client.send("/t".encode())
			except Exception as e:
				print(e)
				deadClients.append(client)
		print(deadClients)
		for client in deadClients:
			broadcast(">>{} has died!".format(clients[connection]).encode(), connection)
			connection.close()
			removeConnection(connection)

		clientsLock.release()
		
		
def clientThread(connection, addr):
	connection.send(">>Welcome to the chatroom!".encode())
	
	while True:
		try:
			message = connection.recv(2048)
			message = message.decode()
			
			splitMessage = message.split()
			command = splitMessage[0]

			if command == '/a':
				clientsLock.acquire()
				clients[connection] = " ".join(message.split()[1:])
				broadcast(">>{} has joined the chatroom!".format(clients[connection]).encode(), connection)
				clientsLock.release()
			elif command == "@":
				receiverName = message.split()[1]
				messageToSend = " ".join(message.split()[2:])
				receiver = userExists(receiverName)
				if receiver:
					try:
						receiver.send(messageToSend.encode())
					except:
						connection.send(">>Failed to send PM".encode())
				else:
					connection.send(">>User not found".encode())
			elif command == "/l":
				clientsLock.acquire()
				broadcast(">>{} has left the chatroom!".format(clients[connection]).encode(), connection)
				connection.close()
				removeConnection(connection)
				clientsLock.release()
			else:
				clientsLock.acquire()
				broadcast("{}: {}".format(clients[connection], message).encode(), connection)
				clientsLock.release()
		except (KeyboardInterrupt, SystemExit):
			raise

def broadcast(message, connection):
	deadClients = []
	for client in clients:
		if client!=connection:
			try: 
				client.send(message) 
			except:
				deadClients.append(client)
	for client in deadClients:
		client.close()
		removeConnection(client)

	
					

def removeConnection(connection): 
	if connection in clients: 
		clients.pop(connection)
		

clientChecker = Thread(target=assertClientStatus)
clientChecker.setDaemon = True
clientChecker.start()

while True:
	try:
		connection, addr = server.accept()
		# 
		clients[connection] = ""
		# 
		print("{} connected with port {}".format(*addr))
		thread = Thread(target=clientThread,args=(connection,addr))
		thread.setDaemon = True
		thread.start()
	except (KeyboardInterrupt, SystemExit):
		raise

# connection.close()
server.close()