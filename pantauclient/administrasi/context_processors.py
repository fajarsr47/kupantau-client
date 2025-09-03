def global_context(request):
    # GLOBAL CONTEXT VIEW
    tombol_jadwalkelas = ['kelas', 'jampel', 'mapel', 'jadwal']
    tombol_presensi = ['deteksi', 'import_gambar', 'manual']
    return {
        'tombol_kelas': 'Jadwal & Kelas',
        'aktive_dalam_kelas': tombol_jadwalkelas,
        'tombol_presensi': 'Presensi',
        'aktive_dalam_presensi': tombol_presensi,
    }