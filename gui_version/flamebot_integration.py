import PySimpleGUI as sg
import wget
import os
from utils import get_current_time, confirm_download
import zipfile
import subprocess
import platform


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
    
def run_flamebot(logs,flame_lang,flame_output_path):
    BrizehUrl = "https://github.com/Brizeh/LogFC/archive/refs/heads/main.zip"
    while not os.path.isdir("LogFC"):
        print(get_current_time(), "LogFC is missing, downloading it")
        confirm_download("Brizeh's Flamebot", "https://github.com/Brizeh/LogFC")
        wget.download(BrizehUrl, "LogFC.zip")
        with zipfile.ZipFile("LogFC.zip", "r") as zip_ref:
            zip_ref.extractall("LogFC")
        os.remove("LogFC.zip")
    
    flame_lang = '"'+flame_lang+'"'
    change_language(flame_lang)
    os.remove("LogFC/LogFC-main/src/input logs.txt")
    # Write the passed files into the required text file
    with open("LogFC/LogFC-main/src/input logs.txt", "w") as file:
        for log in logs:
            file.write(log+"\n")
        file.close()
    # Start the flamebot(Jesus takes the wheel from here), also change working directory accordingly!!
    osname = platform.system()
    if osname == "Windows": 
        flameoutput = subprocess.run(["python","src/main.py"],cwd="LogFC/LogFC-main", capture_output=True, text=True)
    else:
        bill_gates_special()
        flameoutput = subprocess.run(["python3", "src/main.py"],cwd="LogFC/LogFC-main",capture_output=True,text=True)
    
    print(flameoutput.stdout)
    outfile = flame_output_path+"/output.txt"
    with open(outfile, 'w', encoding='utf-8') as file:
        file.write(flameoutput.stdout)
