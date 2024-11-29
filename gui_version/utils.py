import time 
from datetime import datetime
import subprocess
import os
import requests
import platform
from collections import Counter
import PySimpleGUI as sg

def write_log(text):
    try:
        with open(".seen.csv", "a") as f:
            f.write(str(text)+"\n")
    except:
        f = open(".seen.csv", "x")
        f.close
        write_log(text)

def confirm_download(application_name, application_link):
    response = sg.popup_yes_no("The program wants to download or update "+application_name+", is that okay? You can check it out at "+application_link+". Clicking no will close the App.", title="Confirmation")
    if response == 'Yes':
        return True
    else:
        return False

def get_current_time():
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    ts = date_time.strftime("%H:%M:%S")
    ts = "["+ts+"]:"
    return ts
def start_mono_app(app_path, app_arguments):
    osname = platform.system()
    if osname =="Windows":
        subprocess.run([app_path] + app_arguments)
    else:
        try:
            # Use subprocess to start the app with arguments
            subprocess.run(['dotnet', app_path.replace("exe","dll")] + app_arguments)
        except Exception as e:
            print("Do you have .dotnet installed? Check the readme if you havent. On Ubuntu, there is also the option to install via snap.")
            print(e)   
def get_info_from_json(dps_link):
    try:
        url = "https://dps.report/getJson?permalink="+dps_link
        response = requests.get(url)
        content = response.json()
        duration = content.get("duration")
        success = content.get("success")
        parts = duration.split()
        duration = parts[0]+parts[1]
    except Exception as e:
        print(e)
        duration = "0"
        success = False
    return duration, success

def return_json(dps_link):
    url = "https://dps.report/getJson?permalink="+dps_link
    response = requests.get(url)
    content = response.json()
    return content


def get_wingman_percentile(log):
    # Get only postfix of log with dps.report shebang in the front
    postfix = log.split("/")[-1]
    url = "https://gw2wingman.nevermindcreations.de/api/getPercentileOfLog/"+postfix
    response = requests.get(url)
    content = response.json()
    return content.get("percentile")

def get_path():
    path = os.path.abspath(__file__)
    path = path.rstrip(os.path.basename(__file__))
    return path
def check_wingman_conf():
    print(get_current_time(),"Checking for EI config files...")
    # Block for wingman.conf
    wingman_conf = "SaveOutHTML=false\nUploadToDPSReports=true\nUploadToWingman=true\n"
    file = get_path()+"wingman.conf"
    if os.path.isfile(file):
        print(get_current_time(),"wingman.conf found. No action needed.")
    else:
        print(get_current_time(),"wingman.conf missing. Generating...")
        f = open(file, "x")
        f.write(wingman_conf)
        
        
    # Block for no_wingman.conf
    wingman_conf = "SaveOutHTML=false\nUploadToDPSReports=true\nUploadToWingman=false"
    file = get_path()+"no_wingman.conf"
    if os.path.isfile(file):
        print(get_current_time(),"no_wingman.conf found. No action needed.")
    else:
        print(get_current_time(),"no_wingman.conf missing. Generating...")
        f = open(file, "x")
        f.write(wingman_conf)
        
    
    # Block for batch.conf
    wingman_conf = "SaveOutHTML=false\nUploadToDPSReports=false\nUploadToWingman=true"
    file = get_path()+"batch.conf"
    if os.path.isfile(file):
        print(get_current_time(),"batch.conf found. No action needed.")
    else:
        print(get_current_time(),"batch.conf missing. Generating...")
        f = open(file, "x")
        f.write(wingman_conf)

def get_puke(dps_link):
    puked = {'Nobody': -1}
    puker = {'Nobody': -1}

    try:
        url = "https://dps.report/getJson?permalink="+dps_link
        response = requests.get(url)
        content = response.json()
        mechanics = content.get("mechanics")
        to_find = ["Toxic Sickness Hit By Player", "Toxic Sickness Hit To Player"]
        matching_entries = [entry for entry in content.get("mechanics", []) if entry.get("fullName") in to_find]
        if matching_entries:
            print(get_current_time(),matching_entries[0]["description"])
            puker = Counter(entry['actor'] for entry in matching_entries[0]["mechanicsData"])
            print(get_current_time(),dict(puker))
            print(get_current_time(),get_current_time(),matching_entries[1]["description"])
            puked = Counter(entry['actor'] for entry in matching_entries[1]["mechanicsData"])
            print(get_current_time(),dict(puked))
    except Exception as e:
        print(get_current_time(),"dps.report issues, can't fetch mechanics")
    names1, values1 = zip(*puker.items())
    names2, values2 = zip(*puked.items())
    all_keys = set(names1).union(set(names2))
    return_array = []
    for key in all_keys:
        row = [
            key,
            puker.get(key, 0),  # Get value from dict1, default to 0 if key is not present
            puked.get(key, 0)   # Get value from dict2, default to 0 if key is not present
        ]
        return_array.append(row)
    return return_array
def return_instabs(dps_link):
    url = "https://dps.report/getJson?permalink="+dps_link
    response = requests.get(url)
    content = response.json()
    instabs = content.get("presentFractalInstabilities")
    print(instabs)

def get_ah_exposed(dps_link):
    exposed = {'Nobody': -1}
    try:
        url = "https://dps.report/getJson?permalink="+dps_link
        response = requests.get(url)
        content = response.json()
        mechanics = content.get("mechanics")
        all_players = content.get("players")
        all_players = [player["name"] for player in all_players]
        to_find = ["Exposed Applied"]
        matching_entries = [entry for entry in content.get("mechanics", []) if entry.get("fullName") in to_find]
        if matching_entries:
            print(get_current_time(),matching_entries[0]["description"])
            exposed = Counter(entry['actor'] for entry in matching_entries[0]["mechanicsData"])
            print(get_current_time(),dict(exposed))
    except:
        print(get_current_time(),"dps.report issues, can't fetch mechanics")
    return_array = []
    for entry in exposed:
        return_array.append([entry, exposed[entry]])
        all_players.remove(entry)
    # Add all players that had 0 stacks and thus did not appear in the mechanic overview for the debuff
    for entry in all_players:
        return_array.append([entry, 0])
    return_array.sort(key=lambda test_list: test_list[1])
    return return_array

#print(get_ah_exposed("https://dps.report/yxfq-20240624-220623_trin"))
#print(get_puke("https://dps.report/IF64-20240624-200026_ai"))