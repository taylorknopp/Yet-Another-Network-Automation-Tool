


class netDevice():
    def __init__(self):
        self.managementAddress = "0.0.0.0"
        self.hostName = "Generic HostName"
        self.config = "No Config"
        self.dedicatedManagementPort = False
        self.Brand = "not set"
        self.deviceType = "not set"
        self.ports = []
        self.vlans = []
    def printPortIps(self):
       for port in self.ports:
        print(port.name + " | " + port.ipAddress)

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
class vlanInterface():
    def __init__(self):
        self.ipAddress = "0.0.0.0"
        self.ipV6Address = "::0"
        self.ipV6LinkLocaleAddress = "::0"
        self.isUp = False


        
