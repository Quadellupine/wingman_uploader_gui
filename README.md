# Little uploader
Threw it together because the official uploader doesn't work on Linux. Or maybe I'm just stupid.
Does nothing fancy, it watches for new logs and uploads them to dps.report and then optinally adds that to the wingman queue.
# Disclaimer: Use at your own risk
I am trying my best, but I can't take responsibility for this app crashing or not working correctly. If you find any mistakes please let me know. Please check the source code if you do not trust the app. Message me with any concerns, Im not a python expert, send me an email or open an issue or submit a PR if you can see ways to improve it, but try to be nice :(
# Install
## Windows
Because this project depends on Elite Insights, which in turn now depends on the .Net Framework 8.0 you will need to download and install that on your own. Without it, Elite Insights will not be able to start.<br>
**Option 1:**
1. Download gui_version.exe from the release page
2. Move it to a folder of your choosing
3. Run it once to generate the .ini file and download Elite Insights, then close it again
4. Open the .ini file with notepad and add in your log-folder behind "logpath =". Here you can also change some other settings like color scheme etc.
5. Run the executable again.
Unfortunately, I dont know how to create an executable for windows that does not instantly get swatted by Windows Defender. Open to suggestions though!

**Option 2:**
1. Install Python 3.12 via winget```winget install --id=Python.Python.3.12  -e```or download it here: https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
2. Optional: Create a virtual envrionment (https://realpython.com/python-virtual-environments-a-primer/)
3. Download this code by clicking on "Code" at the top right and then: Download Zip
4. Extract the contents to a folder of your choosing
5. Open a terminal by pressing the Windows key and typing in "cmd", then type:```cd pathtoyourfolder```and press enter. You can copy the path to your folder from the navigation bar in your explorer window, it should look something like "C:\wingman_autouploader".
6. Then type```pip install -r requirements.txt```and press enter to install all dependencies
7. Now we're ready to run the program, but we need to navigate to the correct folder first, so type```cd .\gui_version\```and press enter 
8. Finally, type```python gui_version.py```then press enter and the program will run. If you encounter any errors now, the terminal will give you an errormessage, which it wouldn't do it you'd just started it by doubleclicking the script.
9. Confirm that you want to install Elite-Insights and then close the program again once it's done installing
10. Edit the .ini file that was created with notepad and add in your log-folder behind "logpath =". Here you can also change some other settings like color scheme etc.
11. (Optional) Because starting it from the Terminal everytime is kind of tedious, I'd recommend creating a shortcut of gui_version.py and moving it to your Desktop or, alternatively, your Startup folder (Win+R -> shell:startup -> enter)
## Linux
While providing a binary for Linux is much easier, I still havent done so. If there is interest just shoot me a message.
1. Install dotnet8, for example using the install script. I personally used it the way described in the arch wiki:https://wiki.archlinux.org/title/.NET: ```sudo ./dotnet-install.sh -c 8.0 --runtime dotnet --install-dir /usr/share/dotnet```.
For Ubuntu: ```sudo apt-get install -y dotnet-runtime-8.0```
2. Install python and pip
3. Download this Code
4. Optional: Create a virtual envrionment (https://realpython.com/python-virtual-environments-a-primer/)
5. Open a terminal and navigate to the Code, run ```pip install -r requirements.txt```
6. Run ```python3 gui_version.py``` from inside the gui_version folder
# Usage
## First time config
When the App starts for the first time it will generate a config.ini file inside the gui_version folder. Open that file and set your Logpath. Now open GW2 with arcdps installed and fight a boss/golem to generate  log. The log will then be uploaded to dps.report and show up in the table of the main window. 
## Functions
- Click on a log in the table to copy it
- Use any of the copy options
- Filter shitlogs (trio, escort, statues, etc.)
- Hide/Show wipes
- Disable/Enable wingman upload
- Batch Upload (See below)
- Brizeh's Flamebot (See below)
- Remembers your settings across launches
## Batch Upload
Clicking the button opens a second window. While it is open progress on the main window will be held back
until it is closed. This is due to my incompetence and may be fixable.
In the new window, you can choose a folder. When you click upload the program will recursively go down the
folder you have given it (So including subfolders) and upload anything it finds.<br>
After your first time using this feature, a file called .seen.csv will be created. It will keep track of all
successfully uploaded files to prevent them from being reuploaded again in the future.<br>
**ATTENTION**
If you CLOSE to batchupload window the uploading will continue in the background. Only clicking the CANCEL button or fully terminating the Application will stop it. Overall, this feature does work on the backend, but the frontend is still kind of wonky. If you just leave it alone and let it think for a while it will definitely upload your logs, but the status displayed in the window sometimes bugs out. Its on my ToDo list.
## Brizeh's Flamebot
A project by Vs Brizeh: https://github.com/Brizeh/LogFC
In short: Give it a bunch of logs and it will flame. Clicking on the "Brizeh's Flamebot" button will download his code onto your computer and then attempt to execute it with the logs you pasted into the text field.<br>
Recommended usage: Use the Copy All Button in the main Window after your Fullclear and paste it into the popup.<br><br>
The flamebot will output the result into the terminal and textfile called output.txt. By default, this file is generate in the gui_version subfolder. You can set a different path in the config.ini if you like. Rerunning the flamebot will overwrite the previous contents of output.txt. <br>
Please report issues with this, as Brizeh's Code sometimes changes which in turn may cause issues with this integration. I will try to fix it asap.
# Some tips
1. I usually place this window on a seperate workspace. On windows, you can access this feature using
```Windows + Tab```.
2. You can choose your own theme. Check https://media.geeksforgeeks.org/wp-content/uploads/20200511200254/f19.jpg for the available themes.
3. Please report any issues you have on this repo, and suggestions too. I will try to work on them but
I cant promise anything.
4. If you want to see detailed output you should run the terminal version of the app. It will tell you if/when uploads fail, which will make debugging much easier. If the app crashes it will provide a crashdump txt file, please include it if you want to report a crash.
# Etc
Feel free to steal this for anything. Maybe I'll make it less scuffed in the future.<br>
Last tested with my python 3.7 setup on Arch Linux and the state of dps.report/wingman APIs as of 27.10.2023.
# Licenses of used packages
You can also find all these licenses by pressing the "About" button in the App.
requests: Apache 2.0 <br>
psyimplegui: GNU LESSER GENERAL PUBLIC LICENSE<br>
pyperclip: See licenses.txt<br>
watchdog: Apache 2.0
# Contact
Open a github issue! 
