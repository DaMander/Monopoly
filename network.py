import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.150"
        self.port = 5672
        self.addr = (self.server, self.port)

    def connect(self, name):
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode(name))
            val = self.client.recv(8)
            return int(val.decode())
        except ConnectionResetError:
            return False

    def disconnect(self):
        self.client.close()

    def send(self, data, pick=False):
        try:
            if pick:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))
            reply = self.client.recv(8192)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply

        except socket.error as e:
            print(e)
