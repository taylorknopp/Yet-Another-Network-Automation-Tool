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
    print(senCommand(port,"ip address 192.168.50.57 255.255.255.0"))
    print(senCommand(port,"no shutdown"))
    print(senCommand(port,"exit"))
    print(senCommand(port,"hostname rtr102"))
    print(senCommand(port,"ip domain name netw3100.local"))
    print(senCommand(port,"crypto key generate rsa"))
    print(senCommand(port,"1024"))
    print(senCommand(port,"enable secret cisco"))
    print(senCommand(port,"username cisco privilege 15 password cisco"))
    print(senCommand(port,"ip ssh version 2"))
    print(senCommand(port,"line vty 0 4"))
    print(senCommand(port,"login local"))
    print(senCommand(port,"transport input ssh"))
    print(senCommand(port,"exit"))
    read = ""
    while True:
        oldLen = len(read)
        read +=  port.readall().decode('utf-8')
        time.sleep(0.1)
        if oldLen == len(read):
            break
    return read

    


            


