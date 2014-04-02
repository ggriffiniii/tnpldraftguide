from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^player/(?P<player_id>\d+)/$',
        'tnpldraft.draftapp.views.player', name='player-detail'),
    url(r'^team/(?P<team_id>\d+)/$',
        'tnpldraft.draftapp.views.team', name='team-detail'),
    url(r'^players/$',
        'tnpldraft.draftapp.views.player_filter', name='player-list'),
    url(r'^teams/$',
        'tnpldraft.draftapp.views.teams', name='team-list'),
    url(r'^form/player_filter$',
        'tnpldraft.draftapp.views.player_filter_submit',
        name='player-filter'),
    url(r'^form/player_dollar_value$',
        'tnpldraft.draftapp.views.player_dollar_value_submit',
        name='player-dollar-value'),
    url(r'^form/player_ownership$',
        'tnpldraft.draftapp.views.ownership_form_submit',
        name='player-ownership'),
    url(r'^form/player_search$',
        'tnpldraft.draftapp.views.player_search',
        name='player-search'),
    url(r'^form/update_batting_proj$',
        'tnpldraft.draftapp.views.update_batting_proj',
        name='update-batting-proj'),
    url(r'^form/update_pitching_proj$',
        'tnpldraft.draftapp.views.update_pitching_proj',
        name='update-pitching-proj'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '/home/glenng/git/tnpldraft/tnpldraft/static'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)
