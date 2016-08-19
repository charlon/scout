var Filter = {

    get_filter_url: function(type) {
        var filter = {};
        if(type.indexOf("food") > -1) {
            filter = Food_Filter.get_filter_url();
        } else if(type.indexOf("study") > -1) {
            filter = Study_Filter.get_filter_url();
        } else if(type.indexOf("tech") > -1) {
            filter = Tech_Filter.get_filter_url();
        } else {
            console.log(type + "at get_filter_url");
        }

        if(filter === undefined || $.isEmptyObject(filter)){
            return undefined;
        }
        return $.param(filter);
    },

    _get_params_for_select: function(select_results, prefix) {
        var params = {};
        if(select_results !== null && select_results.length > 0){
            $.each(select_results, function(idx, result){
                params[prefix + idx] = result;
            });
        }
        return params;

    },

    _get_filter_label_text: function(){
        var url = window.location.href;
        var type = Filter.get_current_type();
        var filter_categories = [];
        var specific_categories = [];

        if(type.indexOf("food") > -1) {
            specific_categories = Food_Filter._get_filter_label_text(url);
        } else if(type.indexOf("study") > -1) {
            specific_categories = Study_Filter._get_filter_label_text(url);
        } else if(type.indexOf("tech") > -1) {
            specific_categories = Tech_Filter._get_filter_label_text(url);
        } else {
            console.log(type + "at _get_filter_label_text");
        }
        $.merge(filter_categories, specific_categories);

        var filter_string = "";
        for(var i = 0; i < filter_categories.length; i++){
            filter_string += filter_categories[i];
            if (i < filter_categories.length - 1){
                filter_string += ", ";
            }
        }

        return filter_string;
    },

    set_filter_text: function(){
        // this will now have a paramater, so it can set the filter text
        // based on what it recieves as a parameter.

        var filter_text = Filter._get_filter_label_text();
        if(filter_text.length > 0){
            $("#filter_label_text").html(filter_text);
        }
    },

    reset_filter: function(sessionVar, type) {
        // this will now have a paramater, so it can set the delete app type
        // specific filters.
        sessionStorage.removeItem(sessionVar);
        Filter.replace_navigation_href();
        Filter.redirect_to_page(type);
    },

    init_events: function() {

        Filter.set_filter_text();
        Food_Filter.init_events();
        Study_Filter.init_events();
        Tech_Filter.init_events();

    },

    redirect_to_page: function(type) {
        var campus = window.location.pathname.split('/')[1];
        var filter_url = Filter.get_filter_url(type);

        if (filter_url !== undefined){
            window.location.href = "/"+ campus + type + "?" + filter_url;
        } else {
            window.location.href = "/" + campus + type;
        }
    },

    get_current_type: function() {

        var current_page = window.location.pathname;

        if (current_page.indexOf("study") > -1){
            return "/study/";
        } else if (current_page.indexOf("tech") > -1){
            return "/tech/";
        } else if (current_page.indexOf("food") > -1){
            return "/food/";
        } else {
            return "/";
        }

        return current_page;
    },

    init: function() {
        // we can include type as a parameter and web.js
        // pas that!
        var type = Filter.get_current_type();
        if(type.indexOf("food") > -1) {
            Food_Filter.populate_filters_from_saved();
        } else if(type.indexOf("study") > -1) {
            Study_Filter.populate_filters_from_saved();
        } else if(type.indexOf("tech") > -1) {
            Tech_Filter.populate_filters_from_saved();
        } else {
            console.log(type + "at init");
        }
    },

    populate_filters_from_saved: function(sessionVar, param_types) {

        var params = JSON.parse(sessionStorage.getItem(sessionVar));
        if(params == undefined){
            return;
        }

        $.each(params, function(param_key, param_val){
            $.each(param_types, function(type_key, type_val){
                if(param_key.indexOf(type_key) > -1){
                    // find a better way to find out the input val!
                    var item = $("#" + type_val).find("input[value='" + param_val + "']");
                    $(item[0]).prop("checked", true);
                }
            });
        });
    },

    replace_navigation_href: function(){

        // get the campus from the url
        var campus = window.location.pathname.split('/')[1]

        // make sure scout icon goes to correct campus
        $("#link_home").attr("href", "/" + campus + "/");

        var anchors = {
            "/food/" : "#link_food",
            "/study/" : "#link_study",
            "/tech/" : "#link_tech",
        };

        for (anchor in anchors){
            // build the url with filtered params
            var filter = Filter.get_filter_url(anchor);
            var filtered_url = "/" + campus + anchor;
            var anchor_id = $(anchors[anchor]);
            if (filter !== undefined){
                filtered_url = filtered_url + "?" + filter;
            }
            if(anchor_id !== undefined){
                anchor_id.attr('href', filtered_url);
            }
        }

    },

};

/* node.js exports */
if (typeof exports == "undefined") {
    var exports = {};
}
exports.Filter = Filter;
