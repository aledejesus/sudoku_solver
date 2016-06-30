from django.shortcuts import render


def choose_method(request):
    return render(request, 'choose_method.html')
