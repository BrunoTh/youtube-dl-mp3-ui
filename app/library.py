import logging
from pathlib import Path
import youtube_dl
import re
import eyed3

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

available_tracks = []


GENRES = ["trap", "house", "edm", "electronic", "dupstep", "future bass", "drumstep", "electro", "electro house",
          "hip hop", "chill hop"]


class Track:
    def __init__(self, url: str):
        self.url = url
        self.title = ""
        self.original_title = ""
        self.subtitle = ""
        self.artists = []
        self.genres = []
        self.filepath = None

    def __str__(self):
        return self.title

    def download(self):
        def progress_hook(state):
            if state["status"] == "finished":
                mp3_filename = ".".join(state["filename"].split(".")[:-1])
                mp3_filename += ".mp3"
                self.filepath = Path() / mp3_filename  # TODO: replace ending with mp3

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "logger": log,
            "progress_hooks": [progress_hook]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Get meta data and parse it
            info = ydl.extract_info(self.url, download=False)

            track_meta = extract_meta_data_from_title(info["title"])
            track_genres = search_for_genres_in_tags(info["tags"])

            self.title = track_meta["title"]
            self.artists = track_meta["artists"]
            self.subtitle = track_meta["subtitle"]
            self.original_title = track_meta["title"]
            self.genres = track_genres

            # Download and convert
            ydl.download([self.url])

            available_tracks.append(self)

            # Rename file to "Artist(s) - Title.mp3"
            new_filename = f"{', '.join(self.artists)} - {self.title}.mp3"
            self.filepath.rename(new_filename)
            self.filepath = self.filepath.parent / new_filename

        return self

    def write_meta_to_file(self):
        """
        Writes the mp3 tags to the file under `self.filepath`.
        """
        audiofile = eyed3.load(self.filepath)
        audiofile.tag.artist = "/".join(self.artists)
        audiofile.tag.title = self.title
        audiofile.tag.genre = "/".join(self.genres)
        audiofile.tag.save()


def extract_meta_data_from_title(title: str) -> dict:
    """
    Tries to parse the given string to extract artists and the track title.
    :param title: full title of the video
    :return: dict with title, subtitle, artists
    """
    result = {
        "title": "",
        "subtitle": "",
        "artists": [],
    }

    regex_match = re.match(r"(?P<artists>.*)\s*-\s*(?P<title>.*)", title)

    if regex_match:
        result["title"] = regex_match.groupdict().get("title")
        result["artists"] = [regex_match.groupdict().get("artists")]
        # TODO: split x or ,
        # TODO: search for by | ft. | feat. in title

    return result


def search_for_genres_in_tags(tags: list) -> list:
    """
    Searches for possible genres in the tag list.
    :param tags: List with tags
    :return: List with genres
    """
    result = []

    for tag in tags:
        if tag.lower() in GENRES:
            result.append(tag.lower())

    return result
