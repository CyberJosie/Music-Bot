import os
import time
import string
from typing import Union
from pytube import YouTube
from slugify import slugify
from threading import Thread
from datetime import datetime
from youtubesearchpython import VideosSearch
import numpy as np


def distribute(elements: list, groups: int) -> list[list]:
    return np.array_split(elements, groups)


def threads_finished(threads: list[Thread]) -> bool:
    for t in threads:
        if t.is_alive():
            return False
    return True


class PlaylistBot():
    def __init__(self) -> None:
        pass

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
                    if not threaded:
                        print(' [  Ok  ]')
                else:
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

        print('Downloading {} songs [Threads: {}]'.format(
            len(watch_urls),
            threads,))
        while not threads_finished(working_threads):
            time.sleep(2)
            print('.', end='', flush=True)
