import socket
import sys
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# if len(sys.argv) != 3:
# 	print("Correct usage: script IP port")
# 	exit()

# IP_address = str(sys.argv[1])
# Port = int(sys.argv[2])

IP_address = "192.168.43.234"
Port = 666

server.bind(("", 666))
# server.bind((IP_address, Port))
server.listen(100)

list_of_clients = []

users = dict()

def userExists(message, sender, receiverName):
	for connection, user in users.items():
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
				users[conn] = " ".join(message.split()[1:])
				broadcast(">>{} has joined the chatroom!".format(users[conn]).encode(), conn)
				print(users)
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
				# users.popitem
			else:
				broadcast("{}: {}".format(users[conn], message).encode(), conn)
			
		except:
			exit()


def broadcast(message, connection):
	print(message)
	for client in list_of_clients: 
		if client!=connection:
			try: 
				client.send(message) 
			except: 
				client.close() 
				remove(client)

def remove(connection): 
	if connection in list_of_clients: 
		list_of_clients.remove(connection)
		
while True:
	try:
		conn, addr = server.accept()
		list_of_clients.append(conn)
		print("{} connected with port {}".format(*addr))
		thread = Thread(target=clientthread,args=(conn,addr))
		thread.setDaemon = True
		thread.start()
	except KeyboardInterrupt:
		exit()
	

conn.close()
server.close()
