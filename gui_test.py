#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
from tkinter import scrolledtext
import os
import re
import ffmpeg

def make_clip(in_file:str, t1_name:str, t2_name:str, t1_score:int, t2_score:int, t1_color:str, t2_color:str, out_file:str, t1_logo:str=None, t2_logo:str=None, t0:int=None, tf:int=None):
    # get dimensions of video
    probe = ffmpeg.probe(in_file)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])

    # generate spacing constants for overlays
    dim = int(width/40)
    team_dim = f'{dim}x{dim}'
    spacing = int(width/400)
    sw=2*spacing+5*dim # scoreboard width
    sh=2*spacing+dim # scoreboard height

    # grab video stream and audio stream for use in clipping and filtering
    stream = ffmpeg.input(in_file)
    audio = stream.audio

    # trim the clip to the specified size
    if (t0 != None and tf != None):
        audio = audio.filter('atrim', start=t0, end=tf)
        stream = stream.video.trim(start=t0, end=tf)

    # add the scoreboard overlay
    if (t1_logo and t2_logo):
        # scale the team logos
        t1 = ffmpeg.input(t1_logo).filter('scale', team_dim)
        t2 = ffmpeg.input(t2_logo).filter('scale', team_dim) 
        stream = ffmpeg.overlay(stream, t1, x=spacing, y=spacing)
        stream = ffmpeg.overlay(stream, t2, x=(sw-spacing-dim), y=spacing)
    stream = ffmpeg.drawbox(stream, x=0, y=0, width=(sw), height=(sh), color='black', thickness=spacing)
    stream = ffmpeg.drawbox(stream, x=(spacing+dim+dim/3), y=(spacing+dim/3+spacing), width=dim/3, height=dim/3, color=t1_color, thickness=dim/3)
    stream = ffmpeg.drawbox(stream, x=(spacing+3*dim+dim/3), y=(spacing+dim/3+spacing), width=dim/3, height=dim/3, color=t2_color, thickness=dim/3)
    stream = ffmpeg.drawtext(stream, text=f'{t1_score} - {t2_score}', x=f'({sw}-text_w)/2', y=f'({sh}-text_h)/2', fontsize=(dim/2))
    stream = ffmpeg.drawtext(stream, text=t1_name, x=1.5*spacing+dim, y=1.5*spacing, fontsize=(dim/3))
    stream = ffmpeg.drawtext(stream, text=t2_name, x=f'{sw-1.5*spacing-dim}-text_w', y=1.5*spacing, fontsize=(dim/3))
    
    # output
    stream = ffmpeg.output(stream, audio, out_file)
    # stream = ffmpeg.output(stream, out_file)

    ffmpeg.run(stream)

# === TK WINDOW INITIATION === #
root = Tk()
root.title('Clip Compiler')

# === TEAM INFO SETUP === #
# Overall frame
team_info_frame = ttk.LabelFrame(root, text="Team Info")
team_info_frame.pack()

# Vars used by widgets in frame
logo_select = IntVar()
t1_name = StringVar()
t2_name = StringVar()
t1_color = StringVar()
t2_color = StringVar()
t1_logo_fp = StringVar()
t2_logo_fp = StringVar()
t1_logo_fullpath = StringVar()
t2_logo_fullpath = StringVar()

img_types = ('images', ['*.jpg', '*.JPG', '*.png', '*.PNG', '*.gif', '*.GIF'])

# Team name entry frames
team1frame = ttk.Frame(team_info_frame)
team1frame.pack()
T1 = Label(team1frame, text="Team 1: ")
T1.pack( side = LEFT)
E1 = Entry(team1frame, width=5, textvariable=t1_name)
E1.pack(side = RIGHT)
# ---
team2frame = ttk.Frame(team_info_frame)
team2frame.pack()
T2 = Label(team2frame, text="Team 2: ")
T2.pack( side = LEFT)
E2 = Entry(team2frame, width=5, textvariable=t2_name)
E2.pack(side = RIGHT)

# Commands for widget actions in frame
def disp_logo_select():
    if logo_select.get():
        # color_label_frame.pack_forget()
        # color_frame.pack_forget()

        sel_buttons_frame.pack()
        logo_text_frame.pack()
    else:
        # color_label_frame.pack()
        # color_frame.pack()

        sel_buttons_frame.pack_forget()
        logo_text_frame.pack_forget()
# ---
def t1logo_select():
    file = filedialog.askopenfilename(filetypes=[img_types])
    t1_logo_fullpath.set(file)
    t1_logo_fp.set(os.path.basename(file))

def t2logo_select():
    file = filedialog.askopenfilename(filetypes=[img_types])
    t2_logo_fullpath.set(file)
    t2_logo_fp.set(os.path.basename(file))

# Setting up logo selection frame, with checkbox to collapse/expand
logo_select_frame = ttk.Frame(team_info_frame)
logo_select_frame.pack()
logo_select_checkbox = ttk.Checkbutton(logo_select_frame, text='Use Team Logos?', variable = logo_select, command=disp_logo_select)
logo_select_checkbox.pack(side=TOP)

# Color select frame
color_label_frame = ttk.Frame(logo_select_frame)
color_frame = ttk.Frame(logo_select_frame)
color_label_frame.pack()
color_frame.pack()

# Set up the frame with dropdown menus
t1_color_label = ttk.Label(color_label_frame, text='Team 1 Color:')
t2_color_label = ttk.Label(color_label_frame, text='Team 2 Color:')
t1_color_label.pack(side=LEFT, padx=3)
t2_color_label.pack(side=LEFT, padx=3)

color_options = ['Select', 'White', 'Black', 'Gray', 'Red', 'Blue', 'Green', 'Yellow', 'Pink', 'Purple', 'Orange']
t1_color_select = ttk.OptionMenu(color_frame, t1_color, *color_options)
t2_color_select = ttk.OptionMenu(color_frame, t2_color, *color_options)
t1_color_select.pack(side=LEFT, padx=3)
t2_color_select.pack(side=LEFT, padx=3)

# Set up the frames with buttons to select logo file, and logo file text outputs.
sel_buttons_frame = ttk.Frame(logo_select_frame)
logo_text_frame = ttk.Frame(logo_select_frame)

# Add buttons to browse file and then populate the labels
ttk.Button(sel_buttons_frame, text="Select Team 1 Logo", command=t1logo_select).pack(side = LEFT)
ttk.Button(sel_buttons_frame, text="Select Team 2 Logo", command=t2logo_select).pack(side = RIGHT)
team1logo = Label(logo_text_frame, textvariable=t1_logo_fp, width=20).pack(side=LEFT)
team2logo = Label(logo_text_frame, textvariable=t2_logo_fp, width=20).pack(side=RIGHT)

# === CLIPS FRAME === #
# Overall frame
clips_frame = ttk.LabelFrame(root, text='Clips')
clips_frame.pack()

# Vars used by widgets
t1_score_var = StringVar()
t2_score_var = StringVar()
start_var = StringVar()
end_var = StringVar()

# Functions for widget commands
def open_file():
    vid_types = [('mp4', ['*.mp4', '*.MP4']),('mov', ['*.mov', '*.MOV'])]
    files = filedialog.askopenfilenames(filetypes=vid_types)
    for file in files:
        file_name = os.path.basename(file)
        clip_list.insert(parent='', index='end', values=(file, file_name,'','','',''))

def clip_duplicate():
    sel = clip_list.selection()
    if sel:
        i = clip_list.item(sel)
        clip_data = i['values']
        clip_list.insert(parent='', index=clip_list.index(sel)+1, values=clip_data)

def clip_delete():
    sel = clip_list.selection()
    if sel:
        clip_list.delete(sel)

def clip_up():
    sel = clip_list.selection()
    if sel:
        clip_list.move(sel, clip_list.parent(sel), clip_list.index(sel)-1)

def clip_down():
    sel = clip_list.selection()
    if sel:
        clip_list.move(sel, clip_list.parent(sel), clip_list.index(sel)+1)

def update_clip():
    sel = clip_list.selection()
    if sel:      
        curr = clip_list.item(sel)
        iid = curr['values'][0]
        path = curr['values'][1]
        t1s = t1_score_var.get()
        t2s = t2_score_var.get()
        s = start_var.get()
        e = end_var.get()
        clip_list.item(sel, values=(iid,path,t1s,t2s,s,e))

def is_dig(P):
    return (str.isdigit(P) or P == "" or P==":" or P==".")
vcmd = (root.register(is_dig))

def select(_):
    sel = clip_list.selection()
    if sel:
        i = clip_list.item(sel)
        clip_data = i['values']
        t1_score_var.set(clip_data[2])
        t2_score_var.set(clip_data[3])
        start_var.set(clip_data[4])
        end_var.set(clip_data[5])

# Create video selection buttons
ttk.Button(clips_frame, text="Select Videos", command=open_file).pack()

# Set up Treeview to hold list of clips
clip_list = ttk.Treeview(clips_frame, selectmode='browse')
clip_list['columns'] = ("Path", "Input Clip", "T1 Score", "T2 Score", "Start", "End")
clip_list['displaycolumns'] = ("Input Clip", "T1 Score", "T2 Score", "Start", "End")
clip_list.column("#0", width=0, stretch=NO)
clip_list.column("Input Clip", anchor=W, width=100)
clip_list.column("T1 Score", anchor=CENTER, width=100)
clip_list.column("T2 Score", anchor=CENTER, width=100)
clip_list.column("Start", anchor=CENTER, width=100)
clip_list.column("End", anchor=CENTER, width=100)
clip_list.heading("#0", text="", anchor=W)
clip_list.heading("Input Clip", text="Input Clip", anchor=W)
clip_list.heading("T1 Score", text="T1 Score", anchor=CENTER)
clip_list.heading("T2 Score", text="T2 Score", anchor=CENTER)
clip_list.heading("Start", text="Start", anchor=CENTER)
clip_list.heading("End", text="End", anchor=CENTER)
clip_list.bind('<<TreeviewSelect>>', select)
clip_list.pack()

# Set up frame to hold clip data entry fields/buttons
clip_field_frame = ttk.Frame(clips_frame)
clip_field_frame.pack()

# Frame to hold items for moving/duplicating/deleting clips
nav_frame = ttk.Frame(clip_field_frame)
nav_frame.pack(side=LEFT, padx=2)
nav_frame_left=ttk.Frame(nav_frame)
nav_frame_left.pack(side=LEFT, padx=2)
nav_frame_right=ttk.Frame(nav_frame)
nav_frame_right.pack(side=RIGHT, padx=2)
dupe_button = ttk.Button(nav_frame_left, text="Duplicate", command=clip_duplicate)
del_button = ttk.Button(nav_frame_left,  text=" Delete  ", command=clip_delete)
up_button = ttk.Button(nav_frame_right, text=" Clip Up ", command=clip_up)
down_button = ttk.Button(nav_frame_right, text="Clip Down", command=clip_down)
dupe_button.pack()
del_button.pack()
up_button.pack()
down_button.pack()

# Frame to hold entries for the score for a given clip
score_frame = ttk.Frame(clip_field_frame)
score_frame.pack(side=LEFT, padx=2)
score_label = Label(score_frame, text="Score").pack()
score_entry_frame = ttk.Frame(score_frame)
score_entry_frame.pack(side=BOTTOM)
t1_score_entry = Entry(score_entry_frame, textvariable=t1_score_var, width=2, validate='key', validatecommand=(vcmd, '%S')).pack(side=LEFT)
score_dash = Label(score_entry_frame, text=" - ").pack(side=LEFT)
t2_score_entry = Entry(score_entry_frame, textvariable=t2_score_var, width=2, validate='key', validatecommand=(vcmd, '%S')).pack(side=LEFT)

# Frames for entering start/end times of clips
start_frame = ttk.Frame(clip_field_frame)
start_frame.pack(side=LEFT, padx=2)
start_label = Label(start_frame, text="Start: ").pack()
start_entry = Entry(start_frame, textvariable=start_var, width=8, validate='key', validatecommand=(vcmd, '%S')).pack()
end_frame = ttk.Frame(clip_field_frame)
end_frame.pack(side=LEFT, padx=2)
end_label = Label(end_frame, text="End: ").pack()
end_entry = Entry(end_frame, textvariable=end_var, width=8, validate='key', validatecommand=(vcmd, '%S')).pack()

# Frame for the update button
update_frame=ttk.Frame(clip_field_frame)
update_frame.pack(side=LEFT,padx=2)
update_button = ttk.Button(clip_field_frame, text='Update', command=update_clip)
update_button.pack(side=BOTTOM)




# Returns true ONLY if the text is a valid time format for input to FFMPEG
def valid_time(s:str): 
    return (re.fullmatch(r'([0-9]{1,2}:[0-9]{1,2}(\.[0-9]+)?)|([0-9]+(\.[0-9]+)?|\.[0-9]+)', s) != None)

def compile_video():
    # Pre-compile cleanup
    os.system("rm -rf ./tmp")
    os.mkdir("./tmp")

    compile_errors.configure(state='normal')
    compile_errors.delete("1.0", "end")
    # compile_errors.configure(state='disabled')

    compile = True
    
    # Check that teams are named
    if (t1_name.get() == ""): 
        compile_errors.insert(INSERT, "ERROR: TEAM1 NEEDS NAME\n")
        compile = False
    if (t2_name.get() == ""):
        compile_errors.insert(INSERT, "ERROR: TEAM2 NEEDS NAME\n")
        compile = False

    # Check that teams are assigned color
    if (t1_color.get() == "Select"):
        compile_errors.insert(INSERT, "ERROR: TEAM1 NEEDS COLOR\n")
        compile = False
    if (t2_color.get() == "Select"):
        compile_errors.insert(INSERT, "ERROR: TEAM2 NEEDS COLOR\n")
        compile = False
    
    # Check that neither team or both teams have a logo
    a = t1_logo_fullpath.get()
    b = t2_logo_fullpath.get()
    if (a and (not b)) or (b and (not a)):
        compile_errors.insert(INSERT, "ERROR: BOTH OR NEITHER TEAMS NEED LOGO\n")
        compile = False

    # Check that logos exist
    if (a and not os.path.exists(a)):
        compile_errors.insert(INSERT, f"ERROR: LOGO {a} DOES NOT EXIST\n")
        compile = False
    if (b and not os.path.exists(b)):
        compile_errors.insert(INSERT, f"ERROR: LOGO {b} DOES NOT EXIST\n")
        compile = False

    # Grab all the clips and create a list of their data
    iids = clip_list.get_children()

    # Check that there are clips
    if (not iids):
        compile_errors.insert(INSERT, "ERROR: NO CLIPS SELECTED\n")
        compile = False
    
    # Create a list of the data from each clip
    datas = []
    for iid in iids:
        item = clip_list.item(iid)
        datas.append(item['values'])

    # List to hold items that will be sent to clip create function    
    cleaned_data = []
    for data in datas:
        # Grab datapoints from clip entry
        file_path = data[0]
        clip_name = data[1]
        t1score = data[2]
        t2score = data[3]
        t0 = data[4]
        tf = data[5]
        print(data)

        # Check that clip exists
        if not os.path.exists(file_path):
            compile_errors.insert(INSERT, f"<{clip_name}> ERROR: CLIP DOESN'T EXIST\n")
            compile = False
            continue

        probe = ffmpeg.probe(file_path)
        video_data = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        duration = float(video_data['duration'])

        # Grab start/end times for the clip
        if (t0 != '' and tf != ''):
            # Check that timestamps are valid time formats
            if not valid_time(str(t0)):
                compile_errors.insert(INSERT, f"<{clip_name}> ERROR: {t0} IS INVALID TIME FORMAT\n")
                compile = False
                continue
            if not valid_time(str(tf)):
                compile_errors.insert(INSERT, f"<{clip_name}> ERROR: {tf} IS INVALID TIME FORMAT\n")
                compile = False
                continue
            
            if (isinstance(t0, str)):
                if ':' in t0:
                    t = t0.split(':')
                    t0 = (60.0*float(t[0])) + float(t[1])
            if (isinstance(tf, str)):
                if ':' in tf:
                    t = tf.split(':')
                    tf = (60.0*float(t[0])) + float(t[1])
            

            # Check that clip end is after the clip start
            if (float(tf) < float(t0)): 
                compile_errors.insert(INSERT, f"<{clip_name}> ERROR: CLIP START {t0} FOLLOWS CLIP END {tf}\n")
                compile = False
                continue
            
            # print(duration)
            # Check that clip start and end are within duration
            if (float(t0) > duration or float(tf) > duration):
                compile_errors.insert(INSERT, f"<{clip_name}> ERROR: ({t0},{tf}) is outside of duration {duration}s\n")
                compile = False
                continue
        elif (t0 and (tf == "")) or (tf and (t0 == "")):
            compile_errors.insert(INSERT, f"<{clip_name}> ERROR: ONLY ONE CLIP TIME ADDED\n")
            compile = False
            continue

        # Check that each team has a score
        if (t1score == "" or t2score == ""):
            compile_errors.insert(INSERT, f"<{clip_name}> ERROR: SCORE NOT RECORDED\n")
            compile = False
            continue
            

        cleaned_data.append([file_path, 
                            t1_name.get(), t2_name.get(), 
                            t1score, t2score, 
                            t1_color.get(), t2_color.get(),
                            t1_logo_fullpath.get(), t2_logo_fullpath.get(),
                            t0, tf
                            ])
    if compile:
        i = 1
        for c in cleaned_data:
            if c[7] == "": c[7] = None
            if c[8] == "": c[8] = None
            if c[9] == "": c[9] = None
            if c[10] == "": c[10] = None
            
            tmp_name = f'./tmp/{i}.mov'
            vid_name = f'{i}.mov'

            make_clip(c[0], c[1], c[2], c[3], c[4], c[5], c[6], tmp_name, c[7], c[8], c[9], c[10])
            os.system(f'echo file {vid_name} >> tmp/files.txt')
            i += 1
    output_file = f'{t1_name.get()}vs{t2_name.get()}.mov'
    os.system(f'ffmpeg -f concat -i tmp/files.txt -codec copy {output_file}')
    # os.system("rm -rf ./tmp")


# Set up frame for compiling        
compile_frame = ttk.Frame(root)
compile_frame.pack()

# Compile button and action
compile_button = ttk.Button(compile_frame, text='Compile Video', command=compile_video)
compile_button.pack(pady=10)

# Compile output dialog
compile_errors = scrolledtext.ScrolledText(compile_frame, width=40, height=10)
compile_errors.insert(INSERT, "")
compile_errors.configure(state='disabled')
compile_errors.pack(pady=5)

root.mainloop()