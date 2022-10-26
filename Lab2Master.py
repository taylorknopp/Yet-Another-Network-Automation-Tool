from ipaddress import ip_address
from classProvider import netDevice
from classProvider import networkPort
from classProvider import vlanInterface
#import netscan
#import sshUtilities
#import jsonUtils
import socket



def getNetOfHost():
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)
    network = IPAddr.split(".")[0] + IPAddr.split(".")[1] + IPAddr.split(".")[3] + "0"
    return network










menue = '''
A: Scan And Backup
B: Wipe Configs And Reload
What would you like to do?:'''
while True:
    userInput = input(menue).lower()
    #scan for devices, add them to the inventory file and backup there configs.
    if(userInput == "a"):
        network = "0.0.0.0"
        try:
            network = getNetOfHost()
        except:
            print("Error Finding IP Of Host Or Network!")
            continue
        try:
            devices = netScan(IPAddr)
        except:
            print("Error Scanning Network!")
            continue
        try:
            devices = callBackup(devices)
        except:
            print("Error Backingup Devices!")
            continue
        try:
            callJsonSave(devices)
        except:
            print("Error creating Inventory Files!")
            continue
    #Scan for devices and wipe them
    elif(userInput == "b"):
        userInput = input("Are you sure you want to whipe everyhting(Y to continue, anything else to abort)?: ").lower()
        try:
            network = getNetOfHost()
        except:
            print("Error Finding IP Of Host OR Network!")
            continue
        if(userInput == "y"):
            devices = callScan()
            callWipe(devices)
    #quit        
    elif(userInput == "q"):
        break
    else:
        print("invalid input")


