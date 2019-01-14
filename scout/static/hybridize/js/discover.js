Discover = {

    init_cards: function () {


        var discover_divs = $("#discover_cards").children();

        // get the client lat/lng
        var latlng = Geolocation.get_client_latlng();

        $(discover_divs).each(function (idx, div){
            var card_id = $(div).attr('id');
            // ignore if its a static card
            if (card_id && card_id !== "TECH_STATIC") {
                Discover.fetch_cards(card_id, latlng);
            } else {
                $("#" + card_id).fadeIn(3000);
            }
        });
    },

    fetch_cards: function (card_id , latlng) {

        //var campus = Navigation.get_campus_selection();
        var campus = $("body").data("campus");

        var url = "/h/" + campus + "/discover_card/" + card_id + "/";

        var pos_data = {}

        if (Cookies.get("user_location")) {
            pos_data = {
                "latitude": Cookies.get('user_lat'),
                "longitude": Cookies.get('user_lng')
            };
        } else {
            pos_data = {
                "latitude": $("body").data("campus-latitude"),
                "longitude": $("body").data("campus-longitude")
            };
        }

        $.ajax({
            url: url,
            dataType: "html",
            type: "GET",
            data: pos_data,
            accepts: {html: "text/html"},
            success: function(results) {

                Discover._attach_card(card_id, results);
                Discover.add_distance_and_sort(card_id);

                setTimeout(function(){
                  $("#discover_loading").hide();
                }, 1500);

                $("#" + card_id).fadeIn("slow");
            },
            error: function(xhr, status, error) {
                console.log("An error occurred fetching card " + card_id);
            }
        });
    },

    _attach_card: function (card_id, card_html) {
        $("#" + card_id).html(card_html);
    },

    add_distance_and_sort: function(card_id) {
        Discover._add_distance_to_spots(card_id);
        Discover._sort_spots_on_cards(card_id);
    },

    _add_distance_to_spots: function (card_id) {
        var spots = $("#" + card_id).find("li");
        $.each(spots, function(idx, spot){

            var latitude = $(spot).attr("data-lat");
            var longitude = $(spot).attr("data-lon");

            var spot_latlng = Geolocation.get_latlng_from_coords(latitude, longitude);
            var distance = Geolocation.get_distance_from_position(spot_latlng);
            $(spot).find(".scout-spot-distance").html(distance);
            $(spot).attr("data-spot-distance", distance);
        });
    },

    _sort_spots_on_cards: function (card_id) {
        var spots = $("#" + card_id).find("li");
        var spot_parent = spots.parent();
        spots.detach().sort(function(a, b) {
            var a_distance = parseFloat($(a).attr('data-spot-distance'));
            var b_distance = parseFloat($(b).attr('data-spot-distance'));
            // its faster to sort ints.
            if(a_distance < b_distance){
                return -1;
            } else if (a_distance > b_distance){
                return 1;
            } else {
                return 0;
            }
        });
        spot_parent.append(spots);
    },

};
