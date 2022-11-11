import jsonpickle



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
