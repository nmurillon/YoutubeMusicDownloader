from genericpath import isdir
import sys
import os
import re
from tkinter import END, INSERT, Text, Tk, ttk, filedialog, StringVar, LabelFrame
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo
import YoutubeMusicDownloader as ytdl

#TODO: when cancelling download, ask if user wants to keep going from where he stopped
# But if something changed in between (resource link), just proceed to a new download

class App(ttk.Frame):
    def __init__(self, parent: Tk, *args, **kwargs) -> None:
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.line_count = 0
        self.downloader = ytdl.YoutubeMusicDownloader(hide_progress_bar=True)
        self.is_downloading = False
        self.process = False
        
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
        self.types = ttk.Combobox(self.resource_frame, values=ytdl.ALLOWED_TYPES, textvariable=self.types_var, width=47, state='readonly')
        self.types.grid(column=0, row=2)

        self.types_label = ttk.Label(self.resource_frame, text='resource type')
        self.types_label.grid(column=1, row=2)

        ################################
        # Donwload/Stop button
        self.action_button_text_var = StringVar(self, value='download')
        self.action_button = ttk.Button(self, textvariable=self.action_button_text_var, command=self.action)
        self.action_button.grid(column=1, row=3, pady=20)

        ################################
        # Console output
        self.console_frame = LabelFrame(self, border=0.0)
        self.console_frame.grid(column=0, row=4, columnspan=3)

        self.progress_bar = ttk.Progressbar(
            self.console_frame,
            orient='horizontal',
            mode='determinate',
            length=655,
        )
        self.progress_bar.grid(column=0, row=1, columnspan=3)
        self.progress_bar.grid_remove()
        self.progress_label = ttk.Label(self.console_frame)
        self.progress_label.grid(column=0, row=0)
        self.progress_label.grid_remove()

        self.output = Text(self.console_frame)
        self.output.grid(column=0, row = 2)
        sys.stdout.write = self.__redirector

        self.scroll_bar = ttk.Scrollbar(self.console_frame, command=self.output.yview)
        self.scroll_bar.grid(row=2, column=1, sticky='nsew')
        self.output['yscrollcommand'] = self.scroll_bar.set

        self.grid()

    def __browse_files(self):
        return filedialog.askdirectory(initialdir=ytdl.DOCUMENT_PATH)

    def __set_path(self, var: StringVar):
        var.set(self.__browse_files())

    def __update_progress_label(self):
        return f"Current Progress: {self.progress_bar['value']}%"

    def __redirector(self, input: str):
        '''Redirect stdout to TextBox'''
        if input != '\n':
            self.line_count += 1
        m = re.match('(\s*\033\[1;3([12])m).*(\033\[0m)\s*', input)
        if m is not None:
            s = input.replace(m[1], '').replace(m[3], '')
            if m[2] == '1':
                tag_name = 'error'
                foreground = 'red'
            else:
                tag_name = 'success'
                foreground = 'green'
            self.__color_text(s, tag_name, foreground)
        else:
            self.output.insert(INSERT, input)

    def __color_text(self, text, tag, color):
        '''Add a tag to color the text'''
        self.output.insert(INSERT, text)
        self.output.tag_add(tag, f'{float(self.line_count)}', f'{self.line_count}.{len(text)}')
        self.output.tag_configure(tag, foreground=color)
    
    def __check_output_dir(self, dirpath):
        '''Create the dir if it does not exist'''
        if not isdir(dirpath):
            os.mkdir(dirpath)

    def __reset_progress_bar(self):
        '''Display the progress bar if it was hidden and reset it's value'''
        self.progress_bar.grid()
        self.progress_label.grid()
        self.progress_bar['value'] = 0.0
        self.progress_label['text'] = self.__update_progress_label()

    def __reset_console_output(self):
        '''Reset the text in the '''
        self.output['state'] = 'normal'
        self.output.delete(1.0, END)
        self.line_count = 0

    def __toggle_action_button_label(self):
        '''Switch between download and cancel button'''
        self.action_button_text_var.set('cancel' if self.is_downloading else 'download')

    def action(self):
        '''Download audio or cancel a download'''
        if self.action_button_text_var.get() == 'download':
            self.start_download()
        else:
            self.stop()
        
    def start_download(self):
        '''start the download of the resource(s)'''
        if self.check_resource_value():
            self.is_downloading = True
            self.__reset_console_output()
            self.__reset_progress_bar()
            self.__toggle_action_button_label()
            self.__check_output_dir(self.output_path_var.get())
            self.get_values()
            urls = self.downloader.get_list(self.resource_var.get())
            self.download(urls, 0, len(urls))
        
    def download(self, urls, current, limit):
        '''Download audios'''
        if self.is_downloading and current < limit:
            self.root.update()
            self.downloader.download_one(urls[current])
            self.root.after(1000, lambda: self.download(urls, current + 1, limit))
            progress = round(100 * (current + 1) / limit, 1)
            self.progress_bar['value'] = progress
            self.progress_label['text'] = self.__update_progress_label()
        else:
            self.is_downloading = False
            self.output['state'] = 'disabled'
            self.__toggle_action_button_label()

    def stop(self):
        self.is_downloading = False
        self.__toggle_action_button_label()
        self.line_count += 1
        self.__color_text('Cancelling download...', 'cancel', 'orange')

    def get_values(self):
        self.downloader.output_path = self.output_path_var.get()
        self.downloader.format = self.format_var.get()
        self.downloader.type = self.types_var.get()
  
    def check_resource_value(self):
        resource = self.resource_var.get()
        if not resource:
            self.is_downloading = False
            showerror('Resource link error', 'The link to the resource can not be empty !')
            return False
        return True
        # elif self.types_var.get() in ['direct_link', 'playlist']:
        #     try:
        #         resource.index('youtube')
        #     except ValueError:
        #         showerror('Resource link error', 'The link to the resource must refer to a youtube resource !')

if __name__ == '__main__':
    root = Tk()
    root.title("Youtube MP3 Downloader")
    root.geometry('1080x720')
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    App(root, padding=10, width=root.winfo_width())
    root.mainloop()