"""YouTube mp3 downloader.

Usage:
  cli.py <url>
  cli.py (-h | --help)

Options:
  -h --help     Show this screen.
"""

from library import Track
from docopt import docopt

if __name__ == "__main__":
    args = docopt(__doc__)

    if "<url>" in args:
        track = Track(args["<url>"])
        print("Downloading...")
        track.download()

        print(f"Title: {track.title}")
        print(f"Artist(s): {'/'.join(track.artists)}")
        print(f"Genre(s): {'/'.join(track.genres)}")

        track.write_meta_to_file()
        print("Done!")
