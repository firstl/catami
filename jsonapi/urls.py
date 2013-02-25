from django.conf.urls import patterns, include, url
from tastypie.api import Api
import collection.api
import catamidb.api
import jsonapi.api
import staging.api

dev_api = Api(api_name='dev')
v1_api = Api(api_name='v1')

dev_api.register(collection.api.CollectionResource())
dev_api.register(catamidb.api.CampaignResource())
dev_api.register(catamidb.api.DeploymentResource())
dev_api.register(catamidb.api.PoseResource())
dev_api.register(catamidb.api.ImageResource())
dev_api.register(catamidb.api.ScientificImageMeasurementResource())
dev_api.register(catamidb.api.ScientificPoseMeasurementResource())
dev_api.register(catamidb.api.ScientificMeasurementTypeResource())

dev_api.register(catamidb.api.AUVDeploymentResource())
dev_api.register(catamidb.api.BRUVDeploymentResource())
dev_api.register(catamidb.api.DOVDeploymentResource())

dev_api.register(jsonapi.api.UserResource())

dev_api.register(staging.api.StagingFilesResource())

urlpatterns = patterns('',
    (r'^$', 'jsonapi.views.help'),
    (r'', include(dev_api.urls)),
    (r'', include(v1_api.urls)),
)
