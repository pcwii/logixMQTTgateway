# <img src='/images/layout.png' width='100' height='64' style='vertical-align:bottom'/> logixMQTTgateway
Utilize the lightweight MQTT protocol to interface with Rockwell ControlLogix™ PLC's.

## About
This program will permit the reading and writing of tag data to/from a Rockwell ControLogix™ PLC. 
Configuration is done in the settings.json file.
This program will enable any MQTT enabled device to communicate directly with a PLC.

## Credits
pcwii

## Category
**IoT**

## Tags
#plc
#rockwell
#control
#logix
#MQTT
#broker
#Homeassistant
#openHAB

## Requirements
- you must have an active Broker
- [paho-mqtt](https://pypi.org/project/paho-mqtt/).
- [pycomm3](https://github.com/ottowayi/pycomm3).

## Warnings!!
- It is not recommended to use a public MQTT broker at this time as this could expose your commands to other Mycroft Units, or other devices subscribing to your topic.
 


