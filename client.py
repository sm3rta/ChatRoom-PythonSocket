import socket
from threading import Thread
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def receiveMessage():
    try:
        while True:
            print(client.recv(2018).decode())
    except:
        exit()

serverIP = "192.168.43.234"
serverPortNumber = 666

try:
    client.connect((serverIP, serverPortNumber))
except:
    print("Couldn't connect to server")
    exit()

alias = input(">>What's your name? ")



receiver = Thread(target=receiveMessage)
receiver.setDaemon = True
receiver.start()



client.send("/a {}".format(alias).encode())


while True:
    try:
        messageToSend = input()
        client.send(messageToSend.encode())
        if messageToSend.split()[0] == '/l':
            break
    except:
        break 

print(">>You've logged out")
client.close()