import argparse
import textwrap
import shlex
import subprocess
import sys
import socket
import threading



def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()



class NetCat:
    def __init__(self,args,buffer=None):
        self.args = args 
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
            
        
        
    def send(self):
        try:
            self.socket.connect((self.args.target, self.args.port))
            print(f'[*] Connected to {self.args.target}:{self.args.port}')
            
            if self.buffer:
                self.socket.send(self.buffer)
            
            try:
                while True:
                    recv_len = 1
                    response = ''
                    while recv_len > 0:
                        data = self.socket.recv(4096)
                        recv_len = len(data)
                        if recv_len == 0:
                            break
                        response += data.decode()
                        
                        if recv_len < 4096:
                            break
                    if response:
                        print(response)
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
                        
            except KeyboardInterrupt:
                print('\n[*] Exiting...')
            finally:
                self.socket.close()
                
        except ConnectionRefusedError:
            print(f'[!] Connection refused to {self.args.target}:{self.args.port}')
            print('[!] Make sure a server is listening on that address/port')
        except Exception as e:
            print(f'[!] Error: {e}')
        finally:
            self.socket.close()
        

        
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'[*] Listening on {self.args.target}:{self.args.port}')
        
        while True:
            client_socket, addr = self.socket.accept()
            print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')
            client_thread = threading.Thread(target=self.handle_client_thread, args=(client_socket,))
            client_thread.start()
            
    def handle_client_thread(self,client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if not data :
                    break
                file_buffer+=data
            
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
                message = f'Saved file {self.args.upload} successfully.'
                client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                    
                except KeyboardInterrupt:
                    print('\n[*] Exiting...')
                    client_socket.close()
                    sys.exit(0)
                

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Backtrack tool Netcat Clone',
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Examples:
                        python index.py -t 192.168.1.108 -p 5555 -l -c
                        # command shell
                        python index.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt
                        # upload to file
                        python index.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"
                        # execute command
                        echo 'ABC' | python index.py -t 192.168.1.108 -p 135
                        # echo text to server port 135
                        python index.py -t 192.168.1.108 -p 5555
                        # connect to server
''')
    )
    
    parser.add_argument('-c','--command',action='store_true',help='enable command shell')
    parser.add_argument('-e','--execute',help='execute specified command')
    parser.add_argument('-l','--listen',action='store_true',help='listen mode')
    parser.add_argument('-p','--port',type=int,default=5555,help='specified port')
    parser.add_argument('-t','--target',default='192.168.0.120',help='specified ip')
    parser.add_argument('-u','--upload',help='upload a file')
    
    args = parser.parse_args()
    
    if args.listen:
        buffer = ''
    else : 
        import select
        if select.select([sys.stdin],[],[],0) == (sys.stdin,[],[]):
            print('[*] Reading from stdin...')
            buffer = sys.stdin.read()
        else:
            buffer = ''
    nc = NetCat(args,buffer.encode())
    nc.run()


