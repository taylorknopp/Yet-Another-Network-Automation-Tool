from classProvider import netDevice
import os
import IpTools
from SSHutilities import checkIfDeviceIsCisco


def scan(subnet):
    # print ('scan IPs')
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


   
    for n in range(1, 50):
        device_ip = subnet.split(".")[0] + "." + subnet.split(".")[1]+ "." + subnet.split(".")[2]+ "." + str(n)
        print(device_ip)
        loss = os.system('ping -w 50 -n 1 ' + device_ip)
        if loss == 0:
            if checkIfDeviceIsCisco(device_ip):
                newDevice = netDevice()
                newDevice.managementAddress = device_ip
                print("Device found: " + device_ip)
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

                list_of_devices.append(newDevice)
                
        else:
                print ("device is down" ,device_ip)
    return list_of_devices