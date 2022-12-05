

#Class for storing device information of netowrk devices
class netDevice():
    def __init__(self):
        self.managementAddress = "0.0.0.0"
        self.hostName = "Generic HostName"
        self.config = ""
        self.dedicatedManagementPort = False
        self.Brand = "not set"
        self.deviceType = "not set"
        self.ports = []
        self.vlans = []
        self.upTimeLastChecked = ""
        self.OS = ""
        self.SerialNumber = ""
        self.banner = ""
        self.macAddress = ""
        self.username = ""
        self.password = ""
        self.secret = ""
        self.restconfAvailable = False
        self.restconfEnabledAndWorking = False
    def printPortIps(self):
       for port in self.ports:
        print(port.name + " | " + port.ipAddress)
#class for storing information about netowrk port/intefaces that live on the "netDevice" class
class networkPort():
    def __init__(self):
        self.speed = 1000
        self.name = "gigEth0"
        self.isUp = False
        self.isSwitchPort = True
        self.type = "ethernet"
        self.ipAddress = "0.0.0.0 0.0.0.0"
        self.ipV6Address = "::0"
        self.ipV6LinkLocaleAddress = "::0"
        self.IsTrunkPort = False
        self.AllowedVlans = []
        self.mask = ""
#class for storing information about vlans interface thugh cruently unused
class vlanInterface():
    def __init__(self):
        self.ipAddress = "0.0.0.0"
        self.ipV6Address = "::0"
        self.ipV6LinkLocaleAddress = "::0"
        self.isUp = False


        
