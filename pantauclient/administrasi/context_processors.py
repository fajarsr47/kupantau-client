def global_context(request):
    # GLOBAL CONTEXT VIEW
    tombolan = ['kelas', 'jampel', 'mapel', 'jadwal']
    return {
        'tombol_kelas': 'Jadwal & Kelas',
        'aktive_dalam_kelas': tombolan,
    }