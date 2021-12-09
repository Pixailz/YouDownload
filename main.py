#!/usr/bin/env python3
#coding:utf-8

#
# HEADER
def installAndImportModule(package):
    """ Check if module if present and install it
        then finally import the module
    """

    import sys
    import importlib
    import subprocess

    try:
        importlib.import_module(package)

    except ModuleNotFoundError:
        print("module not found installing it")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    finally:
        globals()[package] = importlib.import_module(package)

def installModule(package):
    """ Check if module if present and install it
    """

    import sys
    import importlib
    import subprocess

    try:
        importlib.import_module(package)

    except ModuleNotFoundError:
        print("module not found installing it")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

installModule("pytube")
installModule("pygame")

import contextlib

# import pygame without hello message spawning
with contextlib.redirect_stdout(None):
    from pygame import mixer

import argparse
import pytube
import time
import os
import re

 #
#

class RegexChecker():
    """
        return string instead of list
        https://stackoverflow.com/a/29331140
    """
    @staticmethod
    def getVideoID(link):
        """Find the id of a video from link"""
        return re.findall(r'v=([a-zA-Z0-9_-]{11})', link)[0]

    @staticmethod
    def getPlaylistID(link):
        """Find the id of playlist from link"""
        return re.findall(r'list=([a-zA-Z0-9_-]{34,41})', link)[0]

    @staticmethod
    def retrieveNumber(text):
        """retrieve only number from a string"""
        return re.findall(r'[0-9]+', text)[0]

class YoutubeDownloader():

    def __init__(self):
        self.regex = RegexChecker()

        self.parseArgs()

        if self.args.link_type == "single":
            for link in self.args.url:
                self.downloadSingle(self.regex.getVideoID(link))
            pass

        else:
            for link in self.args.url:
                self.downloadPlaylist(self.regex.getPlaylistID(link))
            pass

    def parseArgs(self):

        parser = argparse.ArgumentParser(
                 prog="YoutubeDownloader",
                 description="Download Youtube Link, in the best quality possible"
                 )

        parser.add_argument("download_type",
                            choices=["music", "video"],
                            help="%(prog)s download either music or video"
                            )

        parser.add_argument("link_type",
                            choices=["single", "playlist"],
                            help="specify if you wan't only one video or all the playlist"
                            )

        parser.add_argument("-o",
                            "--output",
                            required=False,
                            help="output folder for downloaded file, relative or path",
                            metavar="FOLDER",
                            default="out"
                            )

        parser.add_argument("-s",
                            "--sound",
                            action="store_true",
                            #default=False,
                            required=False,
                            help="play that mesmerising F1 sound on each convert complete"
                            )

        parser.add_argument("-u",
                            "--url",
                            nargs="+",
                            required=True,
                            help="url to download, accept multiple link",
                            metavar="LINK"
                            )

        parser.parse_args()

        self.args = parser.parse_args()

    def downloadVideo(self):
        if self.args.link_type == "single":
            out_path = self.args.output

        else:
            out_path = f"{self.args.output}/{self.output_playlist}"



        self.current_stream = self.singleYoutubeVideo.streams.filter(only_video=True).order_by("itag").last()
        filename_video = self.current_stream.default_filename.replace(".webm", ".mp4")
        self.current_stream.download(output_path=out_path, filename=filename_video)

        self.current_stream = self.singleYoutubeVideo.streams.filter(only_audio=True).order_by("itag").last()
        filename_audio = self.current_stream.default_filename.replace(".webm", ".mp3")
        self.current_stream.download(output_path=out_path, filename=filename_audio)

    def downloadMusicLowRes(self, out_path):
        self.current_stream = self.singleYoutubeVideo.streams.order_by("itag").last()
        self.current_stream.download(output_path=out_path)

    def downloadMusic(self):

        if self.args.link_type == "single":
            out_path = self.args.output

        else:
            out_path = f"{self.args.output}/{self.output_playlist}"

        self.current_stream = self.singleYoutubeVideo.streams.filter(only_audio=True).order_by("itag").last()

        try:
            self.current_stream.download(output_path=out_path)

        except AttributeError:
            self.lowResVid = True
            self.downloadMusicLowRes(out_path)

    def convertMusic(self):

        file_name = self.returnSafeFileName(self.current_stream.title)

        if self.args.link_type == "single":
            if not self.lowResVid:
                print(f"converting {file_name} ... ")

                os.system(f'.\\bin\\ffmpeg -loglevel error -hide_banner -y -i ".\\{self.args.output}\\{file_name}.webm" -c:a flac ".\\{self.args.output}\\{file_name}.flac"')

                os.remove(f".\\{self.args.output}\\{file_name}.webm")

            else:
                print(f"converting {file_name} ... ")

                os.system(f'.\\bin\\ffmpeg -loglevel error -hide_banner -y -i ".\\{self.args.output}\\{file_name}.mp4" -vn ".\\{self.args.output}\\{file_name}.mp3"')

                os.remove(f".\\{self.args.output}\\{file_name}.mp4")
        else:
            print(f"converting {file_name} ... ")

            os.system(f'.\\bin\\ffmpeg -loglevel error -hide_banner -y -i ".\\{self.args.output}\\{self.output_playlist}\\{file_name}.webm" -c:a flac ".\\{self.args.output}\\{self.output_playlist}\\{file_name}.flac"')

            os.remove(f".\\{self.args.output}\\{self.output_playlist}\\{file_name}.webm")

        if self.args.sound:
            self.playF1Sound()

    def convertVideo(self):
        file_name = self.returnSafeFileName(self.current_stream.title)

        if self.args.link_type == "single":

            os.system(f'.\\bin\\ffmpeg -loglevel warning -hide_banner -i ".\\{self.args.output}\\{file_name}.mp3" -i ".\\{self.args.output}\\{file_name}.mp4" -c copy ".\\{self.args.output}\\{file_name}.mkv"')

            os.remove(f".\\{self.args.output}\\{file_name}.mp3")
            os.remove(f".\\{self.args.output}\\{file_name}.mp4")

        else:
            os.system(f'.\\bin\\ffmpeg -loglevel warning -hide_banner -i ".\\{self.args.output}\\{self.output_playlist}\\{file_name}.mp3" -i ".\\{self.args.output}\\{self.output_playlist}\\{file_name}.mp4" -c copy ".\\{self.args.output}\\{self.output_playlist}\\{file_name}.mkv"')

            os.remove(f".\\{self.args.output}\\{self.output_playlist}\\{file_name}.mp3")
            os.remove(f".\\{self.args.output}\\{self.output_playlist}\\{file_name}.mp4")

    def downloadSingle(self, videoID):
        link = f"https://www.youtube.com/watch?v={videoID}"

        self.singleYoutubeVideo = pytube.YouTube(link, on_progress_callback=self.progressFunction, on_complete_callback=self.completeFunction)

        if self.args.download_type == "music":
            self.downloadMusic()
            self.convertMusic()
        else:
            self.downloadVideo()
            self.convertVideo()

    def downloadPlaylist(self, playlistID):
        link = f"https://www.youtube.com/playlist?list={playlistID}"

        print (link)

        YouTubePlaylist = pytube.Playlist(link)

        self.output_playlist = self.returnSafeFileName(YouTubePlaylist.title)

        for video_link in YouTubePlaylist.video_urls:
            self.downloadSingle(self.regex.getVideoID(video_link))

    @staticmethod
    def showProgressBar(bytes_received, filesize, filename, progressBarSize=10):
        done = int(progressBarSize * bytes_received / filesize)

        str_full = "█" * done
        str_void = " " * (progressBarSize - done)

        str_pourcentage = f"{int((bytes_received / filesize)*100)}%".ljust(4,)

        str_progress = f"|{str_full}{str_void}|{str_pourcentage} {filename}\r"

        print(f"{str_progress}", flush=True, end="")

    def progressFunction(self, stream, chunk, bytes_remaining):
        bytes_received = stream.filesize - bytes_remaining
        self.showProgressBar(bytes_received, stream.filesize, stream.default_filename.replace(".webm", ""))

    @staticmethod
    def completeFunction(stream, file_path, progressBarSize=10):
        str_full_progress = "█" * progressBarSize
        print(f"|{str_full_progress}|100%", stream.default_filename.replace(".webm", ""))

    @staticmethod
    def returnSafeFileName(t):
        return pytube.helpers.safe_filename(t)

    @staticmethod
    def playF1Sound():
        file_path = os.getcwd() + "\\f1.mp3"

        mixer.init()
        mixer.music.load(file_path)
        mixer.music.play()
        while mixer.music.get_busy():  # wait for music to finish playing
            time.sleep(.25)

if __name__ == "__main__":
    downloader = YoutubeDownloader()

