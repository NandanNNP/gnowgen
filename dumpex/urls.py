
from django.contrib import admin
from django.urls import path, include
from core.views import login_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('core/', include('core.urls')),
    path('employee/', include('employee.urls')),
    path('customer/', include('customer.urls')),
    path('manager/', include('manager.urls', namespace='manager')),
    path('admin-module/', include('admin_module.urls')),
    path('wallet/', include('wallet.urls')),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
