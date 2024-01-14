import dearpygui.dearpygui as dpg
import ntpath
import json
from mutagen.mp3 import MP3
from tkinter import Tk,filedialog
import threading
import pygame
import time
import random
import os
import atexit
import webbrowser
from cryptography.fernet import Fernet 
""" Week One Contribution to an open source project """

def generate_key():
    """
    Generates a key and save it into a file if it doesn't already exist.
    """
    key_file_path = "secret.key"
    if not os.path.exists(key_file_path):
        key = Fernet.generate_key()
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
    else:
        print("Key already exists. No new key generated.")

def load_key():
    """
    Load the previously generated key
    """
    with open("secret.key", "rb") as key_file:
        return key_file.read()

def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message
     
def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

    songs = data["songs"]
    for filename in songs:
        dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1,
                       height=25, user_data=filename.replace("\\", "/"), parent="list")
        
        dpg.add_spacer(height=2, parent="list")


dpg.create_context()
dpg.create_viewport(title="Rainy Music",large_icon="icon.ico",small_icon="icon.ico")
pygame.mixer.init()
global state
state=None

global no
no = 0

_DEFAULT_MUSIC_VOLUME = 0.5
pygame.mixer.music.set_volume(0.5)

def update_volume(sender, app_data):
	pygame.mixer.music.set_volume(app_data / 100.0)

def load_database():
    # Load the encrypted data from the database
    with open("data/songs.json", "rb") as db_file:
        encrypted_data = db_file.read()

    # Decrypt the data
    decrypted_data_str = decrypt_message(encrypted_data)

    # Convert the decrypted data from a string back to a dictionary
    data = json.loads(decrypted_data_str)

    # Clear existing items in the list (if any)
    dpg.delete_item("list", children_only=True)

    # Populate GUI with songs from decrypted data
    for filename in data["songs"]:
        dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1,
                       height=25, user_data=filename.replace("\\", "/"), parent="list")
        dpg.add_spacer(height=2, parent="list")


def update_database(filename: str):
    with open("data/songs.json", "r+") as file:
        data = json.load(file)
        if filename not in data["songs"]:
            data["songs"] += [filename]
        
        # Convert the data to a string
        data_str = json.dumps(data)

        # Encrypt the data
        encrypted_data = encrypt_message(data_str)

        # Write the encrypted data back to the file
        file.seek(0)
        file.write(encrypted_data)
        file.truncate()

def update_slider():
	global state
	while pygame.mixer.music.get_busy() or state != 'paused':
		dpg.configure_item(item="pos",default_value=pygame.mixer.music.get_pos()/1000)
		time.sleep(0.7)
	state = None
	dpg.configure_item("cstate",default_value=f"State: None")
	dpg.configure_item("csong",default_value="Now Playing : ")
	dpg.configure_item("play",label="Play")
	dpg.configure_item(item="pos",max_value=100)
	dpg.configure_item(item="pos",default_value=0)

def play(sender, app_data, user_data):
	global state,no
	if user_data:
		no = user_data
		pygame.mixer.music.load(user_data)
		audio = MP3(user_data)
		dpg.configure_item(item="pos",max_value=audio.info.length)
		pygame.mixer.music.play()
		thread=threading.Thread(target=update_slider,daemon=False).start()
		if pygame.mixer.music.get_busy():
			dpg.configure_item("play",label="Pause")
			state="playing"
			dpg.configure_item("cstate",default_value=f"State: Playing")
			dpg.configure_item("csong",default_value=f"Now Playing : {ntpath.basename(user_data)}")

def play_pause():
	global state,no
	if state=="playing":
		state="paused"
		pygame.mixer.music.pause()
		dpg.configure_item("play",label="Play")
		dpg.configure_item("cstate",default_value=f"State: Paused")
	elif state=="paused":
		state="playing"
		pygame.mixer.music.unpause()
		dpg.configure_item("play",label="Pause")
		dpg.configure_item("cstate",default_value=f"State: Playing")
	else:
		song = json.load(open("data/songs.json", "r"))["songs"]
		if song:
			song=random.choice(song)
			no = song
			pygame.mixer.music.load(song)
			pygame.mixer.music.play()
			thread=threading.Thread(target=update_slider,daemon=False).start()	
			dpg.configure_item("play",label="Pause")
			if pygame.mixer.music.get_busy():
				audio = MP3(song)
				dpg.configure_item(item="pos",max_value=audio.info.length)
				state="playing"
				dpg.configure_item("csong",default_value=f"Now Playing : {ntpath.basename(song)}")
				dpg.configure_item("cstate",default_value=f"State: Playing")

def pre():
	global state,no
	songs = json.load(open('data/songs.json','r'))["songs"]
	try:
		n = songs.index(no)
		if n == 0:
			n = len(songs)
		play(sender=any,app_data=any,user_data=songs[n-1])
	except:
		pass

def next():
	global state,no
	try:
		songs = json.load(open('data/songs.json','r'))["songs"]
		n = songs.index(no)
		if n == len(songs)-1:
			n = -1
		play(sender=any,app_data=any,user_data=songs[n+1])
	except:
		pass

def stop():
	global state
	pygame.mixer.music.stop()
	state=None

def add_files():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	filename=filedialog.askopenfilename(filetypes=[("Music Files", ("*.mp3","*.wav","*.ogg"))])
	root.quit()
	if filename.endswith(".mp3" or ".wav" or ".ogg"):
		if filename not in data["songs"]:
			update_database(filename)
			dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=25,user_data=filename.replace("\\","/"),parent="list")
			dpg.add_spacer(height=2,parent="list")

def add_folder():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	folder=filedialog.askdirectory()
	root.quit()
	for filename in os.listdir(folder):
		if filename.endswith(".mp3" or ".wav" or ".ogg"):
			if filename not in data["songs"]:
				update_database(os.path.join(folder,filename).replace("\\","/"))
				dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=25,user_data=os.path.join(folder,filename).replace("\\","/"),parent="list")
				dpg.add_spacer(height=2,parent="list")

def search(sender, app_data, user_data):
	songs = json.load(open("data/songs.json", "r"))["songs"]
	dpg.delete_item("list", children_only=True)
	for index, song in enumerate(songs):
		if app_data in song.lower():
			dpg.add_button(label=f"{ntpath.basename(song)}", callback=play,width=-1, height=25, user_data=song, parent="list")
			dpg.add_spacer(height=2,parent="list")

def removeall():
	songs = json.load(open("data/songs.json", "r"))
	songs["songs"].clear()
	json.dump(songs,open("data/songs.json", "w"),indent=4)
	dpg.delete_item("list", children_only=True)
	load_database()

# Theme selector function
def switch_theme(sender, app_data, user_data):
    if app_data == "Fallout":
        dpg.bind_theme("fallout_theme")
    else:
        dpg.bind_theme("base")

# Create a single settings window with the specified size, position, and content
with dpg.window(label="Settings", tag="settings_window", width=300, height=200, pos=(100, 100), no_move=False):
    dpg.add_text("Select Theme:")
    dpg.add_combo(["Default", "Fallout"], default_value="Default", callback=switch_theme)

# fallout_theme
with dpg.theme(tag="fallout_theme"):
    with dpg.theme_component():
        # Button colors
        dpg.add_theme_color(dpg.mvThemeCol_Button, (59, 63, 68, 255))          # Muted green
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (50, 55, 50, 255))    # Darker green when clicked
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (78, 83, 63, 255))   # Lighter green when hovered
        
        # Text and other element colors
        dpg.add_theme_color(dpg.mvThemeCol_Text, (216, 169, 91, 255))          # Amber for text
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30, 255))         # Dark gray for child background
        dpg.add_theme_color(dpg.mvThemeCol_Border, (216, 169, 91, 255))        # Amber for borders
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (172, 174, 197, 255)) # Light gray for hovered frames

        # Styles (similar to the base theme)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 14)


with dpg.theme(tag="base"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_Button, (130, 142, 250))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (137, 142, 255, 95))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (137, 142, 255))
		dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
		dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
		dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
		dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
		dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize,0)
		dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,10,14)
		dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25))
		dpg.add_theme_color(dpg.mvThemeCol_Border, (0,0,0,0))
		dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0,0,0,0))
		dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (130, 142, 250))
		dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (221, 166, 185))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (172, 174, 197))

with dpg.theme(tag="slider_thin"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250,99))
		dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="slider"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250,99))
		dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="songs"):
	with dpg.theme_component():
		dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
		dpg.add_theme_color(dpg.mvThemeCol_Button, (89, 89, 144,40))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0,0,0,0))

with dpg.font_registry():
	monobold = dpg.add_font("fonts/MonoLisa-Bold.ttf", 12)
	head = dpg.add_font("fonts/MonoLisa-Bold.ttf", 15)

with dpg.window(tag="main",label="window title"):
	with dpg.child_window(autosize_x=True,height=45,no_scrollbar=True):
		dpg.add_text(f"Now Playing : ",tag="csong")
	dpg.add_spacer(height=2)

	with dpg.group(horizontal=True):
		with dpg.child_window(width=200,tag="sidebar"):
			dpg.add_text("Rainy Musicart",color=(137, 142, 255))
			dpg.add_text("Build by Dev")
			dpg.add_spacer(height=2)
			dpg.add_button(label="Enjoy!",width=-1,height=23,callback=lambda:webbrowser.open(url=""))
			dpg.add_spacer(height=5)
			dpg.add_separator()
			dpg.add_spacer(height=5)
			dpg.add_button(label="Add File",width=-1,height=28,callback=add_files)
			dpg.add_button(label="Add Folder",width=-1,height=28,callback=add_folder)
			dpg.add_button(label="Remove All Songs",width=-1,height=28,callback=removeall)
			dpg.add_spacer(height=5)
			dpg.add_separator()
			dpg.add_spacer(height=5)
			dpg.add_text(f"State: {state}",tag="cstate")
			dpg.add_spacer(height=5)
			dpg.add_separator()

		with dpg.child_window(autosize_x=True,border=False):
			with dpg.child_window(autosize_x=True,height=80,no_scrollbar=True):
				with dpg.group(horizontal=True):
					with dpg.group(horizontal=True):
						dpg.add_button(label="Play",width=65,height=30,tag="play",callback=play_pause)
						dpg.add_button(label="Pre",width=65,height=30,show=True,tag="pre",callback=pre)
						dpg.add_button(label="Next",tag="next",show=True,callback=next,width=65,height=30)
						dpg.add_button(label="Stop",callback=stop,width=65,height=30)
					dpg.add_slider_float(tag="volume", width=120,height=15,pos=(10,59),format="%.0f%.0%",default_value=_DEFAULT_MUSIC_VOLUME * 100,callback=update_volume)
					dpg.add_slider_float(tag="pos",width=-1,pos=(140,59),format="")

			with dpg.child_window(autosize_x=True,delay_search=True):
				with dpg.group(horizontal=True,tag="query"):
					dpg.add_input_text(hint="Search for a song",width=-1,callback=search)
				dpg.add_spacer(height=5)
				with dpg.child_window(autosize_x=True,delay_search=True,tag="list"):
					load_database()

	dpg.bind_item_theme("volume","slider_thin")
	dpg.bind_item_theme("pos","slider")
	dpg.bind_item_theme("list","songs")

dpg.bind_theme("base")
dpg.bind_font(monobold)

def safe_exit():
	pygame.mixer.music.stop()
	pygame.quit()

atexit.register(safe_exit)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main",True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()