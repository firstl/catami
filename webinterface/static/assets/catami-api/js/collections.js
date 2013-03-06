/***********************************************************************************************************************
 * Class: CollectionAPI
 * Creating lists of collections and worksets.
 *
 * @param preview_fnc
 * @param select_fnc
 * @constructor
 **********************************************************************************************************************/

function CollectionAPI(usrsettings) {

    // Default settings params
    var settings = {
        api_baseurl : '/api/dev/collection/',
        linkurl : "/collections/"
    };
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    // Default display config
    var config = {
        theme    : 'cl-sidebar',
        format   : false,
        nested    : false,
        linkname  : false,
        showactions : false,
        preview_fnc : false,
        select_fnc : false,
        checkbox_fnc : false,
        radio_fnc : false,
        unselect_fnc : false
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    if (!config.format) config.format = getFormat(config.theme);


    /* Public methods
     ******************************************************************************************************************/
    /**
     *
     * @param filter
     * @param outputelement
     * @return {*}
     */
    this.getCollectionList = function(filter, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '?'+filter : '');

        var list = createCollectionList(filter, 'list-main');

        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).html(list);
        }
        return list;
    }


    /**
     *
     * @param id
     * @param outputelement
     * @return {String}
     */
    this.getCollectionInfo = function(id, outputelement) {

        var api_url = settings.api_baseurl+'?id='+id;
        var clinfo = '';

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: api_url ,
            success: function(cl){
                var clobj = getClObj(cl.objects[0]);
                clinfo = formatClObj(config.format , clobj);
            }
        });


        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).html(clinfo);
        }
        return clinfo;
    }


    /**
     *
     */
    this.collapseList = function()  {
        $('li > ul.list-sub').each(function(i) {
            var parent_li = $(this).parent('li');           // Find this list's parent list item.
            parent_li.addClass('parent');                   // Style the list item as parent.
            var sub_ul = $(this).remove();                  // Temporarily remove the child-list from the parent

            // Add toggle function to list-toggle class
            parent_li.find('.list-toggle').click(function() {
                if (parent_li.find('.cllistctrl').hasClass('clopen')) parent_li.find('.cllistctrl').removeClass('clopen');
                else parent_li.find('.cllistctrl').addClass('clopen');
                sub_ul.toggle();
            });
            parent_li.append(sub_ul);                       // Reattach child-list.
        });

        $('ul.list-main ul.list-sub').hide(); // Hide child lists.
    }


    /* Private methods
     ******************************************************************************************************************/
    /**
     *
     * @param filter
     * @param listname
     * @param showerror
     * @return {String}
     */
    var createCollectionList = function(filter, listname, showerror) {

        showerror = ((typeof showerror !== 'undefined') ? showerror : true);

        var list = '';

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_baseurl+filter ,
            success: function(cl){
                if (cl.objects.length > 0) {
                    list += '<ul class="'+listname+'">';
                    for (var i = 0; i < cl.objects.length; i++) {
                        list += createListItem(cl.objects[i], filter);
                    }
                    list += '</ul>';
                }
                else if (showerror) {
                    list += '<p class="alert alert-error">There are no collections to display.</p>'
                }
            }
        });
        return list;
    }


    /**
     *
     * @param clobj
     * @param filter
     * @return {String}
     */
    var createListItem = function(clobj, filter) {

        var listitem = '<li>';

        clobj = getClObj(clobj);
        listitem += formatClObj(config.format , clobj);

        if ( clobj.parent_id == null && config.nested) { // This item is a parent Collection
            listitem += createCollectionList(filter+'&parent='+clobj.id, 'list-sub well', false); // Recursive call to create nested workset list (if available)
        }
        listitem += '</li>';


        return listitem;
    }


    /**
     *
     * @param clobj
     * @return {Object}
     */
    function getClObj(clobj) {
        var clobjout = {
            id            : clobj.id,
            name          : clobj.name,
            description   : clobj.description,
            username      : clobj.owner.username,
            image_count   : clobj.image_count,
            parent_id     : clobj.parent_id,
            parent        : clobj.parent,
            creation_info : clobj.creation_info,
            creation_date : clobj.creation_date.substr(0,10),
            access        : (clobj.is_public) ? 'Public' : 'Private',
            link          : (clobj.parent_id) ? settings.linkurl + clobj.parent_id + '/' + clobj.id + '/' : settings.linkurl + clobj.id+'/',
            type          : (clobj.parent_id) ? 'Workset' : 'Collection'
        };

        return clobjout;
    }


    /**
     *
     * @param format
     * @param clobj
     * @return {String|XML|void}
     */
    function formatClObj (format, clobj) {
        return format.replace(/{(.*?)}/g, function(match, string) {
            //alert(string+' : '+match+' : '+clobj[string]);
            return typeof clobj[string] != 'undefined'
                ? clobj[string]
                : match
                ;
        });
    }


    /**
     *
     * @param theme
     * @return {String}
     */
    function getFormat (theme) {
        var format = '';
        if (theme=='cl-sidebar-name') {
            if (config.showactions) {
                format += '<span class="claction btn-group pull-right">';
                if (config.select_fnc) format += '<a class="clactionitem btn btn-mini" onclick="'+config.select_fnc+';" rel="btn-tooltip" title="Select"><i class="icon-circle-arrow-up"></i></a>';
                format += '</span>';
            }
            format += '<span class="clinfo btn-group pull-right"><span class="clinfoitem btn btn-mini disabled" rel="btn-tooltip" title="This {type} contains {image_count} images">{image_count}</span></span>'+
                '<span class="clname">{name}</span>';
        } else if (theme=='cl-sidebar') {
            if (config.showactions) {
                format += '<span class="claction btn-group pull-right">';
                if (config.unselect_fnc) format += '<a class="clactionitem btn btn-mini" onclick="'+config.unselect_fnc+';" rel="btn-tooltip" title="Un-select"><i class="icon-remove-sign"></i></a>';
                if (config.preview_fnc) format += '<a class="clactionitem btn btn-mini" onclick="'+config.preview_fnc+';" rel="btn-tooltip" title="Preview"><i class="icon-signin"></i></a>';
                format += '</span>';
            }
            format += '<span class="clname">{name}</span>'+
                '<span class="clcreation">{creation_info}</span>'+
                '<span class="cldescription">{description}</span>';
        }
        else if (theme=='cl-inline-full-bootstrap') {
            format += '<span class="cllistctrl list-toggle"></span>';
            if (config.showactions) {
                format += '<span class="claction btn-group pull-right">';
                if (config.preview_fnc) format += '<a class="clactionitem btn btn-mini" onclick="'+config.preview_fnc+';" rel="btn-tooltip" title="Preview"><i class="icon-search"></i></a>';
                if (config.select_fnc) {
                    format += '<a class="clactionitem btn btn-mini" onclick="'+config.select_fnc+';" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
                } else {
                    format += '<a class="clactionitem btn btn-mini" href="{link}" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
                }
                format +='<a class="clactionitem btn btn-mini dropdown-toggle" data-toggle="dropdown" rel="btn-tooltip" title="More..."><b class="caret"></b></a>'+
                    '<ul class="dropdown-menu">'+
                    '<li class="nav-header">Jump to:</li>'+
                    '<li><a href="{link}#map" title="View {type} map"><i class="icon-globe"></i> Map view</a></li>'+
                    '<li><a href="{link}#thm" title="View {type} images"><i class="icon-picture"></i> Thumbnail view</a></li>'+
                    '<li class="nav-header">Data Tasks</li>'+
                    '<li><a href="{link}#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>'+
                    '</ul></span>';
            }
            format +='<span class="clinfo btn-group pull-right list-toggle">'+
                '<span class="clinfoitem btn btn-mini disabled {type}" rel="btn-tooltip" title="This item is a {type}">{type}</span>'+
                '<span class="clinfoitem btn btn-mini disabled" rel="btn-tooltip" title="This {type} was created on {creation_date}">{creation_date}</span>'+
                '<span class="clinfoitem btn btn-mini disabled" rel="btn-tooltip" title="This {type} is owned by {username}">{username}</span> '+
                '<span class="clinfoitem btn btn-mini disabled" rel="btn-tooltip" title="This {type} contains {image_count} images">{image_count}</span> '+
                '<span class="clinfoitem btn btn-mini disabled {access}" rel="btn-tooltip" title="This {type} is {access}">{access}</span>'+
                '</span>'+
                '<a href="{link}" class="clname">{name}</a>'+
                '<span class="clcreation">{creation_info}</span>'+
                '<span class="cldescription shorten">{description}</span>';
        }
        return format;
    }
}
