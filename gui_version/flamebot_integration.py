import PySimpleGUI as sg
import wget
import os
from utils import get_current_time, confirm_download
import zipfile
import subprocess
import platform
import requests
import shutil

# please make it stop
def bill_gates_special():
    with open('LogFC/LogFC-main/src/languages_dict/english.py', 'r', encoding='utf-8') as file:
        filedata = file.read()
    filedata = filedata.replace("\u2b17", "-")
    with open('LogFC/LogFC-main/src/languages_dict/english.py', 'w', encoding='utf-8') as file:
        file.write(filedata)

# This is terrible, pls give me a proper way to do this brizeh...
def change_language(lang_string):
    with open('LogFC/LogFC-main/src/main.py', 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('"FR"', lang_string)
    filedata = filedata.replace('"EN"', lang_string)
    with open('LogFC/LogFC-main/src/main.py', 'w') as file:
        file.write(filedata)

def split_links(input_string):
    links = input_string.split("https")
    output = []
    for link in links:
        # Sometimes people surely paste random whitespace that causes issues
        if link:
            output.append("https"+link)
    return output

def flamebot_input(pos_x, pos_y,flame_lang, flame_output_path):
    logs = sg.popup_get_text("Paste the logs you want to run the flamebot on:",location=(pos_x, pos_y))
    if logs == None:
        print(get_current_time(), "Window closed without submitting logs")
        return
    logs = split_links(logs)
    run_flamebot(logs,flame_lang, flame_output_path)

def flatten_directory(path):
    folders = os.listdir(path)
    for item in folders:
        for filename in os.listdir(os.path.join(path, item)):
            new_path = os.path.join(path, filename)
            shutil.move(os.path.join(path,item, filename), os.path.join(path))
        if os.path.isdir(os.path.join(path,item)):
            shutil.rmtree(os.path.join(path,item))

def asset_management():
    # This function manages the LogFC assets
    BrizehUrl = "https://api.github.com/repos/Brizeh/LogFC/releases/latest"
    query = requests.get(BrizehUrl).json()
    version = query["name"]
    if os.path.isdir("LogFC-main") and os.path.isfile("LogFC-main/version.txt"):
        with open("LogFC-main/version.txt", "r") as file:
            installed_version = file.read()
        if version == installed_version:
            print(get_current_time(),"LogFC installed and up to date with latest release!")
            return()
        else:
            print(get_current_time(), "Current version: ",installed_version, " Latest version: ", version)
            print(get_current_time(), "Deleting current install and downloading latest version")
    else:
        print(get_current_time(), "No (proper) LogFC installation, pulling latest release")
    DownloadUrl = "https://api.github.com/repos/Brizeh/LogFC/zipball/logfc"
    if os.path.isdir("LogFC-main"):
        shutil.rmtree("LogFC-main")
    while not os.path.isdir("LogFC-main"):
        print(get_current_time(), "LogFC is missing, downloading it")
        confirm_download("Brizeh's Flamebot", "https://github.com/Brizeh/LogFC")
        wget.download(DownloadUrl, "LogFC.zip")
        with zipfile.ZipFile("LogFC.zip", "r") as zip_ref:
            zip_ref.extractall("LogFC-main")
        os.remove("LogFC.zip")
    flatten_directory("LogFC-main")
    with open("LogFC-main/version.txt", "w") as file:
        file.write(version)

def run_flamebot(logs,flame_lang,flame_output_path):    
    flame_lang = '"'+flame_lang+'"'
    change_language(flame_lang)
    os.remove("LogFC/LogFC-main/src/input_logs.txt")
    # Write the passed files into the required text file
    with open("LogFC/LogFC-main/src/input_logs.txt", "w") as file:
        for log in logs:
            file.write(log+"\n")
        file.close()
    # Start the flamebot(Jesus takes the wheel from here), also change working directory accordingly!!
    osname = platform.system()
    if osname == "Windows": 
        bill_gates_special()
        flameoutput = subprocess.run(["python","src/main.py"],cwd="LogFC/LogFC-main", capture_output=True, text=True)
    else:
        flameoutput = subprocess.run(["python3", "src/main.py"],cwd="LogFC/LogFC-main",capture_output=True,text=True)
    
    print(flameoutput.stdout)
    print(flameoutput.stderr)
    outfile = flame_output_path+"/output.txt"
    with open(outfile, 'w', encoding='utf-8') as file:
        file.write(flameoutput.stdout)

asset_management()
#flatten_directory("LogFC")