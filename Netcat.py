import socket
import sys
import threading


class Netcat:
    
    def __init__(self, args, buffer):
        self.buffer = buffer
        self.args = args
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def execute(self, cmd):
        """Execute a command and return output"""
        import subprocess
        import shlex
        
        cmd = cmd.strip()
        if not cmd:
            return ""
        
        try:
            output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
            return output.decode()
        except Exception as e:
            return f"Error executing command: {e}\n"
    
    def handle_client(self, client_socket):
        if self.args.execute:
            output = self.execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file_buffer += data
            
            try:
                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                client_socket.send(f'Saved file to {self.args.upload}\n'.encode())
            except Exception as e:
                client_socket.send(f'Error saving file: {e}\n'.encode())
                
        elif self.args.command:
            while True:
                try:
                    client_socket.send(b'Netcat> dev by Backtrack\nfrom Terfi Mohammed Wassim\n')
                    client_socket.send(b'Enter command: ')
                    cmd_buffer = b''
                    while b'\n' not in cmd_buffer:
                        data = client_socket.recv(64)
                        if not data:
                            break
                        cmd_buffer += data
                    
                    if not cmd_buffer:
                        break
                        
                    response = self.execute(cmd_buffer.decode().strip())
                    if response:
                        client_socket.send(response.encode())
                except Exception as e:
                    print(f'Error: {e}')
                    client_socket.send(b'Error executing command.\n')
                    break
        
        client_socket.close()
                    
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'Listening on {self.args.target}:{self.args.port}')
        
        while True:
            try:
                client_socket, addr = self.socket.accept()
                print(f'Connection from {addr}')
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.daemon = True
                client_handler.start()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                break
        
        self.socket.close()
    
    def send(self):
        try:
            self.socket.connect((self.args.target, self.args.port))
            if self.buffer:
                self.socket.send(self.buffer)
            
            while True:
                response = self.socket.recv(4096)
                if not response:
                    break
                sys.stdout.write(response.decode())
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            print("\nConnection closed by user.")
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.socket.close()
    
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

