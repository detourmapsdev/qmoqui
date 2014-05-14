from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import os
from os.path import dirname
basedir = dirname(__file__)
from django.views.static import serve
from django.http import HttpResponse
static = '%s/qrmap/static/' % basedir
media = '%s/media/' % basedir

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'qrdetourmaps.views.home', name='home'),
    # url(r'^qrdetourmaps/', include('qrdetourmaps.foo.urls')),
    #media and static
    url(r'^static/(?P<path>.*)$', serve, {'document_root': static, 'show_indexes': True}),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': media, 'show_indexes': True}),
    #web
    url(r'^', include('qrmap.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /media/\nDisallow: /static/\nDisallow: /admin/", mimetype="text/plain")),
)
