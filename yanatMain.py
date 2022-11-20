

#importing all the custom functions fomr all the other files
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
#importing third party and system libraries
import socket
import os
import copy



    

#global variables to be sued throughout the program, list of netowrk devcies and path for inventory json file. 
listOfDevices = []
inventoryFile = "inventory.json"

#what follows is all the functions that are called by the suer input main function, all function ames should be fairly self explanitory. 

#use the socket library to get hte ip of the host
def getIpOfHost():
    hostname=socket.gethostname()   
    IPAddr=socket.gethostbyname(hostname)
    return IPAddr
#Call the NetOperations scanning function
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
#call the sshUtils whipe devcies function
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
#call the sshUtils configure routing function based on user input about what devcie to configure and how
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
#call the sshUtils backup configs function
def backupConfigs():
    global listOfDevices
    listOfDevices = backupConfigsOfDevicesInList(listOfDevices).copy()
    pass
#call the file operations utils csv save function
def extractConfigs():
    exportInfoToCSV(listOfDevices,inventoryFile)
#call the sshUtils ping/traceroute functions absed on user input abut what dev to use and what to do, ping vs traceroute
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
#call the sshUtils information gathering function
def BuildInventory():
    global listOfDevices
    try:
        listOfDevices = BuildInventoryOfDevicesInList(listOfDevices).copy()
    except Exception as e:
        print("Error Backing up configs! " + str(e))
#call the file operations utils inverntory save function using the path goten fomr the suer or the default path
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
            elif usrInput == "" and len(inventoryFile) > 0:
                break
            elif usrInput == "" and len(inventoryFile) == 0:
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
#call the file operations load inventory function
def loadInventory():
    global inventoryFile
    global listOfDevices
    usrInput = ""
    while True:
        usrInput = input("Please enter file path or blank to use the exsiting path: ")
        path = ""
        if usrInput == "" and os.path.exists(inventoryFile):
            break
        elif usrInput == "" and not os.path.exists(inventoryFile):
            print("Inventory file not found! ")
            continue
        elif os.path.exists(usrInput):
            inventoryFile = usrInput
            break
        else:
            print("Invalid input")
    
    listOfDevices = loadInventoryFromFile(inventoryFile)  
#call the sshUtils configure inventory function
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
#call the sshUtils set hostname function with information from the suer about what device to set and what hostname to use       
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
#call the sshUtils set configs form inventory function to set the config of a device with teh config form the inventory
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
        ipAddress = input("Ip Address for device  or q to quit: ").lower()
        if ipAddress == "q":
            return
        elif IpTools.validateIp(ipAddress):
            break
        print("Invalid IP")
    setConfig(devToUse,ipAddress)
#call the sshUtils neighbor table vie fucntion to viwe all devcies eigrp neigbor tables
def neighborTableView():
    global listOfDevices
    showEigrpNeighborsAlDev(listOfDevices)


#A dictionary containing refernces to the functions, used for a more smaller more slimlined user input system. 
menueInputToFunctionMap = {'a':scanNet,'b':BuildInventory,'c':configureRouting, 'd': backupConfigs, 
'e': extractConfigs, 'x':wipeDevices,'y': testConectivity,'s':InventoryFileSetupAndSave ,'l':loadInventory,'i':configInt,'h':setHostnameOfDev,'ac':applyConfigFromInventory,'nt': neighborTableView}

#multiline string for the user input menu
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

#Main user input function
def main():
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
        
        #if the user input exists in the dictionary of possible menu functions, grab that fuinction reference and call it.
        if(userInput in menueInputToFunctionMap.keys()):
            
            funcToCall = menueInputToFunctionMap[userInput]
            funcToCall()
            

        #if user input is q quit    
        elif userInput == "q":
            break
        else:
            #user input is anything else, print invalid
            print("Invaid Input")
        


#calling main
main()