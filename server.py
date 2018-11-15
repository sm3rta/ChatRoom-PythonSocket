import socket
import sys
from threading import Thread, Lock
from time import sleep

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIP = "192.168.1.57"
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
			#choosing alias
			if command == '/a':
				alias = splitMessage[1]
				clientsLock.acquire()
				if userExists(alias):
					connection.send("/aa nok".encode())
				else:
					connection.send("/aa ok".encode())
					clients[connection] = alias
					broadcast(">>{} has joined the chatroom!".format(alias).encode(), connection)
				clientsLock.release()
			#private chat
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
			#user logging out
			elif command == "/l":
				clientsLock.acquire()
				killUser(connection)
				clientsLock.release()
				break
			#normal public chat
			else:
				clientsLock.acquire()
				broadcast("{}: {}".format(clients[connection], message).encode(), connection)
				clientsLock.release()
		#user died
		except Exception as e:
			print(e)
			clientsLock.acquire()
			killUser(connection)
			clientsLock.release()
			break

def killUser(connection):
	broadcast(">>{} has left the chatroom!".format(clients[connection]).encode(), connection)
	connection.close()
	removeConnection(connection)

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
		killUser(client)
					
def removeConnection(connection): 
	if connection in clients: 
		clients.pop(connection)

while True:
	try:
		connection, addr = server.accept()
		clientsLock.acquire()
		clients[connection] = ""
		clientsLock.release()
		print("{} connected with port {}".format(*addr))
		thread = Thread(target=clientThread,args=(connection,addr))
		thread.setDaemon = True
		thread.start()
	except (KeyboardInterrupt, SystemExit):
		raise

server.close()