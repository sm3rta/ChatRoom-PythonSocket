import socket
from threading import Thread, Lock
import sys
from winsound import Beep

frequencies = {"message":(300,300), "super":(700,250)}

#Get username from user and check if username is valid
def getUsername():
    while True:
        alias = input(">>What's your name? ")
        Beep(*frequencies["super"])
        if alias == "":
            print(">>Your alias can't be an empty string")
            Beep(*frequencies["super"])
        elif ' ' in alias:
            print(">>Your alias can't include spaces")
            Beep(*frequencies["super"])
        else:
            break
    return alias

#Thread function for receiving messages
def receiveMessage():
    try:
        while True:
            message = client.recv(2018).decode()
            if message != "/t" and message.split()[0] != "/aa":
                print(message)
                if message.startswith(">>"):
                    Beep(*frequencies["super"])
                else:
                    Beep(*frequencies["message"])
    except:
        exit()

#Connect socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIP = "192.168.1.57"
serverPortNumber = 666

try:
    client.connect((serverIP, serverPortNumber))
    print(">>Welcome to the chatroom!")
    Beep(*frequencies["super"])
except:
    print(">>Couldn't connect to server")
    Beep(*frequencies["super"])
    exit()

#Check if username is not already taken
while True:
    alias = getUsername()
    client.send("/a {}".format(alias).encode())
    #waiting for /aa
    command = ""
    while command != "/aa":
        message = client.recv(2018).decode()
        command = message.split()[0]

    status = message.split()[1]
    if status == "ok":
        break
    else:
        print(">>Username already taken")
        Beep(*frequencies["super"])


#Start receiver function
receiver = Thread(target=receiveMessage)
receiver.setDaemon = True
receiver.start()

#Chat
while True:
    try:
        messageToSend = input()
        client.send(messageToSend.encode())
        if messageToSend.split()[0] == '/l':
            print(">>You've logged out")
            Beep(*frequencies["super"])
            break
    except IndexError:
        pass
    except Exception as e:
        print(e)
        Beep(*frequencies["super"])
        break

#Close connection and go home
print(">>Connection to server terminated")
Beep(*frequencies["super"])
client.close()