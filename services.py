import tftpy
import threading
import time
import os
def tftp_server_start(port, tftp_server_dir,ip):
    CHECK_FOLDER = os.path.isdir(tftp_server_dir + "\\tftp\\")

# If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(tftp_server_dir + "\\tftp\\")
    server = tftpy.TftpServer(tftp_server_dir + "\\tftp\\")
    
    server_thread = threading.Thread(target=server.listen,
                                         kwargs={'listenip': ip,
                                                 'listenport': port})
    server_thread.start()
    
    
    return server_thread, server

def tftpServerStop(serverThread:threading.Thread,Server:tftpy.TftpServer):
    Server.stop()
    print("Attampting to shutdown tftp server.")
