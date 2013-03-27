# Create your views here.
from django.template import RequestContext

from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import guardian
from guardian.shortcuts import get_objects_for_user
from waffle.decorators import waffle_switch
from django.core.urlresolvers import reverse
import logging

#for the geoserver proxy
from django.views.decorators.csrf import csrf_exempt
import httplib2

#not API compliant - to be removed after the views are compliant
from catamidb.models import Pose, Image, Campaign, AUVDeployment, \
    BRUVDeployment, DOVDeployment, Deployment, TIDeployment, TVDeployment
from django.contrib.gis.geos import fromstr
from django.db.models import Max, Min
import simplejson
from django.conf import settings
from collection.api import CollectionResource
from collection.models import Collection, CollectionManager

#account management
from django.contrib.auth import logout

logger = logging.getLogger(__name__)


@waffle_switch('Collections')
class CreateCollectionForm(forms.Form):
    deployment_ids = forms.CharField()
    collection_name = forms.CharField()


class CreateWorksetForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()
    ispublic = forms.CheckboxInput()
    c_id = forms.IntegerField()
    n = forms.IntegerField()


#front page and zones
def index(request):
    """@brief returns root catami html
    """
    return render_to_response('webinterface/index.html',

                              RequestContext(request))
# Account stuff
def logout_view(request):
    """@brief returns user to html calling the logout action

    """
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# Info pages
def faq(request):
    return render_to_response('webinterface/faq.html', {},
                              RequestContext(request))


def contact(request):
    return render_to_response('webinterface/contact.html', {},
                              RequestContext(request))


def about(request):
    return render_to_response('webinterface/about.html', {},
                              RequestContext(request))


def howto(request):
    return render_to_response('webinterface/howto.html', {},

                              RequestContext(request))


# Explore pages
def explore(request):
    """@brief Campaign list html for entire database

    """
    return render_to_response('webinterface/explore.html',
                              {'WMS_URL': settings.WMS_URL,
                               'WMS_layer_name': settings.WMS_LAYER_NAME},
                              context_instance=RequestContext(request))


# Explore pages
def explore_campaign(request, campaign_id):
    return render_to_response('webinterface/explore.html', {},
                              context_instance=RequestContext(request))

# Collection pages
@waffle_switch('Collections')
def projects(request):
#    my_collections_error = ''
#    public_collections_error =''
#
#    collection_list = CollectionResource()
#    try:
#        cl_my_rec = collection_list.obj_get_list(request, owner=request.user.id, parent=None)
#        if (len(cl_my_rec) == 0):
#            my_collections_error = 'Sorry, you don\'t seem to have any collections in your account.'
#
#    except:
#        cl_my_rec = ''
#        if (request.user.is_anonymous):
#            my_collections_error = 'Sorry, you dont appear to be logged in. Please login and try again.'
#        else:
#            my_collections_error = 'An undetermined error has occured. Please contact support'
#
#    try:
#        cl_pub_rec = collection_list.obj_get_list(request, is_public=True, parent=None)
#        if (len(cl_pub_rec) == 0):
#            public_collections_error = 'Sorry, there don\'t seem to be any public collections right now.'
#
#    except:
#        cl_pub_rec = ''
#        if (request.user.is_anonymous):
#            public_collections_error = 'Sorry, public collections arent working for anonymous users right now. Please login and try again.'
#        else:
#            public_collections_error = 'An undetermined error has occured. Please contact support'

    return render_to_response('webinterface/projects.html',
                              #        {"my_rec_cols": cl_my_rec,
                              #         "my_collections_error": my_collections_error,
                              #         "pub_rec_cols": cl_pub_rec,
                              #         "public_collections_error":public_collections_error,
                              {'WMS_URL': settings.WMS_URL,
                               #imported from settings
                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME},
                              RequestContext(request))

# @waffle_switch('Collections')
# def my_collections(request):
#     error_description = ''
#
#     collection_list = CollectionResource()
#
#     try:
#         cl = collection_list.obj_get_list(request, owner=request.user.id)
#         if (len(cl) == 0):
#             error_description = 'Sorry, you don\'t seem to have any collections in your account.'
#     except:
#         cl = ''
#         if (request.user.is_anonymous):
#             error_description = 'Sorry, you dont appear to be logged in. Please login and try again.'
#         else:
#             error_description = 'An undetermined error has occured. Please contact support'
#
#     return render_to_response('webinterface/mycollections.html',
#         {"collections": cl,
#         "listname":"cl_pub_all",
#         "error_description":error_description},
#         RequestContext(request))
#
# @waffle_switch('Collections')
# def public_collections(request):
#     error_description = ''
#
#     collection_list = CollectionResource()
#     try:
#         cl = collection_list.obj_get_list(request, is_public=True)
#         if (len(cl) == 0):
#             error_description = 'Sorry, there don\'t seem to be any public collections right now.'
#     except:
#         cl = ''
#         if (request.user.is_anonymous):
#             error_description = 'Sorry, public collections arent working for anonymous users right now. Please login and try again.'
#         else:
#             error_description = 'An undetermined error has occured. Please contact support'
#
#     return render_to_response('webinterface/publiccollections.html',
#         {"collections": cl,
#          "listname":"cl_pub_all",
#         "error_description":error_description},
#          RequestContext(request))

## view collection table views
def public_collections_all(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list()
    return render_to_response('webinterface/publiccollections.html', {"collections": cl, "listname":"cl_pub_all"}, RequestContext(request))

@waffle_switch('Collections')
def view_collection(request, collection_id):
#    return render_to_response('webinterface/viewcollection.html',
    return render_to_response('webinterface/viewcollectionalternative.html',
                              {"collection_id": collection_id,
                               'WMS_URL': settings.WMS_URL,
                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME},
                              RequestContext(request))


@waffle_switch('Collections')
def view_workset(request, collection_id, workset_id):
#    return render_to_response('webinterface/viewcollection.html',
    return render_to_response('webinterface/viewworkset.html',
                              {"collection_id": collection_id,
                               "workset_id": workset_id,
                               'WMS_URL': settings.WMS_URL,
                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME},
                              RequestContext(request))


# view collection table views
# def public_collections_all(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list()
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_all"}, RequestContext(request))
#
# def public_collections_recent(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list()
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_rec"}, RequestContext(request))
#
# def my_collections_all(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list(request,owner=request.user.id)
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_all"}, RequestContext(request))
#
# def my_collections_recent(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list(request,owner=request.user.id)
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_rec"}, RequestContext(request))

# collection object tasks
@waffle_switch('Collections')
def delete_collection(request):
    return None


@waffle_switch('Collections')
def flip_public_collection(request):
    return None


# Subset pages
@waffle_switch('Collections')
def view_subset(request):
    return render_to_response('webinterface/viewsubset.html', {},
                              RequestContext(request))


@waffle_switch('Collections')
def all_subsets(request, collection_id):
    return render_to_response('webinterface/allsubsets.html',
                              {"collection_id": collection_id},
                              RequestContext(request))


@waffle_switch('Collections')
def my_subsets(request):
    return render_to_response('webinterface/mysubsets.html', {},
                              RequestContext(request))


@waffle_switch('Collections')
def public_subsets(request):
    return render_to_response('webinterface/publicsubsets.html', {},
                              RequestContext(request))


# Single image pages
def image_view(request):
    return render_to_response('webinterface/imageview.html', {},
                              RequestContext(request))


def image_annotate(request):
    return render_to_response('webinterface/imageannotate.html', {},
                              RequestContext(request))


def image_edit(request):
    return render_to_response('webinterface/imageedit.html', {},
                              RequestContext(request))


#Force views from old view setup (NOT API COMPLIANT)
def data(request):
    return render_to_response('webinterface/Force_views/index.html', {},
                              RequestContext(request))


def deployments(request):
    """@brief Deployment list html for entire database

    """
    auv_deployment_list = AUVDeployment.objects.all()
    bruv_deployment_list = BRUVDeployment.objects.all()
    dov_deployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentIndex.html',
        {'auv_deployment_list': auv_deployment_list,
         'bruv_deployment_list': bruv_deployment_list,
         'dov_deployment_list': dov_deployment_list},
        context_instance=RequestContext(request))


def deployments_map(request):
    """@brief Deployment map html for entire database

    """
    latest_deployment_list = Deployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentMap.html',
        {'latest_deployment_list': latest_deployment_list},
        context_instance=RequestContext(request))


def auvdeployments(request):
    """@brief AUV Deployment list html for entire database

    """
    user = request.user

    #just make sure we get the anonymous user from the database - so we can user permissions
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    latest_campaign_list = get_objects_for_user(user, [
        'catamidb.view_campaign'])

    print latest_campaign_list

    latest_auvdeployment_list = AUVDeployment.objects.filter(campaign__in=latest_campaign_list)

    return render_to_response(
        'webinterface/Force_views/auvDeploymentIndex.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployments_map(request):
    """@brief AUV Deployment map html for entire database

    """
    user = request.user

    #just make sure we get the anonymous user from the database - so we can user permissions
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    latest_campaign_list = get_objects_for_user(user, [
        'catamidb.view_campaign'])

    latest_auvdeployment_list = AUVDeployment.objects.filter(
        campaign__in=latest_campaign_list
    )

    return render_to_response(
        'webinterface/Force_views/auvDeploymentMap.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))

def auvdeployment_detail(request, auvdeployment_id):
    """@brief AUV Deployment map and data plot for specifed AUV deployment

    """
    user = request.user

    #just make sure we get the anonymous user from the database - so we can user permissions
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    latest_campaign_list = get_objects_for_user(user, [
        'catamidb.view_campaign'])

    auvdeployment_object = {}

    try:
        auvdeployment_object = list(AUVDeployment.objects.filter(
            id=auvdeployment_id, campaign__in=latest_campaign_list))[0]

    #if it doesn't exist or we dont have permission then go back to the main list
    except Exception:
        return auvdeployments(request)

    return render_to_response(
        'webinterface/Force_views/auvdeploymentDetail.html',
        {'auvdeployment_object': auvdeployment_object,
         'WMS_URL': settings.WMS_URL,
         'WMS_layer_name': settings.WMS_LAYER_NAME,
         'deployment_id': auvdeployment_object.id},
        context_instance=RequestContext(request))

def campaigns(request):
    """@brief Campaign list html for entire database

    """

    user = request.user

    #just make sure we get the anonymous user from the database - so we can user permissions
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    latest_campaign_list = get_objects_for_user(user, [
        'catamidb.view_campaign']) #Campaign.objects.all()
    campaign_rects = list()

    for campaign in latest_campaign_list:
        auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign)
        bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign)
        dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign)
        if len(auv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
        if len(bruv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)

    return render_to_response(
        'webinterface/Force_views/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list,
         'campaign_rects': campaign_rects},
        context_instance=RequestContext(request))


def campaign_detail(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """

    user = request.user
    #just make sure we get the anonymous user from the database - so we can user permissions
    if request.user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    try:
        campaign_object = Campaign.objects.get(id=campaign_id)

        #check for permissions
        if not user.has_perm('catamidb.view_campaign', campaign_object):
            raise Campaign.DoesNotExist

    except Campaign.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
            'webinterface/Force_views/data_missing.html',
            context_instance=RequestContext(request))
    campaign_rects = list()
    #djf = Django.Django(geodjango="extent", properties=[''])

    auv_deployment_list = AUVDeployment.objects.filter(
        campaign=campaign_object)
    bruv_deployment_list = BRUVDeployment.objects.filter(
        campaign=campaign_object)
    dov_deployment_list = DOVDeployment.objects.filter(
        campaign=campaign_object)
    ti_deployment_list = TIDeployment.objects.filter(campaign=campaign_object)
    tv_deployment_list = TVDeployment.objects.filter(campaign=campaign_object)
    #geoj = GeoJSON.GeoJSON()
    #sm = AUVDeployment.objects.filter(transect_shape__bbcontains=pnt_wkt)
    #sm = AUVDeployment.objects.all().extent
    #sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())

    sm = ' '
    if len(auv_deployment_list) > 0:
        sm = fromstr(
            'MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(
                campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    if len(bruv_deployment_list) > 0:
        sm = fromstr(
            'MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(
                campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    try:
        sm_envelope = sm.envelope.geojson
    except AttributeError:
        sm_envelope = ''

    return render_to_response(
        'webinterface/Force_views/campaign_detail.html',
        {'campaign_object': campaign_object,
         'auv_deployment_list': auv_deployment_list,
         'bruv_deployment_list': bruv_deployment_list,
         'dov_deployment_list': dov_deployment_list,
         'ti_deployment_list': ti_deployment_list,
         'tv_deployment_list': tv_deployment_list,

         'campaign_as_geojson': sm_envelope},
        context_instance=RequestContext(request))


@csrf_exempt
def get_multiple_deployment_extent(request):
    if request.method == 'POST':  # If the form has been submitted...
        deployment_ids = request.POST.get('deployment_ids')
        deployment_ids = deployment_ids.__str__().split(",")
        extent = Pose.objects.filter(
            deployment_id__in=deployment_ids).extent().__str__()

        response_data = {"extent": extent}
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype="application/json")

    return HttpResponse(
        simplejson.dumps({"message": "GET operation invalid, must use POST."}),
        mimetype="application/json")


@csrf_exempt
def get_collection_extent(request):
    if request.method == 'POST':  # If the form has been submitted...
        collection_id = request.POST.get('collection_id')
        image_set = Collection.objects.get(id=collection_id).images.all()
        pose_id_set = image_set.values_list("pose_id")

        extent = Pose.objects.filter(id__in=pose_id_set).extent().__str__()

        response_data = {"extent": extent}
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype="application/json")

    return HttpResponse(
        simplejson.dumps({"message": "GET operation invalid, must use POST."}),
        mimetype="application/json")


@csrf_exempt
def create_collection_from_deployments(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = CreateCollectionForm(
            request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # make a new collection here from the deployment list
            CollectionManager().collection_from_deployments_with_name(
                request.user, request.POST.get('collection_name'),
                request.POST.get('deployment_ids'))
            return HttpResponseRedirect('/projects')  # Redirect after POST

    return render(request, 'noworky.html', {'form': form, })


@csrf_exempt
def create_workset_from_collection(request, method):
    if request.method == 'POST':  # If the form has been submitted...
        form = CreateWorksetForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            CollectionManager().workset_from_collection(
                request.user,
                request.POST.get('name'),
                request.POST.get('description'),
                request.POST.get('ispublic') == "true",
                int(request.POST.get('c_id')),
                int(request.POST.get('n')),
                method
            )

            return HttpResponseRedirect(
                '/collections/' + request.POST.get(
                    'c_id') + '/#SelectWorksetModal')  # Redirect after POST

    return HttpResponse(form)

@csrf_exempt
def create_workset_from_project(request, method):
    if request.method == 'POST':  # If the form has been submitted...
        form = CreateWorksetForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            workset = CollectionManager().workset_from_collection(
                request.user,
                request.POST.get('name'),
                request.POST.get('description'),
                request.POST.get('ispublic') == "true",
                int(request.POST.get('c_id')),
                int(request.POST.get('n')),
                method
            )

            return HttpResponseRedirect(
                '/collections/' + request.POST.get('c_id') + '/workset/' + workset.id.__str__())  # Redirect after POST

    return HttpResponse(form)


@csrf_exempt
def proxy(request):

    url = request.GET.get('url',None)

    conn = httplib2.Http()
    if request.method == "GET":
        resp, content = conn.request(url, request.method)
        return HttpResponse(content)
    elif request.method == "POST":
        url = url
        data = request.body
        resp, content = conn.request(url, request.method, data)
        return HttpResponse(content)
