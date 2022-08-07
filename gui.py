import sys
import threading
from tkinter import END, INSERT, Text, Tk, ttk, filedialog, StringVar
from tkinter import filedialog
from tkinter.messagebox import showinfo
import YoutubeMusicDownloader as ytdl

#TODO: rework toggle_buttons method
# add progress bar

class App(ttk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.downloader = ytdl.YoutubeMusicDownloader()
        self.is_downloading = False
        self.process = False
        self.event = threading.Event()
        
        self.output_path_var = StringVar(self, value=ytdl.DEFAULT_DOWNLOAD_PATH)
        self.format_var = StringVar(self, value=ytdl.DEFAULT_FORMAT)
        self.resource_var = StringVar(self)
        
        self.output_path_entry = ttk.Entry(self, textvariable=self.output_path_var, width=50)
        self.output_path_entry.grid(column=0, row=1)
        self.output_path_entry_label = ttk.Label(self, text='output folder')
        self.output_path_entry_label.grid(column=1, row=1)

        self.resource_entry = ttk.Entry(self, textvariable=self.resource_var, width=50)
        self.resource_entry.grid(column=2, row=1)

        self.format_entry = ttk.Entry(self, textvariable=self.format_var)
        self.format_entry.grid(column=0, row=2)
        self.format_label = ttk.Label(self, text='audio format')
        self.format_label.grid(column=1, row=1)

        self.types_var = StringVar(self, value=ytdl.DEFAULT_TYPE)
        self.types = ttk.Combobox(self, values=ytdl.ALLOWED_TYPES, textvariable=self.types_var)
        self.types.grid(column=0, row=5)
        self.types_label = ttk.Label(self, text='resource type')
        self.types_label.grid()

        self.download_button = ttk.Button(self, text='download', command=self.do_tasks)
        self.download_button.grid(column=0, row = 3)
        
        self.stop_button = ttk.Button(self, text='stop', command=self.stop)
        self.stop_button.grid(column=0, row=3)
        self.stop_button.grid_remove()

        self.output = Text(self)
        self.output.grid()
        sys.stdout.write = self.__redirector

        self.grid()

    def __redirector(self, input):
        self.output.insert(INSERT, input)

    def __toggle_buttons(self):
        if self.is_downloading:
            self.download_button.grid_remove()
            self.stop_button.grid()
        else:
            self.stop_button.grid_remove()
            self.download_button.grid()
        
    def download(self, event: threading.Event):
        '''overriding due to thread, had to load audio individually without YoutubeMusicDownloader download method'''
        self.is_downloading = True
        self.output.delete(1.0, END)
        self.__toggle_buttons()
        self.get_values()
        l = self.downloader.get_list(self.resource_var.get())
        for url in l:
            if event.is_set():
                break
            self.downloader.download_one(url)

        self.is_downloading = False
        self.__toggle_buttons()
        self.event.clear()
        #showinfo(message='Download complete!')

    def stop(self):
        self.event.set()
        # self.process.join()
        # self.process = None
        self.is_downloading = False
        self.__toggle_buttons()

    def get_values(self):
        self.downloader.output_path = self.output_path_var.get()
        self.downloader.format = self.format_var.get()
        self.downloader.type = self.types_var.get()

    def browse_files(self):
        filedialog.askdirectory
    
    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)

    def do_tasks(self):
        self.refresh()
        self.downloader.is_interrupted = False
        self.process = threading.Thread(target=self.download, args=(self.event,))
        self.process.start()

if __name__ == '__main__':
    root = Tk()
    root.title("Youtube MP3 Downloader")
    root.geometry('1080x720')
    App(root, padding=10)
    root.mainloop()
