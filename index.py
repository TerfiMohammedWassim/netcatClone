import argparse
import textwrap
import shlex
import subprocess
import sys
from Netcat import Netcat  

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()


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
    parser.add_argument('-l','--listen',action='store_true',help='listen mode')  # Fixed typo
    parser.add_argument('-p','--port',type=int,default=5555,help='specified port')
    parser.add_argument('-t','--target',default='192.168.0.120',help='specified ip')
    parser.add_argument('-u','--upload',help='upload a file')
    
    args = parser.parse_args()

    if args.listen:  
        buffer = ''
    else : 
        buffer = sys.stdin.read()
    
    nc = Netcat(args,buffer.encode())
    nc.run()

