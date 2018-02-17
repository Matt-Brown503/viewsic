from django.contrib import admin

from .models import Track, Artist, User, Genre, UserToTrack, Charts, ChartData

admin.site.register(User)
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(Genre)
# admin.site.register(TrackToGenre)
admin.site.register(UserToTrack)
admin.site.register(Charts)
admin.site.register(ChartData)


