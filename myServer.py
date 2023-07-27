import os
import pickle
import socket
import threading


class User:
    def __init__(self, cl, addr):
        self.name = None
        self.client = cl
        self.addr = addr

    def __repr__(self):
        return f'{self.addr}, {self.name}'


IP = ''
port = 55000
addr = (IP, port)
bufSize = 1024
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(addr)
unicode = 'utf-8'
all_users = []
ports = {}
filess = []
path = f"{os.getcwd()}/ServerFiles"
dirs = os.listdir(path)
for f1 in dirs:
    filess.append(f1)

for i in range(16):
    ports[55000 - i] = False


def online(name, cl):
    namelist = ""

    for user in all_users:
        if user.name == name:
            continue
        namelist += f',{user.name} '
    if namelist == "":
        cl.send(bytes(f'No online users\n', unicode))
    else:
        cl.send(bytes(f'Online users: {namelist[1:]}\n', unicode))


def PM(sender, getter, msg):  # Private message
    b = False
    for user in all_users:
        if getter == user.name:
            b = True
            cl = user.client
            try:
                cl.send(bytes(f'private message from {sender.name} : ', unicode) + msg)
                sender.client.send(bytes(f'sent private message to {getter} : ', unicode) + msg)
            except Exception as e:
                print(e)
    if not b:
        sender.client.send(bytes(f'No such user is online!\n', unicode))


def msg_all(sender, msg):  # Message to all Clients
    for user in all_users:
        cl = user.client
        try:
            cl.send(bytes(f'message from {sender}: ', unicode) + msg)
        except Exception as e:
            print(e)


def disconnect(cl, user):
    cl.close()
    all_users.remove(user)
    msg_all("Server", bytes(f'{user.name} left\n', unicode))
    print(f'{user.name} disconnected')


def client(user):
    cl = user.client
    user.name = cl.recv(bufSize).decode(unicode)  # Get user name
    msg_all("Server", bytes(f'{user.name} joined\n', unicode))  # Notify all

    while True:
        msg = cl.recv(bufSize)
        if msg.split()[0].decode(unicode) == "/quit":  # if user ask to quit
            disconnect(user.client, user)
            break
        # Send private message
        elif msg.split()[0].decode(unicode) == "/pm":  # /pm {username} {msg}
            size = len(msg.split()[1]) + 4  # username length + /pm(4)
            getter = msg.split()[1].decode(unicode)
            msg = msg[size:]
            PM(user, getter, msg)

        # Get user list
        elif msg.split()[0].decode(unicode) == "/users":
            online(user.name, user.client)
        # File list
        elif msg.split()[0].decode(unicode) == "/files":
            user.client.send(bytes("File list:\n", unicode))
            print(filess[0])
            for f in filess:
                print(f)
                user.client.send(bytes(f'{f}\n', unicode))
        # Download File
        elif msg.split()[0].decode(unicode) == "/download":
            # size = len(msg.split()[1]) + 10
            filename = msg.split()[1].decode(unicode)
            files(filename, cl)
            # Commands:
        elif msg.split()[0].decode(unicode) == "/help":
            commands = "Commands: \n" \
                       "/pm {username} {msg} - Private message \n" \
                       "/users - Get online users list\n" \
                       "/files - Get server file list\n" \
                       "/download {filename} - Download file\n" \
                       "/quit - quit server\n"
            user.client.send(bytes(commands, unicode))
        # Notify all
        else:
            msg_all(user.name, msg)
            print(f"{user.name}: ", msg.decode(unicode))


def threading_clients():
    while True:
        try:
            cl, addr = sock.accept()
            user = User(cl, addr)
            all_users.append(user)
            print(f'{addr} connected')
            threading.Thread(target=client, args=(user,)).start()
        except Exception as e:
            print(e)
            break


def files(filename, cl):
    if filename not in filess:
        cl.send(bytes("No such file! (use {/files})", "utf8"))
        return
    port = -1
    # Choose port
    for p, use in ports.items():
        if not use:
            port = p
            break
    if port == -1:
        print("No ports available")
        return
    # UDP socket
    UDPsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(port)
    UDPsock.bind(("", port))
    ports[port] = True
    path = f'{os.getcwd()}/ServerFiles/{filename}'
    size = os.path.getsize(path)
    msg = bytes(f'/Down {filename} {port} {size}', "utf8")
    cl.send(msg)  # msg to start client

    with open(path, "rb") as f:
        msg, addr = UDPsock.recvfrom(bufSize)
        msg = msg.decode(unicode)
        while msg.split()[0] == 'Slice':
            n = int(msg.split()[1])
            f.seek(512 * n)
            data = f.read(512)
            s = len(data)
            data = pickle.dumps((data, s))
            UDPsock.sendto(data, addr)
            msg, addr = UDPsock.recvfrom(bufSize)
            msg = msg.decode(unicode)
            if msg.split()[0] == 'timeout':
                print("Time out")
                break
        if msg.split()[0] == 'dataleft':
            f.seek(size - (size % 512))
            data = f.read(int(msg.split()[1]))
            UDPsock.sendto(data, addr)

        UDPsock.close()
        ports[port] = False
        print("Finish")

if __name__ == "__main__":
    sock.listen(15)  # open server to listen for connections
    print("Connections available")
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print('Server IP:', ip)
    accept = threading.Thread(target=threading_clients)  # Accept thread
    accept.start()
    accept.join()
    sock.close()
