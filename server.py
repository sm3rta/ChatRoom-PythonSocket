import socket
import sys
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverIP = "192.168.1.57"
port = 666

server.bind(("", port))
server.listen(100)

clients = dict()

def userExists(sender, receiverName):
	for connection, user in clients.items():
		if user == receiverName:
			return connection
	return False

def clientthread(connection, addr):
	connection.send(">>Welcome to the chatroom!".encode())
	
	while True:
		try:
			message = connection.recv(2048)
			message = message.decode()
			
			splitMessage = message.split()
			command = splitMessage[0]

			if command == '/a':
				clients[connection] = " ".join(message.split()[1:])
				broadcast(">>{} has joined the chatroom!".format(clients[connection]).encode(), connection)
			elif command == "@":
				receiverName = message.split()[1]
				messageToSend = " ".join(message.split()[2:])
				receiver = userExists(connection, receiverName)
				if receiver:
					try:
						receiver.send(messageToSend.encode())
					except:
						connection.send(">>Failed to send PM".encode())
				else:
					connection.send(">>User not found".encode())
			elif command == "/l":
				broadcast(">>{} has left the chatroom!".format(clients[connection]).encode(), connection)
				connection.close()
				removeConnection(connection)
			else:
				broadcast("{}: {}".format(clients[connection], message).encode(), connection)
		except (KeyboardInterrupt, SystemExit):
			raise

def broadcast(message, connection):
	print(message)
	for client in clients: 
		if client!=connection:
			try: 
				client.send(message) 
			except: 
				client.close() 
				removeConnection(client)

def removeConnection(connection): 
	if connection in clients: 
		clients.pop(connection)
		
while True:
	try:
		connection, addr = server.accept()
		clients[connection] = ""
		print("{} connected with port {}".format(*addr))
		thread = Thread(target=clientthread,args=(connection,addr))
		thread.setDaemon = True
		thread.start()
	except (KeyboardInterrupt, SystemExit):
		raise

server.close()