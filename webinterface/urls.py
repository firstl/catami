"""URL Mappings for the webinterface application.
"""
__author__ = 'Ariell Friedman'

from django.conf.urls import patterns, url, include
#from django.contrib.auth.models import User
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('webinterface.views',
    url(r'^$', 'index', name='index'),

    #front page data views
    #url(r'^front_login_panel$', 'front_login_panel'),
    #url(r'^front_newdata_panel$', 'front_newdata_panel'),
    #url(r'^front_imageview_panel$', 'front_imageview_panel'),

    #Info Pages
    url(r'^faq', 'faq'),
    url(r'^contact', 'contact'),
    url(r'^howto','howto'),
    url(r'^about','about'),

    url(r'^explore$', 'explore'),
    url(r'^explore_campaign/(?P<campaign_id>\d+)/$', 'explore_campaign'),

    #url(r'^viewcollection$', 'viewcollection'),

    #Staging
    url(r'^staging/', include('staging.urls')),

    #Collection List Views
    url(r'^collections$', 'collections'),
    url(r'^collections/(?P<collection_id>\d+)/$', 'view_collection'),
    url(r'^my_collections$', 'my_collections'),
#    url(r'^my_collections_all$', 'my_collections_all'),
#    url(r'^my_collections_recent$', 'my_collections_recent'),
    url(r'^public_collections$', 'public_collections'),
#    url(r'^public_collections_all$', 'public_collections_all'),
#    url(r'^public_collections_recent$', 'public_collections_recent'),

    #Collection Object Views
    url(r'^view_subset$', 'view_subset'),
    url(r'^all_subsets/(?P<collection_id>\d+)/$', 'all_subsets'),
    url(r'^my_subsets$', 'my_subsets'),
    url(r'^public_subsets$', 'public_subsets'),
    url(r'^imageview$', 'image_view'),
    url(r'^imageannotate$', 'image_annotate'),
    url(r'^imageedit$', 'image_edit'),
    
    #force views
    url(r'^data/$', 'data'),
    url(r'^data/auvdeployments/$', 'auvdeployments'),
    url(r'^data/auvdeployments/map/$', 'auvdeployments_map'),
    url(r'^data/auvdeployments/(?P<auvdeployment_id>\d+)/$', 'auvdeployment_display'),
    url(r'^data/auvdeployments/(?P<auvdeployment_id>\d+)/detail/$', 'auvdeployment_detail'),
    url(r'^data/auvdeployments/(?P<auvdeployment_id>\d+)/images/$', 'auvimage_list'),
    url(r'^data/auvdeployments/(?P<auvdeployment_id>\d+)/annotationview/(?P<image_index>\d+)/$', 'annotationview'),

    url(r'^data/bruvdeployments/$', 'bruvdeployments'),
    url(r'^data/bruvdeployments/map/$', 'bruvdeployments_map'),
    url(r'^data/bruvdeployments/(?P<bruvdeployment_id>\d+)/$', 'bruvdeployment_detail'),

    url(r'^data/dovdeployments/$', 'dovdeployments'),
    url(r'^data/dovdeployments/(?P<dovdeployment_id>\d+)/$', 'dovdeployment_detail'),

    url(r'^data/tvdeployments/$', 'tvdeployments'),
    url(r'^data/tvdeployments/(?P<tvdeployment_id>\d+)/$', 'tvdeployment_detail'),

    url(r'^data/tideployments/$', 'tideployments'),
    url(r'^data/tideployments/(?P<tideployment_id>\d+)/$', 'tideployment_detail'),

    url(r'^data/deployments/$', 'deployments'),
    url(r'^data/deployments/map/$', 'deployments_map'),

    url(r'^data/campaigns/$', 'campaigns'),
    url(r'^data/campaigns/(?P<campaign_id>\d+)/$', 'campaign_detail'),

    #API docs
    url(r'^api/', include('jsonapi.urls')),

    #dbadmin tool
    url(r'^report/', include('dbadmintool.urls')),

    # userena
    (r'^accounts/', include('accounts.urls')),
    url(r'^logout/$', 'logout_view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #admin interface
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
         {'template_name': 'registration/login.html'}),
#     url(r'^logout/$', 'catamiPortal.views.logout_view'),
)