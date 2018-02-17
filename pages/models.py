from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.CharField(max_length=255)
    user_img = models.CharField(max_length=200)
    birthdate = models.CharField(max_length=2550)
    user_url = models.CharField(max_length=255)
    last_request = models.DateTimeField(null=True, blank=True)
    track_score = models.CharField(max_length=255)
    artist_score = models.CharField(max_length=255)


class Track(models.Model):
    name = models.CharField(max_length=255)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, related_name='tracks')
    album = models.CharField(max_length=255)
    track_id = models.CharField(max_length=255)
    album_art = models.CharField(max_length=255)
    track_url = models.CharField(max_length=255)
    popularity = models.CharField(max_length=255)
    preview_url = models.CharField(max_length=255)

class Genre(models.Model):
    genre = models.CharField(max_length=255)

    def __str__(self):
        return self.genre
    
    def __repr__(self):
        return self.__str__()

class Artist(models.Model):
    name = models.CharField(max_length=255)
    artist_id = models.CharField(max_length=255)
    artist_img = models.CharField(max_length=255)
    artist_url = models.CharField(max_length=255)
    popularity = models.CharField(max_length=255, null=True, blank=True)
    genre = models.ManyToManyField(Genre)
    

class UserToTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='users')

class Charts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='charts')

class ChartData(models.Model):
    genre = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    chart = models.ForeignKey(Charts, on_delete=models.CASCADE, related_name='chartdata')