import FreeSimpleGUI as sg
import wget
import os
from utils import get_current_time, confirm_download
import zipfile
import subprocess
import platform
import requests
import configparser
import sqlite3

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
# Check if database exists, create it if it doesnt.

def get_position(window):
    main_window_location = window.current_location()
    main_window_x, main_window_y = main_window_location
    return main_window_x, main_window_y


def check_database():
    # Check if the database file exists
    if os.path.isfile("hooks.db"):
        conn = sqlite3.connect('hooks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hooks';")
        table_exists = cursor.fetchone()
        conn.close()
        if table_exists:
            return True  
        else:
            print(get_current_time(), "Database exists but is corrupted.")
            return False 
    else:
        return False
def create_database():
    # Delete existing Database
    if os.path.isfile("hooks.db"):
        os.remove("hooks.db")
    # Create it from scratch
    conn = sqlite3.connect('hooks.db')
    cursor = conn.cursor()
    table = """ CREATE TABLE hooks (
    discord_hook VARCHAR(255) NOT NULL,
    name CHAR(50) NOT NULL
    ); """
    cursor.execute(table)
    conn.close()

def add_entry_to_db(name, discord_hook):
    conn = sqlite3.connect("hooks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hooks (name, discord_hook) VALUES (?, ?)", (name, discord_hook))
    conn.commit()
    conn.close()

def delete_entry_from_db(row_id):
    conn = sqlite3.connect("hooks.db")
    cursor = conn.cursor()
    # Delete using ROWID
    cursor.execute("DELETE FROM hooks WHERE ROWID = ?", (row_id,))
    conn.commit()
    conn.close()


def get_hook_from_name(name):
    conn = sqlite3.connect('hooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT discord_hook FROM hooks WHERE name = ?",(name,)) 
    row = cursor.fetchone()
    conn.close()
    return row[0]

def get_names():
    conn = sqlite3.connect('hooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT discord_hook, name FROM hooks") 
    rows = cursor.fetchall()
    conn.close()
    items = [(row[1]) for row in rows]
    return items

def get_data():
    conn = sqlite3.connect("hooks.db")
    cursor = conn.cursor()
    # Select ROWID along with name and discord_hook
    cursor.execute("SELECT ROWID, name, discord_hook FROM hooks ORDER BY name")
    data = cursor.fetchall()
    conn.close()
    return data

## Window that shows the dropdown to select a guild
def dropdown_tokens(pos_x, pos_y):
    items = get_names()  # Fetch tokens from the database

    layout = [
        [sg.Text('Select a Guild:')],
        [sg.Combo(items, key='-DROPDOWN-', size=(30, 5),font=('Helvetica', 12), readonly=True)],
        [sg.Button('OK'), sg.Button('No Hook'), sg.Button("Manage Hooks")],
    ]
    
    window = sg.Window('Select Guild', layout, location=(pos_x, pos_y))
    
    # Event loop for the dropdown tokens window
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'No Hook':
            selected_token = ""
            break
        
        if event == 'OK':
            selected_token = values['-DROPDOWN-']
            if selected_token:
                print(get_current_time(), selected_token,"selected.")
            else:
                print(get_current_time(), "No token selected.")
            # Exit loop after user selects token
            break

        if event =="Manage Hooks":
            pos_x, pos_y = get_position(window)
            hook_management(pos_x, pos_y)
            window.close()
            dropdown_tokens(pos_x, pos_y)
    window.close()
    # The causes issue because of the recursive calling of the window
    return selected_token


# Window for Hook management
def create_crud_window(pos_x, pos_y):
    data = get_data()

    # Header row
    header = [
        sg.Text("Name", size=(20, 1), font=('Helvetica', 10, 'bold')),
        sg.Text("Discord Hooks", size=(40, 1), font=('Helvetica', 10, 'bold')),
        sg.Text("", size=(3, 1)) # For the 'X' button column
    ]

    # Data rows
    data_rows = []
    for i, row in enumerate(data):
        row_id, name, discord_hook = row
        data_rows.append([
            sg.Input(default_text=name, key=f'-NAME-{row_id}', disabled=True, size=(20,1)),
            sg.Input(default_text=discord_hook, key=f'-HOOK-{row_id}', disabled=True, size=(40,1)),
            sg.Button("X", key=f'-DELETE-{row_id}', size=(3, 1), button_color=('white', 'red'))
        ])

    data_display_column_layout = [header] + data_rows
    add_new_section = [
        sg.Text("New Name:", size=(10, 1)),
        sg.Input(key='-NEW_NAME-', size=(20,1)),
        sg.Text("New Hook:", size=(10, 1)),
        sg.Input(key='-NEW_HOOK-', size=(40,1)),
        sg.Button("Add Entry", key='-ADD_ENTRY-')
    ]

    # Main window layout
    layout = [
        [sg.Column(data_display_column_layout, scrollable=True, vertical_scroll_only=True, size=(680, 300), key='-DATA_COLUMN-', expand_x=True)],
        [sg.HSeparator()],
        add_new_section
    ]

    return sg.Window("Discord Hook Management", layout, finalize=True,location=(pos_x, pos_y))



def hook_management(pos_x, pos_y):
    window = create_crud_window(pos_x, pos_y)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
        elif event == '-ADD_ENTRY-':
            new_name = values['-NEW_NAME-']
            new_hook = values['-NEW_HOOK-']
            if new_name and new_hook:
                add_entry_to_db(new_name, new_hook)
                # Close the current window and create a new one
                window.close()
                window = create_crud_window(pos_x, pos_y) # Recreate window with updated data
            else:
                sg.popup_error("Both Name and Discord Hook are required to add an entry.",location=(pos_x, pos_y))
        elif event.startswith('-DELETE-'):
            row_id_to_delete = int(event.split('-')[-1])
            if sg.popup_yes_no(f"Are you sure you want to delete entry with ROWID {row_id_to_delete}?",location=(pos_x, pos_y)) == 'Yes':
                delete_entry_from_db(row_id_to_delete)
                # Close the current window and create a new one
                window.close()
                window = create_crud_window(pos_x, pos_y) # Recreate window with updated data

    window.close()

def flamebot_input(pos_x, pos_y,flame_lang, flame_output_path, use_webhook):
    logs = sg.popup_get_text("Paste the logs you want to run the flamebot on:",location=(pos_x, pos_y))
    if logs == None:
        print(get_current_time(), "Window closed without submitting logs")
        return
    logs = split_links(logs)
    # Sanity check database, TODO: Add Check for whether the correct table exists
    db_exists = check_database()
    if not db_exists:
        create_database()
        print(get_current_time(), "Database for discord hooks did not exist. Created hooks.db")
    elif db_exists:
        print(get_current_time(), "Database for discord hooks exists and has the correct tables.")


    # Check flame output settings
    # Only open token selection dialog if user wants to output to discord in the first place
    guild = ""
    if use_webhook:
        guild = dropdown_tokens(pos_x, pos_y)
    # Act accordingly
    if guild == "":
        print(get_current_time(), "No guild selected, only running locally")
        run_flamebot(logs,flame_lang, flame_output_path, guild, False)
    else:
        print(get_current_time(), guild,"selected, flaming to discord in addition to regular output")
        run_flamebot(logs,flame_lang, flame_output_path, get_hook_from_name(guild), use_webhook)
    
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
    
    #print(flameoutput.stdout)
    #print(flameoutput.stderr)
    outfile = flame_output_path+"/output.txt"
    with open(outfile, 'w', encoding='utf-8') as file:
        file.write(flameoutput.stdout)
    print(get_current_time(), "Flamebot finished, check your output.txt at", flame_output_path)
    if use_webhook:
        titles = []
        wings = flameoutput.stdout.split("# W")
        for wing in wings:
            try:
                titles.append(wing.splitlines()[0])
            except:
                print(get_current_time(), "Could not parse Flamebot output. If it is empty it is likely stuck on trying to retrieve the wingman percentile data. Delete it so it can be freshly downloaded.")
                print(flameoutput.stdout)
        # Remove debug output from flamebot itself
        wings = wings[1:]
        titles = titles[1:]
        # Remove first line which is used as a title instead, this also catches runs with errors but is not robust. Need to talk to Lemon.
        wings = ["\n".join(s.splitlines()[1:]) for s in wings]
        titles = ["W" + s for s in titles]
        send_discord_embeds(webhook, wings, titles)

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

