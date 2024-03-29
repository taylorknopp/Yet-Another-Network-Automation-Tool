from classProvider import netDevice
import os
import IpTools
from SSHutilities import checkIfDeviceIsCisco
import platform
import scapy.all as scapy
from netifaces import interfaces, ifaddresses, AF_INET
import psutil
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

    addrs = psutil.net_if_addrs()
    addrsKeys = addrs.keys()
    nameToUse = ""
    listOfNames = []
    listOfAddresses = []
    for c,key in enumerate(addrsKeys):
        try:
                listOfNames.append(key)
                listOfAddresses.append(addrs[key][1].address)
        except:
            pass
            
    while True:
        for c in range(len(listOfNames)):
            try:
                print(f"{c}. {listOfNames[c]} | {listOfAddresses[c]}")
            except:
                pass
        usrInput = input("Chose your Interface: ")
        try:
            nameToUse = listOfNames[int(usrInput)]
            break
        except:
            print("Invalid Input")
   
    for n in range(1, 255):
        device_ip = subnet.split(".")[0] + "." + subnet.split(".")[1]+ "." + subnet.split(".")[2]+ "." + str(n)
        print(device_ip)

    

        ArpHost(device_ip,nameToUse)
        loss = ArpHost(device_ip,nameToUse)
        if len(loss) > 0:
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

def ArpHost(IP,nameToUse):

    arp_req_frame = scapy.ARP(pdst = IP)

    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 0.25,iface=nameToUse, verbose = False)[0]
    result = []
    for i in range(0,len(answered_list)):
        client_dict = {"ip" : answered_list[i][1].psrc, "mac" : answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result