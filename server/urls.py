"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve

from . import views

import re

_prefix = f'{settings.JWDJ_SUBPATH.strip("/")}/' if settings.JWDJ_SUBPATH else ''

urlpatterns = [
    path(f'{_prefix}api/session', views.session_setup),
    path(f'{_prefix}api/new', views.new_poll),
    path(f'{_prefix}api/my-polls', views.my_polls),
    path(f'{_prefix}api/poll/<str:poll_id>', views.get_poll),
    path(f'{_prefix}api/poll/<str:poll_id>/exists', views.get_poll_exists),
    path(f'{_prefix}api/poll/<str:poll_id>/vote', views.do_vote),
    path(f'{_prefix}api/poll/<str:poll_id>/update', views.do_update),
    path(f'{_prefix}api/poll/<str:poll_id>/close', views.do_close),
    path(f'{_prefix}api/poll/<str:poll_id>/reopen', views.do_reopen),
    path(f'{_prefix}api/poll/<str:poll_id>/delete', views.do_delete),
]

# Static files
if settings.JWDJ_SERVE_STATIC_FILES:
    urlpatterns += [
        path(f'{_prefix}', serve, {'path': 'index.html', 'document_root': settings.JWDJ_CLIENT_DIST}),
        path(f'{_prefix}favicon.ico', serve, {'path': 'favicon.ico', 'document_root': settings.JWDJ_CLIENT_DIST}),
        re_path(fr'^{re.escape(_prefix)}js/(?P<path>.*)$', serve, {'document_root': settings.JWDJ_CLIENT_DIST / 'js'}),
        re_path(fr'^{re.escape(_prefix)}css/(?P<path>.*)$', serve, {'document_root': settings.JWDJ_CLIENT_DIST / 'css'}),
        re_path(fr'^{re.escape(_prefix)}(?!api/)(?P<path>.*)$', serve, {'path': 'index.html', 'document_root': settings.JWDJ_CLIENT_DIST}),
    ]
