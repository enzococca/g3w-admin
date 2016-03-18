from django.conf.urls import url
from .api.views import *
from .views import *

urlpatterns = [

    # g3w-client bootstrap
    #TODO: set view for url
    url(r'^map/(?P<group_slug>[-_\w\d]+)/(?P<project_type>[-_\w\d]+)/(?P<project_id>[-_\w\d]+)/$', ClientView.as_view(), name='group-project-map'),

    # api urls
    #test djangorest framework
    url(r'^api/test/$', TestApi.as_view()),
    url(r'^api/config/(?P<group_slug>[-_\w\d]+)/(?P<project_type>[-_\w\d]+)/(?P<project_id>[-_\w\d]+)/$', ClientConfigApiView.as_view(), name='group-project-map-config'),
]