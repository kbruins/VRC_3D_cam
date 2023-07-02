# VRC 3D cam
VRC 3D cam is a custom camera that fakes a 3D perspective. by using face tracking the camera gets moved around making it look like your monitor is a window to the virtual world. all for the price of nothing

https://github.com/kbruins/VRC_3D_cam/blob/main/images%20and%20videos/3D%20cam%20preview.mp4

# requirements:

hardware:

* webcam or similar (phone can also be used)

software:

* python 3
* aitrack
* opentrack

# setup:

in the following section we will step trough the setup process. from installing the applications to setting up the prefab on your avatar

# 1 AITrack

AITrack is a free and open source face tracker and will be our main way of determining the camera position.

1. download AITrack from there release page: https://github.com/opentrack/opentrack/releases.
2. unzip the downloaded file. if you want you can place the extracted folder somewhere else.
3. go into the folder and locate AITrack.exe. right click it and select "create shortcut". then drag it onto your desktop.
4. open up AITrack and press configuration. this will open up the setting menu.
5. enable "Use remote OpenTrack client". put "127.0.0.1" in the ip box and 4242 in the port box (both without the "quotes").
6. click apply. you are now done setting up AITrack and can close it for the moment.

# 2 OpenTrack

OpenTrack is an interface between AITrack and whatever game/software you want to use. this way Python can get the position of your face.

1. download the OpenTrack exe from there GitHub: https://github.com/opentrack/opentrack/releases.
2. run the exe file and go through the setup.
3. after installing start OpenTrack up.
4. set Input to UDP over network and select the hammer next to it. set Port to 4242 (or the same port as in AITrack) and select OK.
5. set Output to UDP over network and select its hammer next to it. set the Remote IP address to 127.0.0.1 and the port to 8000.
6. now select options and set Centering method to Disabled.
7. go to the Output tab. enable the checkbox inverted for the x and z. then set roll to -90,00° and press OK to confirm the settings.
8. now select Mapping. in the x and y tab set both Max input and Max Output to 75cm. in the z tab select 150cm for both. press OK again to confirm
9. success you have now set up OpenTrack

to test the face tracking you can open both AITrack and OpenTrack. and starting them both.

**important:** when activating the program windows may pop up with a fire wall message. enable both options and click OK. otherwise the programs will not be able te communicate.

you should now see the octopus mimicking your head movement. if the rotations is off. it does not matter as we do not use it.

# 3 installing python and the camera script

Python is a popular programming language used by many open source projects and/or software. in this case it is used to run the custom script I made to translate the position to OSC commands for VRC.

1. download python 3 from their download page: https://www.python.org/downloads/ as of writing this document pythong 3.11.4 is the latest stable option.
2. go through the python installer. there are many great tutorials out there for how to install python. when the installer asks to add itself to the Path variable select yes.
3. get the 3D cam script from the releases: https://github.com/kbruins/VRC_3D_cam/releases
4. try opening the file. when windows asks which program to open it with select Python.
5. after opening you should see the following pop up.

# 4 setting up the prefab

1. get the 3D cam prefab from the releases page: https://github.com/kbruins/VRC_3D_cam/releases and import it into your unity project.
2. open the 3D cam folder and drag the desktop_3D_cam-base into the hierarchy. **do not yet parent it to your avatar.**
3. set the position and rotation to 0, then parent it directly to your avatar by dragging it on top of your avatar.
4. now move the desktop_3D_Cam_base to where you want the camera to be positioned. it's recommended to place it at the same location as your viewpoint
5. set the source of the parent constraint to your head bone and then press the Activate button on the constraint to lock it in. by default the camera will not look up and down with the head. to enable it set the box x under Freeze rotation axis (found under the Constraint Settings) to true.
6. merge the animator found in animations with your current FX animator. or use this animator if you don't have one yet.
7. add the expression menu and parameters to your avatar.
8. your avatar is now set up. now you can upload it or press build and test in the SDK to test it out first.

# 5 using the 3D cam

1. to use the 3D cam first start up AITrack, OpenTrack and the python script.
2. select start in bth OpenTrack and AITrack to start tracking.
3. in VRC ensure OSC is enabled. you can find it under options > OSC in your radial menu.
4. in your gestureMenu select 3D cam to enable the camera. if the tracking is too sensitive or not sensitive enough you can open the python script with notepad. will see 3 multipliers at the top that you can adjust.