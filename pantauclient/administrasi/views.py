from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from akademik.models import Kelas, Mapel, JamPelajaran, Jadwal, UserGuru, ProfileGuru
from akademik.forms import KelasForm, MapelForm, JamPelajaranForm, JadwalForm, UserGuruForm, ProfileGuruForm
from django.db import transaction

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

def siswa(request):
    context = {
        'title': 'Manajemen Data Siswa',
    }
    return render(request, 'administrasi/siswa.html', context)

def guru(request):
    semua_guru = UserGuru.objects.all()
    context = {
        'title': 'Manajemen Data Guru',
        'semua_objek': semua_guru,
        'page': 'guru',
    }
    return render(request, 'administrasi/guru.html', context)

def kelas(request):
    semua_kelas = Kelas.objects.all()
    context = {
        'title': 'Manajemen Jadwal dan Kelas',
        'semua_objek': semua_kelas,
        'page': 'kelas',
    }
    return render(request, 'administrasi/jadwalkelas/kelas.html', context)

def jampel(request):
    semua_jampel = JamPelajaran.objects.all()
    context = {
        'title': 'Manajemen Jadwal dan Kelas',
        'semua_objek': semua_jampel,
        'page': 'jampel',
    }
    return render(request, 'administrasi/jadwalkelas/jampel.html', context)

def mapel(request):
    semua_mapel = Mapel.objects.all()
    context = {
        'title': 'Manajemen Jadwal dan Kelas',
        'semua_objek': semua_mapel,
        'page': 'mapel',
    }
    return render(request, 'administrasi/jadwalkelas/mapel.html', context)

def jadwal(request):
    semua_jadwal = Jadwal.objects.all()
    context = {
        'title': 'Manajemen Jadwal dan Kelas',
        'semua_objek': semua_jadwal,
        'page': 'jadwal',
    }
    return render(request, 'administrasi/jadwalkelas/jadwal.html', context)

def get_guru(request):
    mapel_id = request.GET.get('mapel_id')
    gurus = UserGuru.objects.filter(mengajar__id=mapel_id).values('id', 'nama')
    return JsonResponse(list(gurus), safe=False)

def jadwal_edit(request, page, obj_id=None):
    """View untuk menangani tambah/edit data Kelas, Mapel, Jam Pelajaran, dan Jadwal."""
    model_map = {
        'kelas': (Kelas, KelasForm),
        'mapel': (Mapel, MapelForm),
        'jampel': (JamPelajaran, JamPelajaranForm),
        'jadwal': (Jadwal, JadwalForm),
    }
    
    Model, Form = model_map.get(page)
    obj = None
    if obj_id:
        obj = get_object_or_404(Model, id=obj_id)

    if request.method == 'POST':
        form = Form(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(page)
    else:
        form = Form(instance=obj)

    context = {
        'title': 'Manajemen Jadwal dan Kelas',
        'form': form,
        'page': page,
        'obj': obj,
    }
    return render(request, 'administrasi/jadwalkelas/edit.html', context)

@transaction.atomic
def guru_edit(request, obj_id=None):
    """View untuk menangani tambah/edit data Guru."""
    if obj_id:
        user_guru = get_object_or_404(UserGuru, id=obj_id)
        profile_guru = getattr(user_guru, 'profileguru', None) or ProfileGuru(guru=user_guru)
    else:
        user_guru = UserGuru()
        profile_guru = ProfileGuru()

    if request.method == 'POST':
        user_form = UserGuruForm(request.POST, instance=user_guru)
        profile_form = ProfileGuruForm(request.POST, instance=profile_guru)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            user_form.save_m2m()  # Menyimpan relasi ManyToMany

            profile = profile_form.save(commit=False)
            profile.guru = user
            profile.save()
            return redirect('guru')
    else:
        user_form = UserGuruForm(instance=user_guru)
        profile_form = ProfileGuruForm(instance=profile_guru)

    context = {
        'title': 'Manajemen Data Guru',
        'user_form': user_form,
        'profile_form': profile_form,
        'page': 'guru',
        'obj': user_guru,
    }
    return render(request, 'administrasi/guru_edit.html', context)

def hapus(request, page, obj_id):
    model_map = {
        'kelas': Kelas,
        'mapel': Mapel,
        'jampel': JamPelajaran,
        'jadwal': Jadwal,
    }
    
    Model = model_map.get(page)
    obj = get_object_or_404(Model, id=obj_id)
    obj.delete()
    return redirect(page)