from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/', include('users.urls')),
    path(r'api/', include('api.urls'))
]
