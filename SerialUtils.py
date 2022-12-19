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


    


            


