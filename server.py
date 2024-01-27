import socket
import threading
import rsa

public_key, private_key = rsa.newkeys(1024)
public_client = None

# this is the private ip and when someone connects to your server they need to have your public ip
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
names = []

# broadcast (send message to all connected clients)
def broadcast(message):
    for client in clients:
        client.send(message)

# handle (handles already connected clients)
def handle(client):
    while True:
        try:
            # recieve encrypted message from client
            encrypted_text = client.recv(1024)

            # print encrypted message
            print("\nthe encrypted text:", encrypted_text)
            print("\n")

            # decrypt it with server's private key
            message = rsa.decrypt(encrypted_text, private_key).decode()
            
            # print decrypted text
            print(f"the message: { names[clients.index(client)]}: {message}")


            # broadcast message to all clients in the server
            broadcast(message)
        # if connection is lost or something crashes client will be removed from system
        except:
            index = clients.index(client)
            clients.pop(index)
            client.close()
            names.pop(index)
            break

# recieve (function that is going to accept new connections by constantly listening)
def recieve():
    while True:

        # accepting connection with client
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        # sending public key to client
        client.send(public_key.save_pkcs1("PEM"))

        # getting name of client
        client.send("NAME".encode('utf-8'))
        name = client.recv(1024)

        # appending new client to our list of clients
        names.append(name)
        clients.append(client)

        # printing connection announcemt messages
        print(f"Name of the client is {name}")
        broadcast(f"{name} connected to the server!\n".encode('utf-8'))
        client.send("Connected to the server".encode('utf-8'))

        # creating a new thread for handling each clients after they are connected
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running...")
# calling only this function because recieve calls handle function and they both call broadcast
recieve()
