from django.shortcuts import render
from django.http import HttpResponse

def get_route(request):
    return HttpResponse("Welcome, ! Here you canget the route from third party API")