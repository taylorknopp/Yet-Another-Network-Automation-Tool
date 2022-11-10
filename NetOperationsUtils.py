from classProvider import netDevice
import os
import IpTools


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
            print("Invlaid Input!")


   
    for n in range(1, 255):
        device_ip = subnet.split(".")[0] + "." + subnet.split(".")[1]+ "." + subnet.split(".")[2]+ "." + str(n)
        print(device_ip)
        loss = os.system('ping -w 10 -n 1 ' + device_ip)
        if loss == 0:
            newDevice = netDevice()
            newDevice.managementAddress = device_ip
            list_of_devices.append(newDevice)
            print ("device is up" ,device_ip) 
        else:
                print ("device is down" ,device_ip)
    return list_of_devices