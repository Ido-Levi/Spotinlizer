from collections import defaultdict
from typing import Dict


def parse_lyrics(lyrics: str) -> Dict:
    """
    Turns a string of lyrics into a dict of how many times a word has occurred inside the song
    :param lyrics: The lyrics
    :return: The dict that we talked about bro
    """
    lyrics = lyrics.lower().replace('\n', ' ').split(' ')
    lyrics_dict = defaultdict(lambda: 0)
    for word in lyrics:
        lyrics_dict[word] = lyrics_dict[word] + 1

    return dict(lyrics_dict)
