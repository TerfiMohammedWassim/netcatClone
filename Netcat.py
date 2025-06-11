import socket
import sys
import threading
import index as execute


class Netcat :
    
    def handle_client(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file_buffer += data
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            client_socket.send(f'Saved file to {self.args.upload}\n'.encode())
        elif self.args.command:
            while True:
                try:
                    client_socket.send(b'Netcat> dev by Backtrack\n from Terfi Mohammed Wassim \n')
                    client_socket.send(b'Enter command: ')
                    cmd_buffer = b''
                    while b'\n' not in cmd_buffer:
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Error: {e}')
                    client_socket.send(b'Error executing command.\n')
                    client_socket.close()
                    sys.exit(0)
                    
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'Listening on {self.args.target}:{self.args.port}')
        
        while True:
            client_socket, addr = self.socket.accept()
            print(f'Connection from {addr}')
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
       
       
       
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                response = self.socket.recv(4096)
                if not response:
                    break
                sys.stdout.write(response.decode())
                sys.stdout.flush()        
            self.socket.close()
        
        except KeyboardInterrupt:
            print("\nConnection closed by user.")
            self.socket.close()
            sys.exit(0)
            
            
    
    def __init__(self,args,buffer):
        self.buffer = buffer
        self.args = args
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
        
        