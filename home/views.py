from django.shortcuts import render


def home(request):
    context = {
        'name': 'Alejandro'
    }

    return render(request, 'home.html', context)
