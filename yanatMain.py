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
from FileOperationsUtils import SaveConfigs
import IpTools
from SSHutilities import rPingFromDevs
from SerialUtils import openSerialPort
from SerialUtils import senCommand
from SerialUtils import bypassSetupWizzard
from SerialUtils import initialSetupOverSerial
from SSHutilities import addDeviceManually
from IpTools import validateIp
from IpTools import getHostIp
from services import tftp_server_start
from SSHutilities import backupAllDevsToTftp
from services import tftpServerStop
from SSHutilities import defaultRouteToAllDevices
from SSHutilities import staticrouteToAllDevices
from SerialUtils import serialRestoreFromTFTP
from SSHutilities import coppyFileToDeviceFlash
from SSHutilities import coppyFileFromDeviceToTFTP
from SSHutilities import bulkVlanCreate
from FileOperationsUtils import convert_image_to_ascii
from FileOperationsUtils import browseFiles

#importing third party and system libraries
import socket
import os
import copy
from tabulate import tabulate
import time
import serial
from netifaces import interfaces, ifaddresses, AF_INET
import tftpy
import signal 
import sys
from subprocess import Popen
#import pynetbox

    

#global variables to be sued throughout the program, list of netowrk devcies and path for inventory json file. 
listOfDevices = []
inventoryFile = "inventory.json"
serialPort = ""
controlPort = ""
tftpServerThread = None
tftpServer = None
baseDir = ""
startDir= ""
#handler for dealing with ctrl-c interupt
def handler(signum, frame):
    msg = "Ctrl-c was pressed. Exeting! "
    print(msg, end="", flush=True)
    global tftpServer
    global tftpServerThread
    try:
        if tftpServer != None:
            tftpServerStop(tftpServerThread,tftpServer)
        pass
    except:
        pass
    quit()
    
 
def cls():
   os.system('cls' if os.name=='nt' else 'clear')


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
        usrInput = input("Please enter file path or blank to use the exsiting path: ")
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
    if not ".json" in inventoryFile:
        inventoryFile += ".json"
    saveToInventoryFile(listOfDevices,inventoryFile)
    global baseDir
    global startDir
    if sys.platform == "win32":
        baseDir = startDir + "\\" + inventoryFile.replace(".json","")
    else:
        baseDir = startDir + "/" + inventoryFile.replace(".json","")
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
    if not ".json" in inventoryFile:
        inventoryFile += ".json"
    listOfDevices = loadInventoryFromFile(inventoryFile)
    global baseDir
    global startDir
    if sys.platform == "win32":
        baseDir = startDir + "\\" + inventoryFile.replace(".json","")
    else:
        baseDir = startDir + "/" + inventoryFile.replace(".json","")
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

def saveAllConfigs():
    global listOfDevices
    SaveConfigs(listOfDevices)

def rPing():
    global listOfDevices
    rPingFromDevs(listOfDevices)
    input("continue?")

def serialSetup():
    global serialPort
    serialPort = openSerialPort()
    initialSetupOverSerial(serialPort)

        

    input("Continure?")

def addNewDev():
    global listOfDevices
    newDev = None
    stringForInput = "Device To Add(or Q to Quit): "
    while True:
        ipToUseFromUser = input(stringForInput).lower()
        if ipToUseFromUser == "q":
            return
        elif IpTools.validateIp(ipToUseFromUser):
            newDev = addDeviceManually(ipToUseFromUser)
            break
        else:
            print("Invalid Input!")
    if not newDev == None:
        listOfDevices.append(newDev)

def tftpBackup():
    global tftpServer
    global tftpServerThread
    deviceMenu = "Addresses:  \n"
    addressList = getHostIp()
    for c,ip in enumerate(addressList):
        deviceMenu += str(c) + ". " + ip + "\n"
    deviceMenu += "Chose an Address to Listen On( Q for Quit): "
    
    ipToUse = ""
    while True:
        usrInput = input(deviceMenu)
        if usrInput == "q":
            return
        try:
            ipToUse =  addressList[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    tftpServerThread,tftpServer = tftp_server_start(69,baseDir,ipToUse)
    backupAllDevsToTftp(listOfDevices,ipToUse)
    tftpServerStop(tftpServerThread,tftpServer)

def bulkConfig():
    global listOfDevices
    listOfOptions = ["Bulk Default Route","Bulk Default Gateway","Bulk Vlan","Bulk Static Route"]
    menu = "Devices:  \n"
    for c,opt in enumerate(listOfOptions):
        menu += str(c) + ". " + opt + "\n"
    menu += "Chose a option or (Q)uit: "
    
    listofDevToUse = []

    portMenu = "Devices: \n"
   
    while True:
        cls()
        print("Selected Devices: ")
        print("--------------------------------------------------------------------")
        for dev in listofDevToUse:
            print(dev.hostName + " | " + dev.managementAddress)
        print("--------------------------------------------------------------------")

        portMenu = ""
        for c,dev in enumerate(listOfDevices):

            portMenu += str(c) + ". " + dev.hostName + " | " + dev.managementAddress +  "\n"
        
        portMenu += "Chose devices to bulk configure, D for done, Q for quit: "
        
        usrInput = input(portMenu)
        if usrInput == "q":
            return
        if usrInput == "d" and len(listofDevToUse) > 0:
            break
        elif usrInput == "d" and len(listofDevToUse) <= 0:
            print("must advertise at least one network in EIGRP")
            continue
        try:
            if not listOfDevices[int(usrInput)] in listofDevToUse:
                listofDevToUse.append(listOfDevices[int(usrInput)])
            else:
                print("Device Already In List.")
        except:
            print("Invalid Input!")
            continue







    usrInput = ""
    while True:
        usrInput = input(menu)
        if usrInput == "q":
            return
        elif usrInput.isnumeric():
            if usrInput == "0":
                while True:
                        usrInput = input("Destination Address or (Q)uit: ").lower()
                        if IpTools.validateIp(usrInput):
                            destinationAddress = usrInput
                            break
                        elif usrInput == "q":
                            return
                        else:
                            print("Invalid Input.")
                defaultRouteToAllDevices(listofDevToUse,usrInput)
                break
            elif usrInput == "1":
                break
            elif usrInput == "2":
                bulkVlanCreate(listofDevToUse)
                break
            elif usrInput == "3":
                staticrouteToAllDevices(listofDevToUse)
                break
        
        print("Invalid Input!")
    

def tftpRestore():
    global tftpServer
    global tftpServerThread
    deviceMenu = "Addresses:  \n"
    addressList = getHostIp()
    for c,ip in enumerate(addressList):
        deviceMenu += str(c) + ". " + ip + "\n"
    deviceMenu += "Chose an Address to Listen On( Q for Quit): "
    
    ipToUse = ""
    while True:

        usrInput = input(deviceMenu)
        if usrInput == "q":
            return
        try:
            ipToUse =  addressList[int(usrInput)]
            break
        except:
            print("Invalid Input!")
            continue
    tftpServerDir = baseDir
    tftpServerThread,tftpServer = tftp_server_start(69,tftpServerDir,ipToUse)

    global serialPort
    global controlPort
    print("Choose Port For Configuration Data")
    serialPort = openSerialPort()
    print("Choose Port For Multiplexer Control")
    controlPort = openSerialPort()
    time.sleep(5)

    serialRestoreFromTFTP(serialPort,controlPort,ipToUse,listOfDevices)
    tftpServerStop(tftpServerThread,tftpServer)

def manualConsole():
    global serialPort
    global controlPort
    print("Choose Port For Multiplexer Control")
    controlPort = openSerialPort()
    time.sleep(5)
    try:
        minicomCommand = ["lxterminal", "-e", "minicom Console"]
        Popen(minicomCommand)
    except:
        pass
    selectedIndex = 1
    serialPortToNumberDict = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'g',8:'h',9:'i',10:'j',11:'k',12:'l',13:'m',14:'n',15:'o',16:'p'}
    letterToHostNameDict = {}
    for i in range(1,9):
        for dev in listOfDevices:
            if dev.serialPortAssociation.lower() == serialPortToNumberDict[i]:
                letterToHostNameDict[serialPortToNumberDict[i]] = dev.hostName
                break
    while True:
        controlPort.write(serialPortToNumberDict[selectedIndex].encode('utf-8'))
        for i in range(1,9):
            hostName = "???????"
            try:
                hostName = letterToHostNameDict[serialPortToNumberDict[i]]
            except:
                pass
            if selectedIndex == i:
                print(f"[{serialPortToNumberDict[i]}] -> {hostName}. {i}")
            else:
                print(f"{serialPortToNumberDict[i]} -> {hostName}. {i}")
        usrInput = input("Select port or Q for quit: ").lower()
        if usrInput == "q":
            controlPort.close()
            break
        elif usrInput.isnumeric():
            try:
                if int(usrInput) in serialPortToNumberDict.keys():
                    selectedIndex = int(usrInput)
                    continue
                else:
                    print("Invalid Input")
                    continue
            except:
                print("Invalid Input")
                continue
        else:
            print("Invlaid Input")
            continue
        




def tftpUtils():
    global listOfDevices
    global tftpServer
    global tftpServerThread
    listOfOptions = ["Copy File To Flash From TFTP","Copy File From Flash To TFTP","Start TFTP Sevrer"]
    menu = "Options:  \n"
    for c,opt in enumerate(listOfOptions):
        menu += str(c) + ". " + opt + "\n"
    menu += "Chose a option or (Q)uit: "
    
    usrInput = ""
    while True:
        usrInput = input(menu)
        if usrInput == "q":
            return
        elif usrInput.isnumeric():
            break
        print("Invalid Input!")

    if usrInput == "0":
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
        deviceMenu = "Addresses:  \n"
        addressList = getHostIp()
        for c,ip in enumerate(addressList):
            deviceMenu += str(c) + ". " + ip + "\n"
        deviceMenu += "Chose an Address to Listen On( Q for Quit): "
        
        ipToUse = ""
        while True:
            usrInput = input(deviceMenu)
            if usrInput == "q":
                return
            try:
                ipToUse =  addressList[int(usrInput)]
                break
            except:
                print("Invalid Input!")
                continue
        coppyFileToDeviceFlash(devToUse,ipToUse,inventoryFile)

    elif usrInput == "1":
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
        deviceMenu = "Addresses:  \n"
        addressList = getHostIp()
        for c,ip in enumerate(addressList):
            deviceMenu += str(c) + ". " + ip + "\n"
        deviceMenu += "Chose an Address to Listen On( Q for Quit): "
        
        ipToUse = ""
        while True:
            usrInput = input(deviceMenu)
            if usrInput == "q":
                return
            try:
                ipToUse =  addressList[int(usrInput)]
                break
            except:
                print("Invalid Input!")
                continue
        coppyFileFromDeviceToTFTP(devToUse,ipToUse,inventoryFile)
    elif usrInput == "2":
        deviceMenu = ""
        addressList = getHostIp()
        for c,ip in enumerate(addressList):
            deviceMenu += str(c) + ". " + ip + "\n"
        deviceMenu += "Chose an Address to Listen On( Q for Quit): "
        
        ipToUse = ""
        while True:
            usrInput = input(deviceMenu)
            if usrInput == "q":
                return
            try:
                ipToUse =  addressList[int(usrInput)]
                break
            except:
                print("Invalid Input!")
                continue
        
        global tftpServer
        global tftpServerThread
        tftp_server_dir = os.getcwd() + "\\" + inventoryFile.removesuffix(".json")
        tftpServerThread,tftpServer = tftp_server_start(69,tftp_server_dir,ipToUse)
        input("TFTP Running, Enter to stop...")
        tftpServerStop(tftpServerThread,tftpServer)

def img2ascii():
    path = browseFiles(os.getcwd())
    print(convert_image_to_ascii(path,115,24))

""" def netBoxQuery():
    nb = pynetbox.api(
    'http://192.168.3.111:8001',
    token='0123456789abcdef0123456789abcdef01234567'
    )
    devices = nb.dcim.devices.all()
    
    for dev in devices:
        print(dev.name)
        print("     ID: " + str(dev.id))
        print("     ROLE: " + str(dev.device_role))
        print("     SN:" + str(dev.serial))
        print("     Site:" + str(dev.site))
        print("     PIP:" + str(dev.primary_ip))
        print("     url:" + str(dev.url))
        interfaces = nb.dcim.interfaces.filter(device=dev.name)
        print("     Interfaces:")
        for interface in interfaces:
            addresses = nb.ipam.ip_addresses.filter(assigned_object_id=interface.id)
            for address in addresses:
                try:
                    if address.assigned_object_id == interface.id:
                        print("         Name:" + interface.name + " - " + address.address)
                except:
                    pass """
            

            

    
    #input(".......")

#A dictionary containing refernces to the functions, used for a more smaller more slimlined user input system. 
menueInputToFunctionMap = {'a':scanNet,'g':BuildInventory,'c':configureRouting, 'd': backupConfigs, 
'e': extractConfigs, 'x':wipeDevices,'y': testConectivity,'s':InventoryFileSetupAndSave ,'l':loadInventory,
    'i':configInt,'h':setHostnameOfDev,'ac':applyConfigFromInventory,'nt': neighborTableView,'sc':saveAllConfigs,'r':rPing,'t':serialSetup,'aa':addNewDev,'ss':tftpBackup,
    'b':bulkConfig,'tt':tftpRestore,"tf":tftpUtils,"asc":img2ascii,"mc":manualConsole, "zz": netBoxQuery}
#multiline string for the user input menu


MenueTableList = [["A: "," Scan","S: "," Save Inventory File"],
["AA: "," Add Device Manually","SS: "," TFTP Backup"],
["G: "," Gather Device Info","SC: "," Save Configs as IOS Files"],
["C: "," Configure static or Dynamic Routing on a L3 Device","AC: "," Apply Config From Inventory"],
["D: "," Grab Configurations ","NT: "," View Neighbor Tables for all Devices"],
["E: "," Save Device Info To CSV","LC: ", "Load Devices From CSV"],
["H: "," Set Device Hostname","X: "," Wipe Configs And Reload"],
["I: "," Configure Interface On Device","Y: "," Connectivity Test, ping/trace(WARNING, can take a very long time)"],
["T: ","Serial Setup","R: ", "Ping Everything from Everywhere"],
["B: ","Bulk Config, simple config to all devices","TT: ", "Restore Configs From TFTP"],
["TF: ","TFTP Utils Menue","ASC: ","IMG to ASCII"],
["MC: ","Manual Serial Console", "ZZ: ","netboxTest"],
["L: "," Load Inventory File","Q: "," Quit"]]



#Main user input function
def main():
    global baseDir
    global startDir
    baseDir = os.getcwd()
    startDir = os.getcwd()
    while True:
        headers = ["Address","Hostname","Interfaces","Type","S/N","Username","Management Port","RestConf Available","RestConf Configured","Serial Port"]
        table = []
        print("Inventory: " + inventoryFile)
        print("Base Directory: " + baseDir)
        for dev in listOfDevices:
                try:
                    numPorts = len(dev.ports)
                except:
                    numPorts = 0
                devList = [dev.managementAddress,dev.hostName, str(numPorts),dev.deviceType,dev.SerialNumber,dev.username,dev.dedicatedManagementPort,str(dev.restconfAvailable),str(dev.restconfEnabledAndWorking),dev.serialPortAssociation]
                table.append(devList.copy())
        width = os.get_terminal_size().columns
        print("=" * width)
        print(tabulate(table,headers,tablefmt="simple_grid"))
        print("=" * width)
        print(tabulate(MenueTableList,tablefmt="simple"))


        userInput = input("What would you like to do?: ").lower()
        
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
signal.signal(signal.SIGINT, handler)
main()