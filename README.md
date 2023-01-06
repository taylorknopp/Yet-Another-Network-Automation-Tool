**YANAT: Yet Another Network Automation Tool**

An ongoing project made initially to satisfy the requirements of Educational labs but continued with the intent of automating and simplifying network configuration and management tasks. Still very much a work in progress with limited device support; currently, only cisco devices are supported.

**Features**

- Networking scanning for device Discovery.
- Inventory JSON file for device information storage and organization.
- Manual device addition for adding devices without running a lengthy scan.
- Bulk TFTP backup of device configurations to a local TFTP server.
- Automated Device information gathering for populating device info once scanned/added.
- Ability to save device configurations as IOS files from inventory file.
- Tool for Configuring static or Dynamic Routing on a L3 Device; currently, only EIGRP is supported.
- Remotely export configurations into inventory file over SSH.
- View EIGRP Neighbor Tables for all Devices.
- Save device Info To CSV for Inventory Management.
- Load devices from CSV for bulk importing devices without scanning.
- Set device Hostname.
- Wipe configs and reload, mainly cleanup when working in a lab environment.
- Interface Configuration.
- Connectivity Test, ping/trace from a selected device in the inventory to a specific IP address.
- Serial Setup basic configuration of a single device over serial.
- Ping everything from everywhere, a Multithreaded tool to connect to all devices in inventory over ssh and ping every other devices IP assigned interfaces for complete network connectivity mapping.
- Bulk configure simple options on all devices in the inventory, EX: Static Route, Default Route, Default Gateway
- Restore Configs From TFTP using ssh. Tool for connecting to all devices in the inventory, using a serial multiplexing device(See Multiplexer Section), and configuring them with the minimum to connect to this tool's local TFTP server and restore the save configuration.
