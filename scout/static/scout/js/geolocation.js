var Geolocation = {

    // campus default_locations (center)
    // seattle: { latitude: 47.653811, longitude: -122.307815 },
    // slu: { latitude: 47.62456939, longitude: -122.34105337 },
    // bothell: { latitude: 47.75907121, longitude: -122.19103843 },
    // tacoma: { latitude: 47.24458187, longitude: -122.43763134 },

    // drumheller fountain
    default_location: { latitude: 47.653811, longitude: -122.307815 },

    campus_locations: function(campus){
        var locations = {
            "seattle": { "latitude": 47.653811, "longitude": -122.307815 },
            "south_lake_union": { "latitude": 47.62456939, "longitude": -122.34105337 },
            "bothell": { "latitude": 47.75907121, "longitude": -122.19103843 },
            "tacoma": { "latitude": 47.24458187, "longitude": -122.43763134 },
        };
        $.event.trigger(Geolocation.location_updating);
        if(locations[campus] !== undefined){
            Geolocation.default_location.latitude = locations[campus]["latitude"];
            Geolocation.default_location.longitude = locations[campus]["longitude"];
        }
    },

    location_changed:  {"type": "location_changed"},

    location_updating:  {"type": "location_updating"},

    geolocation_status: { watchid: undefined },

    update_location: function () {
        // current user location is given more precedence over campus location.
        if (!Geolocation.get_is_using_location()) {
            Geolocation.set_campus_location();
        } else {
            Geolocation.query_client_location();
        }
        if(!window.has_set_loc){
            // Fire this event so pages can handle location on page load
            $.event.trigger(Geolocation.location_changed);
        }
        window.has_set_loc = true;
    },

    get_is_using_location: function () {
        return (localStorage.getItem("using_location") === 'true');
    },

    set_is_using_location: function (is_using_location) {
        // Setting should be bool
        // Persists between sessions
        localStorage.setItem("using_location", is_using_location);
        Geolocation.update_location();
    },

    set_location_type: function (type) {
        // Values: 'default', 'supplied', 'user'
        // Session only
        sessionStorage.setItem("location_type", type);
    },

    get_location_type: function () {
         return sessionStorage.getItem("location_type") || 'default';
     },

    set_client_location: function(position) {
        sessionStorage.setItem("lat", position.coords.latitude);
        sessionStorage.setItem("lng", position.coords.longitude);
        Geolocation.set_location_type("user");
        $.event.trigger(Geolocation.location_changed);
    },

    get_latlng_from_coords: function(lat, lng) {
        return new google.maps.LatLng(lat, lng);
    },

    get_client_latlng: function () {
        var lat = sessionStorage.getItem("lat");
        var lng = sessionStorage.getItem("lng");
        return Geolocation.get_latlng_from_coords(lat, lng);
    },

    handle_watch_position: function (position) {
       if(Geolocation.get_is_using_location()){
           var new_position = Geolocation.get_latlng_from_coords(position.coords.latitude, position.coords.longitude);
           var distance = Geolocation.get_distance_from_position(new_position);
           Geolocation.set_client_location(position);
       }
    },

    query_client_location: function() {
        // deal w/ error state
        if (navigator.geolocation) {
            Geolocation.geolocation_status.watchid = navigator.geolocation.watchPosition(Geolocation.handle_watch_position);
        }
    },

    stop_watching_location: function(){
        var watchid = Geolocation.geolocation_status.watchid;
        if(watchid){
            navigator.geolocation.clearWatch(watchid);
        }
    },

    set_campus_location: function() {
        //var index = 0;
        var campus = JSON.parse(sessionStorage.getItem("filter_params"))["campus0"];
        Geolocation.campus_locations(campus);
        sessionStorage.setItem('lat', Geolocation.default_location.latitude);
        sessionStorage.setItem('lng', Geolocation.default_location.longitude);
        Geolocation.set_location_type("default");
        $.event.trigger(Geolocation.location_changed);
    },

    get_distance_from_position: function (item_latlng) {
        // Returns distance in miles, rounded to 2 decimals
        var current_latlng = Geolocation.get_client_latlng();
        var distance = google.maps.geometry.spherical.computeDistanceBetween(current_latlng, item_latlng);
        var miles_per_meter = 0.000621371;
        distance = (distance * miles_per_meter).toFixed(2);
        return distance;

    },


    display_location_status: function () {

        if (Geolocation.get_location_type() === "default") {

            $("#default_position").show();
            $("#default_position").attr("aria-hidden", "false");

            $("#shared_position").hide();
            $("#shared_position").attr("aria-hidden", "true");

        } else {

            $("#default_position").hide();
            $("#default_position").attr("aria-hidden", "true");

            $("#shared_position").show();
            $("#shared_position").attr("aria-hidden", "false");

        }
    },

    init_location_toggles: function() {
        $("#use_location").click(function(e) {

            e.preventDefault();
            $.event.trigger(Geolocation.location_updating);
            Geolocation.set_is_using_location(true);

            $("#shared_position").show();
            $("#shared_position").attr("aria-hidden", "false");

            $("#default_position").hide();
            $("#default_position").attr("aria-hidden", "true");

        });

        $("#forget_location").click(function(e) {

            e.preventDefault();
            $.event.trigger(Geolocation.location_updating);
            Geolocation.set_is_using_location(false);
            Geolocation.stop_watching_location();

            $("#shared_position").hide();
            $("#shared_position").attr("aria-hidden", "true");

            $("#default_position").show();
            $("#default_position").attr("aria-hidden", "false");

        });
    }


};

/* node.js exports */
if (typeof exports == "undefined") {
    var exports = {};
}
exports.Geolocation = Geolocation;
