from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Create your views here.
def index(request):
    context = {
        'title': 'Dashboard',
        # AKTIFASI TOMBOL
        'icon': 'bg-[#3d3d3d]',
    }
    return render(request, 'administrasi/index.html', context)

def presensi(request):
    context = {
        'title': 'Presensi',
    }
    return render(request, 'administrasi/presensi.html', context)

def rekap(request):
    context = {
        'title': 'Rekap',
    }
    return render(request, 'administrasi/rekap.html', context)

def pengaturan(request):
    context = {
        'title': 'Pengaturan',
    }
    return render(request, 'administrasi/pengaturan.html', context)
