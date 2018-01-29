# Synopsis

PiCameraApp: A graphical user interface (GUI) for the Picamera library written in Python using Tkinter / ttk.

## Motivation

While developing a camera interface to a 32x32 RGB matrix, I was constantly programming the Picamera in code to test options. I decided to develop a GUI that provides an interface to all of the Picamera's API. Since I haven't done much GUI programming in Linux, I used the Tkinter API. 

Note: I am an old (old, old, old, ..., so very old) Windows programmer going back to the days of Windows 2.1 (Petzold). Both the Python language as well as Linux on the Raspberry Pi are new to me, so please forgive unintentional (or blatant) misuses of the API or Python coding 'standards'.

![alt tag](https://cloud.githubusercontent.com/assets/3778024/20574032/44029314-b178-11e6-90f5-243d38602be0.png)

## Installation

Download the Source directory and execute PiCameraApp.py. Under Wheezy, you must run as **root** in order to access the GPIO on the PiCamera. If you are not running as **root**, then the LED interface is disabled.

To run, open a terminal, change to the directory containing the source files, and enter **sudo python PiCameraApp.py**.

## API Reference

PiCameraApp has been developed using Python ver 2.7. In addition, it uses the following additonal Python libraries:

| Library    | Usage                                               |
| :--------- | :-------------------------------------------------- |
| picamera   | The python interface to the PiCamera hardware. See https://picamera.readthedocs.io/en/release-1.13/install.html |
| RPi.GPIO   | Required to toggle the LED on the camera. Can get it at http://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/ |
| PIL | The Python Image Library. |
|     |    | 

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
 implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/.
