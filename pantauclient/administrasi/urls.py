from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('test', views.testapp, name='test'),
    path('presensi', views.presensi, name='presensi'),
    path('rekap', views.rekap, name='rekap'),
    path('pengaturan', views.pengaturan, name='pengaturan'),
]