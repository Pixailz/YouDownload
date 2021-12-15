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
        with contextlib.redirect_stdout(None):
            importlib.import_module(package)

    except ModuleNotFoundError:
        print("module not found installing it")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    finally:
        globals()[package] = importlib.import_module(package)

import contextlib
import subprocess
import argparse
import requests
import shutil
import time
import os
import re

installAndImportModule("zipfile")
installAndImportModule("pytube")
installAndImportModule("pygame")

 #
#


class PosixUtils():
    @staticmethod
    def _getPrefix():
        return "ffmpeg"

    @staticmethod
    def _getPath(base, file, folder=list()):

        if len(folder) < 1 :
            path = f"./{base}/{file}"

        else:
            path = f"./{base}"

            for f in folder:
                path += f"/{f}"

            path += f"/{file}"

        return path


class WindowsUtils():

    def __init__(self):
        self.regex = RegexChecker()
        self.ffmpegCheckInstallation()

    @staticmethod
    def convert_byte(number, rounded=False):

        """Byte converter"""

        number = int(number)

        if number > 1_000_000_000_000:
            multiplier = 8 / (8 * 1024 * 1024 * 1024 * 1024)
            measure_unit = "TiB"

        elif number > 1_000_000_000:
            multiplier = 8 / (8 * 1024 * 1024 * 1024)
            measure_unit = "GiB"

        elif number > 1_000_000:
            multiplier = 8 / (8 * 1024 * 1024)
            measure_unit = "MiB"

        elif number > 1_000:
            multiplier = 8 / (8 * 1024)
            measure_unit = "KiB"

        else:
            multiplier = 1
            measure_unit = f"B"

        if rounded:
            tmp_number = int(round(number * multiplier))
            converted = f"{tmp_number}{measure_unit}"

        else:
            tmp_number = round(number * multiplier, 2)
            converted = f"{tmp_number}{measure_unit}"

        return converted

    @staticmethod
    def download(link, file_path, title=""):

        """
        based on this:
        https://stackoverflow.com/a/21868231/7261056
        """

        with open(file_path, "wb") as f:

            # download of file
            response = requests.get(link, stream=True)
            # get length of ile in header
            total_length = response.headers.get("content-length")

            # if total length is not present in header
            if total_length is None:
                # write without progress bar :'(
                f.write(response.content)

            else:
                # cast in int of str
                total_length = int(total_length)
                # convert in human readable
                converted_length = WindowsUtils.convert_byte(total_length, rounded=True)

                # epoch begin time
                begin_time = time.time()

                # need to be declared out of the loop
                downloaded_byte = 0
                str_speed = ""
                tmp_seconde = 0

                for data in response.iter_content(chunk_size=4096):

                    # add lenght of data in downloaded _byte
                    downloaded_byte += len(data)
                    # write data
                    f.write(data)

                    # get a list of second(0) and millisecond(1)
                    elapsed_time_brute = str(time.time() - begin_time).split(".")

                    seconde = int(elapsed_time_brute[0])
                    # cut for 2 digits
                    ms = elapsed_time_brute[1][:2]

                    # cross product for a length of 25
                    done = int(25 * downloaded_byte / total_length)
                    # cross product for pourcentage
                    pourcentage_done = int(100 * downloaded_byte / total_length)

                    number_of_dot = (seconde % 3) + 1
                    dot = "." * number_of_dot
                    space = " " * (3 - number_of_dot)
                    str_dot = "Download" + dot + space

                    # done str
                    egal_str = "=" * done
                    # head str
                    egal_str += ">"
                    # empty str
                    empy_str = " " * (25 - done)
                    str_progress = f"[{egal_str}{empy_str}]"

                    # elapsed time
                    minute = seconde // 60
                    seconde = seconde % 60
                    str_elapsed = f"[{str(minute).zfill(2)}:{str(seconde).zfill(2)}:{ms}]"

                    # refresh per second
                    if seconde > tmp_seconde:
                        tmp_seconde = seconde
                        # speed convertion
                        download_speed = WindowsUtils.convert_byte(downloaded_byte / seconde)
                        str_speed = f"{download_speed}/s"

                    downloaded_done = WindowsUtils.convert_byte(downloaded_byte, rounded=True)
                    str_downloaded = f"({downloaded_done}/{converted_length}/{pourcentage_done}%)"

                    print(f"\r{str_dot}{str_progress} {title} {str_elapsed} {str_speed} {str_downloaded}", flush=True, end="")

                print(" done")

    @staticmethod
    def checkIsInstalled():
        if os.path.isdir("./ffmpeg"):
            return True

        else:
            return False

    def checkIsUpToDate(self):
        with contextlib.redirect_stdout(os.devnull):
            output = subprocess.getoutput(self._getPrefix() + " -version")

        current_version = self.regex.ffmpegRetrieveVersion(output)

        if current_version == self.latest_version:
            return 1

        else:
            return 0

    @staticmethod
    def ffmpegGetVersion(link):
        response = requests.get(link + ".ver")
        return response.content.decode('ascii')

    def ffmpegInstall(self, update=False):
        if not os.path.isdir("./tmp"):
            os.mkdir("./tmp")

        self.download(self.link, "./tmp/ffmpeg_latest_release.zip", "ffmpeg")

        with zipfile.ZipFile("./tmp/ffmpeg_latest_release.zip", "r") as zip_ref:
            zip_ref.extractall("./tmp")

        ffmpeg_folder = f"./tmp/ffmpeg-{self.latest_version}-essentials_build"

        if update:
            shutil.rmtree("./ffmpeg")

        with contextlib.redirect_stdout(os.devnull):
            os.rename(ffmpeg_folder, "./ffmpeg/")

        shutil.rmtree("./tmp")

    def ffmpegCheckInstallation(self):
        self.link = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        self.latest_version = self.ffmpegGetVersion(self.link)

        if self.checkIsInstalled():
            if self.checkIsUpToDate():
                print("[ffmpeg] Up to date")

            else:
                print("[ffmpeg] Outdated, updating.")
                self.ffmpegInstall(update=True)

        else:
            print("[ffmpeg] not found installing...")
            self.ffmpegInstall()
            print("[ffmpeg] Installed")

    @staticmethod
    def _getPrefix():
        return ".\\ffmpeg\\bin\\ffmpeg.exe"

    @staticmethod
    def _getPath(base, file, folder=list()):

        if len(folder) < 1 :
            path = f".\\{base}\\{file}"

        else:
            path = f".\\{base}"

            for f in folder:
                path += f"\\{f}"

            path += f"\\{file}"

        return path


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

    @staticmethod
    def ffmpegRetrieveVersion(text):
        return re.findall(r'^ffmpeg version ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', text)[0]


class YoutubeDownloader():

    def __init__(self):
        if os.name == "posix":
            self.utils = PosixUtils()

        else:
            self.utils = WindowsUtils()


        self.lowResVid = False
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
        self.download_mode = "video"
        self.current_stream.download(output_path=out_path, filename=filename_video)

        self.current_stream = self.singleYoutubeVideo.streams.filter(only_audio=True).order_by("itag").last()
        filename_audio = self.current_stream.default_filename.replace(".webm", ".mp3")
        self.download_mode = "audio"
        self.current_stream.download(output_path=out_path, filename=filename_audio)

    def downloadMusicLowRes(self, out_path):
        self.current_stream = self.singleYoutubeVideo.streams.order_by("itag").last()
        self.current_stream.download(output_path=out_path)

    def downloadMusic(self):
        self.download_mode = "audio"
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

        prefix = self.utils._getPrefix()
        options = " -loglevel error -hide_banner -y"
        base = prefix + options

        print(f"converting {file_name} ... ")

        if self.args.link_type == "single":
            if not self.lowResVid:

                input_file = self.utils._getPath(self.args.output, file_name + ".webm")
                out_options = "-c:a flac"
                out_file = self.utils._getPath(self.args.output, file_name + ".flac")

            else:

                input_file = self.utils._getPath(self.args.output, file_name + ".mp4")
                out_options = "-vn"
                out_file = self.utils._getPath(self.args.output, file_name + ".mp3")

        else:
            if not self.lowResVid:
                input_file = self.utils._getPath(self.args.output, file_name + ".webm", [self.output_playlist])
                out_options = "-c:a flac"
                out_file = self.utils._getPath(self.args.output, file_name + ".flac", [self.output_playlist])

            else:
                input_file = self.utils._getPath(self.args.output, file_name + ".mp4", [self.output_playlist])
                out_options = "-vn"
                out_file = self.utils._getPath(self.args.output, file_name + ".mp3", [self.output_playlist])

        command = f"{base} -i \"{input_file}\" {out_options} \"{out_file}\""

        os.system(command)
        os.remove(input_file)

        if self.args.sound:
            self.playF1Sound()

    def convertVideo(self):
        file_name = self.returnSafeFileName(self.current_stream.title)

        prefix = self.utils._getPrefix()
        options = " -loglevel error -hide_banner -y"
        base = prefix + options

        print(f"converting {file_name} ... ")

        if self.args.link_type == "single":
            input_audio = self.utils._getPath(self.args.output, file_name + ".mp3")
            input_video = self.utils._getPath(self.args.output, file_name + ".mp4")
            out_options = "-c copy"

            out_file = self.utils._getPath(self.args.output, file_name + ".mkv")

        else:
            input_audio = self.utils._getPath(self.args.output, file_name + ".mp3", [self.output_playlist])
            input_video = self.utils._getPath(self.args.output, file_name + ".mp4", [self.output_playlist])
            out_options = "-c copy"

            out_file = self.utils._getPath(self.args.output, file_name + ".mkv", [self.output_playlist])

        command = f"{base} -i '{input_audio}' -i '{input_video}' {out_options} '{out_file}'"

        os.system(command)

        os.remove(input_audio)
        os.remove(input_video)

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

        YouTubePlaylist = pytube.Playlist(link)

        self.output_playlist = self.returnSafeFileName(YouTubePlaylist.title)

        for video_link in YouTubePlaylist.video_urls:
            self.downloadSingle(self.regex.getVideoID(video_link))

    def showProgressBar(self, bytes_received, filesize, filename, progressBarSize=10):
        done = int(progressBarSize * bytes_received / filesize)

        str_full = "█" * done
        str_void = " " * (progressBarSize - done)

        str_pourcentage = f"{int((bytes_received / filesize)*100)}%".ljust(4,)

        str_progress = f"|{str_full}{str_void}|{str_pourcentage} {filename} ({self.download_mode})\r"

        print(f"{str_progress}", flush=True, end="")

    def progressFunction(self, stream, chunk, bytes_remaining):
        bytes_received = stream.filesize - bytes_remaining
        self.showProgressBar(bytes_received, stream.filesize, stream.default_filename.replace(".webm", ""))

    def completeFunction(self, stream, file_path, progressBarSize=10):
        str_full_progress = "█" * progressBarSize
        print(f"|{str_full_progress}|100% {stream.default_filename.replace('.webm', '')} ({self.download_mode})")

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

