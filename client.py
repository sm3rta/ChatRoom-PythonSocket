import socket
from threading import Thread, Lock
import sys
from winsound import Beep
from classmodule import MessageType, Message
import pickle

frequencies = {"message":(300,300), "super":(700,250)}

#Get username from user and check if username is valid
def getUsername():
    while True:
        alias = input(">>What's your name? ")
        Beep(*frequencies["super"])
        if alias == str():
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
            message = pickle.loads(client.recv(2018))
            if message.type not in [MessageType.TEST, MessageType.ALIAS_ASSERTION]:
                print(message)
                if message.type in [MessageType.PUBLIC, MessageType.PRIVATE]:
                    Beep(*frequencies["message"])
                else:
                    Beep(*frequencies["super"])
    except:
        exit()

#Connect socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIP = "192.168.1.16"
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
    client.send(pickle.dumps(Message(MessageType.ALIAS, alias)))
    #waiting for /aa
    messageType = None    
    while messageType != MessageType.ALIAS_ASSERTION:
        message = client.recv(2018)
        message = pickle.loads(message)
        messageType = message.type

    status = message.content
    if status == "OK":
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
        targetName = None
        userInput = input()
        if len(userInput.split()) == 0:
            continue
        if userInput.startswith('/l'):
            messageType = MessageType.LOGOUT
            message = Message(messageType)
        # #Uncomment this section to give the user the ability to change their username at will
        # elif userInput.startswith('/a'):
        #     messageType = MessageType.ALIAS
        #     content = userInput[3:]
        #     message = Message(messageType, content)
        elif userInput.startswith('@'):
            messageType = MessageType.PRIVATE
            if userInput[1] == ' ':
                targetName = userInput.split()[1]
                content = " ".join(userInput.split()[2:])
            else:
                targetName = userInput.split()[0][1:]
                content = " ".join(userInput.split()[1:])
            message = Message(messageType, content, targetName)
        else:
            message = Message(MessageType.PUBLIC, userInput)

        messageToSend = pickle.dumps(message)
        client.send(messageToSend)
        if message.type == MessageType.LOGOUT:
            print(">>You've logged out")
            Beep(*frequencies["super"])
            break
    except IndexError:
        print(">>Incorrect command usage")
        Beep(*frequencies["super"])
        pass
    except Exception as e:
        print(e)
        Beep(*frequencies["super"])
        break

#Close connection and go home
print(">>Connection to server terminated")
Beep(*frequencies["super"])
client.close()
