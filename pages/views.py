from django.shortcuts import render, HttpResponseRedirect, redirect
import spotipy
import spotipy.util as util
from spotipy import oauth2
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from pages.models import User, Track, UserToTrack, Artist, Genre
from collections import Counter
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from colour import Color
from urllib3.exceptions import HTTPError




@login_required(login_url='/home/')
def home(request):
    return HttpResponseRedirect('/profile/')


def update_user_info(user_data, request):
    try:
        userimg = user_data['images'][0]['url']
    except IndexError:
        userimg = 'http://via.placeholder.com/300x300'
    
    if user_data['display_name'] is not None:
        display_name = user_data['display_name']
    else:
        display_name = user_data['id']
        request.user.first_name = display_name
        
    request.user.username = display_name
    request.user.user_img = userimg 
    request.user.user_id = user_data['id']
    request.user.birthdate = user_data['birthdate']
    request.user.save()

def save_tracks(data, user, artist):
    

    track, created = Track.objects.update_or_create(
    name = data['name'],
    artist = artist,
    album = data['album']['name'],
    track_id = data['id'],
    album_art = data['album']['images'][1]['url'],
    track_url = data['external_urls']['spotify'],
    preview_url=data['preview_url'] or '#',
    defaults={
        'popularity': data['popularity']
        }
    )

    # if created:

    # else:
    #     print('found')
    
    rel, junction = UserToTrack.objects.update_or_create(
    track=track,
    user=user
    )
    

def update_track(data):
    track, created = Track.objects.update_or_create(
track_id=data['id'],
defaults={
    'danceability': data['danceability'],
    'valence': data['valence'],
    'duration': data['duration_ms'],
    'energy': data['energy']
    }
)

def save_artist(data):
    artist, created = Artist.objects.update_or_create(
    name=data['artists'][0]['name'],
    artist_id = data['artists'][0]['id'],
    artist_url = data['artists'][0]['external_urls']['spotify'],
    )
    return artist

def update_artist(data, genre):
    artist, created = Artist.objects.update_or_create(
    name=data['name'],
    defaults={
        'artist_img': data['images'][0]['url'],
        'popularity': data['popularity'],
        }
    )
    artist.genre.add(genre)
    artist.save()

def update_artist_no_genre(data):
    try:
        userimg = data['images'][1]['url']
    except IndexError:
        userimg = ''
    artist, created = Artist.objects.update_or_create(
    name=data['name'],
    defaults={
        'artist_img': userimg,
        'popularity': data['popularity'],
        }
    )

def make_genre(data):
    genre, created = Genre.objects.update_or_create(
        genre = data
    )
    return genre


def collect_top_artists(data):
    artist_data = []
    top_artists = {}
    for trackid in data:
        artist_data.append(trackid.track.artist.name)
    artist_count = Counter(artist_data).most_common(10)
    #top artists and counts
    count = 0
    for i in artist_count:
        a_id = str(Artist.objects.filter(name=i[0])[0].id)
        top_artists['artist{}'.format(count)] = {}
        top_artists['artist{}'.format(count)]['name'] = i[0]
        top_artists['artist{}'.format(count)]['img'] = Artist.objects.filter(name=i[0])[0].artist_img or 'http://via.placeholder.com/300x300'
        top_artists['artist{}'.format(count)]['url'] = Artist.objects.filter(name=i[0])[0].artist_url
        top_artists['artist{}'.format(count)]['popularity'] = Artist.objects.filter(name=i[0])[0].popularity
        genres = []
        for g in Artist.objects.filter(name=i[0])[0].genre.all()[:2]:
            genres.append(str(g))
        top_artists['artist{}'.format(count)]['genre'] = genres
        for g in Track.objects.filter(artist_id=a_id).all()[:1]:
            top_artists['artist{}'.format(count)]['preview'] = g.preview_url
        count += 1
        
            
    return top_artists

def colorPicker(fcolor, lcolor, count):
            start = Color(fcolor)
            color_list = list(start.range_to(Color(lcolor), count))
            return color_list

def collect_genre_data(data,user):
    genre_data = [] 
    top_genres = {}
    for trackid in data:
        for genre in trackid.track.artist.genre.all():
            genre_data.append(genre)
    user_genre_count = Counter(genre_data).most_common(15)
    #top genres and counts
    count = 0
    colors = colorPicker('#222831', '#02d9e3', 15)
    for i in user_genre_count:
        top_genres['genre{}'.format(count)] = {}
        top_genres['genre{}'.format(count)]['genre'] = '{}'.format(i[0])
        top_genres['genre{}'.format(count)]['value'] = i[1]
        top_genres['genre{}'.format(count)]['color'] = '{}'.format(colors[count])
        count += 1
    
    # save unique genres
    user.genre_count = len(set(genre_data))
    user.save()
    return top_genres

def collect_track_info(data):
    top_tracks = {}
    count = 0
    
    for trackid in data:
        top_tracks['track{}'.format(count)] = {}
        top_tracks['track{}'.format(count)]['name'] = trackid.track.name
        top_tracks['track{}'.format(count)]['artist'] = trackid.track.artist.name
        top_tracks['track{}'.format(count)]['img'] = trackid.track.album_art
        top_tracks['track{}'.format(count)]['url'] = trackid.track.track_url
        top_tracks['track{}'.format(count)]['preview'] = trackid.track.preview_url
        top_tracks['track{}'.format(count)]['popularity'] = trackid.track.popularity
        count += 1
    return top_tracks

def track_avg(data):
    total = 0
    for trackid in data:
        try:
            total += int(trackid.track.popularity)
        except ValueError:
             total += 0
    total = total // len(data)
    print('track avg:')
    return total
        
def artist_avg(data):
    total = 0
    for trackid in data: 
        try:
            total += int(trackid.track.artist.popularity)
        except ValueError:
            total += 0
    total = total // len(data)
    print('artist avg:')
    print(total)
    return total

def danceability_avg(data):
    total = 0
    for trackid in data:
        try:
            total += float(trackid.track.danceability)
        except ValueError:
            total += 0
    
    total = total / len(data)
    print('dance avg:')
    print(total)
    return total

def valence_avg(data):
    total = 0
    for trackid in data:
        try:
            total += float(trackid.track.valence)
        except ValueError:
            total += 0
    total = total / len(data)
    print('valence avg:')
    print(total)
    return total

def energy_avg(data):
    total = 0
    for trackid in data:
        try:
            total += float(trackid.track.energy)
        except ValueError:
            total += 0
    total = total / len(data)
    print('energy avg:')
    print(total)
    return total

def update_user_avg(data, request):
    request.user.track_score = track_avg(data)
    request.user.artist_score = artist_avg(data)
    request.user.dance_score = danceability_avg(data)
    request.user.valence_score = valence_avg(data)
    request.user.energy_score = energy_avg(data)
    request.user.save()

def all_user_track_avg(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += int(user.track_score)
        except ValueError:
            missed += 1
            pass
    total = total // (len(data)-missed)
    return total

def all_user_artist_avg(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += int(user.artist_score)
        except ValueError:
            missed += 1
            pass
    total = total // (len(data)-missed)
    return total
def all_user_dance_score(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += float(user.dance_score)
        except ValueError:
            missed += 1
            pass
    total = total / (len(data)-missed)
    return total
        
def all_user_valence_score(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += float(user.valence_score)
        except ValueError:
            missed += 1
            pass
    total = total / (len(data)-missed)
    return total

def all_user_energy_score(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += float(user.energy_score)
        except (ValueError, TypeError) as error:
            missed += 1
            pass
    total = total / (len(data)-missed)
    return total

def all_user_genre_avg(data):
    total = 0
    missed = 0
    for user in data:
        try:
            total += int(user.genre_count)
        except ValueError:
            missed += 1
            pass
    total = total // (len(data)-missed)
    return total

@login_required(login_url='/home/')
def profile(request):
    print(request.user.username)
    
    last_request = request.user.last_request
    current_request = timezone.now()

    if last_request:
        difference = current_request - last_request
        print(difference.seconds)
    else:
        difference = None

    print('older than 5 minutes')
    if not difference or difference.seconds > 10:
        # 3600
        all_user_tracks = request.user.tracks.all()
        token = request.user.social_auth.all()[0].extra_data

        try:
            sp = spotipy.Spotify(auth=token['access_token'])
        except spotipy.client.SpotifyException:
            return HttpResponseRedirect('/')
        try:
            user_top = sp.current_user_top_tracks(limit=50, time_range='long_term')
        except spotipy.client.SpotifyException:
            return HttpResponseRedirect('/')
        user_info = sp.current_user()
        
        update_user_info(user_info, request)
        # print('Library of: {} Email: {} External: {}'.format(user_info['display_name'], user_info['email'], user_info['external_urls']['spotify']))
        
        for data in user_top['items']:
            artist = save_artist(data)
            save_tracks(data, request.user, artist)
            # print('track saved')
        
        #appending artist id to query for artist data + genre info
        artist_info = []
        track_info = []
        for trackid in all_user_tracks:
            track_info.append(trackid.track.track_id)
            artist_info.append(trackid.track.artist.artist_id)
            
        #updates artist info and genre info
        myset = list(set(artist_info))
        a_data = sp.artists(myset)
        for content in a_data['artists']:
            for entry in content['genres']:
                genre = make_genre(entry)
                update_artist(content,genre)
            update_artist_no_genre(content)
      

        track_details = sp.audio_features(track_info)
        for song in track_details:
            update_track(song)

        request.user.last_request = timezone.now()
        request.user.save()


    return render(request, 'pages/profile.html',)


class ChartData(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    

    def get(self, request, format=None):
        data = request.user.tracks.all()
        allusers = []
        users = User.objects.all()
        for user in users:
            if user.is_superuser:
                pass
            else:
                allusers.append(user)

        update_user_avg(data, request)

        page_data = {
            'artists': [collect_top_artists(data)],
            'genres': [collect_genre_data(data,request.user)],
            'tracks': [collect_track_info(data)],
            'track_score': request.user.track_score,
            'artist_score': request.user.artist_score,
            'track_avg': all_user_track_avg(allusers),
            'artist_avg': all_user_artist_avg(allusers),
            'dance_score': request.user.dance_score,
            'dance_avg': all_user_dance_score(allusers),
            'valence_score': request.user.valence_score,
            'valence_avg': all_user_valence_score(allusers),
            'genre_score': request.user.genre_count,
            'genre_avg': all_user_genre_avg(allusers),
            'energy_score': request.user.energy_score,
            'energy_avg': all_user_energy_score(allusers)
        }
        return Response(page_data)
