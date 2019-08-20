# iSpindelTool 🍺

> Minimalistic GUI app listening to [iSpindel](https://github.com/universam1/iSpindel) electronic hydrometers, to allow easy testing and calibration.

![Screenshot](https://raw.githubusercontent.com/plut0nium/iSpindelTool/master/doc/Screenshot_2019-08-20_212508.png)

The use case of this script/app is very simple: I had to build and configure 10+ iSpindel electronic hydrometers for my local homebrewer association.
Rather than switching from one device to another in configuration mode, or configuring all devices to upload to an IoT cloud service (Ubidots, Brewspy...),
this app listens to all devices on the LAN and displays transmitted parameters in a simple Treeview.

It uses the simple iSpindel TCP transmission protocol.

No external dependencies other than the Python standard libraries (socketserver, json, tkinter...).

No history of the transmitted values is kept.
This app is not designed for continuous fermentation monitoring, but should be limited to testing and calibration of your devices.

## How to use

Configure your iSpindel device(s) to report to your computer IP address through TCP, using the the port defined in the script (default 9901).
It is recommended to set a low update interval (10-30s) for testing purpose.

Run the app on your computer.

Each iSpindel should appear in the Treeview as a node, and all transmitted parameters as children.

## Credits

* iSpindel project: [universam1/iSpindel](https://github.com/universam1/iSpindel)
* iSpindel TCP server: [DottoreTozzi/iSpindel-TCP-Server](https://github.com/DottoreTozzi/iSpindel-TCP-Server)

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**

