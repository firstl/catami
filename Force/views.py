"""@brief Django views generation (html) for Catami data.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""

# Create your views here.
from django.template import RequestContext
#from django.http import Http404
from django.shortcuts import render_to_response, redirect
#from django.core import serializers
#from django.contrib.gis.geos import GEOSGeometry
#from django.contrib.gis.geos import *
from vectorformats.Formats import Django, GeoJSON
from django.contrib.gis.geos import fromstr

from Force.models import Campaign, AUVDeployment,BRUVDeployment, DOVDeployment, Deployment, StereoImage


def index(request):
    """@brief Root html for Catami data

    """
    context = {}

    return render_to_response(
        'Force/index.html',
        context,
        RequestContext(request))


def add_campaign(request):
    """@brief redirect to admin view to create a campaign object

    """

    return redirect('/admin/Force/campaign/add/')  # Redirect after POST


def deployments(request):
    """@brief Deployment list html for entire database

    """
    auv_deployment_list = AUVDeployment.objects.all()
    bruv_deployment_list = BRUVDeployment.objects.all()
    dov_deployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'Force/DeploymentIndex.html',
        {'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list},
        context_instance=RequestContext(request))


def deployments_map(request):
    """@brief Deployment map html for entire database

    """
    latest_deployment_list = Deployment.objects.all()
    return render_to_response(
        'Force/DeploymentMap.html',
        {'latest_deployment_list': latest_deployment_list},
        context_instance=RequestContext(request))


def auvdeployments(request):
    """@brief AUV Deployment list html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'Force/auvDeploymentIndex.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployments_map(request):
    """@brief AUV Deployment map html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'Force/auvDeploymentMap.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployment_detail(request, auvdeployment_id):
    """@brief AUV Deployment html for a specifed AUV deployment

    """
    # the hard way. All columns in the geojson
    #djf=Django.Django(geodjango="transect_shape", properties=[])

    #geoj = GeoJSON.GeoJSON()
    #deployment_as_geojson = geoj.encode(djf.decode([AUVDeployment.objects.get(id=auvdeployment_id)]))

    auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)

    # the easy way is to just return
    # auvdeployment_object.transect_shape.geojson
    return render_to_response(
        'Force/auvdeploymentInstance.html',
        {'auvdeployment_object': auvdeployment_object,
        'deployment_as_geojson': auvdeployment_object.transect_shape.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def bruvdeployments(request):
    """@brief BRUV Deployment list html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'Force/bruvDeploymentIndex.html',
        {'latest_bruvdeployment_list': latest_bruvdeployment_list},
        context_instance=RequestContext(request))


def bruvdeployments_map(request):
    """@brief BRUV Deployment map html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'Force/bruvDeploymentMap.html',
        {'latest_bruvdeployment_list': latest_bruvdeployment_list},
        context_instance=RequestContext(request))


def bruvdeployment_detail(request, bruvdeployment_id):
    """@brief BRUV Deployment html for a specifed AUV deployment

    """

    bruvdeployment_object = BRUVDeployment.objects.get(id=bruvdeployment_id)
    image_list = StereoImage.objects.filter(deployment=bruvdeployment_id)

    return render_to_response(
        'Force/bruvdeploymentInstance.html',
        {'bruvdeployment_object': bruvdeployment_object,
        'deployment_as_geojson': bruvdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def campaigns(request):
    """@brief Campaign list html for entire database

    """
    latest_campaign_list = Campaign.objects.all()
    campaign_rects=list()

    for campaign in latest_campaign_list:
        auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign)
        bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign)
        dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign)
        if(len(auv_deployment_list) > 0):
            sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
        if(len(bruv_deployment_list) > 0):
            sm = fromstr('MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)


    return render_to_response(
        'Force/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list,
        'campaign_rects':campaign_rects},
        context_instance=RequestContext(request))


def campaign_detail(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """
    campaign_object = Campaign.objects.get(id=campaign_id)
    campaign_rects=list()

    #djf = Django.Django(geodjango="extent", properties=[''])

    auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign_object)
    bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign_object)
    dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign_object)

    #geoj = GeoJSON.GeoJSON()
    #sm = AUVDeployment.objects.filter(transect_shape__bbcontains=pnt_wkt)
    #sm = AUVDeployment.objects.all().extent
    #sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())

    if(len(auv_deployment_list) > 0):
        sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    if(len(bruv_deployment_list) > 0):
        sm = fromstr('MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)

    return render_to_response(
        'Force/campaignInstance.html',
        {'campaign_object': campaign_object,
        'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list,
        'campaign_as_geojson': sm.envelope.geojson},
        context_instance=RequestContext(request))
