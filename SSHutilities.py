import string
import netmiko
from classProvider import netDevice
from classProvider import networkPort
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
    while True:
        if usrInput == "q":
            return
        try:
            portToUse =  device.ports[int(usrInput)]
            continue
        except:
            print("Invalid Input!")
            continue
    


    







    
    
    DeviceInfo = {
            'device_type': 'cisco_ios',
            'ip': device.managementAddress,
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