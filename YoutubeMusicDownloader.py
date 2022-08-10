from genericpath import isdir
import shutil
import sys
import os
from pytube import YouTube, Playlist, Stream
from pytube.cli import on_progress

DOCUMENT_PATH = f'C:/Users/{os.getlogin()}/Documents'
YOUTUBE_EXAMPLE = 'https://www.youtube.com/watch?v=JRIfWazqIQ8'
DEFAULT_DOWNLOAD_PATH = f'C:/Users/{os.getlogin()}/Documents/YoutubeMusicDownloads'
DEFAULT_TYPE = 'direct_link'
DEFAULT_FORMAT = 'mp4'
ALLOWED_TYPES = [
    'direct_link',
    'playlist',
    'file'
]

class YoutubeMusicDownloader:
    def __init__(self, format: str = DEFAULT_FORMAT, type: str = DEFAULT_TYPE, output_path: str = DEFAULT_DOWNLOAD_PATH, hide_progress_bar=False) -> None:
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
        self.hide_progress_bar = hide_progress_bar

    def on_progress(self, stream: Stream, chunk: bytes, bytes_remaining: int):
        '''Display a progress bar if self.hide_progress_bar is False'''
        if not self.hide_progress_bar:
            on_progress(stream, chunk, bytes_remaining)
        
    def on_download_complete(self, _stream: Stream, _filepath: str):
        '''Display a message to tell the download of an audio is complete'''
        print('\t\033[1;32mDownload complete\033[0m\t')

    def download_one(self, url: str) -> None:
        '''Download an audio from Youtube video'''
        try:
            yt = YouTube(url, on_progress_callback=self.on_progress, on_complete_callback=self.on_download_complete)
            audio = yt.streams.get_audio_only(self.format)
            if not audio:
                print(f"\033[1;31m{self.format} is not a supported format for '{url}'\033[0m")
                return
            
            print(f'Downloading {audio.title}...')
            audio.download(self.output_path)
        except Exception:
            print(f'\033[1;31mThe link provided ({url}) is not a youtube video\033[0m')

    def download(self, link: str):
        '''used with cli'''
        if not isdir(self.output_path):
            os.mkdir(self.output_path)
        print(f'Going to save the audio in {self.output_path}')
        
        l = self.get_list(link)
        for url in l:
            self.download_one(url)
    
    def get_list_from_one(self, link):
        '''Return an array containing the given link'''
        return [link]

    def get_list_from_playlist(self, link):
        '''Return an array containing all the video urls from a playlist'''
        try:
            playlist = Playlist(link)
            return playlist.video_urls
        except Exception:
            print(f'\033[1;31mThe link you provided ({link}) is not a youtube playlist !\033[0m')
            return []

    def get_list_from_file(self, filepath):
        '''Return an array of urls contained in the given file'''
        try:
            with open(filepath, 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            print(f'\033[1;31mThe file {filepath} does not exist !\033[0m')
            return []

    def get_list(self, link):
        '''Return the array of video urls depending on the resource type (file, playlist or video)'''
        return self.ALLOWED_TYPE.get(self.type, lambda _link: [])(link)