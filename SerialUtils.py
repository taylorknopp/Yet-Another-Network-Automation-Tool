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
    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return read

def bypassSetupWizzard(port: serial.Serial):
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
            

def initialSetupOverSerial(port: serial.Serial):
    port.flushInput()
    port.flushOutput()
    out = senCommand(port,"")
    if "[yes/no]" in out:
        bypassSetupWizzard(port)
    print()


    print(senCommand(port,"en"))
    print(senCommand(port,"config t"))
    print(senCommand(port,"interface gig0/0"))
    print(senCommand(port,"ip address 192.168.50.56 255.255.255.0"))
    print(senCommand(port,"no shutdown"))
    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return read

    
def serialRestoreFromTFTP(portForConfig: serial.Serial,portForControl: serial.Serial,ip):
    initialSetupOverSerial(portForConfig)
    print(senCommand(portForConfig,"exit"))
    print(senCommand(portForConfig,"ip default-gateway 192.168.50.1"))
    print(senCommand(portForConfig,"ip route 0.0.0.0 0.0.0.0 192.168.50.1"))
    print(senCommand(portForConfig,"exit"))
    print(senCommand(portForConfig,"copy tftp: running-config"))
    print(senCommand(portForConfig,ip))
    print(senCommand(portForConfig,"rtr101.ios"))
    print(senCommand(portForConfig,""))
    print(senCommand(portForConfig,""))
    read = ""
    while True:
        oldLen = len(read)
        read +=  senCommand(portForConfig,"")
        time.sleep(0.1)
        if not oldLen == len(read):
            print(read)
            if "rtr101" in read:
                break
    return read

            


