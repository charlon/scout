var Layout = {

    init_layout: function(){

        // async load css by flipping the media attribute to all
    	$('link[rel="stylesheet"]').attr('media', 'all');

        var isMobile = $("body").data("mobile");
        var offsetHeight;

        // set minimum page heights for the content area
        var page_path = window.location.pathname;

        if (page_path.indexOf("/food") !== -1) {
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-filter-results").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-list-container").css({minHeight: $(window).outerHeight() - offsetHeight });
        }
        else if (page_path.indexOf("/study") !== -1) {
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-filter-results").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-list-container").css({minHeight: $(window).outerHeight() - offsetHeight });
        }
        else if (page_path.indexOf("/tech") !== -1) {
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-filter-results").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-list-container").css({minHeight: $(window).outerHeight() - offsetHeight });
        }
        else {

            // discover page doesn't have filter results display
            offsetHeight = ($(".scout-header").outerHeight() + $(".scout-geolocation").outerHeight() + $(".scout-footer").outerHeight());
            $(".scout-discover-container").css({minHeight: $(window).outerHeight() - offsetHeight });

            // 404 page
            if($("#page_404").length > 0) {
                var offsetHeight = ($(".scout-header").outerHeight() + $(".scout-footer").outerHeight());
                $("#page_404").css({minHeight: $(window).outerHeight() - offsetHeight });
            }

        }

        // if mobile, calculate height of image container
        if (isMobile !== undefined ) {
            var aspectHeight = Math.round(( $(".spot-detail-main-image").width() /100)*67); //(i.e. 16:9 or 100:67)
            $(".spot-detail-main-image").height(aspectHeight);
        }

    },
};
