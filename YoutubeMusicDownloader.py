from genericpath import isdir
import shutil
import sys
import os
from pytube import YouTube, Playlist, Stream
from pytube.cli import on_progress

DEFAULT_DOWNLOAD_PATH = f'C:/Users/{os.getlogin()}/Documents/YoutubeMusicDownloads'
DEFAULT_TYPE = 'direct_link'
DEFAULT_FORMAT = 'mp4'
ALLOWED_TYPES = [
    'direct_link',
    'playlist',
    'file'
]

class YoutubeMusicDownloader:
    def __init__(self, format: str = DEFAULT_FORMAT, type: str = DEFAULT_TYPE, output_path: str = DEFAULT_DOWNLOAD_PATH) -> None:
        self.ALLOWED_TYPE = {
            'direct_link': self.download_one,
            'playlist': self.download_from_playlist,
            'file': self.download_from_file
        }

        if type not in self.ALLOWED_TYPE.keys():
            raise ValueError(f'\033[1;31m{type} is unsupported\nAllowed types are {self.ALLOWED_TYPE.keys()}\033[0m')

        self.format = format
        self.type = type
        self.output_path = output_path

    def display_progress_bar(self, bytes_received: int, filesize: int, scale: float = 0.35):
        columns = shutil.get_terminal_size().columns
        width = int(columns * scale)

        filled = int(width * bytes_received / float(filesize))
        percentage = round(100 * bytes_received/ float(filesize), 1)
        sys.stdout.write(f"[{filled * '█' + ' ' * (width - filled)}] {percentage}%")
        sys.stdout.flush()

    def on_progress(self, stream: Stream, _chunk: bytes, bytes_remaining: int) -> None:
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.display_progress_bar(bytes_received, filesize)

    def on_download_complete(self, _stream: Stream, _filepath: str):
        print('\t\033[1;32mDownload complete\033[0m\t')

    def download_one(self, url: str) -> None:
        '''Download an audio from Youtube video'''
        yt = YouTube(url, on_progress_callback=on_progress, on_complete_callback=self.on_download_complete)
        audio = yt.streams.get_audio_only(self.format)
        if not audio:
            raise ValueError(f'\033[1;31m{self.format} is not a supported format \033[0m')

        print(f'Downloading {audio.title}...')
        audio.download(self.output_path)

    def download_from_playlist(self, playlist_link: str) -> None:
        playlist = Playlist(playlist_link)
        for url in playlist.video_urls:
            self.download_one(url)

    def download_from_file(self, filepath: str):
        with open(filepath, 'r') as file:
            for url in file.readlines():
                self.download_one(url)
    
    def download(self, link: str):
        if not isdir(self.output_path):
            os.mkdir(self.output_path)
        print(f'Going to save the audio in {self.output_path}')
        
        self.ALLOWED_TYPE[self.type](link)