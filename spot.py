import sys
import os
import spotipy
import spotipy.util as util
import matplotlib.pyplot as plt
from matplotlib.cbook import get_sample_data
import numpy as np
from PIL import Image
import requests
from io import BytesIO

from spotipy.oauth2 import SpotifyClientCredentials

os.environ['SPOTIPY_CLIENT_ID'] = '4e2ba88cc79247a8acc4160d1510764f'
os.environ['SPOTIPY_CLIENT_SECRET'] = '1698c2d495ed4d6fba3967974ced8423'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_all_tracks(username, playlist):
    results = sp.user_playlist_tracks(username,playlist)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def show_tracks(tracks, name, username, playlist_url):
    allA = []
    for track in tracks:
        if len(track['track']['album']['artists']) != 0:
            artist = track['track']['album']['artists'][0]['name']
            allA = check_artist(allA, artist)
    objects = []
    frequency = []
    for artists in allA:
        objects.append(artists[0])
        frequency.append(len(artists))
    plot(objects, frequency, name, username, playlist_url)

def plot(objects, frequency, name, username, url):

    fig, ax = plt.subplots()

    combined = []

    for i in range(len(objects)):
        combined.append([objects[i], frequency[i]])

    max = 30
    combined.sort(reverse=True, key=takeSecond)

    objects = []
    frequency = []

    if len(combined) < max:
        max = len(combined)
    for i in range(max):
        if len(combined[i][0]) > 15:
            newWord = combined[i][0] + "..."
            objects.append(newWord)
        else:
            objects.append(combined[i][0])
        frequency.append(combined[i][1])
    y_pos = np.arange(max)
    plt.bar(y_pos, frequency, align='center', alpha=0.5, zorder=1)
    plt.xticks(y_pos, objects, fontsize='medium', rotation=90, zorder=1)
    plt.ylabel('Frequency', zorder=1)
    plt.title('Artists in ' + sp.user(username)['display_name'] + "'s playlist: " + name, fontsize='small', zorder=1)
    plt.tight_layout(pad=4)

    response = requests.get(sp.user(username)['images'][0]['url'])
    response2 = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img2 = Image.open(BytesIO(response2.content))

    im = np.array(img).astype(np.float) / 255
    im2 = np.array(img2).astype(np.float) / 255

    # Place the image in the upper-right corner of the figure
    #--------------------------------------------------------
    # We're specifying the position and size in _figure_ coordinates, so the image
    # will shrink/grow as the figure is resized. Remove "zorder=-1" to place the
    # image in front of the axes.
    newax = fig.add_axes([0, 0.7, 0.3, 0.3], anchor='NW', zorder=-1)
    newax.imshow(im)
    newax.axis('off')

    newax2 = fig.add_axes([0.7, 0.7, 0.3, 0.3], anchor='NE', zorder=-1)
    newax2.imshow(im2)
    newax2.axis('off')

    plt.savefig('graph.png', dpi=80)

    plt.show()

def takeSecond(elem):
    return elem[1]

def check_artist(allA, artist):
    if len(allA) == 1:
        artists = [artist]
        allA.append(artists)
        return allA
    else:
        for i in range(len(allA)):
            if allA[i][0] == artist:
                allA[i].append(artist)
                return allA
        allA.append([artist])
        return allA        


if __name__ == "__main__":
    keepGoing = True
    username = input("Check who? ")

    while keepGoing:
        playlists = sp.user_playlists(username)
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                print("%4d %s" % (i + 1 + playlists['offset'],  playlist['name']))
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None

        playlists = sp.user_playlists(username)['items']
        value = int(input("Which playlist do you want? ")) - 1

        playlist = playlists[value]

        tracks = get_all_tracks(sys.argv, playlist['id'])

        show_tracks(tracks, playlist['name'], username, playlist['images'][0]['url'])
        
        decision = input("New user? ")
        if decision == "no":
            decision = input("New playlist? ")
            if decision == "no":
                keepGoing = False
        else:
            username = decision
                






