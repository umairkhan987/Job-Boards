"""jobBoard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include('hireo.urls')),
    path("account/", include('accounts.urls')),
    path('employer/', include('employer.urls')),
    path('freelancer/', include('freelancers.urls')),
    path('notifications/', include("notification.urls")),
    path('', include("messenger.urls")),

    path('change-the-admin/', admin.site.urls),

    #     REST_API urls
    path("api/", include('hireo.api.urls')),
    path("api/", include("accounts.api.urls")),
    path("api/", include("employer.api.urls")),
    path("api/", include("freelancers.api.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)
    # print("program in debug mode")
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        # print("debug toolbar is present")
        import debug_toolbar

        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
