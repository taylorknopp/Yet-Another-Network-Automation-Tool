from classProvider import netDevice
from classProvider import networkPort
from classProvider import vlanInterface
import serial
import time



def openSerialPort():
    while True:
        listOfPorts = list(serial.tools.list_ports.comports())
        for c,port in enumerate(listOfPorts):
            print(str(c) +" | " + port.device)
        
        portToChose = input("Chose the serial port to open: ")
        if not portToChose.isnumeric():
            print("Invalid Input")
            continue
        elif not int(portToChose) >= 0 or not int(portToChose) <= len(listOfPorts):
            print("Invalid Input")
            continue
        else:
            try:
                ser =serial.Serial(
                        port=listOfPorts[int(portToChose)].device,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        xonxoff=True,
                        rtscts=False,
                        dsrdtr=False,
                        timeout=1
                    )
                return ser
            except Exception as e:
                print("Error Opening Port | " + str(e))

def senCommand(port: serial.Serial,command: str):
    port.flushInput()
    port.flushOutput()
    command += "\r"
    port.write(command.encode('utf-8'))
    time.sleep(0.25)
    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return read

def senCommandToControl(port: serial.Serial,command: str):
    port.flushInput()
    port.flushOutput()
    port.write(command.encode('utf-8'))
    time.sleep(0.25)
    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return read

def bypassSetupWizzard(port: serial.Serial):
    print("WizzardBypass")
    port.flushInput()
    port.flushOutput()
    port.write("no\r".encode("utf-8"))
    time.sleep(20)
    read = ""
    while True:
        oldLen = len(read)
        time.sleep(15)
        newRead = port.readall().decode('utf-8')
        read +=  newRead
        if len(newRead) > 0:
            read+=newRead
            time.sleep(5)
        else:
            print(senCommand(port,""))
            break
            

def initialSetupOverSerial(port: serial.Serial,dev:netDevice,tftpIp:str):
    print("InicialSerialSettup")
    port.flushInput()
    port.flushOutput()
    out = senCommand(port,"\r")
    time.sleep(5)
    if "[yes/no]" in out:
        bypassSetupWizzard(port)
    print()
    out = senCommand(port,"\r")
    time.sleep(5)
    out = senCommand(port,"\r")
    time.sleep(5)
    out = senCommand(port,"\r")
    time.sleep(5)
    usrInput = input("VRF Name(blank for none)?: ")
    vrfName = usrInput
    pingCommand = ""
    if not usrInput == "":
        pingCommand = f"do ping vrf {usrInput} {tftpIp}"
    else:
        pingCommand = f"do ping {tftpIp}"
    

    print(senCommand(port,"en"))
    print(senCommand(port,"config t"))
    pingCount = 0;
    while True:
        pingCount += 1
        print(f"Pinging {tftpIp}")
        pingResults = senCommand(port, pingCommand)
        print(pingResults)
        if "!" in pingResults:
            break
        else:
            if pingCount <= 2:
                time.sleep(5)
                print(senCommand(port,f"interface {dev.ManagementPortName}"))
                print(senCommand(port,f"ip address {dev.managementAddress} 255.255.255.0"))
                print(senCommand(port,"no shutdown"))
                continue
            else:
                input("Failed to set ip on interface or to contact server address, quitingn press any key to continue...")
                return vrfName,"",False
    

    """ usrInput = ""
    while True:
        usrInput = input("Does it look like the managementport was configured corectly? Y/N").lower()
        if usrInput == "y":
            break
        elif usrInput == "no":
            print("Trying Again...")
            time.sleep(5)
            print(senCommand(port,f"interface {dev.ManagementPortName}"))
            print(senCommand(port,f"ip address {dev.managementAddress} 255.255.255.0"))
            print(senCommand(port,"no shutdown"))
            print(senCommand(port,"do show ip interface brief"))
            print(senCommand(port,"\r"))
            print(senCommand(port,"\r"))
            print(senCommand(port,"\r"))
            print(senCommand(port,"\r"))
            print(senCommand(port,"\r"))
            print(senCommand(port,"\r"))
        else:
            print("Invalid input.") """
            

    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return vrfName,read,True

    
def serialRestoreFromTFTP(portForConfig: serial.Serial,portForControl: serial.Serial,ip,devList:list[netDevice]):
    serialPortToNumberDict = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'g',8:'h',9:'i',10:'j',11:'k',12:'l',13:'m',14:'n',15:'o',16:'p'}
    if len(devList) > 16:
        for x in len(devList)/16:
            for i in range(1,17):
                try:
                    if devList[i+x].serialPortAssociation == 'z':
                        devList[i+x].serialPortAssociation = serialPortToNumberDict[i]
                except:
                    continue
    else:
        for i in range(1,17):
                try:
                    if devList[i+x].serialPortAssociation == 'z':
                        devList[i+x].serialPortAssociation = serialPortToNumberDict[i]
                except:
                    continue
    for dev in devList:
        print(f"{dev.hostName} -> {dev.serialPortAssociation}")
    
    input("Are All Conections As Bove? ")

    for dev in devList:
        print(senCommandToControl(portForControl,dev.serialPortAssociation.lower()))
        time.sleep(5)
        vrfName,outStr,serialOutBool = initialSetupOverSerial(portForConfig,dev,ip)
        if not serialOutBool:
            print(f"Failed serial settup for {dev.hostName}...Moving on")
        print("PostSerialSettup")
        print(senCommand(portForConfig,"end"))
        if not vrfName == "":
            print(senCommand(portForConfig,f"copy tftp run vrf {vrfName}"))
        else:
            print(senCommand(portForConfig,f"copy tftp run"))
            
        print(senCommand(portForConfig,ip))
        while True:
            tftpOut = senCommand(portForConfig,f"{dev.hostName}.ios")
            tftpOut += senCommand("\r")
            if "OK" in tftpOut:
                break
            else:
                print("Socket or other error, retrying serial setup.")
                vrfName,outStr,serialOutBool = initialSetupOverSerial(portForConfig,dev,ip)



        print(senCommand(portForConfig,""))
        print(senCommand(portForConfig,""))
        read = ""
        count = 0
        configLoadedSuccessfully = False
        while True:
            oldLen = len(read)
            read +=  senCommand(portForConfig,"")
            time.sleep(0.1)
            count+=1
            if not oldLen == len(read):
                print(read)
                if dev.hostName in read:
                    configLoadedSuccessfully = True
                    break
                elif count > 500:
                    input(f"Error Configuring Over Serial for {dev.hostNameame}, continue?")
                    break
        if configLoadedSuccessfully:
            print(senCommand(portForConfig,"config t"))
            print(senCommand(portForConfig,"crypto key generate rsa"))
            print(senCommand(portForConfig,"1024"))

            


