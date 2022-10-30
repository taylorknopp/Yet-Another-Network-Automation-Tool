def callJsonSave(listiget):    
    import jsonpickle
    
    #This creates or if it exits writes over the json file made by in this program.
    #Starts a file with the initial text needed for it to be in json format.
    filename = "inventory.json"
    with open(filename, 'w') as file:
        file.write('{"Device list":{')
    
    i = 1
    for dev in listiget:
        fileconv = jsonpickle.encode(dev)
        key = dev.hostName
        with open(dev.hostName + ".ios", 'a') as file:
            file.write(dev.config)
            file.close()


    #This is opening the file again to append and writing the relevant info it gets from the loop.   
        with open(filename, 'a') as file:
            if i != 10:
                file.write('"' + key + '":' + fileconv + ",\n")
            else: 
                file.write('"' + key + '":' + fileconv)
                file.write("}}")
        i = i + 1
