from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.


def main(request):
    return render(request, 'GenomeTag/main.html')
    #return HttpResponse("bruh")

def authenticate(request):
    return HttpResponse("Here you will be able to authenticate")

def annotations(request):
    return HttpResponse("Here you will be able to make see annotations")

def create(request):
    return HttpResponse("Here you will be able to create new annotations")