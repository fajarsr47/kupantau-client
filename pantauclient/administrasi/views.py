from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from akademik.models import Kelas, Mapel, JamPelajaran, Jadwal, UserGuru, ProfileGuru, GuruMapel
from akademik.forms import KelasForm, MapelForm, JamPelajaranForm, JadwalForm, UserGuruForm, ProfileGuruForm, GuruMapelForm
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
    if obj_id:
        user_guru = get_object_or_404(UserGuru, id=obj_id)
        profile_guru = getattr(user_guru, 'profileguru', None) or ProfileGuru(guru=user_guru)
        mapel_diampu = GuruMapel.objects.filter(guru=user_guru)
    else:
        user_guru = UserGuru()
        profile_guru = ProfileGuru()
        mapel_diampu = None

    if request.method == 'POST':
        user_form = UserGuruForm(request.POST, instance=user_guru)
        profile_form = ProfileGuruForm(request.POST, instance=profile_guru)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            
            # Password otomatis diisi dengan NIP jika objek baru
            if not obj_id and user_form.cleaned_data.get('nip'):
                user.set_password(user_form.cleaned_data.get('nip'))
            
            user.save()

            profile = profile_form.save(commit=False)
            profile.guru = user
            profile.save()
            
            messages.success(request, 'Data guru berhasil disimpan.')
            return redirect('edit_guru', obj_id=user.id)
    else:
        user_form = UserGuruForm(instance=user_guru)
        profile_form = ProfileGuruForm(instance=profile_guru)

    context = {
        'title': 'Manajemen Data Guru',
        'user_form': user_form,
        'profile_form': profile_form,
        'page': 'guru',
        'obj': user_guru,
        'mapel_diampu': mapel_diampu
    }
    return render(request, 'administrasi/guru_edit.html', context)

def guru_mapel_add(request, guru_id):
    guru = get_object_or_404(UserGuru, id=guru_id)
    if request.method == 'POST':
        form = GuruMapelForm(request.POST)
        if form.is_valid():
            mapel = form.cleaned_data['mapel']
            # Cek jika mapel sudah ada
            if GuruMapel.objects.filter(guru=guru, mapel=mapel).exists():
                messages.error(request, f'Guru sudah mengampu mata pelajaran {mapel.nama_mapel}.')
            else:
                kode_ajar = f"{mapel.kode_mapel}{guru.nip[-4:]}"
                GuruMapel.objects.create(guru=guru, mapel=mapel, kode_ajar=kode_ajar)
                messages.success(request, f'Mata pelajaran {mapel.nama_mapel} berhasil ditambahkan.')
            return redirect('edit_guru', obj_id=guru_id)
    else:
        form = GuruMapelForm()

    context = {
        'title': 'Tambah Mata Pelajaran', 'form': form, 'guru': guru
    }
    return render(request, 'administrasi/guru_mapel_add.html', context)

def guru_mapel_delete(request, gurumapel_id):
    guru_mapel = get_object_or_404(GuruMapel, id=gurumapel_id)
    guru_id = guru_mapel.guru.id
    if request.method == 'POST':
        guru_mapel.delete()
        messages.success(request, 'Mata pelajaran berhasil dihapus.')
        return redirect('edit_guru', obj_id=guru_id)
    return redirect('edit_guru', obj_id=guru_id)

def guru_password_reset(request, guru_id):
    if request.method == 'POST':
        guru = get_object_or_404(UserGuru, id=guru_id)
        guru.set_password(guru.nip)
        guru.save()
        messages.success(request, 'Password berhasil direset sama dengan NIP.')
        return redirect('edit_guru', obj_id=guru_id)
    return HttpResponseForbidden()

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