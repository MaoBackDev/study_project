from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q

from .models import *
from .forms import *


# LOGIN PAGE
def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
       return HttpResponseRedirect(reverse_lazy('base:home')) 

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('base:home'))
        else:
            messages.error(request, 'User or password does not exist')

    context = {'page': page}
    return render(request, 'base/login.html', context)


# REGISTER PAGE
def register_page(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Usamos commit=False para realizar modificaciones a los atributos antes de realizar el guardado en la base de datos. Estos deben estar en una variable
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('base:home'))
        else:
            messages.error(request, 'An error occurred during registration!!')

    return render(request, 'base/login.html', {'form': form})


# USER LOGOUT
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('base:home'))



# MAIN PAGE
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[:4]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)



# DETAIL ROOM
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    #  Creación de un mensaje a tráves del chat
    if request.method == 'POST':
        msg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        # Cada que un nuevo usuario realiza un comentario o envía un mensaje, se agrega automaticante como participante
        room.participants.add(request.user)
        return redirect('base:room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    }
    return render(request, 'base/room.html', context)


# USER PROFILE CONTENT
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


# CREATE ROOM
@login_required(login_url='base:login')
def create_room(request):
    form_context = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return HttpResponseRedirect(reverse_lazy('base:home'))

    context = {'form': form_context, 'topics': topics}
    return render(request, 'base/room_form.html', context)


# UPDATE ROOM
@login_required(login_url='base:login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()

        return HttpResponseRedirect(reverse_lazy('base:home'))

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


# DELETE ROOM
@login_required(login_url='base:login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    # Valida que solo el usuario al que pertenece la sala pueda ejercer la acción
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return HttpResponseRedirect(reverse_lazy('base:home'))

    return render(request, 'base/delete.html', {'obj': room})


# DELETE MESSAGE IN CHAT
@login_required(login_url='base:login')
def delete_message(request, pk):
    msg = Message.objects.get(id=pk)

    if request.user != msg.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        msg.delete()
        return HttpResponseRedirect(reverse_lazy('base:home'))

    return render(request, 'base/delete.html', {'obj': msg})


# UPDATE USER
@login_required(login_url='base:login')
def update_user(request):
    user = request.user
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('base:profile', pk=user.id)

    context = {
        'form': form
    }
    return render(request, 'base/update-user.html', context)


# MOBILE RESPONSIVE
# LIST ALL TOPICS IN MODE MOBILE
def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    return render(request, 'base/topics.html', {'topics': topics})

# LIST ALL RECENT ACTIVITIES IN MODE MOBILE
def activities_page(request):
    room_messages = Message.objects.all()
    context = {
        'room_messages': room_messages
    }
    return render(request, 'base/activity.html', context)
