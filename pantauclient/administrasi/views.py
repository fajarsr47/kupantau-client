import re
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from akademik.models import Kelas, Mapel, JamPelajaran, Jadwal, UserGuru, ProfileGuru, GuruMapel
from akademik.forms import KelasForm, MapelForm, JamPelajaranForm, JadwalForm, UserGuruForm, ProfileGuruForm
from django.db import transaction
from django.contrib.auth.hashers import make_password

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
    """
    Admin:
    - TIDAK bisa ganti password lewat form.
    - CREATE: password = NIP (di-hash).
    - RESET PASSWORD: password = NIP (di-hash).
    """
    if obj_id:
        user_guru = get_object_or_404(UserGuru, id=obj_id)
        profile_guru = getattr(user_guru, 'profileguru', None) or ProfileGuru(guru=user_guru)
    else:
        user_guru = UserGuru()
        profile_guru = ProfileGuru()

    if request.method == 'POST':
        # Tombol reset password
        if 'reset_password' in request.POST and (obj_id or user_guru.id):
            guru_obj = user_guru if user_guru.id else get_object_or_404(UserGuru, id=obj_id)
            guru_obj.password = make_password(guru_obj.nip)
            guru_obj.save(update_fields=['password'])
            messages.success(request, 'Password berhasil di-reset ke NIP.')
            return redirect('edit_guru', obj_id=guru_obj.id)

        user_form = UserGuruForm(request.POST, instance=user_guru)
        profile_form = ProfileGuruForm(request.POST, instance=profile_guru)

        # === Penting: longgarkan requirement tanpa ubah tampilan ===
        if 'password' in user_form.fields:
            user_form.fields['password'].required = False
        if 'mengajar' in user_form.fields:
            user_form.fields['mengajar'].required = False  # karena tidak ada inputnya di template

        if user_form.is_valid() and profile_form.is_valid():
            is_create = user_guru.id is None
            user = user_form.save(commit=False)

            if is_create:
                # password awal mengikuti NIP
                user.password = make_password(user.nip)
            else:
                # Saat edit, jangan sentuh password
                original = UserGuru.objects.get(id=user_guru.id)
                user.password = original.password

            user.save()
            # relasi M2M (abaikan kalau tidak ada inputnya—tidak mengapa)
            try:
                user_form.save_m2m()
            except Exception:
                pass

            profile = profile_form.save(commit=False)
            profile.guru = user
            profile.save()

            messages.success(request, 'Data guru berhasil disimpan.')
            return redirect('guru')
        else:
            # Tampilkan error ke user (tanpa ubah UI lain)
            if user_form.errors:
                messages.error(request, f"User form error: {user_form.errors.as_text()}")
            if profile_form.errors:
                messages.error(request, f"Profile form error: {profile_form.errors.as_text()}")

    else:
        user_form = UserGuruForm(instance=user_guru)
        profile_form = ProfileGuruForm(instance=profile_guru)
        # Longgarkan juga di GET agar konsisten (tidak wajib diisi)
        if 'password' in user_form.fields:
            user_form.fields['password'].required = False
        if 'mengajar' in user_form.fields:
            user_form.fields['mengajar'].required = False

    context = {
        'title': 'Manajemen Data Guru',
        'user_form': user_form,
        'profile_form': profile_form,
        'page': 'guru',
        'obj': user_guru,
        'list_gurumapel': GuruMapel.objects.filter(guru=user_guru).select_related('mapel'),
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

@transaction.atomic
def guru_mapel_tambah(request, guru_id):
    guru = get_object_or_404(UserGuru, id=guru_id)
    semua_mapel = Mapel.objects.all().order_by('nama_mapel')

    if request.method == 'POST':
        mapel_id = request.POST.get('mapel')
        if not mapel_id:
            messages.error(request, 'Silakan pilih mata pelajaran.')
            return redirect('tambah_mapel_guru', guru_id=guru.id)

        mapel = get_object_or_404(Mapel, id=mapel_id)

        # kode_ajar = kode_mapel + 3 digit terakhir dari NIP (hanya digit)
        nip_digits = re.sub(r'\D', '', guru.nip or '')
        suffix = nip_digits[-3:] if len(nip_digits) >= 3 else nip_digits
        kode_ajar = f"{mapel.kode_mapel}{suffix}"

        # Cegah duplikasi (guru-mapel yang sama)
        if GuruMapel.objects.filter(guru=guru, mapel=mapel).exists():
            messages.warning(request, 'Guru sudah mengampu mapel tersebut.')
            return redirect('edit_guru', obj_id=guru.id)

        gm = GuruMapel.objects.create(
            guru=guru,
            mapel=mapel,
            kode_ajar=kode_ajar
        )
        messages.success(request, f"Mapel '{mapel.nama_mapel}' ditambahkan. Kode ajar: {gm.kode_ajar}")
        return redirect('edit_guru', obj_id=guru.id)

    # GET → tampilkan form pilih mapel
    context = {
        'title': 'Tambah Mapel Diampu',
        'guru': guru,
        'semua_mapel': semua_mapel,
    }
    return render(request, 'administrasi/guru_mapel_tambah.html', context)

@transaction.atomic
def guru_mapel_hapus(request, guru_id, gm_id):
    guru = get_object_or_404(UserGuru, id=guru_id)
    gm = get_object_or_404(GuruMapel, id=gm_id, guru=guru)
    gm.delete()
    messages.success(request, 'Mapel berhasil dihapus dari daftar ampuan.')
    return redirect('edit_guru', obj_id=guru.id)