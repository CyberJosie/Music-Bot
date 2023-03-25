import os
import sys
import argparse
import subprocess
import shutil


def execute(cmd) -> str:
    return str(subprocess.run([cmd], stdout=subprocess.PIPE, shell=True).stdout.decode())


def main(args) -> None:

    if os.geteuid() != 0:
        print('This script must be ran as root!')
        exit()

    if not os.path.isdir(args.dir):
        os.makedirs(args.dir)
        if not os.path.isdir(args.dir):
            print('Failed to create directory: {}'.format(args.dir))
            exit()

    install_dir = os.path.join(args.dir, 'musicbot')
    os.makedirs(install_dir)

    RUN_SCRIPT = '''
#!/bin/bash
export args=""
export pypath=$(which python3)

for var in "$@"; do
    args="${{args}} $var "
done;

$pypath {}/musicbot.py $args

'''.format(install_dir)

    with open(os.path.join(install_dir, 'musicbot.sh'), 'w') as f:
        f.write(RUN_SCRIPT)

    # Copy over files
    shutil.copy('musicbot.py', os.path.join(
        install_dir, 'musicbot.py'))
    os.makedirs(os.path.join(install_dir, 'Src'))
    shutil.copy('Src/Downloader.py', os.path.join(
        install_dir, 'Src/Downloader.py'))

    # Make symbolic links
    os.system('ln -s {} /usr/local/bin/musicbot'.format(
        os.path.join(install_dir, 'musicbot.sh'),))

    os.system('chmod +x {}'.format(os.path.join(install_dir, 'musicbot.sh')))

    if os.path.isfile('/usr/local/bin/musicbot'):
        print('Installed! Run with \'musicbot\'')
    else:
        print('Failed to auto-install!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='MusicBot Installer Script',
    )

    parser.add_argument(
        'dir',
        action='store',
        help='Directory to install to',
    )

    main(parser.parse_args())
