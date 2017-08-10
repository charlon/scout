var Tech_Filter = {
    // class handles filters for tech
    // filters are stored under the session variable
    // tech_filter_params.

    set_filter_params: function(){
        // similar implementation as the current filter.js for this
        // method. This just specifically gets params set for
        // tech filters.html.

        var params = {};
        var param_types = {
            "brand": "brand_select input:checkbox:checked",
            "subcategory": "subcategory_select input:checkbox:checked",
        };

        $.each(param_types, function(type, param){
            var result = $("#" + param).map(function() {
                return $(this).val();
            }).get();
            params = $.extend(params, Filter._get_params_for_select(result, type));
        });

        // Store these tech_filter_params
        sessionStorage.setItem("tech_filter_params", JSON.stringify(params));

        // pass the params to native apps via bridge
        console.log($.param(params));
        Filter.call_js_bridge($.param(params));

    },

    get_filter_url: function(){
        // Again, similar implementation as the current filter.js for
        // this method. Instead of just returning tech specific filters,
        // it combines the filter-params filters and tech-filter-params.

        var specific_filter = {};
        try {
            specific_filter = JSON.parse(sessionStorage.getItem("tech_filter_params"));
            if(specific_filter === undefined || $.isEmptyObject(specific_filter)){
                specific_filter = {};
            }
        } catch(e) {
            console.log(e);
        }
        return specific_filter;
    },

    _get_filter_label_text: function(url){
        // similar implementation as the current filter.js for
        // this method. More tech specific.

        var filter_categories = [];
        filter_labels = {
            "brand": "Brand",
            "subcategory": "Type",
        };
        $.each(filter_labels, function(filter, label){
            if(url.indexOf("&" + filter) > -1 || url.indexOf("?" + filter) > -1){
                filter_categories.push(label);
            }
        });
        return filter_categories;
    },

    /**
    reset_filter: function(){
        // just makes a call to generic filter.js reset_filter with
        // the session variable as the parameter.
        Filter.reset_filter("tech_filter_params", "/tech/");
    },
    **/

    init_events: function(){
        // Very similar to the current implementation in fllter.js
        // No tests required for this, I guess?

        /**
        $("#run_tech_search").click(function(){
            Tech_Filter.set_filter_params();
            Filter.redirect_to_page("/tech/");
        });

        $("#reset_tech_button").click(function() {
            Tech_Filter.reset_filter();
        });

        $("#reset_tech_list").click(function() {
            Tech_Filter.reset_filter();
        });
        **/
    },

};
