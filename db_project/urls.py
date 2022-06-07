from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index',),
    re_path(r'get\/\d+', views.get, name='get'),
    path(r'form', views.form, name='form'),
    path(r'form/result', views.addResult, name='addResult'),
    path(r'form/unit', views.addUnit, name='addUnit'),
    path(r'form/measurement_type', views.addMeasurementType, name='addMeasurementType'),
    path(r'form/result_type', views.addResultType, name='addResultType')
]
