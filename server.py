import socket
import sys
from threading import Thread, Lock
from time import sleep

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverIP = "192.168.1.57"
# serverIP = "192.168.43.234"
port = 666

server.bind(("", port))
server.listen(100)

clients = dict()
clientsLock = Lock()

def clientThread(connection, addr):
	while True:
		try:
			message = connection.recv(2048)
			message = message.decode()
			
			splitMessage = message.split()
			command = splitMessage[0]

			if command == '/a':
				alias = " ".join(message.split()[1:])
				clientsLock.acquire()
				if userExists(alias):
					connection.send("/aa nok".encode())
				else:
					connection.send("/aa ok".encode())
					clients[connection] = alias
					broadcast(">>{} has joined the chatroom!".format(clients[connection]).encode(), connection)
				clientsLock.release()
			elif command == "@":
				receiverName = message.split()[1]
				messageToSend = " ".join(message.split()[2:])
				clientsLock.acquire()
				receiver = userExists(receiverName)
				clientsLock.release()
				if receiver:
					try:
						receiver.send("<{}>: {}".format(clients[connection], messageToSend).encode())
					except:
						connection.send(">>Failed to send PM".encode())
				else:
					connection.send(">>User not found".encode())
			elif command == "/l":
				killUser(connection)
				break
			else:
				clientsLock.acquire()
				broadcast("{}: {}".format(clients[connection], message).encode(), connection)
				clientsLock.release()
		except Exception as e:
			print(e)
			killUser(connection)
			break

def killUser(connection):
	clientsLock.acquire()
	broadcast(">>{} has left the chatroom!".format(clients[connection]).encode(), connection)
	connection.close()
	removeConnection(connection)
	clientsLock.release()

def userExists(receiverName):
	for connection, user in clients.items():
		if user == receiverName:
			return connection
	return False

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

server.close()