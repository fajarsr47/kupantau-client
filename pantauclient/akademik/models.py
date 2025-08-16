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

# UNTUK MEMILIH HARI
class Hari(models.TextChoices):
    SENIN = 'Senin', _('Senin')
    SELASA = 'Selasa', _('Selasa')
    RABU = 'Rabu', _('Rabu')
    KAMIS = 'Kamis', _('Kamis')
    JUMAT = 'Jumat', _('Jumat')
    SABTU = 'Sabtu', _('Sabtu')
    MINGGU = 'Minggu', _('Minggu')


class Mapel(models.Model):
    kode_mapel = models.CharField(max_length=5)
    nama_mapel = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_mapel

# GURU.
class UserGuru(models.Model):
    nama = models.CharField(max_length=100)
    nip = models.CharField(max_length=20)
    email = models.EmailField(_("email"), max_length=100)
    password = models.CharField(max_length=100)
    mengajar = models.ManyToManyField(Mapel, through='GuruMapel')
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class ProfileGuru(models.Model):
    guru = models.OneToOneField(UserGuru, on_delete=models.CASCADE)
    nuptk = models.CharField(max_length=20)
    jenis_kelamin = models.CharField(max_length=1, choices=JenisKelamin.choices)
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    alamat = models.TextField(max_length=200)
    no_hp = models.CharField(max_length=20)

    def __str__(self):
        return self.guru.nama

class GuruMapel(models.Model):
    kode_guru_mapel = models.CharField(max_length=6)
    guru = models.ForeignKey(UserGuru, on_delete=models.CASCADE)
    mapel = models.ForeignKey(Mapel, on_delete=models.CASCADE)

    def __str__(self):
        return self.guru.nama + ' | ' + self.mapel.nama_mapel

class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=100)
    guru = models.OneToOneField(UserGuru, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_kelas

class Siswa(models.Model):
    nama = models.CharField(max_length=100)
    nipd = models.CharField(max_length=20)
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

class PresensiSekolah(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    tanggal = models.DateField(default=timezone.now)
    waktu = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=PresensiStatus.choices)
    keterangan = models.TextField(max_length=200)
    bukti = models.ImageField(upload_to='bukti_presensi/', null=True, blank=True)

    def __str__(self):
        return self.siswa.nama + ' - ' + self.tanggal.strftime('%d-%m-%Y') + ' - ' + self.status

class PresensiMapel(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    tanggal = models.DateField(default=timezone.now)
    waktu = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=PresensiStatus.choices)
    keterangan = models.TextField(max_length=200)
    bukti = models.ImageField(upload_to='bukti_presensi/', null=True, blank=True)
    guru_mapel = models.ForeignKey(GuruMapel, on_delete=models.CASCADE)

    def __str__(self):
        return self.siswa.nama + ' - ' + self.tanggal.strftime('%d-%m-%Y') + ' - ' + self.status

class JamPelajaran(models.Model):
    nama_jam = models.CharField(max_length=10)
    jam_mulai = models.TimeField()
    jam_akhir = models.TimeField()
    durasi = models.CharField(max_length=10)


    def __str__(self):
        return self.nama_jam

class Jadwal(models.Model):
    hari = models.CharField(max_length=10, choices=Hari.choices)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE)
    jampel = models.ForeignKey(JamPelajaran, on_delete=models.CASCADE)
    guru_mapel = models.ForeignKey(GuruMapel, on_delete=models.CASCADE)

    def __str__(self):
        return self.hari + ' | ' + self.kelas.nama_kelas + ' - ' + self.guru_mapel.mapel.nama_mapel

class PengumumanStatus(models.TextChoices):
    BERJALAN = 'berjalan', _('Berjalan')
    SELESAI = 'selesai', _('Selesai')

class Pengumuman(models.Model):
    perihal = models.CharField(max_length=100)
    waktu = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=PengumumanStatus.choices)

    guru = models.ForeignKey(UserGuru, on_delete=models.CASCADE)
