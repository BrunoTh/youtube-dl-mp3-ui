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
        track.download()
        track.write_meta_to_file()
        print("Done!")
