from django.shortcuts import render, redirect
from django.http import HttpResponse
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



# Create your views here.
@login_required
def home(request):
    User = get_user_model()
    users = User.objects.all()
    rooms = Room.objects.all()  # to get all rooms
    chats = {}
    if request.method == 'GET' and 'u' in request.GET:
        # chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
        chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
        chats = chats.order_by('date_created')
    context = {
        "page":"home",
        "users":users,
        "chats":chats,
        "rooms": rooms,  # room context
        "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
    }
    print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
    return render(request,"chat/home.html",context)

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



