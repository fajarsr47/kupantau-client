from django.urls import path
from . import views

urlpatterns = [
    # =========================
    #   Dashboard
    # =========================
    path('', views.index, name='index'),

    # =========================
    #   Presensi
    # =========================
    path('deteksi', views.deteksi, name='deteksi'),
    # Presensi deteksi realtime
    path('presensi/deteksi/frame', views.deteksi_frame, name='deteksi_frame'),
    path('presensi/deteksi/save', views.deteksi_save, name='deteksi_save'),
    path('presensi/deteksi/resolve', views.deteksi_resolve, name='deteksi_resolve'),

    path('import_gambar', views.import_gambar, name='import_gambar'),
    
    path('manual', views.manual, name='manual'),
    path('presensi/manual/get-siswa', views.get_siswa_presensi_manual, name='get_siswa_presensi_manual'),
    path('presensi/manual/save', views.save_presensi_manual, name='save_presensi_manual'),

    # =========================
    #   Rekap
    # =========================
    path('rekap', views.rekap, name='rekap'),
    path('rekap/get-data', views.get_rekap_data, name='get_rekap_data'),
    # -- excel --
    path('rekap/export-excel', views.export_rekap_excel, name='export_rekap_excel'),

    # =========================
    #   Pengaturan
    # =========================
    path('pengaturan', views.pengaturan, name='pengaturan'),

    # =========================
    #   Siswa
    # =========================
    path('siswa', views.siswa, name='siswa'),
    path('get_siswa/', views.get_siswa, name='get_siswa'),
    path('siswa/import/', views.siswa_import, name='siswa_import'),

    # =========================
    #   Guru
    # =========================
    path('guru', views.guru, name='guru'),
    path('guru/tambah/', views.guru_edit, name='tambah_guru'),
    path('guru/edit/<int:obj_id>/', views.guru_edit, name='edit_guru'),
    path('guru/<int:guru_id>/mapel/tambah/', views.guru_mapel_tambah, name='tambah_mapel_guru'),
    path('guru/<int:guru_id>/mapel/<int:gm_id>/hapus/', views.guru_mapel_hapus, name='hapus_mapel_guru'),
    # URL untuk AJAX
    path('get_guru/', views.get_guru, name='get_guru'),
    
    
    # =========================
    #   Jadwal dan Kelas
    # =========================
    path('kelas', views.kelas, name='kelas'),
    path('jadwal', views.jadwal, name='jadwal'),
    path('mapel', views.mapel, name='mapel'),
    path('jampel', views.jampel, name='jampel'),
    path('<str:page>/tambah/', views.jadwal_edit, name='tambah'),
    path('<str:page>/edit/<int:obj_id>/', views.jadwal_edit, name='edit'),
    path('<str:page>/hapus/<int:obj_id>/', views.hapus, name='hapus'),
]