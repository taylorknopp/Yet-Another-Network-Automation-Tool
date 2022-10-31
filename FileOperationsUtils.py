import jsonpickle



def saveToInventoryFile(ListOfDevicesToSaveInInventoryFile,filename="inventory.json"):
    listAsJson = jsonpickle.encode(ListOfDevicesToSaveInInventoryFile)
    f = open("inventory.json", "w")
    f.write(listAsJson)
    f.close()
