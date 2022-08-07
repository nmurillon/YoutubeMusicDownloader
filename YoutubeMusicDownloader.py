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
            'direct_link': self.get_list_from_one,
            'playlist': self.get_list_from_playlist,
            'file': self.get_list_from_file
        }

        if type not in self.ALLOWED_TYPE.keys():
            raise ValueError(f'\033[1;31m{type} is unsupported\nAllowed types are {self.ALLOWED_TYPE.keys()}\033[0m')

        self.format = format
        self.type = type
        self.output_path = output_path
        
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

    # def download_from_playlist(self, playlist_link: str) -> None:
    #     playlist = Playlist(playlist_link)
    #     try:
    #         for url in playlist.video_urls:
    #             self.download_one(url)
    #     except Exception as e:
    #         print(e) 

    # def download_from_file(self, filepath: str):
    #     with open(filepath, 'r') as file:
    #         try:
    #             for url in file.readlines():
    #                 self.download_one(url)
    #         except Exception as e:
    #             print(e) 
    
    def download(self, link: str):
        '''used with cli'''
        self.is_interrupted=False
        if not isdir(self.output_path):
            os.mkdir(self.output_path)
        print(f'Going to save the audio in {self.output_path}')
        
        l = self.get_list(link)
        for url in l:
            self.download_one(url)
    
    def get_list_from_one(self, link):
        return [link]

    def get_list_from_playlist(self, link):
        playlist = Playlist(link)
        return playlist.video_urls

    def get_list_from_file(self, filepath):
        with open(filepath, 'r') as file:
            return file.readlines()

    def get_list(self, link):
        '''use for gui'''
        return self.ALLOWED_TYPE[self.type](link)