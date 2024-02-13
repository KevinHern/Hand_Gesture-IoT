# AIoT
This is a project that essentially combines Artificial Intelligence and IoT.

The main objective of this project is to connect both worlds into a single cool project, specifically, Computer Vision and IoT.

The idea of this project is to use Artificial Intelligence to detect hand gestures (like closing the gap between fingers, swipe, etc.) and translate those motions into commands that activate IoT devices (for example, change colors in the neopixels, etc.).
Here is the diagram of the project:

![](https://github.com/KevinHern/Hand_Gesture-IoT/blob/main/misc/ProjectScheme.png)

# Technical Details

## Programming Language
We decided to use Python as our main programming language for 2 main reasons:
* There is support of OpenCV in Python and it is easier to manipulate
* There is a subset of Python called MicroPython for IoT, essentially, it is Python

## Artificial Intelligence
We decided to use OpenCV to handle the Artificial Intelligence section, since its a library with a lot of documentation and is also optimized for these kind of real time applications.

## IoT
As stated above, we decided to give [MicroPython](https://github.com/FunPythonEC/Python_para_MicroControladores) a try since it has been a surging technology recently and one of the members of the team had direct contact with this tool when working with IoT. Also, we were inspired by the team of Ecuador called FunPython which is a team speciallized in IoT with MicroPython.

## Hardware
Since we needed a microchip with WiFi module to decentralize the hardware, we decided to use the cheap version of the ESP that is ESP8266 for the production model. However, during the prototype, development and testing phase, we used an ESP32 that was embeded in a PCB with already mounted components to optimize debugging and the overall time investment during the development.

## Software
The project uses a bunch of libraries. The required libraries (that can be installed using PIP) are:
- opencv-python
- mediapipe
- pycaw
- comtypes
- ctypes
- numpy

# Inspiration
The main project that inspired this idea was a short project done in Python with OpenCV. In summary, the project consisted of detecting, in real time, a hands of the user and register the distance between the fingex and thumb finger. Depending on how close they were, the volume of the computer was adjusted. If the distance was short, then the volume was very dim and if the distance was large, then the volume was louder.
The link of the project [is this one](https://itsourcecode.com/free-projects/python-projects/volume-control-with-hand-detection-opencv-python-with-source-code/).

# Communication Protocol
A communication protocol was designed to allow the AI Hand Gesture Detector application with the ESP module. The protocol consists of passing down a 32 bit number (or 8 hex numbers) to tell the ESP what to do.
The basic structure is as follows: (Example number: 0x014488FF)
* The first 2 leftmost hex numbers (called **IoT ID**) represent the IoT that is going to be activated or updated with a new value
* The rest of the hexadecimal numbers are just values that vary between each IoT device

## IoT Devices
Currently, there are 2 IoT devices implemented, which are:
* Neopixels (IoT ID = 0x01): 6 hex numbers are passed down, in the respective RGB order, that represent the amount of Red, Green and Blue that should have all the neopixels.
* Buzzer (IoT ID = 0x02): A number between 0 and 1500 is passed down. The value is encoded in the 3 rightmost hex numbers.

# Execution

## Network
You need a network to make this project work. A private network without internet access is enough.

NOTES*
This project doesn't work under corporate network infrastructures.

## ESP Server
1. Go to the **ESP32-server.py** file and modify the following variables:
  - **ssdi**: Name of the network you are going to connect.
  - **password**: Password of the network
2. Send the **ESP32-server.py** file to the ESP Microcontroller.

## Computer
1. Go to the **hand_detector.py** file and modify the following variables:
  - **HOST**: The IP address of the ESP Microcontroller after it connected to the network
2. Execute **hand_detector.py** file in your computer

## IMPORTANT NOTES:
- Sometimes, the installed antivirus might block the Program from executing. Tell the antivirus to refrain from preventing the program to execute. Use your antivirus' documentation to do that
