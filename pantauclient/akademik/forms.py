# pantauclient/akademik/forms.py

from django import forms
from .models import Kelas, Mapel, JamPelajaran, Jadwal, UserGuru, ProfileGuru, GuruMapel

# Atribut CSS umum untuk konsistensi
form_control_attrs = {
    'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-1.5'
}

class KelasForm(forms.ModelForm):
    class Meta:
        model = Kelas
        fields = ['nama_kelas', 'guru']
        widgets = {
            'nama_kelas': forms.TextInput(attrs=form_control_attrs),
            'guru': forms.Select(attrs=form_control_attrs),
        }

class MapelForm(forms.ModelForm):
    class Meta:
        model = Mapel
        fields = ['nama_mapel', 'kode_mapel']
        widgets = {
            'kode_mapel': forms.TextInput(attrs=form_control_attrs),
            'nama_mapel': forms.TextInput(attrs=form_control_attrs),
        }

class JamPelajaranForm(forms.ModelForm):
    class Meta:
        model = JamPelajaran
        fields = ['nama_jam', 'jam_mulai', 'jam_akhir', 'durasi']
        widgets = {
            'nama_jam': forms.TextInput(attrs=form_control_attrs),
            'jam_mulai': forms.TimeInput(attrs={**form_control_attrs, 'type': 'time'}),
            'jam_akhir': forms.TimeInput(attrs={**form_control_attrs, 'type': 'time'}),
            'durasi': forms.TextInput(attrs=form_control_attrs),
        }

class JadwalForm(forms.ModelForm):
    mapel = forms.ModelChoiceField(
        queryset=Mapel.objects.all(),
        widget=forms.Select(attrs=form_control_attrs)
    )
    guru = forms.ModelChoiceField(
        queryset=UserGuru.objects.none(),
        widget=forms.Select(attrs=form_control_attrs)
    )

    class Meta:
        model = Jadwal
        fields = ['hari', 'kelas', 'jampel', 'mapel', 'guru']
        widgets = {
            'hari': forms.Select(attrs=form_control_attrs),
            'kelas': forms.Select(attrs=form_control_attrs),
            'jampel': forms.Select(attrs=form_control_attrs),
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
                self.fields['guru'].queryset = UserGuru.objects.filter(gurumapel__mapel_id=mapel_id).order_by('first_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['guru'].queryset = self.instance.guru_mapel.mapel.userguru_set.order_by('first_name')
            
    def save(self, commit=True):
        mapel = self.cleaned_data.get('mapel')
        guru = self.cleaned_data.get('guru')
        
        guru_mapel, created = GuruMapel.objects.get_or_create(mapel=mapel, guru=guru)
        if created:
             guru_mapel.kode_ajar = f"{mapel.kode_mapel}{guru.nip[-4:]}"
             guru_mapel.save()

        self.instance.guru_mapel = guru_mapel
        return super().save(commit=commit)

# --- FORM UNTUK GURU ---

class UserGuruForm(forms.ModelForm):
    first_name = forms.CharField(label='Nama Lengkap', widget=forms.TextInput(attrs=form_control_attrs))
    password = forms.CharField(
        label='Password',
        widget=forms.TextInput(attrs={**form_control_attrs, 'readonly': True}), 
        required=False
    )
    username = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = UserGuru
        fields = ['first_name', 'username', 'nip', 'email', 'password', 'role']
        widgets = {
            'nip': forms.TextInput(attrs={**form_control_attrs, 'id': 'nip_field'}),
            'email': forms.EmailInput(attrs=form_control_attrs),
            'role': forms.Select(attrs=form_control_attrs),
        }

class ProfileGuruForm(forms.ModelForm):
    class Meta:
        model = ProfileGuru
        fields = ['nuptk', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir', 'alamat', 'no_hp']
        widgets = {
            'nuptk': forms.TextInput(attrs=form_control_attrs),
            'jenis_kelamin': forms.Select(attrs=form_control_attrs),
            'tempat_lahir': forms.TextInput(attrs=form_control_attrs),
            'tanggal_lahir': forms.DateInput(attrs={**form_control_attrs, 'type': 'date'}),
            'alamat': forms.Textarea(attrs={**form_control_attrs, 'rows': 1}),
            'no_hp': forms.TextInput(attrs=form_control_attrs),
        }

class GuruMapelForm(forms.ModelForm):
    class Meta:
        model = GuruMapel
        fields = ['mapel']
        widgets = {
            'mapel': forms.Select(attrs=form_control_attrs),
        }