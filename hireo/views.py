from django.shortcuts import render


def index(request):
    return render(request, 'Hireo/index.html')


def messages(request):
    return render(request, 'Hireo/messages.html')


def bookmarks(request):
    return render(request, 'Hireo/bookmarks.html')
