import netmiko
from classProvider import netDevice
from classProvider import networkPort
import IpTools

    
#ssh into and update the info of a single entwork device
def updateDevice(CiscoDevice: netDevice):
    try:
        DeviceInfo = {
        'device_type': 'cisco_ios',
        'ip': CiscoDevice.managementAddress,
        'username': 'cisco',
        'password': 'cisco',
        'secret': 'cisco',
        }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        serailNumber = ""
        Hostname = ssh.send_command('show run | sec hostname').split()[1]
        try:
            serailNumber = ssh.send_command('show run | sec license').split()[-1]
        except:
            if serialNumber == "":
                    serialNumber = ssh.send_command("show version | sec Processor board").split()[3]
        CiscoDevice.hostName = Hostname
        interfaces = ssh.send_command("show ip interface brief",use_textfsm= True)
        CiscoDevice.ports.clear()
        for port in interfaces:
            interface = networkPort()
            interface.name = port["intf"]
            interface.ipAddress = port["ipaddr"]
            if "up" in port["status"]:
                interface.isUp = True
            else:
                interface.isUp = False
            CiscoDevice.ports.append(interface)
        versionInfo = ssh.send_command("show version")
        versionInfoAsList = versionInfo.split("\n")
        uptime = ""
        systemOS = ""
        Version = ""
        serialNumber = ""
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
        CiscoDevice.SerialNumber = serailNumber
        CiscoDevice.banner = banner
        ssh.disconnect()
        return CiscoDevice



        

    except Exception as e:
        print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
    

#ssh into all the devices in the lsit and gather information about them to be saved in the inventory or exported to json
def BuildInventoryOfDevicesInList(DeviceList: list[netDevice]):
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
            Hostname = ssh.send_command('show run | sec hostname').split()[1]
            serialNumber = ""
            try:
                serialNumber = ssh.send_command('show run | sec license').split()[-1]
                
            except:
                if serialNumber == "":
                    serialNumber = ssh.send_command("show version | sec Processor board").split()[3]
            CiscoDevice.hostName = Hostname
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
                CiscoDevice.ports.append(interface)
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



            
            print(Hostname)
            ssh.disconnect()
        except Exception as e:
            print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
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
    except:
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


