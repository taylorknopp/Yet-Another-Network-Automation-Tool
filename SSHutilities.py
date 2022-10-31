import string
import netmiko
from classProvider import netDevice
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