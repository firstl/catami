from urllib2 import urlopen, HTTPError
from staging.models import Progress

import json
import datetime
import tempfile
import os.path

from django.db import transaction
from django.core import serializers

from staging.extras import update_progress

from staging.auvimport import NetCDFParser, LimitTracker, TrackParser
def get_known_file(key, url):
    # download the file async to get the file and give feedback
    resp = urlopen(url)

    size = int(resp.headers["content-length"])
    downloaded = 0

    # if we get here there must be a valid file we would assume...
    file_handle = tempfile.SpooledTemporaryFile(mode='rw+b')

    while True:
        data = resp.read(8192)
        downloaded += len(data)
        if data == "":
            update_progress(key, 100)
            break
        else:
            file_handle.write(data)
            percent = int(float(100.0 * downloaded) / float(size))
            update_progress(key, percent)

    if downloaded < size:
        raise EOFError("Not enough data read in. Got {0} whilst expecting {1}".format(downloaded, size))

    file_handle.seek(0)

    return file_handle

def get_netcdf_file(key, url_pattern, initial_time):
    search_seconds = 10
    
    for i in xrange(search_seconds):
        initial_time += datetime.timedelta(0,1) # add a second
        url = url_pattern.format(date_string=initial_time.strftime('%Y%m%dT%H%M%S'))
        try:
            #(filename, headers) = urlretrieve(url, reporthook=create_download_hook(key))
            file_handle = get_known_file(key, url)
        except HTTPError as e:
            print "HTTPError (expected) {0}".format(e)
            pass
        else:
            # no error in finding the file - have the right one so escape
            break
    else:
        raise IOError(0, "Cannot find netcdf file.", url_pattern)

    return file_handle

def auvfetch(base_url, campaign_date, campaign_name, mission_name):
    # the YYYMMDD_hhmmss of the mission
    (day, time) = mission_name.lstrip('r').split('_')[0:2]

    mission_datetime = "{0}_{1}".format(day, time)

    # the descriptive text part of the name
    mission_text = mission_name.split('_', 2)[2]

    mission_base = base_url + "/" + campaign_name + "/" + mission_name

    # the base directory for the geotiffs
    image_base =  mission_base + "/i" + mission_datetime + "_gtif/"

    # the track file that contains image positions and names
    trackfile_name = mission_base + "/track_files/" + mission_text + "_latlong.csv"

    # the netcdf that give water condition measurements
    netcdf_base = mission_base + '/hydro_netcdf/'

    # still need to replace the string with the date... seconds need to be
    # incremented
    netcdfseabird_name = netcdf_base + 'IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc'

    datetime_object = datetime.datetime.strptime(mission_datetime, "%Y%m%d_%H%M%S")

    return (trackfile_name, netcdfseabird_name, datetime_object)
def auvprocess(track_file, netcdf_file, base_url, campaign_datestring, campaign_name, mission_name, limit=None):
    # recreate the mission parameters etc.
    (day, time) = mission_name.lstrip('r').split('_')[0:2]
    mission_datetime = "{0}_{1}".format(day, time)

    # the descriptive text part of the name
    mission_text = mission_name.split('_', 2)[2]
    mission_base = base_url + "/" + campaign_name + "/" + mission_name

    # the base directory for the geotiffs
    image_base =  mission_base + "/i" + mission_datetime + "_gtif/"

    # these have the precise local names of the files
    netcdf_seabird = NetCDFParser(netcdf_file)
    trackparser = TrackParser(track_file)

    datetime_object = datetime.datetime.strptime(mission_datetime, "%Y%m%d_%H%M%S")
    start_datestring = str(datetime_object)

    deployment_nk = [start_datestring , mission_text]


    # the running max and min survey depths
    depth_lim = LimitTracker('depth')

    # latitude and longitude limits
    lat_lim = LimitTracker('latitude')
    lon_lim = LimitTracker('longitude')

    poselist = []

    earlier_seabird = netcdf_seabird.next()
    later_seabird = netcdf_seabird.next()

    for row in trackparser:
        if limit and len(poselist) / 2 >= limit:
            break

        limage = row['leftimage']
        rimage = row['rightimage']

        pose = dict()
        pose['deployment'] = deployment_nk # the foreign key, whatever the natural key is
        seconds, centiseconds = row['second'].split('.')
        pose['date_time'] = datetime.datetime(int(row['year']), int(row['month']), 
                                    int(row['day']), int(row['hour']), 
                                    int(row['minute']), int(seconds),
                                    int(centiseconds) * 10000) # convert to microseconds

        pose['image_position'] = "POINT ({0} {1})".format(row['latitude'], row['longitude'])

        pose['left_image_reference'] = image_base + "{0}.tif".format(os.path.splitext(limage)[0])

        pose['pitch'] = row['pitch']
        pose['roll'] = row['roll']
        pose['yaw'] = row['heading']

        pose['altitude'] = row['altitude']
        pose['depth'] = row['depth']

        # get the two measurements either side of the stereo pose
        while pose['date_time'] > later_seabird['date_time']:
            earlier_seabird, later_seabird = later_seabird, netcdf_seabird.next()

        # find which is closer - could use interpolation instead
        if (later_seabird['date_time'] - pose['date_time']) > (pose['date_time'] - earlier_seabird['date_time']):
            closer_seabird = earlier_seabird
        else:
            closer_seabird = later_seabird

        # add in salinity and temperature
        pose['temperature'] = closer_seabird['temperature']
        pose['salinity'] = closer_seabird['salinity']

        pose['date_time'] = str(pose['date_time'])

        depth_lim.check(pose)
        # lat and long are embedded in pose, but direct in row
        lat_lim.check(row)
        lon_lim.check(row)

    
        # get the actual image (probably png/tiff)
        #pose['left_thumbnail_reference'] = thumbnailer(os.path.join(img_dir_name, pose['left_image_reference']))
        #pose['right_thumbnail_reference'] = thumbnailer(os.path.join(img_dir_name, pose['right_image_reference']))

        # quick hax to use instead of embedding the thumbnail
        pose['left_thumbnail_reference'] = pose['left_image_reference']


        # add the stereo here
        stereopose = {}
        stereopose['image_ptr'] = [deployment_nk, pose['date_time']] #list(deployment_nk).append(pose['date_time'])
        stereopose['right_image_reference'] = image_base + "{0}.tif".format(os.path.splitext(rimage)[0])
        stereopose['right_thumbnail_reference'] = stereopose['right_image_reference']


        print "Added pose at ", pose['date_time']

        poselist.append({'pk': None, 'model': 'Force.Image', 'fields': pose})
        poselist.append({'pk': None, 'model': 'Force.StereoImage', 'fields': stereopose})

    deployment = {}
    # take the position of the first image
    deployment['campaign'] = [ campaign_datestring, campaign_name] # the foreign key
    deployment['short_name'] = mission_text
    deployment['start_position'] = poselist[0]['fields']['image_position']
    # the start from the mission time - potentially should shift to first image?
    deployment['start_time_stamp'] = start_datestring 
    # from the last image taken (last image, not stereoImages)
    deployment['end_time_stamp'] = poselist[-2]['fields']['date_time']
    deployment['mission_aim'] = "The aim of the mission."
    deployment['min_depth'] = depth_lim.minimum
    deployment['max_depth'] = depth_lim.maximum


    auvdeployment = {}
    auvdeployment['deployment_ptr'] = deployment_nk # the foreign key, whatever the natural key is
    auvdeployment['transect_shape'] = "POLYGON(({0} {2}, {0} {3}, {1} {3}, {1} {2}, {0} {2} ))".format(lat_lim.minimum, lat_lim.maximum, lon_lim.minimum, lon_lim.maximum)
    auvdeployment['distance_covered'] = 100.0 # just make it up... will work out later

    deploy = { 'pk': None, 'model': 'Force.Deployment', 'fields': deployment }
    auvdeploy = { 'pk': None, 'model': 'Force.AUVDeployment', 'fields': auvdeployment }

    structure = [deploy, auvdeploy]
    structure.extend(poselist)

    return json.dumps(structure)

def json_sload(json_string):
    # now load into the database 
    json_real_load(json_string)

def json_fload(file_name):
    # now load into the database 
    json_file = open(file_name, 'r')
    print file_name
    json_real_load(json_file)

def json_real_load(data):
    with transaction.commit_manually():
        try:
            for obj in serializers.deserialize('json', data):
                # check if the class is in Force
                if obj.object.__class__.__module__ == "Force.models":
                   obj.save()
                else:
                    raise ValueError('Object does not come from target Module.', obj.object)
        except:
            transaction.rollback()
            # reraise the same error
            raise
        else:
            transaction.commit()