var List = {

    init: function () {

        // Gets the current type the page is on!
        var currentType = $("body").data("app-type")

        if (currentType.indexOf("study") > -1) {

            List.add_distances("scout-list-item", "data-spot-lat", "data-spot-lng");
            List.add_distances("scout-list-building", "data-building-lat", "data-building-lng");
            List.order_list("scout-list-building", "scout_study_list", true);

        } else if (currentType.indexOf("tech") > -1)  {

            List.add_distances("scout-list-item", "data-spot-lat", "data-spot-lng");
            List.add_additional_tech_distances();
            List.order_list("scout-list-item", "scout_tech_list", false);

        } else {


          // request food/list/ async
          var campus = $("body").data("campus");

          // get the food params in query string and append to url construction
          var food_params = ""
          food_params =  location.search;

          // build the ajax url with food params
          var url = "/h/" + campus + "/food/list/" + food_params;

          $.ajax({
              url: url,
              dataType: "html",
              type: "GET",
              accepts: {html: "text/html"},
              success: function(results) {

                $("#food_list").html(results);

                List.add_distances("scout-list-item", "data-spot-lat", "data-spot-lng");
                List.order_list("scout-list-item", "scout_food_list", false);

                setTimeout(function(){
                  $("#food_placeholder").hide();
                }, 1500);

              },
              error: function(xhr, status, error) {
                  console.log("An error occurred fetching food list");
              }
          });



        }

    },

    add_distances: function (className, latAttr, lngAttr) {
        var objects = $("." + className).not(".scout-error");

        $.each(objects, function(index, object){

            var lat = $(object).attr(latAttr);
            var lng = $(object).attr(lngAttr);

            var latlng = Geolocation.get_latlng_from_coords(lat, lng);
            var distance = Geolocation.get_distance_from_position(latlng);

            $(object).attr("data-spot-distance", distance);
            $($(object).find(".distance-number")[0]).html(distance);
        });
    },

    add_additional_tech_distances: function() {
        var spots = $(".scout-list-item").not(".scout-error");
        $.each(spots, function(idx, item){
            var distance = $(item).attr("data-spot-distance");
            $.each($(item).find(".scout-list-item-object"), function(idx, item_object) {
                $(item_object).attr("data-spot-distance", distance);
                $($(item_object).find(".distance-number")[0]).html(distance);
            });
        });
    },


    order_list: function (className, listName, isBuilding) {
        var objects = $("." + className).not(".scout-error").detach();
        if(isBuilding) {
            $.each(objects, function(idx, object){
                var spots = $(object).find(".scout-list-item").detach();
                var spot_ol = $(object).find(".scout_study_spot_list");
                $(spot_ol[0]).append(List.sort_spots_by_distance(spots));
            });
        }
        objects = List.sort_spots_by_distance(objects);
        $("#" + listName).append(objects);
    },

    sort_spots_by_distance: function(spots) {
        spots.sort(function(a, b) {
            var a_distance = parseFloat($(a).attr('data-spot-distance'));
            var b_distance = parseFloat($(b).attr('data-spot-distance'));
            if(a_distance < b_distance){
                return -1;
            } else if (a_distance > b_distance){
                return 1;
            } else {
                return 0;
            }
        });
        return spots;
    },
};
