import os
import pickle
import socket
import threading
import time


class Client:
    IP = '10.100.102.5'
    port = 55000
    addr = (IP, port)
    bufSize = 1024

    def __init__(self, name):
        self.name = name
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # TCP
        self.sock.connect(self.addr)
        # self.UDPsock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  # UDP
        # self.UDPsock.connect(self.addr)
        self.msglist = []
        # receive_thread = threading.Thread(target=self.messages)
        # receive_thread.start()
        self.message_out(name)
        self.lock = threading.Lock()

    def messages(self):
        while True:
            try:
                msg = self.sock.recv(self.bufSize).decode('utf-8')
                print(f'user {self.name} received message: {msg}')
                print(msg)
                if msg.split()[0] == "/Down":
                    filename = msg.split()[1]
                    port = int(msg.split()[2])
                    size = int(msg.split()[3])
                    self.files(filename, port, size)
                # Lock thread
                self.lock.acquire()
                self.msglist.append(msg)
                self.lock.release()
            except Exception as e:
                print(e)
                break

    def message_out(self, msg):
        try:
            self.sock.send(bytes(msg, 'utf8'))
            if msg == "/quit":
                self.sock.close()
        except Exception as e:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sock.connect(self.addr)
            print(e)

    def massage_in(self):
        msg = ''.join(self.msglist)
        # Lock thread
        self.lock.acquire()
        self.msglist.clear()
        self.lock.release()
        return msg

    def disconnect(self):
        self.sock.close()
        self.message_out("/quit")

    def files(self, filename, port, size):
        path = os.path.join(os.getcwd(), 'Downloads')
        try:
            os.mkdir(path)
        except:
            pass
        try:
            path = f'{os.getcwd()}/Downloads/{filename}'
            bufneed = size / 512
            dataleft = size % 512
            starttime = time.time()

            with open(path, "wb") as f:
                server = (self.IP, port)
                UDPsock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  # UDP
                j = 0
                for i in range(int(bufneed)):
                    UDPsock.sendto(bytes(f"Slice {i}", "utf-8"), server)
                    msg, addr = UDPsock.recvfrom(1024)
                    msg, s = pickle.loads(msg)
                    if int(s) != len(msg):
                        print("lost packet")
                        j += 1
                        if j > 10:
                            print("Time out")
                            UDPsock.sendto(bytes("timeout", "utf-8"), server)
                            break
                        i -= 1
                        continue
                    f.write(msg)
                    j = 0
                    print(f"{round(i / bufneed * 100, 2)}% downloaded")
                if dataleft > 0:
                    UDPsock.sendto(bytes(f"dataleft {dataleft}", "utf-8"), server)
                    msg, addr = UDPsock.recvfrom(dataleft)
                    f.write(msg)
            print("100%")
        finally:
            UDPsock.sendto(bytes("done", "utf-8"), server)
            UDPsock.close()









