import os
import argparse
import tqdm

from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Tuple, List, Dict
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from lyricsgenius import Genius
from dotenv import load_dotenv

from lyrics_utils import parse_lyrics

load_dotenv()


scope = "user-library-read"


def get_spotify_creds() -> Tuple[str, str, str]:
    client_id = os.environ.get('SPOTIFY_CLIENT_ID', None)
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', None)
    redirect_uri = os.environ.get('SPOTIFY_REDIRECT_URI', None)

    assert client_id, 'Missing the SPOTIFY_CLIENT_ID env var! please follow the README.md :('
    assert client_secret, 'Missing the SPOTIFY_CLIENT_SECRET env var! please follow the README.md :('
    assert redirect_uri, 'Missing the SPOTIFY_redirect_uri env var! please follow the README.md :('

    return client_id, client_secret, redirect_uri


def get_saved_tracks_from_spotify() -> List:
    client_id, client_secret, redirect_uri = get_spotify_creds()

    spotify_client = Spotify(
        auth_manager=SpotifyOAuth(scope=scope,
                                  client_id=client_id,
                                  client_secret=client_secret,
                                  redirect_uri=redirect_uri)
    )

    saved_tracks = []
    total_saved_tracks = spotify_client.current_user_saved_tracks().get('total', 0)

    print(f'Found {total_saved_tracks} total saved songs, starting to poll songs info')
    for offset in tqdm.tqdm(range(0, total_saved_tracks, 50)):
        try:
            results = spotify_client.current_user_saved_tracks(limit=50, offset=offset)
            for idx, item in enumerate(results['items']):
                track = item['track']
                saved_tracks.append(track)
        except Exception as ex:
            print('Got exception while polling for tracks')
            print(ex)

    return saved_tracks


def get_genius_creds() -> str:
    genius_access_token = os.environ.get('GENIUS_ACCESS_TOKEN', None)
    assert genius_access_token, 'Missing the GENIUS_ACCESS_TOKEN env var! please follow the README.md :('
    return genius_access_token


# TODO: add caching
def get_genius_track_ids_from_spotify_track(spotify_track: Dict, genius_client: Genius) -> List[int]:
    track_name = spotify_track.get('name', None)

    if not track_name:
        print(f'Got a track from spotify with no name :(')
        print(spotify_track)
        return []

    track_artists_search_string = ''
    track_artists_list: List[Dict] = spotify_track.get('artists', [])
    for artist in track_artists_list:
        track_artists_search_string += artist.get('name', '')

    if track_artists_search_string == '':
        print('Got a track from spotify with no artist :(')
        print(spotify_track)
        return []

    genius_tracks = genius_client.search(search_term=f'{track_name} {track_artists_search_string}')

    possible_track_ids = []

    for genius_track in genius_tracks.get('hits', []):
        track_result = genius_track.get('result', {})
        if track_name in track_result.get('title', ''):
            possible_track_ids.append(track_result.get('id'))

    # TODO: Read these lines with veborse and save them into a list to show in the end
    # if len(possible_track_ids) == 0:
    #     print(f'Found 0 tracks in genius for the song: {track_name} by {track_artists_list}')

    return possible_track_ids


# TODO: Change how we check if it's the right lyrics, maybe some ML project could be fun, like it works now, right? but
# it still gives a lot of junk (depends on likeliness_threshold)
def check_if_its_the_missing_song(track: Dict, genius_client: Genius, known_lyrics_words: List[str],
                                  likeliness_threshold: float):
    try:
        genius_track_ids = get_genius_track_ids_from_spotify_track(track, genius_client)
        known_words_in_lyrics = 0
        for genius_track_id in genius_track_ids:
            song_lyrics = parse_lyrics(genius_client.lyrics(song_id=genius_track_id))
            for known_word in known_lyrics_words:
                known_words_in_lyrics += song_lyrics.get(known_word, 0)

        if known_words_in_lyrics / len(known_lyrics_words) >= likeliness_threshold:
            print(f'Found a song that might be gutten! - {track.get("name", "")} by'
                  f' {track.get("artists", [])[0].get("name")} with the strength of'
                  f' {known_words_in_lyrics / len(known_lyrics_words)}')

    except Exception as ex:
        return (track, ex)


def run_tasks(parallel_tasks: List):
    results = []
    with Pool(cpu_count() - 1) as pool:
        for task in parallel_tasks:
            results.append(pool.apply_async(task))
        for result in results:
            result.wait()


def command(known_lyrics: str, likeliness_threshold: float):
    saved_tracks = get_saved_tracks_from_spotify()

    genius_client = Genius(get_genius_creds())

    known_lyrics_words = known_lyrics.lower().split(' ')

    print('Starting to look for good songs, this might take a '
          'while - get something nice to drink, smile and recoms would pop up :D')

    tracks_to_test = []
    for track in saved_tracks:
        tracks_to_test.append(partial(
            check_if_its_the_missing_song, track, genius_client, known_lyrics_words, likeliness_threshold)
        )

    run_tasks(tracks_to_test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This script is meant to find a song that is just stuck in your head '
                    'with some certainty, enter some words that you can remember from the song'
                    'and how much tolerant would you like the algo to find it, read more about it in the README.md')

    parser.add_argument('-kl', '--known_lyrics',
                        help='Some words that you remember, can be in random order separated by a space',
                        type=str, required=True)

    parser.add_argument('-lt', '--likeliness_threshold',
                        help='How strong is the lyrics match has to be',
                        type=float, required=False, default=0.8)

    args = parser.parse_args()

    command(known_lyrics=args.known_lyrics, likeliness_threshold=args.likeliness_threshold)
