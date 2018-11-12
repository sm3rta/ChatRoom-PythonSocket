import socket
import sys
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# if len(sys.argv) != 3:
# 	print("Correct usage: script IP port")
# 	exit()

# serverIP = str(sys.argv[1])
# Port = int(sys.argv[2])

serverIP = "192.168.1.57"
Port = 666

server.bind(("", 666))
# server.bind((serverIP, Port))
server.listen(100)

clients = dict()

def userExists(message, sender, receiverName):
	for connection, user in clients.items():
		if user == receiverName:
			return connection
		return False

def clientthread(conn, addr):
	conn.send(b">>Welcome to the chatroom!")
	
	while True:
		try:
			message = conn.recv(2048)
			message = message.decode()
			
			split = message.split()
			firstWord = split[0]
			print(firstWord)
			if firstWord == '/a':
				clients[conn] = " ".join(message.split()[1:])
				broadcast(">>{} has joined the chatroom!".format(clients[conn]).encode(), conn)
				print(clients)
			elif firstWord == "@":
				print("private message? sneaky!")
				receiverName = message.split()[1]
				messageToSend = " ".join(message.split()[2:])
				try:
					connection = userExists(message, conn, receiverName)
					connection.send(messageToSend.encode())
				except:
					conn.send(">>User not found")
				
			elif firstWord == "/l":
				conn.close()
				remove(conn)
				# clients.popitem
			else:
				broadcast("{}: {}".format(clients[conn], message).encode(), conn)
			
		except:
			exit()


def broadcast(message, connection):
	print(message)
	for client in clients: 
		if client!=connection:
			try: 
				client.send(message) 
			except: 
				client.close() 
				remove(client)

def remove(connection): 
	if connection in clients: 
		clients.pop(connection)
		
while True:
	try:
		conn, addr = server.accept()
		clients[conn] = ""
		print("{} connected with port {}".format(*addr))
		thread = Thread(target=clientthread,args=(conn,addr))
		thread.setDaemon = True
		thread.start()
	except KeyboardInterrupt:
		exit()
	

conn.close()
server.close()
