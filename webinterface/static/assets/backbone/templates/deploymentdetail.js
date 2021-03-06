var Deployment = window.TastypieModel.extend({
    url: function () {
        // Important! It's got to know where to send its REST calls.
        return this.id ? '/api/dev/generic_deployment/' + this.id : '/api/dev/generic_deployment/';
    }
});

DeploymentDetailView = Backbone.View.extend({
    model : Deployment,
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {
        var deploymentVariables = {
            "campaignlist_url": CampaignListUrl,
            "campaign_url": CampaignUrl,
            "campaign_name": deployment.get("campaign_name"),
            "deployment_name": deployment.get("short_name")            
        };
        var deploymentDetailTemplate = _.template($("#DeploymentDetailTemplate").html(), deploymentVariables);
        // Load the compiled HTML into the Backbone "el"
        this.$el.html(deploymentDetailTemplate);
               
        var did = deployment.get("id");
        //instantiate openlayer map via Geoserver
        var map = new BaseMap(WMS_URL, WMSLayerName, "deployment-map");
        //load layer and filter by deployment id
        filter_array = []
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "deployment_id",
            value: did
        }));
        map.updateMapUsingFilter(filter_array);
    
        plotMeasurement("/api/dev/generic_image/?format=json&deployment=" + did + "&output=flot&limit=10000", "#placeholder_01", "Depth (m)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + did + "&mtype=salinity&limit=10000&output=flot", "#placeholder_02", "Salinity (psu)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + did + "&mtype=temperature&limit=10000&output=flot", "#placeholder_03", "Temperature (cel)")
           
        return this;
    }
});

deployment = new Deployment({ id: catami_getDeploymentId() });
deployment.fetch({
    success: function (model, response, options) {
        var deploymentdetail_view = new DeploymentDetailView({
            el: $("#DeploymentDetailContainer"),
            model : deployment
        });
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }
});

function plotMeasurement(url, divId, axisLabel) {
    $.ajax({
        type: "GET",
        url: url,
        success: function (response, textStatus, jqXHR) {
            $.plot($(divId),
                    [{
                        data: response.data,
                        lines: { show: true, fill: false },
                        shadowSize: 0
                    }], {
                        yaxes: [
                            { axisLabel: axisLabel }
                        ], grid: { borderWidth: 0 }
                    }
            );
        }
    });
}