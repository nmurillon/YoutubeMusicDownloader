###############################
# Project by Nicolas MURILLON #
# Youtube MP3 downloader      #
# Written with Python 3.10    #
###############################

from genericpath import isdir
import sys
import os
import shutil
import optparse
from pytube import YouTube, Playlist, Stream

DEFAULT_DOWNLOAD_PATH = f'C:/Users/{os.getlogin()}/Documents/YoutubeMusicDownloads'
DEFAULT_TYPE = 'direct_link'
DEFAULT_FORMAT = 'mp4'

class YoutubeMusicDownloader:
    def __init__(self, format: str, type: str, output_path: str) -> None:
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

    def on_download_complete(self, _stream: Stream, filepath: str):
        print(' \033[1;32mDownload complete\033[0m')

    def download_one(self, url: str) -> None:
        '''Download an audio from Youtube video'''
        yt = YouTube(url, on_progress_callback=self.on_progress, on_complete_callback=self.on_download_complete)
        audio = yt.streams.get_audio_only(self.format)
        if not audio:
            raise ValueError(f'\033[1;31m{self.format} is not a supported format \033[0m')

        print(f'Downloading {audio.title}...')
        audio.download(self.output_path)

    def download_from_playlist(self, playlist_link: str) -> None:
        playlist = Playlist(playlist_link)
        for url in playlist.video_urls():
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

def parse_options() -> tuple:
    parser = optparse.OptionParser()
    parser.add_option('-f', '--format', dest='format', help='audio format', default=DEFAULT_FORMAT)
    parser.add_option('-t', '--type', dest='type', help='type of the input (direct_link, playlist or file for example)', default=DEFAULT_TYPE)
    parser.add_option('-o', '--output-path', dest='output_path', help='Destination folder', default=DEFAULT_DOWNLOAD_PATH)
    
    return parser.parse_args()

def main():
    (options, values) = parse_options()
    if (not len(values)):
        raise ValueError('\033[1;31mYou must provide either the url of a playlist/video or the path to a file containing the urls\033[0m')

    downloader = YoutubeMusicDownloader(options.format, options.type, options.output_path)
    downloader.download(values[0])

if __name__ == '__main__':
    main()