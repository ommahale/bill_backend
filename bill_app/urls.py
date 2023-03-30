from django.urls import path
from . import views

urlpatterns = [
    path('bills/',views.BillListApiView.as_view()),
    path('billunits/',views.BillUnitListApiView.as_view()),
]