import jsonpickle
from classProvider import netDevice


#Take the master lsit of netowrk devices, encode it as json with json pickle and save it to a txt
def saveToInventoryFile(ListOfDevicesToSaveInInventoryFile,filename="inventory.json"):
    listAsJson = jsonpickle.encode(ListOfDevicesToSaveInInventoryFile)
    f = open(filename, "w")
    f.write(listAsJson)
    f.close()


#load the json file, deserialize it into a list of netowrk devcies, and chekc to amke sure all have username/password/secret
def loadInventoryFromFile(filename="inventory.json"):
    f = open(filename,"r")
    inventoryJson = f.read()
    objectsList = list[netDevice]
    if not inventoryJson == "":
        objectsList = jsonpickle.decode(inventoryJson)
    else:
        objectsList = []
    for dev in objectsList:
        if dev.username == "" or dev.password == "" or dev.secret == "":
            while True:
                usrInput = input("username for " + dev.managementAddress + ": ")
                if not usrInput == "":
                    dev.username = usrInput
                    break
                else:
                    print("Username cannot be blank.")
                
            while True:
                usrInput = input("Password for " + dev.managementAddress + ": ")
                if not usrInput == "":
                    dev.password = usrInput
                    break
                else:
                    print("Password cannot be blank.")
            while True:
                usrInput = input("Secret for " + dev.managementAddress + ": ")
                if not usrInput == "":
                    dev.secret = usrInput
                    break
                else:
                    print("Secret cannot be blank.")


    return objectsList.copy()




#export and csv of info about teh entwork devices
def exportInfoToCSV(devList: list[netDevice],inventoryFile: str):
    configsSet = False

    filePathParts = inventoryFile.split("\\")
    filePath = ""
    if len(filePathParts) > 1:
        for part in filePathParts[0:len(filePathParts ) - 1]:
            filePath += part + "\\"
    filePath += "configs.csv"
    file = open(filePath,"w")
    file.write("Hostname,MAC,Type,Serial Number,OS,Number Of Interfaces,Up Time,Banner Text \n")
    for dev in devList:
        line = (dev.hostName.replace(",","") + "," + dev.macAddress.replace(",","") + "," + dev.deviceType + "," + dev.SerialNumber.replace(",","") + "," + dev.OS.replace(",","")  + "," + str(len(dev.ports))  + "," + dev.upTimeLastChecked.replace(",","") + "," + dev.banner.replace(",","").replace("\n","").replace("^C","") + "\n")
        file.write(line)
    file.close

