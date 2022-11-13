import netmiko
from classProvider import netDevice
from classProvider import networkPort
import IpTools
def netmikoSendCommandsToDevice(commands: list,Device : netDevice):
    DeviceInfo = {
            'device_type': Device.Brand,
            'ip': Device.managementAddress,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            }
    for command in commands:
        pass
    

def BuildInventoryOfDevicesInList(DeviceList):
    for CiscoDevice in DeviceList:
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
            Hostname = ssh.send_command('show run | sec hostname').split()[1]
            CiscoDevice.hostName = Hostname
            interfaces = ssh.send_command("show ip interface brief",use_textfsm= True)
            for port in interfaces:
                interface = networkPort()
                interface.name = port["intf"]
                interface.ipAddress = port["ipaddr"]
                if "up" in port["status"]:
                    interface.isUp = True
                else:
                    interface.isUp = False
                CiscoDevice.ports.append(interface)

                

                

            
            #print(ShowRun)
            print(Hostname)
            ssh.disconnect()
        except Exception as e:
            print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
    return DeviceList



def backupConfigsOfDevicesInList(DeviceList):

    for CiscoDevice in DeviceList:
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
            ShowRun = ssh.send_command('show run')
            CiscoDevice.config = ShowRun
            Hostname = ssh.send_command('show run | sec hostname').split()[1]
            CiscoDevice.hostName = Hostname
            
            #print(ShowRun)
            print(Hostname)
            ssh.disconnect()
        except Exception as e:
            print("Connection Failure For: " + CiscoDevice.managementAddress + " | " + str(e))
    return DeviceList

def eraseAllDevices(DeviceList):
    for CiscoDevice in DeviceList:
        try:
            DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': CiscoDevice.managementAddress,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            }
            print("Wiping " + CiscoDevice.managementAddress)
            ssh = netmiko.ConnectHandler(**DeviceInfo)
            ssh.enable()
            out = ssh.send_command_timing('write erase \n\n')
            out = ssh.send_command_timing('\n\n')
            print(out)
            
        except:
            print("Connection Failure For: " + CiscoDevice.managementAddress)



def checkIfDeviceIsCisco(managementAddress) -> bool:
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': managementAddress,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            }

    
    try:
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        ssh.disconnect()
        return True
    except:
        return False

def configureInterface(device):

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
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
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
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    ssh.send_command_timing("hostname " + hostname)

def setConfig(configDevToSet: netDevice,ip):
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    ssh.config_mode()
    configToSend = configDevToSet.config.split('\n')
    ssh.send_config_set(configToSend)
    
def pingFromDev(dev:netDevice,ip):
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': dev.managementAddress,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco',
            "fast_cli": False,
            }
    ssh = netmiko.ConnectHandler(**DeviceInfo)
    ssh.enable()
    out = ssh.send_command_timing("ping " + ip)
    print(out)

def traceFromDev(dev:netDevice,ip):
    try:
        DeviceInfo = {
                'device_type': 'cisco_ios',
                'ip': dev.managementAddress,
                'username': 'cisco',
                'password': 'cisco',
                'secret': 'cisco',
                }
        ssh = netmiko.ConnectHandler(**DeviceInfo)
        ssh.enable()
        out = ssh.send_command("traceroute " + ip,delay_factor=1200,read_timeout=60000)

        print(out)
    except:
        print("Trace Failed")