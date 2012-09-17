from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^player/(?P<player_id>\d+)/$', 'draftapp.views.player'),
    url(r'^team/(?P<team_id>\d+)/$$', 'draftapp.views.team'),
    url(r'^players/$', 'draftapp.views.player_filter'),
    url(r'^teams/$', 'draftapp.views.teams'),
    url(r'^form/player_filter$', 'draftapp.views.player_filter_submit'),
    url(r'^form/player_ownership$', 'draftapp.views.ownership_form_submit'),
    url(r'^form/player_search$', 'draftapp.views.player_search'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '/home/griffin/django/tnpldraft/static'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
