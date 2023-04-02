from django.urls import path
from . import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Bill API",
      default_version='v1',
      description="Api for bill app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="omanohar15@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('bills/',views.BillListApiView.as_view()),
    path('billunits/',views.BillUnitListApiView.as_view()),
    path('faultbills/',views.FaultBillListApiView.as_view()),
    path('billmeters/',views.BillMeterListApiView.as_view()),
    path('analytics/<str:bill_meter_id>/',views.AmountAnalyticsApiView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]