import os
import argparse
import textwrap
from sys import platform
from Src.Downloader import PlaylistBot

# Linux
if platform == "linux" or platform == "linux2":
    DEFAULT_DIR = os.path.join('/home', os.environ.get('USER'), 'Music')
# OSX
elif platform == "darwin":
    DEFAULT_DIR = '/dev/null'  # heh, sucker
# Windows
elif platform == "win32":
    DEFAULT_DIR = os.path.join('Users', os.environ.get('USERNAME'), 'Music')


def main(args) -> None:
    bot = PlaylistBot()

    playlist_url = ''
    max_songs = -1
    folder = DEFAULT_DIR
    song_names = []
    thread_count = 1

    if args.dir != None:
        # Try to create the dir if it does not
        # exist, and quit program if cannot
        # then set folder to it
        if not os.path.isdir(args.dir):
            os.makedirs(args.dir)
            if not os.path.isdir(args.dir):
                print("Error: Could not make directory: {}".format(args.dir))
                exit()
        folder = args.dir

    output_folder = os.path.join(folder, args.name)

    if args.i.startswith('http'):
        if verify_ytmusic_url(args.i):
            playlist_url = args.i

            song_names = scrape_songs(playlist_url)
        else:
            print('Invalid YouTube Music URL: {}'.format(args.i))
            exit()
    elif args.i == '-':
        print('Start entering song names now. When you are done,\n enter DONE on the next line.')
        while True:
            s = input("> ")
            if s.lower() == 'done':
                print("Stored {} songs.".format(
                    len(song_names)))
                break
            else:
                song_names.append(s.strip())

    elif os.path.isfile(args.i):
        with open(args.i, 'r') as f:
            song_names = [s.strip().replace('\n', '') for s in f.readlines()]
    else:
        print('{} if not a valid YouTube Music playlist or a file on this system.'.format(
            args.i))
        exit()

    if args.threads != None:
        thread_count = int(args.threads)

    # Scrape list of songs from youtube
    # song_names = []

    watch_urls = [bot.watch_url(s) for s in song_names]
    # bot.download_collection(output_folder, watch_urls, verbose=True)
    bot.download_fast(
        output_folder,
        watch_urls,
        thread_count,
        True)

    print('Done.')
    print('Downloaded to: {}'.format(output_folder))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='Playlist Bot',
    )

    parser.add_argument(
        'name',
        action='store',
        help=textwrap.dedent('''
        Name to use for the folder in which the songs are saved, must be a valid path string. (To be safe: A-Z,a-z,0-9,_,-)
        '''),
    )

    parser.add_argument(
        '-i',
        action='store',
        help=textwrap.dedent('''
        Path to list of songs
         OR
        use \'-\' to enter names interactively.
        '''),
    )

    parser.add_argument(
        '--threads', '-t',
        action='store',
        type=int,
        help='Number of threads to download with. (Optional)'
    )

    parser.add_argument(
        '--dir', '-d',
        action='store',
        help=textwrap.dedent('''
        Folder to use as music directory. (Optional)
        Default option is your operating systems default.
        '''),
    )

    main(parser.parse_args())
