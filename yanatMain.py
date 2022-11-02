
from re import A
from turtle import back
from classProvider import netDevice
from classProvider import networkPort
from classProvider import vlanInterface
from NetOperationsUtils import scan
from SSHutilities import backupConfigsOfDevicesInList
from SSHutilities import eraseAllDevices
from FileOperationsUtils import saveToInventoryFile
import socket
import os



def getIpOfHost():
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)
    return IPAddr

def scanNet():
    network = "0.0.0.0"
    try:
        network = getIpOfHost()
    except:
        print("Error Finding IP Of Host Or Network!")
        return
    try:
        devices = scan(network)
        #loop to check and remove our pc from the device list
        for dev in devices:
            if dev.managementAddress == network:
                    devices.remove(dev)
    except Exception as e:
        print("Error Scanning Network! " + str(e))
        return
    try:
        saveToInventoryFile()
    except Exception as e:
        print("Error Saving to JSon File: " + e)

def wipeDevices():
    userInput = input("Are you sure you want to wipe everything(Y to continue, anything else to abort)?: ").lower()
    try:
        network = getIpOfHost()
    except:
        print("Error Finding IP Of Host Or Network!")
        return
    if(userInput == "y"):
        try:
            devices = scan(network)
            for dev in devices:
                if dev.managementAddress == network:
                    devices.remove(dev)
            eraseAllDevices(devices)
        except Exception as e:
            print("Error Clearing Devices! " + str(e))
            return

def ScanANdBuildInventory():
    print("san")
    pass

def uploadConfigs():
    print("upload Config")
    pass

def configureRouting():
    print("Config Routing")
    pass

def backupConfigs():
    print("backupConfigs")
    pass

def extractConfigs():
    print("extractConfigs")
    pass

def wipeConfigs():
    print("wipeConfigs")
    pass

def testConectivity():
    print("test connectivity")
    pass





menueInputToFunctionMap = {'a':scanNet,'b':wipeDevices, 'c': configureRouting, 'd': backupConfigs, 
'e': extractConfigs, 'x':wipeConfigs,'y': testConectivity}


menue = '''
A: Scan And Build Inventory File
B: Apply Config Backup To Device or Devices
C: Configure static or Dynamic Routing on a L3 Device
D: Backup Configurations into Inventory File
E: Extract configs from inventory
X: Wipe Configs And Reload
Y: Connectivity Test(ping/trace)
What would you like to do?: '''


while True:
    userInput = input(menue).lower()
    #scan for devices, add them to the inventory file and backup there configs.
    if(userInput in menueInputToFunctionMap.keys()):
        
        funcToCall = menueInputToFunctionMap[userInput]
        funcToCall()
    elif userInput == "q":
        break;
    else:
        print("Invaid Input")
        




