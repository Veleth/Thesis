from django.shortcuts import render, render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('index.html')

def room(request, room_number):
    context = {
        'room_number' : room_number,
    }
    return render_to_response('room.html', context=context) #room_number, player_name etc