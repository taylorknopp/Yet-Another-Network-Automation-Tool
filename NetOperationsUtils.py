from classProvider import netDevice
import os
import IpTools
from SSHutilities import checkIfDeviceIsCisco

#scan for network devices, gather info aboutnthem fomr the user(username,password,secret) and store it on netDev class instances. 
#Then taempt to ssh into those devices to ensure they are acutlly cisco devices before adding them to the amster device lsit
def scan(subnet):

    list_of_devices = []

    stringForInput = "Network to Scan or D for default( " + str(subnet) + "): "
    netToUseFromUser = None
    while True:
        netToUseFromUser = input(stringForInput).lower()
        if netToUseFromUser == "d":
            break
        elif IpTools.validateIp(netToUseFromUser):
            subnet = netToUseFromUser
            break
        else:
            print("Invalid Input!")


   
    for n in range(1, 110):
        device_ip = subnet.split(".")[0] + "." + subnet.split(".")[1]+ "." + subnet.split(".")[2]+ "." + str(n)
        print(device_ip)
        loss = os.system('ping -w 50 -n 1 ' + device_ip)
        if loss == 0:
            newDevice = netDevice()
            newDevice.managementAddress = device_ip
            print("Device found: " + device_ip)
            while True:
                usrInput = input("username for " + device_ip + "(Default is 'cisco'): ")
                if not usrInput == "":
                    newDevice.username = usrInput
                    break
                else:
                    newDevice.username = "cisco"
                    break
                
            while True:
                usrInput = input("Password for " + device_ip + "(Default is 'cisco'): ")
                if not usrInput == "":
                    newDevice.password = usrInput
                    break
                else:
                    newDevice.password = "cisco"
                    break
            while True:
                usrInput = input("Secret for " + device_ip + "(Default is 'cisco'): ")
                if not usrInput == "":
                    newDevice.secret = usrInput
                    break
                else:
                    newDevice.secret = "cisco"
                    break

            if checkIfDeviceIsCisco(device_ip,newDevice.username,newDevice.password):
                

                list_of_devices.append(newDevice)
                
        else:
                print ("device is down" ,device_ip)
    return list_of_devices