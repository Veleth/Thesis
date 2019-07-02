from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', 'roll.views.index'),
    url(r'^room/(?P<room_number>\d+)', 'roll.views.room')
]