import tftpy
import threading
import time
import os
import platform
import sys
def tftp_server_start(port, tftp_server_dir,ip):
    if sys.platform == 'win32':
        tftp_server_dir += "\\tftp\\"
    else:
        tftp_server_dir = tftp_server_dir.replace("\\","/")
        tftp_server_dir += "/tftp/"

    CHECK_FOLDER = os.path.isdir(tftp_server_dir)

# If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(tftp_server_dir)
    server = tftpy.TftpServer(tftp_server_dir)
    
    server_thread = threading.Thread(target=server.listen,
                                         kwargs={'listenip': ip,
                                                 'listenport': port,
                                                 'timeout':100})
    server_thread.start()
    
    
    return server_thread, server

def tftpServerStop(serverThread:threading.Thread,Server:tftpy.TftpServer):
    Server.stop()
    print("Attempting to shutdown tftp server.")
