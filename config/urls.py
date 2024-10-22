from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from main.views import MainView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('authen.urls')),
    path('', MainView.as_view(), name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
