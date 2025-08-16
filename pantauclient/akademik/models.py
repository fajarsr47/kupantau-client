from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# UNTUK MEMILIH JENIS KELAMIN
class JenisKelamin(models.TextChoices):
    L = 'L', _('Laki-laki')
    P = 'P', _('Perempuan')

# UNTUK MEMILIH STATUS PRESENSI
class PresensiStatus(models.TextChoices):
    H = 'H', _('Hadir')
    S = 'S', _('Sakit')
    I = 'I', _('Izin')
    A = 'A', _('Alpha')

# GURU.
class UserGuru(models.Model):
    nama = models.CharField(max_length=100)
    nip = models.CharField(max_length=20)
    email = models.EmailField(_("email"), max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class ProfileGuru(models.Model):
    guru = models.models.OneToOneField(UserGuru, on_delete=models.CASCADE)
    nuptk = models.CharField(max_length=20)
    jenis_kelamin = models.CharField(max_length=1, choices=JenisKelamin.choices)
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    alamat = models.TextField(max_length=200)
    no_hp = models.CharField(max_length=20)

    def __str__(self):
        return self.guru.nama

class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=100)
    guru = models.OneToOneField(UserGuru, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_kelas

class Siswa(models.Model):
    nama = models.CharField(max_length=100)
    nipd = models.Charfield(max_length=20)
    jenis_kelamin = models.CharField(max_length=1, choices=JenisKelamin.choices)
    nisn = models.CharField(max_length=20)
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    nama_ayah = models.CharField(max_length=100)
    nama_ibu = models.CharField(max_length=100)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE)
    no_siswa = models.CharField(max_length=20)
    no_ortu = models.CharField(max_length=20)

    def __str__(self):
        return self.nama

class PresensiSiswa(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    tanggal = models.DateField(default=timezone.now)
    waktu = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=PresensiStatus.choices)
    keterangan = models.TextField(max_length=200)
    bukti = models.ImageField(upload_to='bukti_presensi/')


