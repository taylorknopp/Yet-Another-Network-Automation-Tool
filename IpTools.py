import re
from netifaces import interfaces, ifaddresses, AF_INET
#Dictyionary for use as a lookup tbale for validating and converting subnet masks
CiderVSDecimalLookupDict = {
"1":	"128.0.0.0",
"2":	"192.0.0.0",
"3":	"224.0.0.0",
"4":	"240.0.0.0",
"5":	"248.0.0.0",
"6":	"252.0.0.0",
"7":	"254.0.0.0",
"8":	"255.0.0.0",
"9":	"255.128.0.0",
"10":	"255.192.0.0",
"11":	"255.224.0.0",
"12":	"255.240.0.0",
"13":	"255.248.0.0",
"14":	"255.252.0.0",
"15":	"255.254.0.0",
"16":	"255.255.0.0",	
"17":	"255.255.128.0",
"18":	"255.255.192.0",
"19":	"255.255.224.0",
"20":	"255.255.240.0",
"21":	"255.255.248.0",
"22":	"255.255.252.0",
"23":	"255.255.254.0",
"24":	"255.255.255.0",
"25":	"255.255.255.128",
"26":	"255.255.255.192",
"27":	"255.255.255.224",
"28":	"255.255.255.240",
"29":	"255.255.255.248",
"30":	"255.255.255.252",
"31":	"255.255.255.254",
"32":	"255.255.255.255" }
#check the validity of an ip address with regex
def validateIp(ip):
    try:
        regexParsedIp = re.fullmatch(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$',ip) #regex string Source: Danail Gabenski | https://stackoverflow.com/questions/5284147/validating-ipv4-addresses-with-regexp
        
    except:
        #if the regex throws any kind of error increment error count, print the error and restart the loop
        return False
    if str(regexParsedIp) == 'None':
        return False
        
    else:
        #no errors have been cought so the IP should be valid and we should exit this loop and move on to the mask section
        return True
#convert a cider mask to decimal
def ciderToDecimal(cider):
    decimal = ""
    #try looking up the decimal for of the mask by the key that is the number of cider bits
    decimal = CiderVSDecimalLookupDict[cider.replace('/','')]
    #return the decimal value or a blank variable if no decimal was found
    return decimal
#convert a decimal mask to cider
def DecimalToCider(decimal):
    #count variable to look up cider key value
    count = 0
    #Loop over the values in the lookup tale dictionary, counting as we go, and checking if we have found a decimal version that matches the input
    for dec in CiderVSDecimalLookupDict.values():
        if dec == decimal:
            #input matches current value, meaning count is the index of the key that is the cider form of the mask, so return it
            keys = list(CiderVSDecimalLookupDict.keys())
            return keys[count]
        #this iteration is not the correct value so increment the index counter
        count += 1
    return ""
#check the validity of a subnet mask
def ValidateMask(mask: str):
    if "/" in mask:
        if mask.replace('/','') in CiderVSDecimalLookupDict.keys():
            return True
    elif mask in CiderVSDecimalLookupDict.values():
        return True
    return False

def getHostIp():
    listOfIps = [] 
    for ifaceName in interfaces():
        interface = ifaddresses(ifaceName)
        for key in interface.keys():

            addresses = interface[key][0]['addr']
            if(validateIp(addresses)):
                listOfIps.append(addresses)
    return listOfIps