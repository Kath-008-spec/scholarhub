from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ScholarHub.urls')),
]

handler403 = 'ScholarHub.views.custom_permission_denied_view'
handler404 = 'ScholarHub.views.custom_page_not_found_view'
handler500 = 'ScholarHub.views.custom_server_error_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)