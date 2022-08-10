###############################
# Project by N.MURILLON       #
# Youtube MP3 downloader      #
# Written with Python 3.10    #
###############################

import optparse
import YoutubeMusicDownloader as ytdl

# TODO: add possibility to dl from multiple inputs ?
def parse_options() -> tuple:
    parser = optparse.OptionParser()
    parser.add_option('-f', '--format', dest='format', help='audio format', default=ytdl.DEFAULT_FORMAT)
    parser.add_option('-t', '--type', dest='type', help='type of the input (direct_link, playlist or file for example)', default=ytdl.DEFAULT_TYPE)
    parser.add_option('-o', '--output-path', dest='output_path', help='destination folder', default=ytdl.DEFAULT_DOWNLOAD_PATH)
    
    return parser.parse_args()

def main():
    (options, values) = parse_options()
    if (not len(values)):
        raise ValueError('\033[1;31mYou must provide either the url of a playlist/video or the path to a file containing the urls\033[0m')

    downloader = ytdl.YoutubeMusicDownloader(options.format, options.type, options.output_path)
    downloader.download(values[0])

if __name__ == '__main__':
    main()