from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import chatMessages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserModel
from django.db.models import Q
import json,datetime
from django.core import serializers
from .models import Room, Message

@login_required
def home(request):
    User = get_user_model()
    users = User.objects.all()
    rooms = Room.objects.all()  # to get all rooms
    
    chats = []
   # room_messages = []

    if request.method == 'GET' and 'u' in request.GET:
        # Fetching private messages
        chats = chatMessages.objects.filter(
            Q(user_from=request.user.id, user_to=request.GET['u']) | 
            Q(user_from=request.GET['u'], user_to=request.user.id)
        ).order_by('date_created')
   # elif request.method == 'GET' and 'room' in request.GET:
        # Fetching group messages
       # room = get_object_or_404(Room, id=request.GET['room'])
       # room_messages = Message.objects.filter(room=room).order_by('date_added')[:25]
    context = {
        "page": "home",
        "users": users,
        "chats": chats,
        "rooms": rooms,  # room context
       # "room_messages": room_messages,
        "chat_id": int(request.GET.get('u', 0)),
      #  "room_id": int(request.GET.get('room', 0)),
    }
    return render(request, "chat/home.html", context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account successfully created!')
            return redirect('chat-login')
        context = {
            "page":"register",
            "form" : form
        }
    else:
        context = {
            "page":"register",
            "form" : UserRegistrationForm()
        }
    return render(request,"chat/register.html",context)

@login_required
def profile(request):
    context = {
        "page":"profile",
    }
    return render(request,"chat/profile.html",context)

def get_messages(request):
    last_id = request.POST.get('last_id')
    if last_id is not None:
        chats = chatMessages.objects.filter(
            Q(id__gt=last_id),
            Q(user_from=request.user.id, user_to=request.POST['chat_id']) | Q(user_from=request.POST['chat_id'], user_to=request.user.id)
        )
        new_msgs = []
        for chat in list(chats):
            data = {
                'id': chat.id,
                'user_from': chat.user_from.id,
                'user_to': chat.user_to.id,
                'message': chat.message,
                'date_created': chat.date_created.strftime("%b-%d-%Y %H:%M")
            }
            new_msgs.append(data)
        return HttpResponse(json.dumps(new_msgs), content_type="application/json")
    else:
        # Return a response with an error message and a 400 status code
        return HttpResponse(json.dumps({'error': 'last_id is missing'}), content_type="application/json", status=400)



def send_chat(request):
    resp = {}
    User = get_user_model()
    if request.method == 'POST':
        post =request.POST
        
        u_from = UserModel.objects.get(id=post['user_from'])
        u_to = UserModel.objects.get(id=post['user_to'])
        insert = chatMessages(user_from=u_from,user_to=u_to,message=post['message'])
        try:
            insert.save()
            resp['status'] = 'success'
        except Exception as ex:
            resp['status'] = 'failed'
            resp['mesg'] = ex
    else:
        resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")

""" 
def send_chat(request):
    if request.method == 'POST':
        user_from_id = request.POST.get('user_from')
        message = request.POST.get('message')
        if 'user_to' in request.POST:  # Single chat
            user_to_id = request.POST.get('user_to')
            user_to = get_object_or_404(get_user_model(), id=user_to_id)
            user_from = get_object_or_404(get_user_model(), id=user_from_id)
            chat_message = chatMessages(user_from=user_from, user_to=user_to, message=message)
            chat_message.save()
            return JsonResponse({'status': 'success'})
        elif 'room' in request.POST:  # Group chat
            room_id = request.POST.get('room')
            room = get_object_or_404(Room, id=room_id)
            user_from = get_object_or_404(get_user_model(), id=user_from_id)
            members = room.members.all()
            for member in members:
                message = Message(room=room, user=user_from, content=message)
                message.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}) """


""" grp chat """
                                                
@login_required
def rooms(request):
    rooms = Room.objects.all()
    return render(request, 'chat/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)[0:25]
    return render(request, 'chat/room.html', {'room': room, 'messages': messages})


