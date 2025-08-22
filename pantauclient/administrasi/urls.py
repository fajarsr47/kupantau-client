from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('presensi', views.presensi, name='presensi'),
    path('rekap', views.rekap, name='rekap'),
    path('pengaturan', views.pengaturan, name='pengaturan'),
    path('siswa', views.siswa, name='siswa'),
    path('guru', views.guru, name='guru'),

    # URL untuk Manajemen Jadwal dan Kelas
    path('kelas', views.kelas, name='kelas'),
    path('jadwal', views.jadwal, name='jadwal'),
    path('mapel', views.mapel, name='mapel'),
    path('jampel', views.jampel, name='jampel'),

    # --- URL KHUSUS Guru (Dipindahkan ke atas) ---
    path('guru/tambah/', views.guru_edit, name='tambah_guru'),
    path('guru/edit/<int:obj_id>/', views.guru_edit, name='edit_guru'),

    # --- URL Generik untuk Jadwal dan Kelas ---
    path('<str:page>/tambah/', views.jadwal_edit, name='tambah'),
    path('<str:page>/edit/<int:obj_id>/', views.jadwal_edit, name='edit'),

    # URL Hapus (bisa tetap di sini)
    path('<str:page>/hapus/<int:obj_id>/', views.hapus, name='hapus'),
    
    # URL untuk AJAX
    path('get_guru/', views.get_guru, name='get_guru'),
]