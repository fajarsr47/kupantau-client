# pantauclient/akademik/forms.py

from profile import Profile
from django import forms
from .models import Kelas, Mapel, JamPelajaran, Jadwal, UserGuru, GuruMapel, ProfileGuru


class KelasForm(forms.ModelForm):
    class Meta:
        model = Kelas
        fields = ['nama_kelas', 'guru', 'nama_grup_wa']
        widgets = {
            'nama_kelas': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'guru': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'nama_grup_wa': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
        }

class MapelForm(forms.ModelForm):
    class Meta:
        model = Mapel
        fields = ['nama_mapel', 'kode_mapel']
        widgets = {
            'kode_mapel': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'nama_mapel': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
        }

class JamPelajaranForm(forms.ModelForm):
    class Meta:
        model = JamPelajaran
        fields = ['nama_jam', 'jam_mulai', 'jam_akhir', 'durasi']
        widgets = {
            'nama_jam': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'jam_akhir': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'durasi': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
        }

class JadwalForm(forms.ModelForm):
    mapel = forms.ModelChoiceField(
        queryset=Mapel.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'})
    )
    guru = forms.ModelChoiceField(
        queryset=UserGuru.objects.none(),
        widget=forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'})
    )

    class Meta:
        model = Jadwal
        fields = ['hari', 'kelas', 'jampel', 'mapel', 'guru']
        widgets = {
            'hari': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'kelas': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
            'jampel': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['mapel'].initial = self.instance.guru_mapel.mapel
            self.fields['guru'].queryset = UserGuru.objects.filter(gurumapel__mapel=self.instance.guru_mapel.mapel)
            self.fields['guru'].initial = self.instance.guru_mapel.guru
        
        if 'mapel' in self.data:
            try:
                mapel_id = int(self.data.get('mapel'))
                self.fields['guru'].queryset = UserGuru.objects.filter(gurumapel__mapel_id=mapel_id).order_by('nama')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['guru'].queryset = self.instance.guru_mapel.mapel.userguru_set.order_by('nama')
            
    def save(self, commit=True):
        mapel = self.cleaned_data.get('mapel')
        guru = self.cleaned_data.get('guru')
        
        # Cek apakah guru mengajar mapel yang dipilih
        if not GuruMapel.objects.filter(mapel=mapel, guru=guru).exists():
            # Jika tidak ada, Anda bisa menampilkan error atau membuat objek GuruMapel baru
            # Di sini kita akan membuatnya jika belum ada
            guru_mapel, created = GuruMapel.objects.get_or_create(mapel=mapel, guru=guru, defaults={'kode_ajar': 'Auto'}) # Ganti 'Auto' dengan logika kode ajar Anda
        else:
            guru_mapel = GuruMapel.objects.get(mapel=mapel, guru=guru)

        self.instance.guru_mapel = guru_mapel
        return super().save(commit=commit)

class UserGuruForm(forms.ModelForm):
    class Meta:
        model = UserGuru
        fields = ['nama', 'nip', 'email', 'password', 'role', 'mengajar']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-input'}),
            'nip': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'password': forms.PasswordInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
            'mengajar': forms.SelectMultiple(attrs={'class': 'form-input'}),
        }

class ProfileGuruForm(forms.ModelForm):
    class Meta:
        model = ProfileGuru
        fields = ['nuptk', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir', 'alamat', 'no_hp']
        widgets = {
            'nuptk': forms.TextInput(attrs={'class': 'form-input'}),
            'jenis_kelamin': forms.Select(attrs={'class': 'form-input'}),
            'tempat_lahir': forms.TextInput(attrs={'class': 'form-input'}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'alamat': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'no_hp': forms.TextInput(attrs={'class': 'form-input'}),
        }