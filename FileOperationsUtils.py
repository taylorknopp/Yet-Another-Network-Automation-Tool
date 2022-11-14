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
def exportConfigsToCSV(devList: list[netDevice],inventoryFile: str):
    configsSet = False
    for dev in devList:
        configsSet = not dev.config == ""
    
    if not configsSet:
        print("No Configs In Inventory")
        return


    filePathParts = inventoryFile.split("\\")
    filePath = ""
    if len(filePathParts) > 0:
        for part in filePathParts[0:len(filePathParts - 1)]:
            filePath += part + "\\"
    filePath += "configs.csv"
    file = open(filePath,"w")
    file.write("Hostname,ConfigurationText")
    lines = [str]
    for dev in devList:
        line = dev.hostName + "," + dev.config
        lines+= line
    file.writelines(lines)
    file.close

