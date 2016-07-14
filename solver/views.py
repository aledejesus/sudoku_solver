from django.shortcuts import render


def choose_method(request):
    return render(request, 'choose_method.html')

def input_numbers(request):
    return render(request, 'input_numbers.html')
