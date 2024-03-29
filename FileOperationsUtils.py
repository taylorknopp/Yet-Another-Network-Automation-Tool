import jsonpickle
from classProvider import netDevice
import re
import numpy as np
from PIL import Image
from tkinter import filedialog
from tkinter import *
import os
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from classProvider import settingsHolderClass
ASCII_CHARS = ["@", "#", "＄", "%", "?", "*", "+", ";", ":", ",", "."]

#Take the master lsit of netowrk devices, encode it as json with json pickle and save it to a txt
def saveToInventoryFile(ListOfDevicesToSaveInInventoryFile,settings,filename="inventory.json"):
    listAsJson = jsonpickle.encode(ListOfDevicesToSaveInInventoryFile)
    settingsAsJson = jsonpickle.encode(settings)
    f = open(filename, "w")
    f.write(listAsJson)
    f.close()
    f = open("Settings-"+filename, "w")
    f.write(settingsAsJson)
    f.close()


#load the json file, deserialize it into a list of netowrk devcies, and chekc to amke sure all have username/password/secret
def loadInventoryFromFile(filename="inventory.json"):
    f = open(filename,"r")
    inventoryJson = f.read()
    f.close()
    settings = settingsHolderClass()
    try:
        f = open("Settings-"+filename,"r")
        settingsAsJson = f.read()
        settings = jsonpickle.decode(settingsAsJson)

        f.close()
    except:
        print("Settigns Fiole Not Found")
        settingsAsJson = ""
    








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


    return objectsList.copy() , settings




#export and csv of info about teh entwork devices
def exportInfoToCSV(devList: list[netDevice],inventoryFile: str):
    configsSet = False

    filePathParts = inventoryFile.split("\\")
    filePath = ""
    if len(filePathParts) > 1:
        for part in filePathParts[0:len(filePathParts ) - 1]:
            filePath += part + "\\"
    filePath += "Devices.csv"
    file = open(filePath,"w")
    for dev in devList:
        file.write("Hostname,Serial Number,OS,Number Of Interfaces,Up Time \n")
        line = (dev.hostName.replace(",","") + "," + dev.SerialNumber.replace(",","") + "," + dev.OS.replace(",","")  + "," + str(len(dev.ports))  + "," + dev.upTimeLastChecked.replace(",","") +  "\n")
        file.write(line)
        file.write("Interfaces,,,, \n")
        file.write("Name,Ip Address,Mask,Enabeled, \n")
        for p in dev.ports:
            line2 = f"{p.name},{p.ipAddress},{p.mask},{p.isUp}, \n"
            file.write(line2)
        file.write(",,,,, \n")

    
    file.close



def SaveConfigs(ListOfDevicesToSaveInInventoryFile: list[netDevice]):






    for device  in ListOfDevicesToSaveInInventoryFile:

        f = open(device.hostName + str(".ios"), "w")
        

        # Split the show run output into individual lines
        lines = device.config

        # Define a regular expression that matches user configuration commands
        user_config_regex = re.compile(r"^\S+\s+(\S+)\s+(.*)$") #regex Generated by OpenAI GPTChat

        # Iterate over the lines of the show run output
        for line in lines:
            # Use the regular expression to search for user configuration commands
            match = user_config_regex.search(line)
            if match:
                # If a user configuration command is found, print it
                command, arguments = match.groups()
                f.write(f"{command} {arguments}" + "\n")
        f.close()


def browseFiles(path):


    files = os.listdir(path)
    while True:
        print("Select a file or enter '..' to go up one directory:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")
        selection = input("Enter the number of the file you want to select: ")
        try:
            index = int(selection) - 1
            if 0 <= index < len(files):
                file = files[index]
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    path = full_path
                    files = os.listdir(path)
                else:
                    return full_path
            else:
                print("Invalid selection.")
        except ValueError:
            if selection == "..":
                path = os.path.dirname(path)
                files = os.listdir(path)
            else:
                print("Invalid selection.")
	
																						


def convert_image_to_ascii(image_path, width=80, height=80,greyscale=False, ascii_chars=' .:-=+*#%@'):
    image = Image.open(image_path).resize((width, height))
    if greyscale:
        image = image.convert('L')
    ascii_image = []
    for yPos in range(image.height):
        for xPos in range(image.width):
            pos = x, y = xPos, yPos
            pixel = image.getpixel(pos)
            color=(pixel[1]+pixel[2]+pixel[3])/3
            ascii_image.append(ascii_chars[int(color / 256 * (len(ascii_chars) - 1))])
        ascii_image.append("\n")
    


    with open('c:\\temp\\readme.txt', 'w') as f:
        f.write(''.join(ascii_image))
    return ''.join(ascii_image)
    