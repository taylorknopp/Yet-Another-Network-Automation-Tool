import jsonpickle
from classProvider import netDevice



def saveToInventoryFile(ListOfDevicesToSaveInInventoryFile,filename="inventory.json"):
    listAsJson = jsonpickle.encode(ListOfDevicesToSaveInInventoryFile)
    f = open(filename, "w")
    f.write(listAsJson)
    f.close()


    
def loadInventoryFromFile(filename="inventory.json"):
    f = open(filename,"r")
    inventoryJson = f.read()
    if not inventoryJson == "":
        objectsList = jsonpickle.decode(inventoryJson)
    else:
        objectsList = []
    return objectsList.copy()





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

