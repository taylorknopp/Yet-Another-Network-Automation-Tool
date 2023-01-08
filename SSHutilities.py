import netmiko
from classProvider import netDevice
from classProvider import networkPort
import IpTools
# import the requests library
import requests
import json
from tabulate import tabulate
import time
import os
from concurrent.futures import ThreadPoolExecutor
from operator import attrgetter
from services import tftp_server_start
from services import tftpServerStop    
#ssh into and update the info of a single entwork device
def updateDevice(CiscoDevice: netDevice):
    try:


        
        DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': CiscoDevice.managementAddress,
        'username': CiscoDevice.username,
        'password': CiscoDevice.password,
        'secret': CiscoDevice.secret,
        }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        Hostname = ssh.send_command('show run | sec hostname').split()[1]

        
        
        



        serialNumber = ""
        try:
            serialNumber = ssh.send_command('show run | sec license').split()[-1]
            
        except:
            if serialNumber == "":
                serialNumber = ssh.send_command("show version | sec Processor board").split()[3]
        CiscoDevice.hostName = Hostname

        # disable warnings from SSL/TLS certificates
        requests.packages.urllib3.disable_warnings()

        # Define module and host
        module = 'ietf-yang-library:modules-state'
        host = CiscoDevice.managementAddress

        # Define URL
        url = f"https://{host}/restconf/data/{module}"
        uname = CiscoDevice.username
        password = CiscoDevice.password



        # Form header information
        headers = {'Content-Type': 'application/yang-data+json',
                'Accept': 'application/yang-data+json'}


        # Performs a GET on the gevin url
        response = None
        try:
            response = requests.get(url, headers=headers, verify=False,auth=(uname,password))
        except:
            print("Resconf Request Failed, Likely Not Supported or Configurted")




        if not response == None:
            if (not response.status_code == 200):
                
                CiscoDevice.restconfEnabledAndWorking = False
                if "restconf" in CiscoDevice.config:
                    CiscoDevice.restconfAvailable = True
                else:
                    ssh.config_mode()
                    try:
                        checkIfRestOut = ssh.send_command("restconf")
                        if "Invalid" in checkIfRestOut or len(checkIfRestOut) > 0:
                            CiscoDevice.restconfAvailable = False
                        else:
                            CiscoDevice.restconfAvailable = True
                            ssh.send_command("no restconf")
                        ssh.send_command_timing("end")
                    except:
                        CiscoDevice.restconfAvailable = False
            else:
                CiscoDevice.restconfAvailable = True
                CiscoDevice.restconfEnabledAndWorking = True
        else:
            if "restconf" in CiscoDevice.config:
                    CiscoDevice.restconfAvailable = True
            else:
                ssh.config_mode()
                try:
                    checkIfRestOut = ssh.send_command("restconf")
                    if "Invalid" in checkIfRestOut or len(checkIfRestOut) > 0:
                        CiscoDevice.restconfAvailable = False
                    else:
                        CiscoDevice.restconfAvailable = True
                        ssh.send_command("no restconf")
                    ssh.send_command_timing("end")
                except:
                    CiscoDevice.restconfAvailable = False

 
        

        
        

        


        if CiscoDevice.restconfEnabledAndWorking:
            requests.packages.urllib3.disable_warnings()

            # Define module and host
            module = 'ietf-interfaces:modules-state'
            host = CiscoDevice.managementAddress

            # Define URL
            url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface"
            uname = CiscoDevice.username
            password = CiscoDevice.password



            # Form header information
            headers = {'Content-Type': 'application/yang-data+json',
                    'Accept': 'application/yang-data+json'}


            # Performs a GET on the gevin url
            response = requests.get(url, headers=headers, verify=False,auth=(uname,password))
            modules = json.loads(response.content)
            CiscoDevice.ports.clear()

            for module in modules['Cisco-IOS-XE-native:interface']:
                mod = modules['Cisco-IOS-XE-native:interface'][module]
                for intf in range(0,len(mod)):
                    intfDict = modules['Cisco-IOS-XE-native:interface'][module][intf]
                    #print(modules['Cisco-IOS-XE-native:interface'][module][intf])
                    interface = networkPort()
                    interface.name = module + str(intfDict["name"])
                    intfDictKeys = intfDict.keys()
                    if not "shutdown" in intfDictKeys:
                        ipDict = intfDict['ip']['address']
                        primaryDict  = ipDict['primary']
                        interface.ipAddress = primaryDict['address']
                        interface.mask = primaryDict['mask']
                        interface.isUp = True
                    else:
                        interface.isUp = False
                        #print(interface.ipAddress + " | " + interface.mask)
                    CiscoDevice.ports.append(interface)
            
        else:

            interfaces = ssh.send_command("show ip interface brief",use_textfsm= True)
            CiscoDevice.ports.clear()
            for port in interfaces:
                interface = networkPort()
                interface.name = port["intf"]
                
                interface.ipAddress = port["ipaddr"]
                ipINfo = ssh.send_command("show run interface " + interface.name).split("\n")
                for line in ipINfo:
                    if "ip address" in line:
                        interface.mask = line.split()[-1]
                        break

                if "up" in port["status"]:
                    interface.isUp = True
                else:
                    interface.isUp = False
                if interface.name == "mgmt":
                    CiscoDevice.dedicatedManagementPort = True
                    CiscoDevice.managementAddress = interface.ipAddress
                CiscoDevice.ports.append(interface)
        


        #get version info over ssh
        versionInfo = ssh.send_command("show version")
        versionInfoAsList = versionInfo.split("\n")
        uptime = ""
        systemOS = ""
        Version = ""
        
        macAddress = ""
        banner = ssh.send_command("show run | sec banner")
        for line in versionInfoAsList:
            if " uptime " in line:
                uptime = line.split()[1] + " " + line.split()[2] + " " + line.split()[3] + " " + line.split()[4] + " " + line.split()[5]
                continue
            if "Cisco IOS" in line and not "rights" in line and not "Copyright" in line:
                systemOS = line   
        CiscoDevice.upTimeLastChecked = uptime
        CiscoDevice.OS = systemOS
        CiscoDevice.SerialNumber = serialNumber
        CiscoDevice.banner = banner

       
        for interface in CiscoDevice.ports:
            if interface.ipAddress == CiscoDevice.managementAddress:
                CiscoDevice.ManagementPortName = interface.name


            
        print(Hostname)
        ssh.disconnect()
        return CiscoDevice

    except Exception as e:
        print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
    

#ssh into all the devices in the lsit and gather information about them to be saved in the inventory or exported to json
def BuildInventoryOfDevicesInList(DeviceList: list[netDevice]):
    serialPortToNumberDict = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',8:'H',9:'I',10:'J',11:'K',12:'L',13:'M',14:'N',15:'O',16:'P'}
    i = 1
    for CiscoDevice in DeviceList:
        updateDevice(CiscoDevice)
        CiscoDevice.serialPortAssociation = serialPortToNumberDict[i];
        i += 1
        if i > 16:
            i = 0

    return DeviceList


#ssh into all devcies in the list and grab the entire running config, formated in an applyable manner for future restoration
def backupConfigsOfDevicesInList(DeviceList:list[netDevice]):

    for CiscoDevice in DeviceList:
        try:
            DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': CiscoDevice.managementAddress,
            'username': CiscoDevice.username,
            'password': CiscoDevice.password,
            'secret': CiscoDevice.secret,
            }
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            ShowRun = ssh.send_command('show run').split("\n")
            splitLine = 0
            for c,line in enumerate(ShowRun):
                if "hostname" in line:
                    splitLine = c
                elif "secret" in line:
                    ShowRun.pop(c)
            CiscoDevice.config = ShowRun[splitLine:]
            Hostname = ssh.send_command('show run | sec hostname').split()[1]
            CiscoDevice.hostName = Hostname
            
            
            print(Hostname)
            ssh.disconnect()
        except Exception as e:
            print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
    return DeviceList
#wipe all devcies in teh list. 
def eraseAllDevices(DeviceList:list[netDevice]):
    for CiscoDevice in DeviceList:
        try:
            DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': CiscoDevice.managementAddress,
            'username': CiscoDevice.username,
            'password': CiscoDevice.password,
            'secret': CiscoDevice.secret,
            }
            print("Wiping " + CiscoDevice.managementAddress)
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            out = ssh.send_command_timing('write erase \n\n')
            out = ssh.send_command_timing('\n\n')
            print(out)
            
        except:
            print("Connection Failure For: " + CiscoDevice.managementAddress)


#attempt to ssh into the devcie to check it is a cisco device with ssh enabled 
def checkIfDeviceIsCisco(managementAddress,username,password) -> bool:
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': managementAddress,
            'username': username,
            'password': password,
            }

    
    try:
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.disconnect()
        return True
    except Exception as E:
        print(f"SSH Error For Device: {managementAddress} | Error: {E}")
        return False
#ssh into a devcie and configure the apropriate interface
def configureInterface(device:netDevice):

    portToUse = ""
    portMenu = "interfaces: \n"
   
    for c,port in enumerate(device.ports):

        portMenu += str(c) + ". " +port.name + "\n"
    portMenu += "chose port to configure or q to quit: "
    usrInput = input(portMenu)
    portToUse
    while True:
        if usrInput == "q":
            return
        try:
            portToUse =  device.ports[int(usrInput)]
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
    while True:
        mask = input("Subnet Mask for Interface or q to quit: ").lower()
        if mask == "q":
            return
        elif IpTools.ValidateMask(mask):
            break
        print("Invalid mask")
    
    if "/" in mask:
        mask = IpTools.ciderToDecimal(mask)
    
    print(ipAddress + " " + mask)
    
    
    

    try:
        DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': device.managementAddress,
            'username': device.username,
            'password': device.password,
            'secret': device.secret,
            }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        commandsToSend = ["interface " + portToUse.name,"ip address " + ipAddress + " " + mask,"no shutdown","exit"]



        ssh.enable()
        ssh.config_mode()
        out = ssh.send_multiline_timing(commandsToSend)
        ssh.disconnect()
        return True
    except Exception as e:
        print(e)
        return False
#ssh into a devcie and set it;s hostname
def setHostname(device: netDevice):
    hostname = ""
    while True:
        usrInput = input("New Hostname: ")
        if usrInput == "":
            print("Host Name Cannot Be Blank")
        else:
            hostname = usrInput
            break
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': device.managementAddress,
            'username': device.username,
            'password': device.password,
            'secret': device.secret,
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    ssh.send_command_timing("hostname " + hostname)
#ssh into a device and apply the entire running config curently stored in the loaded inventory
def setConfig(configDevToSet: netDevice,ip):
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': configDevToSet.username,
            'password': configDevToSet.password,
            'secret': configDevToSet.secret,
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    configToSend = configDevToSet.config.split('\n')
    ssh.send_config_set(configToSend)
#ssh into a devcie and attempt to ping an address fomr that device    
def pingFromDev(dev:netDevice,ip):
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': dev.managementAddress,
            'username': dev.username,
            'password': dev.password,
            'secret': dev.secret,
            "fast_cli": False,
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    out = ssh.send_command_timing("ping " + ip)
    print(out)
#ssh into a devcie and attempt to traceroute an address fomr that device
def traceFromDev(dev:netDevice,ip):
    try:
        DeviceInfo = {
                'device_type': 'cisco_ios',
                'ip': dev.managementAddress,
                'username': dev.username,
                'password': dev.password,
                'secret': dev.secret,
                }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        out = ssh.send_command("traceroute " + ip,delay_factor=1200,read_timeout=60000)

        print(out)
    except:
        print("Trace Failed")
#ssh into a device and apply a basic eigrp setup based on user input for encluded netowrks and passive interfaces.
def configureEIGRP(device : netDevice):
    portToUse = []
    portMenu = "interfaces: \n"
   
    
    while True:
        print("Selected ports/networks: ")
        print("--------------------------------------------------------------------")
        for port in portToUse:
            print(port.name + " | " + port.ipAddress)
        print("--------------------------------------------------------------------")

        portMenu = ""
        for c,port in enumerate(device.ports):

            portMenu += str(c) + ". " + port.name + " | " + port.ipAddress +  "\n"
        
        portMenu += "Chose port networks to advertise in EIGRP q to quit or d for done: "
        
        usrInput = input(portMenu)
        if usrInput == "q":
            return
        if usrInput == "d" and len(portToUse) > 0:
            break
        elif usrInput == "d" and len(portToUse) <= 0:
            print("must advertise at least one network in EIGRP")
            continue
        try:
            if not device.ports[int(usrInput)] in portToUse:
                portToUse.append(device.ports[int(usrInput)])
            else:
                print("Port Already In List.")
                break
        except:
            print("Invalid Input!")
            continue

    passivePorts = []
    while True:
        print("Selected ports/networks: ")
        print("--------------------------------------------------------------------")
        for port in passivePorts:
            print(port.name + " | " + port.ipAddress)
        print("--------------------------------------------------------------------")

        portMenu = ""
        for c,port in enumerate(device.ports):

            if not port in portToUse:

                portMenu += str(c) + ". " + port.name + " | " + port.ipAddress +  "\n"
        
        portMenu += "Chose passive ports q to quit or d for done: "
        
        usrInput = input(portMenu)
        if usrInput == "q":
            return
        if usrInput == "d" and len(portToUse) > 0:
            break
        
        try:
            if not device.ports[int(usrInput)] in passivePorts:
                passivePorts.append(device.ports[int(usrInput)])
            else:
                print("Port Already In List.")
                break
        except:
            print("Invalid Input!")
            continue


    
    
    commandsToSend = []
    commandsToSend.append("router eigrp 100")
    for port in portToUse:
        commandsToSend.append("network " + port.ipAddress)
    for port in passivePorts:
        commandsToSend.append("passive-interface " + port.name)
    commandsToSend.append("do wr")
    DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': device.managementAddress,
        'username': device.username,
        'password': device.password,
        'secret': device.secret,
        "fast_cli": False,
        }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    routingOutput = ssh.send_multiline_timing(commandsToSend)
    if len(routingOutput) > 0:
        print(routingOutput)
        input("continue?")
    
    
    
#ssh into a device and apply a static route based in user input        
def configStaticRouting(dev:netDevice):
    destinationAddress = ""
    destinationMask = ""
    nextHpAddress = ""
    while True:
        usrInput = input("Destination Address or (Q)uit: ").lower()
        if IpTools.validateIp(usrInput):
            destinationAddress = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    while True:
        usrInput = input("Destination Mask or (Q)uit: ").lower()
        if IpTools.ValidateMask(usrInput) or usrInput == "0.0.0.0":
            destinationMask = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    while True:
        usrInput = input("Next Hop Address or (Q)uit: ").lower()
        if IpTools.validateIp(usrInput):
            nextHpAddress = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    DeviceInfo = {
    'device_type': 'cisco_ios',
    'ip': dev.managementAddress,
    'username': dev.username,
    'password': dev.password,
    'secret': dev.secret,
    "fast_cli": False,
    }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    routingOutput = ssh.send_command("ip route " + destinationAddress + " " + destinationMask + " " + nextHpAddress)
    if len(routingOutput) > 0:
        print(routingOutput)
        input("continue?")
#ssh into all devcies and show there eigrp neighbor tables
def showEigrpNeighborsAlDev(devs:list[netDevice]):
    for dev in devs:
        DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': dev.managementAddress,
        'username': dev.username,
        'password': dev.password,
        'secret': dev.secret,
        "fast_cli": False,
        }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        out = ssh.send_command("show ip eigrp neighbors")
        print("Neighbors for " + dev.hostName + ": ")
        print("-------------------------------------------------------------------------")
        print(out)
        print("-------------------------------------------------------------------------")
        input("Enter for Next: ")

def rPingFromDevs(devs:list[netDevice]):
    #Header list for building table
    headers = [" "]
    #list for containing subsequent lists of ping results for eatch device interface wiht an address
    pings = []
    startTime = time.time()
    #Take our list of device and iterate over them
    listOfListsToPing = []
    for dev in devs:
        headers.append(dev.hostName)
        #on each device iterate over the lsit of interfaces on that device
        DictOfThingsToPingForThisDev = {}
        for dev2 in devs:
            if dev2 == dev:
                continue
            for interface in dev2.ports:
                if "unassigned" in interface.ipAddress:
                    continue
                DictOfThingsToPingForThisDev[f"{dev2.hostName} | {interface.name}"] = interface
        thisDevsPingSetAslist = [dev,DictOfThingsToPingForThisDev]
        print(len(DictOfThingsToPingForThisDev))
        listOfListsToPing.append(thisDevsPingSetAslist)
    with ThreadPoolExecutor(len(devs)) as executor:
        future_results = executor.map(pingListFromDev, listOfListsToPing)
        results = [result for result in future_results]
    
    print(results)
    resultsDict = {}
    for dict in results:
        print(len(dict))
        resultsDict.update(dict)
    for dev in devs:

        for interface in dev.ports:
            if "unassigned" in interface.ipAddress:
                    continue
            listOfResultsForThisINterface = []
            listOfResultsForThisINterface.append(f"{dev.hostName} | {interface.name} {interface.ipAddress}")
            for device in headers[1:]:
                if device == dev.hostName:
                    listOfResultsForThisINterface.append("N/A")
                    continue
                listOfResultsForThisINterface.append(resultsDict[device][interface.ipAddress])
            pings.append(listOfResultsForThisINterface)



    
    #print the table
    print(tabulate(pings,headers,tablefmt="simple_grid"))
    endtTime = time.time()
    timeTaken = endtTime-startTime
    print("Time Taken: " + str(timeTaken))

def pingListFromDev(listOfInfo: list):
    dev = listOfInfo[0]
    dictOfDevices = listOfInfo[1]
    DictOfResults = {}

    for key in dictOfDevices.keys():
        interface = dictOfDevices[key]
        DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': dev.managementAddress,
            'username': dev.username,
            'password': dev.password,
            'secret': dev.secret,
            "fast_cli": False,
            }
        pingResult = ""
        #try to do the ssh, run the command and store the restults
        try:
            print(f"{dev.hostName} -> {interface.ipAddress}")
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            out = ssh.send_command_timing("ping " + interface.ipAddress,last_read=15)
            
            outList = out.split('\n')
           
            if "Sending" in outList[2] and len(outList) >= 4:
                pingResul = outList[3]
            elif "Sending" in outList[2] and not len(outList) >= 4:
                pingResul = "Error" 
            else:
                pingResul = outList[2]
            ssh.disconnect()
        except Exception as e:
            print("Something Went Wrong: " + str(e))
            pingResul =  "Error"
        if pingResul == "":
            pingResul == "Error"
        DictOfResults[interface.ipAddress] = pingResul
    returnDict = {dev.hostName:DictOfResults}
    return returnDict


def addDeviceManually(device_ip : str):

    newDevice = netDevice()
    while True:
                usrInput = input("username for " + device_ip + ": ")
                if not usrInput == "":
                    newDevice.username = usrInput
                    break
                else:
                    print("Username cannot be blank.")
                
    while True:
        usrInput = input("Password for " + device_ip + ": ")
        if not usrInput == "":
            newDevice.password = usrInput
            break
        else:
            print("Password cannot be blank.")
    while True:
        usrInput = input("Secret for " + device_ip + ": ")
        if not usrInput == "":
            newDevice.secret = usrInput
            break
        else:
            print("Secret cannot be blank.")
    if checkIfDeviceIsCisco(device_ip,newDevice.username,newDevice.password):
                
        newDevice.managementAddress = device_ip
        return newDevice
                
    else:
        print ("Device is inaccessible: " ,device_ip)

def backupAllDevsToTftp(listOfDevs: list[netDevice],ip:str):
    for dev in listOfDevs:
        try:
            DeviceInfo = {
                'device_type': 'cisco_ios',
                'ip': dev.managementAddress,
                'username': dev.username,
                'password': dev.password,
                'secret': dev.secret,
                "fast_cli": False,
                }
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            command = f"copy running-config tftp \r{ip}\r{dev.hostName}.ios"
            out = ssh.send_command_timing(command)
            ssh.disconnect()
            print(f"{dev.hostName} tftp -> {ip}: {out}")
        except Exception as e:
            print(f"Error in TFTP Backup: " + e)

def defaultRouteToAllDevices(listOfDevs: list[netDevice],ip:str):
    for dev in listOfDevs:
        try:
            DeviceInfo = {
                'device_type': 'cisco_ios',
                'ip': dev.managementAddress,
                'username': dev.username,
                'password': dev.password,
                'secret': dev.secret,
                "fast_cli": False,
                }
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            ssh.config_mode()
            command = "ip route 0.0.0.0 0.0.0.0 " + ip
            out = ssh.send_command(command)
            ssh.disconnect()
            print(f"{dev.hostName} | {out}")
        except Exception as e:
            print(f"Error Creating Route: " + e)

def staticrouteToAllDevices(listOfDevs: list[netDevice]):
    destinationAddress = ""
    destinationMask = ""
    nextHpAddress = ""
    while True:
        usrInput = input("Destination Address or (Q)uit: ").lower()
        if IpTools.validateIp(usrInput):
            destinationAddress = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    while True:
        usrInput = input("Destination Mask or (Q)uit: ").lower()
        if IpTools.ValidateMask(usrInput) or usrInput == "0.0.0.0":
            destinationMask = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    while True:
        usrInput = input("Next Hop Address or (Q)uit: ").lower()
        if IpTools.validateIp(usrInput):
            nextHpAddress = usrInput
            break
        elif usrInput == "q":
            return
        else:
            print("Invalid Input.")
    command = "ip route " + destinationAddress + " " + destinationMask + " " + nextHpAddress
    for dev in listOfDevs:
        try:
            DeviceInfo = {
                'device_type': 'cisco_ios',
                'ip': dev.managementAddress,
                'username': dev.username,
                'password': dev.password,
                'secret': dev.secret,
                "fast_cli": False,
                }
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            ssh.config_mode()
            
            out = ssh.send_command(command)
            ssh.disconnect()
            print(f"{dev.hostName} | {out}")
        except Exception as e:
            print(f"Error Creating Route: " + e)


def coppyFileFromDeviceToTFTP(dev:netDevice,ip):
    tftp_server_dir = os.getcwd()
    files = os.listdir(tftp_server_dir + "\\tftp\\")

    
        

    # Return the selected file
    
    serverThread,server = tftp_server_start(69,tftp_server_dir,ip)

    try:
        DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': dev.managementAddress,
        'username': dev.username,
        'password': dev.password,
        'secret': dev.secret,
        "fast_cli": False,
        }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()

        outFiles = ssh.send_command("show flash",use_textfsm=True).split("\n")
        files = []
        for line in outFiles:
            files.append(line.split(" ")[-1])
        files.pop(0)
        files.pop()
        files.pop()
        files.pop()

        while True:
            for i, file in enumerate(files):
                print(f"{i}: {file}")

            # Prompt the user to select a file
            file_index_In = input("Enter the index of the file you want to select: ")
            
            try:
                if(file_index_In.lower() == "q"):
                    return
                fileIindex = int(file_index_In)
                fileName = files[fileIindex]
                break
            except:
                print("Invalid Input")


        out = ssh.send_command_timing("copy flash tftp:")
        print(out)
        out = ssh.send_command_timing(fileName)
        print(out)
        out = ssh.send_command_timing(ip)
        print(out)
        out = ssh.send_command_timing("",read_timeout=10000)
        print(out)
    except Exception as e:
        print("Error Moving File: " + str(e))
    
    tftpServerStop(serverThread,server)


def coppyFileToDeviceFlash(dev:netDevice,ip):
    tftp_server_dir = os.getcwd()
    files = os.listdir(tftp_server_dir + "\\tftp\\")

    while True:
        for i, file in enumerate(files):
            print(f"{i}: {file}")

        # Prompt the user to select a file
        file_index_In = input("Enter the index of the file you want to select: ")
        
        try:
            if(file_index_In.lower() == "q"):
                return
            fileIindex = int(file_index_In)
            filePath = files[fileIindex]
            break
        except:
            print("Invalid Input")
        

    # Return the selected file
    
    serverThread,server = tftp_server_start(69,tftp_server_dir,ip)

    try:
        DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': dev.managementAddress,
        'username': dev.username,
        'password': dev.password,
        'secret': dev.secret,
        "fast_cli": False,
        }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        out = ssh.send_command_timing("copy tftp: flash")
        print(out)
        out = ssh.send_command_timing(ip)
        print(out)
        out = ssh.send_command_timing(filePath)
        print(out)
        out = ssh.send_command_timing("",read_timeout=10000)
        print(out)
    except Exception as e:
        print("Error Moving File: " + str(e))
    
    tftpServerStop(serverThread,server)