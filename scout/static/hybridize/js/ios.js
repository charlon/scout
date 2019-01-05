// Initialize your hybrid app


$(document).on('turbolinks:load', function() {

    console.log("turbolinks ios fired!");

    // track visits in google analytics
    try{
        ga('send', 'pageview', (location.pathname + location.search));
        console.info("Navigated to: " + location.pathname + location.search);
    }
    catch(e){
        console.log("No ga function, GOOGLE_ANALYTICS_KEY may not be set.");
    };

    // initialize framework7
    var myApp = new Framework7({
		router: false,
		fastClicks: true,
		activeState: true,
	});

    // get the app_type
    var type = $("body").data("app-type")

    if (type.indexOf("food") !== -1) {
        // food
        List.init();
        Filter.init();

    } else if (type.indexOf("study") !== -1){
        // study
        List.init();
        Filter.init();

        // study detail image slider
        if ($( ".photo-gallery").length) {
            $('.photo-gallery').not('.slick-initialized').slick({
                dots: true,
                arrows: false,
            });
        }

    } else if (type.indexOf("tech") !== -1){
        // tech
        List.init();
        Filter.init();
    } else {
        // discover
        // Discover.init_cards();
    }

    // Geolocation
    //Geolocation.update_location();

    // filter
    Filter.init_events();

});
