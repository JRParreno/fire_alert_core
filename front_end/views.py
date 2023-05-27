from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from fire_guard.models import FireAlertServices


def login_view(request):
    msg_error = ""

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('home')
        else:
            msg_error = "email and password didn't match"

    return render(request, 'front_end/login.html', {'error': msg_error})


@login_required(login_url='login')
def home(request):

    queues = FireAlertServices.objects.filter(is_accepted=False, is_done=False)

    return render(request, 'front_end/home.html', {'queues': queues})


@login_required(login_url='login')
def refresh_home(request):

    queues = FireAlertServices.objects.filter(is_accepted=False, is_done=False)

    return render(request, 'front_end/queue.html', {'queues': queues})
