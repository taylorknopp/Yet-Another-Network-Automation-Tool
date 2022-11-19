from classProvider import netDevice
from classProvider import networkPort
from classProvider import vlanInterface
from NetOperationsUtils import scan
from SSHutilities import backupConfigsOfDevicesInList
from SSHutilities import BuildInventoryOfDevicesInList
from SSHutilities import eraseAllDevices
from SSHutilities import configureInterface
from FileOperationsUtils import saveToInventoryFile
from SSHutilities import checkIfDeviceIsCisco
from FileOperationsUtils import loadInventoryFromFile
from SSHutilities import setHostname
from SSHutilities import setConfig
from SSHutilities import pingFromDev
from SSHutilities import traceFromDev
from FileOperationsUtils import exportInfoToCSV
from SSHutilities import updateDevice
from SSHutilities import configureEIGRP
from SSHutilities import configStaticRouting
from SSHutilities import showEigrpNeighborsAlDev
import IpTools
import socket
import os
import copy



    


listOfDevices = []
inventoryFile = "inventory.json"


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
        global listOfDevices
        listOfDevices = devices.copy()
    except Exception as e:
        print("Error scanning network! " + str(e))
        return

    
            
    
        
                

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

def uploadConfigs():
    print("upload Config")
    pass

def configureRouting():
    global listOfDevices
    deviceMenu = "Devices:  \n"
    for c,dev in enumerate(listOfDevices):
        deviceMenu += str(c) + ". " + dev.hostName + "\n"
    deviceMenu += "Chose a device: "
    
    devToUse = netDevice()
    while True:
        usrInput = input(deviceMenu)
        if usrInput == "q":
            return
        try:
            devToUse =  listOfDevices[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    while True:
        usrInput = input("(S)tatic Route, (D)ynamic Route, or (Q)uit?: ").lower()
        if usrInput == "s":
            configStaticRouting(devToUse)
            break
        elif usrInput == "d":
            configureEIGRP(devToUse)
            break
        elif usrInput == "q":
            return
        else:
            print("invalid input.")

def backupConfigs():
    global listOfDevices
    listOfDevices = backupConfigsOfDevicesInList(listOfDevices).copy()
    pass

def extractConfigs():
    exportInfoToCSV(listOfDevices,inventoryFile)

def wipeConfigs():
    print("wipeConfigs")
    pass

def testConectivity():
    thingToDo = ""
    while True:
        thingToDo = input("(P)ing, (T)race or (Q)uit: ").lower()
        if thingToDo == "p":
            break
        elif thingToDo == "t":
            break
        elif thingToDo == "q":
            return
        
        print("Invalid Input")
    global listOfDevices
    deviceMenu = "Devices:  \n"
    for c,dev in enumerate(listOfDevices):
        deviceMenu += str(c) + ". " + dev.hostName + "\n"
    deviceMenu += "Chose a device To Test From: "
    usrInput = input(deviceMenu)
    devToUse = netDevice()
    while True:
        if usrInput == "q":
            return
        try:
            devToUse =  listOfDevices[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    ipAddress = ""
    while True:
        ipAddress = input("Target Address or q to quit: ").lower()
        if ipAddress == "q":
            return
        elif IpTools.validateIp(ipAddress):
            break
        print("Invalid IP")
    if thingToDo == "p":
        pingFromDev(devToUse,ipAddress)
    elif thingToDo == "t":
        traceFromDev(devToUse,ipAddress)
    input("Continue?")




def BuildInventory():
    global listOfDevices
    try:
        listOfDevices = BuildInventoryOfDevicesInList(listOfDevices).copy()
    except Exception as e:
        print("Error Backing up configs! " + str(e))

def InventoryFileSetupAndSave():
    global inventoryFile
    while True:
        usrInput = input("Please enter file path or blank to sue the exsiting path: ")
        path = ""
        

            
        if "\\" in usrInput:
            path = ""
            if ".json" in usrInput:
                parts = usrInput.split('\\')
                for part in parts[0:len(parts) - 1]:
                    path += part + '\\'
            else:
                path = usrInput
            if usrInput != "" and os.path.exists(path):
                inventoryFile = usrInput
                break
            elif userInput == "" and len(inventoryFile) > 0:
                break
            elif userInput == "" and len(inventoryFile) == 0:
                print("File path/name cannot be blank")
            else:
                print("Invalid Input")
        else:
            if usrInput == "" and len(inventoryFile) > 0:
                break
            elif usrInput == "" and len(inventoryFile) == 0:
                print("File path/name cannot be blank")
            elif usrInput != "":
                inventoryFile = usrInput
                break
            else:
                print("Invalid Input")
        print(path) 
          
    print(path)
    saveToInventoryFile(listOfDevices,inventoryFile)

def loadInventory():
    global inventoryFile
    global listOfDevices
    usrInput = ""
    while True:
        usrInput = input("Please enter file path or blank to use the exsiting path: ")
        path = ""
        if usrInput == "" and os.path.exists(inventoryFile):
            break
        elif userInput == "" and not os.path.exists(inventoryFile):
            print("Inventory file not found! ")
            continue
        elif os.path.exists(usrInput):
            inventoryFile = usrInput
            break
        else:
            print("Invalid input")
    
    listOfDevices = loadInventoryFromFile(inventoryFile)  

def configInt():
    global listOfDevices
    deviceMenu = "Devices:  \n"
    for c,dev in enumerate(listOfDevices):
        deviceMenu += str(c) + ". " + dev.hostName + "\n"
    deviceMenu += "Chose a device: "
    usrInput = input(deviceMenu)
    devToUse = netDevice()
    while True:
        if usrInput == "q":
            return
        try:
            devToUse =  listOfDevices[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    configureInterface(devToUse)
    updatetedDev = updateDevice(devToUse)
    for i,dev in enumerate(listOfDevices):
        if dev.managementAddress == updatetedDev.managementAddress:
            listOfDevices[i] = copy.copy(updatetedDev)

    
        
def setHostnameOfDev():
    global listOfDevices
    deviceMenu = "Devices:  \n"
    for c,dev in enumerate(listOfDevices):
        deviceMenu += str(c) + ". " + dev.hostName + "\n"
    deviceMenu += "Chose a device: "
    usrInput = input(deviceMenu)
    devToUse = netDevice()
    while True:
        if usrInput == "q":
            return
        try:
            devToUse =  listOfDevices[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    setHostname(devToUse)

def applyConfigFromInventory():
    global listOfDevices
    deviceMenu = "Devices:  \n"
    for c,dev in enumerate(listOfDevices):
        deviceMenu += str(c) + ". " + dev.hostName + "\n"
    deviceMenu += "Chose a device: "
    usrInput = input(deviceMenu)
    devToUse = netDevice()
    while True:
        if usrInput == "q":
            return
        try:
            devToUse =  listOfDevices[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    ipAddress = ""
    while True:
        ipAddress = input("Ip Address for Interface  or q to quit: ").lower()
        if ipAddress == "q":
            return
        elif IpTools.validateIp(ipAddress):
            break
        print("Invalid IP")
    setConfig(devToUse,ipAddress)
def neighborTbaleView():
    global listOfDevices
    showEigrpNeighborsAlDev(listOfDevices)



menueInputToFunctionMap = {'a':scanNet,'b':BuildInventory,'c':configureRouting, 'd': backupConfigs, 
'e': extractConfigs, 'x':wipeConfigs,'y': testConectivity,'s':InventoryFileSetupAndSave ,'l':loadInventory,'i':configInt,'h':setHostnameOfDev,'ac':applyConfigFromInventory,'nt': neighborTbaleView}


menue = '''
A: Scan
B: Gather Device Info
C: Configure static or Dynamic Routing on a L3 Device
D: Grab Configurations 
E: Save Device Info To CSV
H: Set Device Hostname
I: Configure Interface On Device
L: Load Inventory File
S: Save Inventory File
AC: Apply COnfig From Inventory
NT: View Neighbor Tables for all Devices
X: Wipe Configs And Reload
Y: Connectivity Test, ping/trace(WARNING, can take a very long time)
Q: Quit
What would you like to do?: '''


while True:
    
    print("Inventory: " + inventoryFile)
    print("Devices: ")
    print("==============================================================================")
    for dev in listOfDevices:
            try:
                numPorts = len(dev.ports)
            except:
                numPorts = 0
            print(dev.managementAddress + " | " + dev.hostName + " | Number Of Interfaces: " + str(numPorts) + " | Serial Number: " + dev.SerialNumber)
    print("==============================================================================")



    userInput = input(menue).lower()
    
    #scan for devices, add them to the inventory file and backup there configs.
    if(userInput in menueInputToFunctionMap.keys()):
        
        funcToCall = menueInputToFunctionMap[userInput]
        funcToCall()
        

        
    elif userInput == "q":
        break
    else:
        print("Invaid Input")
        



