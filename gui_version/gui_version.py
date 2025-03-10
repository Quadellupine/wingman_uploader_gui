import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import os
import requests
import FreeSimpleGUI as sg
import pyperclip
import configparser
import queue
import wget
import zipfile
from batchupload import batch_upload_window
from flamebot_integration import flamebot_input
from utils import (
    write_log,
    get_current_time,
    start_mono_app,
    get_info_from_json,
    get_path,
    check_wingman_conf,
    get_puke,
    get_ah_exposed,
    confirm_download
)


# Find latest EI release
EIQueryURL = (
    "https://api.github.com/repos/baaron4/GW2-Elite-Insights-Parser/releases/latest"
)
# Queue for multithreading
result_queue = queue.Queue()
# Load configuration
config = configparser.ConfigParser()
config_file_path = "config.ini"
data = []
if not os.path.exists(config_file_path):
    with open("config.ini", "w") as file:
        # Create .ini file with some defaults
        file.write(
            "[Settings]\nshowwipes = False\nlogpath=.\ntheme = Topanga\npushwipes = False\nno_wingman = False\nfilter_shitlogs = True\nheight=500\nwidth=470\nflame_lang=EN\nflame_output_path=."
        )
        file.close()
    config.read(config_file_path)

# Apply retrieved config
try:
    config.read(config_file_path)
    showwipes = config.getboolean("Settings", "showwipes")
    path = config["Settings"]["logpath"]
    logpath = config["Settings"]["logpath"]
    sg.theme(config["Settings"]["theme"])
    pushwipes = config.getboolean("Settings", "pushwipes")
    no_wingman = config.getboolean("Settings", "no_wingman")
    filter_shitlogs = config.getboolean("Settings", "filter_shitlogs")
    height = config["Settings"]["height"]
    width = config["Settings"]["width"]
    size_tuple = (width, height)
    flame_lang = config["Settings"]["flame_lang"]
    flame_output_path = config["Settings"]["flame_output_path"]
except:
    sg.popup("Malformed config.ini. Delete it to generate a clean one.", title="Error")
    exit()


# Watchdog Eventhandling
def on_created(event):
    return


def on_deleted(event):
    return


def on_modified(event):
    return
def license_popup():
    # Define the layout
    layout_popup = [[sg.Text('Visit the project at https://github.com/Quadellupine/wingman_autouploader',font=('Helvetica', 14))],
            [sg.HorizontalSeparator()],
            [sg.Text("Licensing:",justification="center",font=('Helvetica', 14))],
            [sg.Text("Requests: Apache 2.0")],
            [sg.Text("Pysimplegui/Freesimplegui (Version 4.x): GNU LESSER GENERAL PUBLIC LICENSE")],
            [sg.Text("watchdog: Apache 2.0")],
            [sg.Text("wget: Public Domain")],
            [sg.Text("Pyperclip: See licenses.txt on github(link above)")],
            [sg.HorizontalSeparator()],
            [sg.Text("The flamebot was made by Brizeh and can be found on github: https://github.com/Brizeh/LogFC")],
            [sg.HorizontalSeparator()],
            [sg.Text("This project is published under the Unlicense license!")],
            [sg.Button('Close')]]
    
    # Create the window
    window = sg.Window('Licensing and Help', layout_popup)

    # Event loop
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Close':
            break

    # Close the window
    window.close()
    
def on_moved(event):
    historicalSize = -1
    if event.dest_path not in seen_files and (event.dest_path.endswith(".zevtc")):
        seen_files.append(event.dest_path)
        while historicalSize != os.path.getsize(event.dest_path):
            historicalSize = os.path.getsize(event.dest_path)
            time.sleep(5)
        print(
            get_current_time(),
            event.dest_path.split(path)[1],
            "log creation has now finished",
        )
        if "WvW/" in event.dest_path:
            window.start_thread(
                lambda: upload(event.dest_path, True,0), ("-THREAD-", "-THEAD ENDED-")
            )
        else:
            window.start_thread(
                lambda: upload(event.dest_path, no_wingman, 0),
                ("-THREAD-", "-THEAD ENDED-"),
            )


def upload(log, wingman, retry_count):
    print("Starting upload")
    configpath = get_path() + "wingman.conf"
    config = ["-c", configpath]
    if not wingman:
        configpath = get_path() + "wingman.conf"
        config = ["-c", configpath]
    if wingman:
        configpath = get_path() + "no_wingman.conf"
        config = ["-c", configpath]
    print(get_current_time(), "Selected config: ", config)
    args = config + [log]
    start_mono_app("EI/GuildWars2EliteInsights-CLI.exe", args)
    ei_log = log.replace(".zevtc", ".log")
    with open(ei_log,encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    os.remove(ei_log)
    dps_link = ""
    for line in lines:
        if "dps.report" in line:
            dps_link = line.split(" ")[1]
            dps_link = dps_link.replace("\n", "")
            print(get_current_time(), "permalink:", dps_link)
        if "Wingman: UploadProcessed" in line:
            print(get_current_time(), line.replace("\n", ""))
        if "Completed for killed wvw" in line:
            print(get_current_time(), line.replace("\n", ""))
    print("dps link:",dps_link)
    # Restart if upload fails?? 
    if not wingman and dps_link == "":
        print(get_current_time(),"Upload failed, retrying")
        if retry_count < 30:
            time.sleep(30)
            retry_count = retry_count +1
            upload(log, wingman, retry_count)
        else:
            print("Reached retry limit of 30")
        return
    duration, success_value = get_info_from_json(dps_link)    
    result_queue.put((success_value, dps_link, duration))
    write_log(log)


def is_shitlog(dps_link):
    shitlogs = ["_trio", "_tc", "_esc", "_bk", "_eyes", "_se", "_rr", "_race"]
    for substring in shitlogs:
        if substring in dps_link:
            return True
    return False

def is_fractal(dps_link):
    fractals = ["_ai", "_kana", "_skor", "_arriv", "_arkk", "_mama", "_siax","_enso"]
    for substring in fractals:
        if substring in dps_link:
            return True
    return False
# Clear table
def clear_table():
    global data
    data = []
    window["table"].update(values=data)

def get_position():
    main_window_location = window.current_location()
    main_window_x, main_window_y = main_window_location
    return main_window_x, main_window_y

# Wow binary tables actually being useful for once
def reprint():
    print(get_current_time(), "Reprint requested...")
    clear_table()
    for link in link_collection:
        if link[0] or showwipes:
            if not (is_shitlog(link[1]) and filter_shitlogs):
                new_entry = [link[2], link[1], link[0]]
                data.append(new_entry)
                # Update the table
                window["table"].update(values=data)
def get_EI_version():
    try:
        with open("version.txt", "r") as file:
            content = file.read()
        return content
    except:
        print(get_current_time(),"Downloading EI for the first ime...")
        return ""
def flame_popup(popup_layout):
    popup = sg.Window('Puke incidents', popup_layout, no_titlebar=False, finalize=True)
    popup.move(mouse_x, mouse_y)  # Move the popup to mouse coordinates
    popup.read()
    popup.close()
# Check for EI 
print(get_current_time(), "Checking for EI folder....")
query = requests.get(EIQueryURL).json()
content = get_EI_version()
try:
    if content != query["name"]:
        try:
            shutil.rmtree("EI")
            print(get_current_time(),"EI out of date, updating")
        except Exception as e:
            print(e)
            pass
    else:
        print(get_current_time(),"EI up to date with version: "+content)
except:
    print("Rate limited by github, occurs mostly during testing...")
while not os.path.isdir("EI"):
    print(get_current_time(), "EI is missing, downloading it")
    query = requests.get(EIQueryURL).json()
    with open("version.txt", "w") as file:
        file.write(query["name"])
    print("Version: ", query["html_url"])
    recentEI = query["assets"][2]
    assetURL = query["assets"][2]["browser_download_url"]
    print(assetURL)
    if not confirm_download("Elite Insights", "https://github.com/baaron4/GW2-Elite-Insights-Parser"):
        exit()
    wget.download(assetURL, "EI.zip")
    with zipfile.ZipFile("EI.zip", "r") as zip_ref:
        zip_ref.extractall("EI")
    os.remove("EI.zip")
    # Update internal string 
    content = get_EI_version()
    print(get_current_time(),"EI up to date with version: "+content)
# Check for EI configs
check_wingman_conf()

# Begin the actual PROGRAM
# ----------------  Create main Layout  ----------------
headings = ["Time", "Link (Click to copy)", "Success"]
col_widths = [5, 32, 7]
textbox = [
    sg.Table(
        values=[],
        headings=headings,
        key="table",
        expand_x=True,
        expand_y=True,
        enable_events=True,
        auto_size_columns=False,
        col_widths=col_widths,
        row_height=20,
        justification="center",
        header_relief="RELIEF_FLAT",
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
    )
]
button_row_one = [
    sg.Button("Reset", size=(26, 2)),
    sg.Button("Copy last to Clipboard", size=(26, 2)),
]

button_row_two = [
    sg.Button("Copy all to Clipboard", size=(26, 2)),
    sg.Button("Copy only Kills", size=(26, 2)),
]
checkbox_one = [
    sg.Checkbox("Show wipes  ", key="wipes", default=showwipes),
    sg.Checkbox("Filter shitlogs", key="shitlog_checkbox", default=filter_shitlogs),
]
checkbox_two = [
    sg.Checkbox("Disable Wingman Upload", key="global_wingman", default=no_wingman)
]
batch_upload = [
    sg.Button("Batch Upload", key="batch", size=(13, 1)),
    sg.Button("Brizeh's Flamebot", key="flame", size=(13, 1)),
    sg.Button("About", key="about", size=(13, 1)),
]

layout = [
    textbox,
    button_row_one,
    button_row_two,
    checkbox_one,
    checkbox_two,
    batch_upload,
]
# Set icon on windows, still need to figure out how to detect Linux binaries
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = "."
icon_path = os.path.join(base_dir, "icon.ico")
window = sg.Window(
    "Autouploader",
    layout,
    auto_size_buttons=True,
    keep_on_top=False,
    grab_anywhere=True,
    resizable=True,
    size=size_tuple,
    icon="icon.ico",
    return_keyboard_events=True
)
window.set_icon(icon_path)
patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(
    patterns=["*"],  # Example pattern: matches all files
    ignore_patterns=[],  # Example: no ignored patterns
    ignore_directories=True,  # Whether to ignore directories
    case_sensitive=False  # Whether matching is case-sensitive
)

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)
my_observer.start()

start_time = time.time()
# Keeping track of the seen files is necessary because somehow the modified event gets procced a million times
seen_files = []
# List of ALL logs that have been uploaded. Not necessarily all logs currently shown in the GUI
link_collection = []
# These are for debugging if needed
#duration, success = get_info_from_json("https://dps.report/NxAB-20240320-215554_matt")
#result_queue.put((True, "https://dps.report/UnVl-20240624-215137_trin", 10))
#result_queue.put((True, "https://dps.report/KzO5-20240624-231234_skor", 10))
#result_queue.put((True, "https://dps.report/yxfq-20240624-220623_trin", 10))
#result_queue.put((False, "_trio_wipe", 0))

try:
    while True:
        time.sleep(0.05)
        event, values = window.read(timeout=100)
        # The threads will place finished logs in a queue. The GUI periodically checks for new logs in the queue and then processes them
        try:
            success_value, dps_link, duration = result_queue.get_nowait()
            link_collection.append((success_value, dps_link, duration))
            # Print according to user selection
            reprint()
        except queue.Empty:
            pass

        # Check for events, extremely UGLY but what can you do
        if event == sg.WIN_CLOSED or event == "Exit":
            with open(config_file_path, "w") as configfile:
                config.write(configfile)
            break
        # Open additional Window to start a batch upload, handled in additional python file
        # Catch m key and do some handling to show mechanics
        elif event == "m:58":
            try:
                selected_row = values['table'][0]  # Get the first selected row index
            except:
                print(get_current_time(), "No Row selected")
                continue
            selected_cell_value = data[selected_row][1]
            if(is_fractal(selected_cell_value)):
                    result_table = get_puke(selected_link)
                    mouse_x, mouse_y = window.current_location()
                    popup_layout = [[sg.Table(
                        values = result_table,
                        headings=["Player","Times Puked","Times Puked On"],
                        auto_size_columns=False,
                        col_widths=[15,14,14],
                        row_height=20,
                        justification="center",
                        header_relief="RELIEF_FLAT",
                        hide_vertical_scroll="True",
                        num_rows=5
                        )]]
                    if result_table[0][1] == -1:
                        print(get_current_time(),"No Toxic Sickness instab")
                    else:                        
                        flame_popup(popup_layout)

            if("_trin" in selected_cell_value):
                result_table = get_ah_exposed(selected_link)
                mouse_x, mouse_y = window.current_location()
                popup_layout = [[sg.Table(
                    values = result_table,
                    headings=["Player","Times Exposed"],
                    auto_size_columns=False,
                    col_widths=[15,14,14],
                    row_height=20,
                    justification="center",
                    header_relief="RELIEF_FLAT",
                    hide_vertical_scroll="True",
                    num_rows=10
                    )]]
                if -1 in result_table:
                    print(get_current_time(),"No Exposed stacks")
                else:                        
                    flame_popup(popup_layout)
        elif event == "about":
            license_popup()
        elif event == "batch":
            batch_upload_window(logpath)
           
        elif "table" in event:            
            # The event objects contains: The source, the event name and then the cell that has been clicked as a tuple. This means we can access the row like this:
            row = event[2][0]
            selected_row = values["table"][0]
            try:
                # Now we look up the log in the data array, which holds the contents of the table that is displayed
                selected_link = data[selected_row][1]
                pyperclip.copy(selected_link)
                #sg.popup_notify("Copied!", display_duration_in_ms=1000, fade_in_duration=0, alpha=1)
            except Exception as e:
                print(e)
                pass
        # Copying last visible link to clipboard
        elif event == "Copy last to Clipboard":
            try:
                last = window["table"].get()
                last = last[-1][1]
            except Exception as e:
                print(get_current_time(), e)
                last = ""
            pyperclip.copy(last)
        # Copy all visible links to clipboard
        elif event == "Copy all to Clipboard":
            s = ""
            for entry in link_collection:
                if entry[0] or showwipes:
                    if not (is_shitlog(entry[1]) and filter_shitlogs):
                        s = s + (entry[1]) + "\n"
            pyperclip.copy(s)
        # Only copy kills, even if wipes are visible
        elif event == "Copy only Kills":
            s = ""
            for entry in link_collection:
                if entry[0] == True and not (is_shitlog(entry[1]) and filter_shitlogs):
                    s = s + (entry[1]) + "\n"
            pyperclip.copy(s)
        elif event == "flame":
            print(get_current_time(), "Activating flamebot")
            pos_x, pos_y = get_position()
            flamebot_input(pos_x, pos_y, flame_lang,flame_output_path)
        # Reset memory of links
        elif event == "Reset":
            clear_table()
            link_collection = []
        # Upload wipes
        elif values["wipes"] == True:
            config.set("Settings", "ShowWipes", "True")
            if values["wipes"] != showwipes:
                showwipes = True
                reprint()
        elif values["wipes"] == False:
            config.set("Settings", "ShowWipes", "False")
            if values["wipes"] != showwipes:
                showwipes = False
                reprint()
        # Disable wingman upload entirely
        if values["global_wingman"] == True:
            config.set("Settings", "no_wingman", "True")
            no_wingman = True
        elif values["global_wingman"] == False:
            config.set("Settings", "no_wingman", "False")
            no_wingman = False
        # Filter Shitlogs
        if values["shitlog_checkbox"] == True:
            config.set("Settings", "filter_shitlogs", "True")
            if values["shitlog_checkbox"] != filter_shitlogs:
                filter_shitlogs = True
                reprint()
        elif values["shitlog_checkbox"] == False:
            config.set("Settings", "filter_shitlogs", "False")
            if values["shitlog_checkbox"] != filter_shitlogs:
                filter_shitlogs = False
                reprint()

except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
except Exception as e:
    print("Oh no!")
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    print(f"Error occured at {e.__traceback__.tb_lineno}")
    exception = str(type(e).__name__) +" " + str(e) + " " + str(e.__traceback__.tb_lineno)
    now = datetime.now()
    filename = now.strftime("%d_%m_%Y_%H:%M:%S")
    filename = filename + "_crash.txt"
    f = open(filename, "w+")
    f.write(exception)
    f.close()