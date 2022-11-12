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
import socket
import os



    


listOfDevices = []
inventoryFile = ""


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
    print("Config Routing")
    pass

def backupConfigs():
    global listOfDevices
    listOfDevices = backupConfigsOfDevicesInList(listOfDevices).copy()
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
        usrInput = input("Please enter file path or blank to sue the exsiting path: ")
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
        
menueInputToFunctionMap = {'a':scanNet,'b':BuildInventory,'c':configureRouting, 'd': backupConfigs, 
'e': extractConfigs, 'x':wipeConfigs,'y': testConectivity,'s':InventoryFileSetupAndSave ,'l':loadInventory,'i':configInt}


menue = '''
A: Scan
B: Build Inventory
C: Configure static or Dynamic Routing on a L3 Device
D: Grab Configurations 
E: Extract configs from inventory
L: Load Inventory File
S: Save Inventory File
X: Wipe Configs And Reload
Y: Connectivity Test(ping/trace)
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
            print(dev.managementAddress + " | " + dev.hostName + " | Number Of Interaces: " + str(numPorts))
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
        




