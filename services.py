import tftpy
import threading
import time
import os
import platform
import sys
import urllib.request
import zipfile
import subprocess
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



def DHCPSetupWindows():
    print("Checking DHCP Settup in " + os.getcwd())
    if not os.path.exists("DHCP"):
        print("Creating dhcp direcotry" )
        os.mkdir("DHCP")

        
    if not len(os.listdir("DHCP")) > 2:
        print("Downloading and  installing/re-installing DHCP server...")
         
        # Get a list of all the files and directories in the directory
        dir_contents = os.listdir("DHCP")

        # Delete each file and subdirectory in the directory
        for content in dir_contents:
            content_path = os.path.join("DHCP", content)
            if os.path.isfile(content_path):
                os.remove(content_path)
            elif os.path.isdir(content_path):
                os.rmdir(content_path)



        # Define the URL of the file to download
        url = "https://github.com/crossbowerbt/dhcpserver/archive/refs/heads/master.zip"
        # Define the local file path to save the downloaded file
        local_file_path = r"DHCP\dhcp.zip"
        print(urllib.request.urlretrieve(url, local_file_path))
        # Define the zip file path
        print("Extracting Zip...")
        zip_file_path = "DHCP/dhcp.zip"

        # Define the directory path to extract the files to
        extract_dir_path = "DHCP"

        # Open the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extract all the files to the extract directory
            zip_ref.extractall(extract_dir_path)
        print("running make on downlaoded DHCP repo")

        # Define the directory path where the extracted files are located
        extract_dir_path = "DHCP"

        # Change the current working directory to the extract directory
        # This step is required to run the make command in the correct directory
        os.chdir(extract_dir_path + r"\dhcpserver-master")

        # Run the make command
        subprocess.run(["make"])

        

    
    pass

def DHCPSetupWindowsLinux():
    print("Checking DHCP Settup in " + os.getcwd())
    if not os.path.exists("DHCP"):
        print("Creating dhcp direcotry" )
        os.mkdir("DHCP")

        
    if not len(os.listdir("DHCP")) > 2:
        print("Downloading and  installing/re-installing DHCP server...")
         
        # Get a list of all the files and directories in the directory
        dir_contents = os.listdir("DHCP")

        # Delete each file and subdirectory in the directory
        for content in dir_contents:
            content_path = os.path.join("DHCP", content)
            if os.path.isfile(content_path):
                os.remove(content_path)
            elif os.path.isdir(content_path):
                os.rmdir(content_path)



        # Define the URL of the file to download
        url = "https://github.com/crossbowerbt/dhcpserver/archive/refs/heads/master.zip"
        # Define the local file path to save the downloaded file
        local_file_path = r"DHCP\dhcp.zip"
        print(urllib.request.urlretrieve(url, local_file_path))
        # Define the zip file path
        print("Extracting Zip...")
        zip_file_path = "DHCP\dhcp.zip"

        # Define the directory path to extract the files to
        extract_dir_path = "DHCP"

        # Open the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extract all the files to the extract directory
            zip_ref.extractall(extract_dir_path)
        print("running make on downlaoded DHCP repo")

        # Define the directory path where the extracted files are located
        extract_dir_path = "DHCP"

        # Change the current working directory to the extract directory
        # This step is required to run the make command in the correct directory
        os.chdir(extract_dir_path + r"\dhcpserver-master")

        # Run the make command
        subprocess.run(["make"])

        

    
    pass