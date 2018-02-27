# Synopsis

PiCameraApp: A graphical user interface (GUI) for the Picamera library written in Python using Tkinter / ttk.

## Motivation

While developing a camera interface to a 32x32 RGB matrix, I was constantly programming the Picamera in code to test options. I decided to develop a GUI that provides an interface to all of the Picamera's API. Since I haven't done much GUI programming in Linux, I used the Tkinter API. 

Note: I am an old (old, old, old, ..., so very old) Windows programmer going back to the days of Windows 2.1 (Petzold). Both the Python language as well as Linux on the Raspberry Pi are new to me, so please forgive unintentional (or blatant) misuses of the API or Python coding 'standards'.

## Version History

| Version    | Notes                               |
| :--------- | :----------------------------------------------------- |
| 0.1 | <ul><li>Initial release. Only tested under Python 2.7X</li><li>Tested using the RPI V1 camera module </li></ul> |
| 0.2 | <ul><li>Tested using Python ver 2.7.13 and Python ver 3.5.3. If there are any problems please send me new issues.</li><li>Awaiting a V2 camera module for test.</li><li>User interface update. Reorganized controls, added new icons.</li><li>Added tooltips. The file **/Assets/Tooltips.txt** can be modified by the user to add his/her own tips</li><li>Additional camera functionality in accordance with https://picamera.readthedocs.io/en/release-1.13/.</li><li>New dialogs for Preferences, Video and Image capture formats, and Annotation.</li><li>Support for many of the image effect parameters.</li><li>Code for the Camera programming tabs **Basic**, **Exposure**, and **Advanced** moved to separate files.</li></ul> |
| | |

<li></li>

![mainscreen0 2](https://user-images.githubusercontent.com/3778024/36648609-43091bc0-1a5b-11e8-97c8-be0db1249a32.png)

## Installation

Download the zip file and extract to a directory of your choosing. To run, open a terminal, change to the directory containing the source files, and enter **sudo python PiCameraApp.py** or **sudo python3 PiCameraApp.py**.

## Known Issues

| Issue      | Description / Workaround                               |
| :--------- | :----------------------------------------------------- |
| LED | The led_pin parameter can be used to specify the GPIO pin which should be used to control the camera’s LED via the led attribute. If this is not specified, it should default to the correct value for your Pi platform. At present, the camera’s LED cannot be controlled on the Pi 3 (the GPIOs used to control the camera LED were re-routed to GPIO expander on the Pi 3). There are circumstances in which the camera firmware may override an existing LED setting. For example, in the case that the firmware resets the camera (as can happen with a CSI-2 timeout), the LED may also be reset. If you wish to guarantee that the LED remain off at all times, you may prefer to use the disable_camera_led option in config.txt (this has the added advantage that sudo privileges and GPIO access are not required, at least for LED control). Thanks https://picamera.readthedocs.io/en/release-1.13/|
| Sensor Mode | Use this with discretion. In any mode other than Mode 0 (Auto), I've experienced sudden 'freezes' of the application forcing a complete reboot. |
| framerate_range and H264 video | The App would raise an exception when attempting to cature H264 video when framerate_range was selected. The exception complained the framerate_delta could not be specified with framerate_range??? Until I resolve this bug, I don't allow capturing H264 videos with framerate_range selected. |
| framerate and framerate_delta error checking | There are cases where the code may not catch an exception. Avoid setting framerate and framerate_delta values that could add to numbers less than or equal to zero.  A future update will fix this issue.
| JPEG image parameters | The JPEG image capture parameter 'Restart' is not supported with this release. |
| H264 video parameters | The H264 video capture parameter 'Intra Period' is not supported with this release. |
| Other video paramaters | 'bitrate' and 'quality' are not supported in this release. |
| Image Effects parameters | The Image Effect parameters for 'colorbalance', 'film', 'solarize', and 'film' are not supported with this release. |
| EXIF data display | The python exif module does not support all EXIF metadata. Find a better solution. |
| Image flip buttons | The two image flip buttons on the bottom image pane are disabled. These are meant to 'flip' the PIL image that is displayed. To flip or rotate the camera image, use the buttons on the top preview pane. |
| | |

## TODO List (future enhancements)

| TODO       | Description                               |
| :--------- | :----------------------------------------------------- |
| Save Camera State | Allow the user to save and restore the current camera programming state. |
| Output Samples | Allow the user to generate a simple Python script that will program the camera and take a still image or video. |
| INI File | Have a configuration file that saves / restores Preferences |
| Time Delay | Support programming the camera to take still (or videos of length **time**), starting **start time**, then every **time** sec, delaying **time** sec until **number** or **end time** is reached. |
| GPIO Support | Better suport the LED GPIO - this is still buggy (or not fully understood). Also, allow the user to specify GPIO pin(s) that can be toggled (or held high or low) while a still image or video capture is in progress. | 
| Better error checking | Reorgainze code |
| | |

## API Reference

PiCameraApp has been developed using Python ver 2.7.13 and Python ver 3.5.3. In addition, it uses the following additonal Python libraries. See the PiCameraApp About dialog for exact versions used.

| Library    | Usage                                               |
| :--------- | :-------------------------------------------------- |
| picamera   | The python interface to the PiCamera hardware. See https://picamera.readthedocs.io/en/release-1.13/install.html |
| RPi.GPIO   | Required to toggle the LED on the camera. Can get it at http://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/ |
| PIL / Pillow | The Pillow fork of the Python Image Library. One issue is with PIL ImageTk under Python 3.x. It was not installed on my RPI. If you have similar PIL Import Errors use:  **sudo apt-get install python3-pil.imagetk**. |
|     |    | 

![about](https://user-images.githubusercontent.com/3778024/36648694-71283a1c-1a5c-11e8-9c85-ec1f07218cca.png)

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
 implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/.
