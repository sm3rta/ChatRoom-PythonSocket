import socket
import sys
from threading import Thread, Lock
from time import sleep
from classmodule import MessageType, Message
import pickle


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
            message = pickle.loads(message)

            messageType = message.type
            # choosing alias
            if messageType == MessageType.ALIAS:
                alias = message.content
                clientsLock.acquire()
                if userExists(alias):
                    connection.send(pickle.dumps(
                        Message(MessageType.ALIAS_ASSERTION, "NOT OK")))
                else:
                    connection.send(pickle.dumps(
                        Message(MessageType.ALIAS_ASSERTION, "OK")))
                    clients[connection] = alias
                    broadcast(pickle.dumps(Message(
                        MessageType.PRIVATE, ">>{} has joined the chatroom!".format(alias))), connection)
                clientsLock.release()
            # private chat
            elif messageType == MessageType.PRIVATE:
                receiverName = message.targetName
                clientsLock.acquire()
                receiver = userExists(receiverName)
                clientsLock.release()
                if receiver:
                    try:
                        receiver.send(pickle.dumps(Message(
                            MessageType.PRIVATE, "<{}>: {}".format(clients[connection],
                                                                   message.content))))
                    except:
                        connection.send(pickle.dumps(
                            Message(MessageType.ERROR, ">>Failed to send PM")))
                else:
                    connection.send(pickle.dumps(
                        Message(MessageType.ERROR, ">>User not found")))
            # user logging out
            elif messageType == MessageType.LOGOUT:
                clientsLock.acquire()
                killUser(connection)
                clientsLock.release()
                break
            # normal public chat
            else:
                clientsLock.acquire()
                broadcast(pickle.dumps(Message(MessageType.PUBLIC, "{}: {}".format(
                    clients[connection], message))), connection)
                clientsLock.release()
        # user died
        except Exception as e:
            print(e)
            clientsLock.acquire()
            killUser(connection)
            clientsLock.release()
            break


def killUser(connection):
    broadcast(pickle.dumps(Message(MessageType.LOGOUT,
                                   ">>{} has left the chatroom!".format(clients[connection]))), connection)
    connection.close()
    removeConnection(connection)


def userExists(receiverName):
    for connection, user in clients.items():
        if user == receiverName:
            return connection
    return False


def broadcast(message, sender):
    deadClients = []
    for client in clients:
        if client != sender:
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
        thread = Thread(target=clientThread, args=(connection, addr))
        thread.setDaemon = True
        thread.start()
    except (KeyboardInterrupt, SystemExit):
        raise

server.close()
