
import socket
import select



class connection():

    def __init__(self, host="localhost", port=9999, buf_size=4096):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)
        self.connected = True
        self.__verbose = True

    def send(self, msg):
        if self.connected:
            try:
                _, ready_to_writes, _ = select.select([], [self.socket], [])
                if self.socket in ready_to_writes:
                    self.__verbose and print("Sending", len(msg), "bytes:", msg.strip())
                    self.socket.sendall(msg.encode())
            except select.error:
                self.close()

    def recv(self):
        val = ""
        self.ready_to_read = False
        if self.connected:
            try:
                ready_to_reads, _, _ = select.select([self.socket], [], [], 0.5)
                if self.socket in ready_to_reads:
                    self.ready_to_read = True
                    val = self.socket.recv(self.buf_size).decode('utf-8')
                    self.__verbose and print("Received", len(val), "bytes:", val.strip())
            except select.error:
                pass
        return val

    def close(self):
        try:
            self.connected = False
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except OSError:
            pass

