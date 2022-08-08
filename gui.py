import sys
from tkinter import END, INSERT, Text, Tk, ttk, filedialog, StringVar, LabelFrame
from tkinter import filedialog
from tkinter.messagebox import showinfo
import YoutubeMusicDownloader as ytdl

#TODO: rework toggle_buttons method
# add progress bar

class App(ttk.Frame):
    def __init__(self, parent: Tk, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.downloader = ytdl.YoutubeMusicDownloader(hide_progress_bar=True)
        self.is_downloading = False
        self.process = False
        self.is_interrupted = False
        
        ################################
        # Output panel
        self.format_var = StringVar(self, value=ytdl.DEFAULT_FORMAT)
        self.resource_var = StringVar(self, value=ytdl.YOUTUBE_EXAMPLE)
        
        self.output_frame = LabelFrame(self, text='Output information', padx=10, pady=10)
        self.output_frame.grid(column=0, row=0)

        self.output_path_var = StringVar(self.output_frame, value=ytdl.DEFAULT_DOWNLOAD_PATH)
        self.output_path_entry = ttk.Entry(self.output_frame, textvariable=self.output_path_var, width=50)
        self.output_path_entry.grid(column=0, row=0)

        self.output_path_button = ttk.Button(self.output_frame, text='browse', command=lambda: self.__set_path(self.output_path_var))
        self.output_path_button.grid(column=1, row=0, padx=5)

        self.format_entry = ttk.Entry(self.output_frame, textvariable=self.format_var, width=50)
        self.format_entry.grid(column=0, row=1)
        self.format_label = ttk.Label(self.output_frame, text='audio format')
        self.format_label.grid(column=1, row=1)

        ################################
        # Resource panel (link type)
        self.resource_frame = LabelFrame(self, text='Resource Link', padx=10, pady=10)
        self.resource_frame.grid(column=2, row=0)

        self.resource_entry = ttk.Entry(self.resource_frame, textvariable=self.resource_var, width=50)
        self.resource_entry.grid(column=0, row=1)

        self.resource_entry_button = ttk.Button(self.resource_frame, text='browse', command=lambda: self.__set_path(self.resource_var))
        self.resource_entry_button.grid(column=1, row=1, padx=5)

        self.types_var = StringVar(self.resource_frame, value=ytdl.DEFAULT_TYPE)
        self.types = ttk.Combobox(self.resource_frame, values=ytdl.ALLOWED_TYPES, textvariable=self.types_var, width=47)
        self.types.grid(column=0, row=2)

        self.types_label = ttk.Label(self.resource_frame, text='resource type')
        self.types_label.grid(column=1, row=2)

        ################################
        # Donwload/Stop buttons
        self.download_button = ttk.Button(self, text='download', command=self.start_download)
        self.download_button.grid(column=1, row =3, pady=20)
        
        self.stop_button = ttk.Button(self, text='stop', command=self.stop)
        self.stop_button.grid(column=1, row=3, pady=20)
        self.stop_button.grid_remove()

        ################################
        # Console output
        self.output = Text(self)#, width=int(0.75*self.winfo_width()))
        self.output.grid(column=0, row = 7, columnspan=5)
        sys.stdout.write = self.__redirector

        self.progress_bar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280,
        )
        self.progress_bar.grid(column=0, row=6, columnspan=5)
        self.progress_bar.grid_remove()
        self.progress_label = ttk.Label(self)
        self.progress_label.grid(column=1, row=6)
        self.progress_label.grid_remove()

        self.grid()

    def __browse_files(self):
        return filedialog.askdirectory(initialdir=ytdl.DOCUMENT_PATH)

    def __set_path(self, var: StringVar):
        var.set(self.__browse_files())

    def __update_progress_label(self):
        return f"Current Progress: {self.progress_bar['value']}%"

    def __redirector(self, input):
        self.output.insert(INSERT, input)

    def __toggle_buttons(self):
        if self.is_downloading:
            self.download_button.grid_remove()
            self.stop_button.grid()
        else:
            self.stop_button.grid_remove()
            self.download_button.grid()
        
    def start_download(self):
        self.is_downloading = True
        self.is_interrupted = False
        self.progress_bar.grid()
        self.progress_label.grid()
        self.progress_bar['value'] = 0.0
        self.output.delete(1.0, END)
        self.__toggle_buttons()
        self.get_values()
        urls = self.downloader.get_list(self.resource_var.get())
        self.download(urls, 0, len(urls))
        
    def download(self, urls, current, limit):
        if not self.is_interrupted and current < limit:
            self.root.update()
            self.downloader.download_one(urls[current])
            self.root.after(1000, lambda: self.download(urls, current + 1, limit))
            progress = round(100 * (current + 1) / limit, 1)
            self.progress_bar['value'] = progress
            self.progress_label['text'] = self.__update_progress_label()
        else:
            self.is_downloading = False
            self.is_interrupted = False
            self.__toggle_buttons()

    def stop(self):
        self.is_interrupted = True
        self.is_downloading = False
        self.__toggle_buttons()

    def get_values(self):
        self.downloader.output_path = self.output_path_var.get()
        self.downloader.format = self.format_var.get()
        self.downloader.type = self.types_var.get()

if __name__ == '__main__':
    root = Tk()
    root.title("Youtube MP3 Downloader")
    root.geometry('1080x720')
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    App(root, padding=10, width=root.winfo_width())
    root.mainloop()