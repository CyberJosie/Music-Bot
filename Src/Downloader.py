import os
import time
import string
import numpy as np
from typing import Union
from colorama import Fore
from pytube import YouTube
from slugify import slugify
from threading import Thread
from datetime import datetime
from youtubesearchpython import VideosSearch


def distribute(elements: list, groups: int) -> list[list]:
    return np.array_split(elements, groups)


def threads_finished(threads: list[Thread]) -> bool:
    '''
    Returns True if a list of thread objects have all completed
    their processess, otherwise False.

    :param threads: List of started thread objects
    '''
    for t in threads:
        if t.is_alive():
            return False
    return True


class PlaylistBot():
    def __init__(self) -> None:
        self.downloaded = 0
        self.failed = 0

    def completed(self) -> int:
        '''
        Return the sum of the total downloadd and failed songs
        '''
        return self.downloaded+self.failed

    def watch_url(self, song: str) -> Union[str, None]:
        '''
        Gets a YouTube watch URL for a given song name

        :param song: Song name/title
        '''
        url = None
        videosSearch = VideosSearch(song, limit=1)
        result = videosSearch.result()['result'][0]
        url = result['link']
        return url

    def download(self, watch_url: str, dir: str) -> bool:
        '''
        Downloads a MP3 from a YouTube watch URL

        :param watch_url: Watch URL of the video/song
        :param dir: Directory to download the song to
        '''
        success = False
        yt = YouTube(watch_url)
        try:
            video = yt.streams.filter(only_audio=True).first()
            out_filename = video.download(
                output_path=dir,
                filename="{}.mp3".format(slugify(video.title.title())))
            success = True
        except Exception as e:
            print("Failed to download: {}\n{}".format(
                watch_url, str(e),))
        return success

    def download_collection(self, dir: str, watch_urls: list, verbose: bool = False, threaded: bool = False) -> None:
        '''
        Downloads a collection of MP3s from YouTube watch URLs

        :param watch_url: Watch URL of the video/song
        :param dir: Directory to download the song to
        :param verbose: show verbose output
        :param threaded: STDOUT fixes when running concurrently
        '''
        for u in watch_urls:
            if verbose:
                if not threaded:
                    print('Downloading {}...'.format(u), end='', flush=True)
            downloaded = self.download(u, dir)
            if verbose:
                if downloaded:
                    self.downloaded += 1
                    if not threaded:
                        print(' [  Ok  ]')
                else:
                    self.failed += 1
                    if not threaded:
                        print(' [ Fail ]')

    def download_fast(self, dir: str, watch_urls: list, threads: int = 2, verbose: bool = False) -> None:
        '''
        Download a collection with multiple threads.

        :param dir: Directory to use as playlist dir
        :param watch_urls: List of youtube watch URLs
        :param threads: Number of threads to use (more is faster)
        :param verbose: Show verbose messages
        '''
        working_threads = []
        workloads = distribute(watch_urls, threads)
        for i in range(threads):
            dt = Thread(target=self.download_collection, args=(
                dir,
                workloads[i],
                verbose,
                True))
            dt.daemon = True
            dt.start()
            working_threads.append(dt)

        print('Downloading {}{}{} songs [Threads: {}]'.format(
            Fore.LIGHTCYAN_EX,
            len(watch_urls),
            Fore.RESET,
            threads,
        ))

        while not threads_finished(working_threads):
            percent = self.completed() * 100 / len(watch_urls)
            print('{c1}Progress: {_1} %{r} [{c2}{_2} / {_3} Attempted{r} | {c3}{_4} Downloaded{r} | {c4}{_5} Failed{r} ]'.format(
                c1=Fore.LIGHTWHITE_EX,
                c2=Fore.LIGHTYELLOW_EX,
                c3=Fore.LIGHTGREEN_EX,
                c4=Fore.LIGHTRED_EX,
                r=Fore.RESET,
                _1=percent,
                _2=self.completed(),
                _3=len(watch_urls),
                _4=self.downloaded,
                _5=self.failed,
            ), end='', flush=True)
            time.sleep(2)
            print('\r', end='', flush=True)
        print()
