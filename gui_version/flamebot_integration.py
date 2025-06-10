import FreeSimpleGUI as sg
import wget
import os
from utils import get_current_time, confirm_download
import zipfile
import subprocess
import platform
import requests
import configparser

# This is terrible, pls give me a proper way to do this brizeh...
def change_language(lang_string):
    with open('GW2-Flamebot-Extended/GW2-Flamebot-Extended-main/main.py', 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('"FR"', lang_string)
    filedata = filedata.replace('"EN"', lang_string)
    with open('GW2-Flamebot-Extended/GW2-Flamebot-Extended-main/main.py', 'w') as file:
        file.write(filedata)

def split_links(input_string):
    links = input_string.split("https")
    output = []
    
    for link in links:
        # Sometimes people surely paste random whitespace that causes issues
        if link:
            output.append("https"+link)
    return output

def flamebot_input(pos_x, pos_y,flame_lang, flame_output_path, webhook, use_webhook):
    logs = sg.popup_get_text("Paste the logs you want to run the flamebot on:",location=(pos_x, pos_y))
    if logs == None:
        print(get_current_time(), "Window closed without submitting logs")
        return
    logs = split_links(logs)
    run_flamebot(logs,flame_lang, flame_output_path, webhook, use_webhook)
    
def run_flamebot(logs,flame_lang,flame_output_path, webhook, use_webhook):
    BrizehUrl = "https://github.com/Lemon-Dealer/GW2-Flamebot-Extended/archive/refs/heads/main.zip"
    while not os.path.isdir("GW2-Flamebot-Extended"):
        print(get_current_time(), "Flamebot is missing, downloading it!")
        confirm_download("Lemon's Flamebot, based on the original from Brizeh", "https://github.com/Lemon-Dealer/GW2-Flamebot-Extended")
        wget.download(BrizehUrl, "GW2-Flamebot-Extended-main.zip")
        with zipfile.ZipFile("GW2-Flamebot-Extended-main.zip", "r") as zip_ref:
            zip_ref.extractall("GW2-Flamebot-Extended")
        os.remove("GW2-Flamebot-Extended-main.zip")
    
    flame_lang = '"'+flame_lang+'"'
    change_language(flame_lang)
    os.remove("GW2-Flamebot-Extended/GW2-Flamebot-Extended-main/src/input_logs.txt")
    # Write the passed files into the required text file
    with open("GW2-Flamebot-Extended/GW2-Flamebot-Extended-main/src/input_logs.txt", "w") as file:
        for log in logs:
            file.write(log+"\n")
        file.close()
    # Start the flamebot(Jesus takes the wheel from here), also change working directory accordingly!!
    osname = platform.system()
    if osname == "Windows": 
        flameoutput = subprocess.run(["python","main.py"],cwd="GW2-Flamebot-Extended/GW2-Flamebot-Extended-main", capture_output=True, text=True)
    else:
        flameoutput = subprocess.run(["python3", "main.py"],cwd="GW2-Flamebot-Extended/GW2-Flamebot-Extended-main",capture_output=True,text=True)
    
    print(flameoutput.stdout)
    print(flameoutput.stderr)
    outfile = flame_output_path+"/output.txt"
    with open(outfile, 'w', encoding='utf-8') as file:
        file.write(flameoutput.stdout)
    
    if use_webhook:
        titles = []
        wings = flameoutput.stdout.split("# W")
        for wing in wings:
            titles.append(wing.splitlines()[0])
        # Remove debug output from flamebot itself
        wings = wings[1:]
        titles = titles[1:]
        # Remove first line which is used as a title instead
        wings = ["\n".join(s.splitlines()[1:]) for s in wings]
        titles = ["W" + s for s in titles]
        send_discord_embeds(webhook, wings, titles)

import requests

def send_discord_embeds(webhook_url: str, contents: list[str], titles: list[str] = None, max_chars=6000):
    if titles is None:
        titles = [f"Message {i+1}" for i in range(len(contents))]
    elif len(titles) != len(contents):
        raise ValueError("Length of titles must match length of contents")

    batch_contents = []
    batch_titles = []
    batch_length = 0

    def send_batch(contents_batch, titles_batch):
        embeds = []
        for i, content in enumerate(contents_batch):
            embeds.append({
                "title": titles_batch[i],
                "description": content,
                "color": 3447003
            })
        data = {"embeds": embeds}
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Batch sent successfully.")
        else:
            print(f"Failed to send batch: {response.status_code} - {response.text}")

    for content, title in zip(contents, titles):
        # Calculate length if we add this embed to current batch
        # Count title + description length
        embed_length = len(content) + len(title)

        # Check if adding this embed exceeds the max allowed characters
        if batch_length + embed_length > max_chars and batch_contents:
            # Send current batch first
            send_batch(batch_contents, batch_titles)
            # Reset batch
            batch_contents = []
            batch_titles = []
            batch_length = 0

        batch_contents.append(content)
        batch_titles.append(title)
        batch_length += embed_length

    # Send the last batch if any
    if batch_contents:
        send_batch(batch_contents, batch_titles)

