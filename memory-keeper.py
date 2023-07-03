import csv
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import shutil
from PIL import Image, ImageTk
import threading
import subprocess

memory_entry = None
description_entry = None
view_memories_window = None

def add_memory():
    global memory_entry, description_entry

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory = memory_entry.get()
    description = description_entry.get("1.0", "end-1c")

    filetypes = (("Video files", "*.mp4"), ("Image files", "*.jpg;*.jpeg;*.png"),
                 ("Audio files", "*.wav;*.mp3"), ("All files", "*.*"))
    file_path = filedialog.askopenfilename(filetypes=filetypes)

    if file_path:
        destination_folder = "memories/"
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        file_name = os.path.basename(file_path)
        new_file_path = os.path.join(destination_folder, file_name)

        try:
            shutil.copy(file_path, new_file_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        with open('relationship_memories.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, memory, description, new_file_path])

        messagebox.showinfo("Success", "Memory added successfully!")
    else:
        messagebox.showwarning("Warning", "No file selected!")

    memory_entry.delete(0, END)
    description_entry.delete("1.0", END)

    if view_memories_window:
        view_memories_window.destroy()

    threading.Thread(target=view_memories).start()

def view_memories():
    global view_memories_window

    view_memories_window = Toplevel()
    view_memories_window.title("View Memories")

    scrollbar = Scrollbar(view_memories_window)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas = Canvas(view_memories_window, yscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    memories_inner_frame = Frame(canvas)

    with open('relationship_memories.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 4:
                continue

            date = row[0]
            memory = row[1]
            description = row[2]
            file_path = row[3]

            memory_label = Label(memories_inner_frame, text=f"[{date}] {memory}")
            memory_label.pack()

            description_text = Text(memories_inner_frame, height=3, width=50)
            description_text.insert("1.0", description)
            description_text.config(state=DISABLED)
            description_text.pack()

            file_extension = os.path.splitext(file_path)[-1].lower()
            if file_extension == ".jpg" or file_extension == ".jpeg" or file_extension == ".png":
                image = Image.open(file_path)
                photo = ImageTk.PhotoImage(image)
                image_label = Label(memories_inner_frame, image=photo)
                image_label.image = photo
                image_label.pack()
            elif file_extension == ".mp4":
                play_button = Button(memories_inner_frame, text="Play Video", command=lambda f=file_path: play_video(f))
                play_button.pack()
            elif file_extension == ".wav" or file_extension == ".mp3":
                play_button = Button(memories_inner_frame, text="Play Audio", command=lambda f=file_path: play_audio(f))
                play_button.pack()
            else:
                file_label = Label(memories_inner_frame, text="Unsupported file type")
                file_label.pack()

            separator = Frame(memories_inner_frame, height=2, bd=1, relief=SUNKEN)
            separator.pack(fill=X, padx=5, pady=5)

    memories_inner_frame.update_idletasks()
    canvas.create_window(0, 0, anchor=NW, window=memories_inner_frame)
    canvas.configure(scrollregion=canvas.bbox("all"))
    scrollbar.config(command=canvas.yview)

def play_audio(file_path):
    global audio_thread
    messagebox.showinfo("Info", f"Playing audio: {file_path}")

    def play():
        subprocess.call(['start', '', file_path], shell=True)

    audio_thread = threading.Thread(target=play)
    audio_thread.start()

def play_video(file_path):
    global video_thread
    messagebox.showinfo("Info", f"Playing video: {file_path}")

    def play():
        subprocess.call(['start', '', file_path], shell=True)

    video_thread = threading.Thread(target=play)
    video_thread.start()

def main():
    global memory_entry, description_entry

    root = Tk()
    root.title("Memory Keeper")

    memory_label = Label(root, text="Memory:")
    memory_label.pack()

    memory_entry = Entry(root, width=50)
    memory_entry.pack()

    description_label = Label(root, text="Description:")
    description_label.pack()

    description_entry = Text(root, height=5, width=50)
    description_entry.pack()

    add_button = Button(root, text="Add Memory", command=add_memory)
    add_button.pack()

    view_button = Button(root, text="View Memories", command=view_memories)
    view_button.pack()

    root.mainloop()

if __name__ == '__main__':
    main()
