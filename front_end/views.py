from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from fire_guard.models import FireAlertServices
from .forms import FireAlertServicesForm


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
def on_going(request):

    queues = FireAlertServices.objects.filter(is_accepted=True, is_done=False)

    return render(request, 'front_end/on_going.html', {'queues': queues})


@login_required(login_url='login')
def completed(request):

    queues = FireAlertServices.objects.filter(
        is_accepted=True, is_done=True, is_rejected=False)

    return render(request, 'front_end/completed.html', {'queues': queues})


@login_required(login_url='login')
def rejected(request):

    queues = FireAlertServices.objects.filter(is_rejected=True)

    return render(request, 'front_end/rejected.html', {'queues': queues})


@login_required(login_url='login')
def refresh_home(request):

    queues = FireAlertServices.objects.filter(
        is_accepted=False, is_done=False, is_rejected=False)

    return render(request, 'front_end/queue.html', {'queues': queues})


@login_required(login_url='login')
def edit_report_view(request, pk):
    service = get_object_or_404(FireAlertServices, pk=pk)
    form = FireAlertServicesForm(instance=service)

    if request.POST:
        form = FireAlertServicesForm(request.POST, instance=service)

        if form.is_valid():
            form.save()

    url = f'http://www.google.com/maps/place/{service.latitude},{service.longitude}'
    data = {
        'form': form,
        'pk': pk,
        'url': url,
    }

    return render(request, 'front_end/edit_form.html', data)
