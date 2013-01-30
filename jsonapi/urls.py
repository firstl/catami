from django.conf.urls import patterns, include, url
from tastypie.api import Api
import collection.api
import Force.api
import jsonapi.api

dev_api = Api(api_name='dev')
v1_api = Api(api_name='v1')

dev_api.register(collection.api.CollectionResource())
dev_api.register(Force.api.CampaignResource())
dev_api.register(Force.api.DeploymentResource())
dev_api.register(Force.api.ImageResource())

dev_api.register(Force.api.AUVDeploymentResource())
dev_api.register(Force.api.BRUVDeploymentResource())
dev_api.register(Force.api.DOVDeploymentResource())

dev_api.register(jsonapi.api.UserResource())

urlpatterns = patterns('',
    (r'^$', 'jsonapi.views.help'),
    (r'', include(dev_api.urls)),
    (r'', include(v1_api.urls)),
)