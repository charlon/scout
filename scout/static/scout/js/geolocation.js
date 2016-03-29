var Geolocation = {

    // red square
    default_location: { latitude: 47.6558539, longitude: -122.3094925 },

    // drumheller fountain
    //default_location: { latitude: 47.653811, longitude: -122.307815 },

    location_changed:  new CustomEvent("location_changed"),

    location_updating:  new CustomEvent("location_updating"),

    update_location: function () {
        if (!Geolocation.get_is_using_location()) {
            Geolocation.set_default_location();
        } else {
            Geolocation.query_client_location();
        }
        if(!window.has_set_loc){
            // Fire this event so pages can handle location on page load
            window.dispatchEvent(Geolocation.location_changed);
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
        window.dispatchEvent(Geolocation.location_changed);
    },

    get_latlng_from_coords: function(lat, lng) {
        return new google.maps.LatLng(lat, lng);
    },

    get_client_latlng: function () {
        var lat = sessionStorage.getItem("lat");
        var lng = sessionStorage.getItem("lng");
        return Geolocation.get_latlng_from_coords(lat, lng);
    },

    handle_watch_position: function (updated_location) {
       if(Geolocation.get_is_using_location()){
           var new_position = Geolocation.get_latlng_from_coords(updated_location.coords.latitude, updated_location.coords.longitude);
           var distance = Geolocation.get_distance_from_position(new_position);
           if(distance > 100){
               Geolocation.set_client_location(updated_location);
           }
       }
    },

    query_client_location: function() {
        // deal w/ error state
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(Geolocation.handle_watch_position);
        }
    },

    set_default_location: function() {
        sessionStorage.setItem('lat', Geolocation.default_location.latitude);
        sessionStorage.setItem('lng', Geolocation.default_location.longitude);
        Geolocation.set_location_type("default");
        window.dispatchEvent(Geolocation.location_changed);
    },

    get_distance_from_position: function (item_latlng) {
        // Returns distance in rounded feet
        var current_latlng = Geolocation.get_client_latlng();
        var distance = google.maps.geometry.spherical.computeDistanceBetween(current_latlng, item_latlng);
        distance = Math.round(distance * 3.280839895);
        return distance;

    },


    display_location_status: function () {
        if (Geolocation.get_location_type() === "default") {

            $("#default_position").show();
            $("#default_position").attr("aria-hidden", "false");

            $("#shared_position").hide();
            $("#shared_position").attr("aria-hidden", "true");

            $("#forget_location").hide();
            $("#forget_location").attr("aria-hidden", "true");

            $("#use_location").show();
            $("#use_location").attr("aria-hidden", "false");

        } else {

            $("#default_position").hide();
            $("#default_position").attr("aria-hidden", "true");

            $("#shared_position").show();
            $("#shared_position").attr("aria-hidden", "false");

            $("#use_location").hide();
            $("#use_location").attr("aria-hidden", "true");

            $("#forget_location").show();
            $("#forget_location").attr("aria-hidden", "false");
        }
    },

    init_location_toggles: function() {
        $("#use_location").click(function(e) {

            e.preventDefault();
            Geolocation.set_is_using_location(true);
            window.dispatchEvent(Geolocation.location_updating);

            $("#shared_position").show();
            $("#shared_position").attr("aria-hidden", "false");

            $("#default_position").hide();
            $("#default_position").attr("aria-hidden", "true");

            $("#use_location").hide();
            $("#use_location").attr("aria-hidden", "true");

            $("#forget_location").show();
            $("#forget_location").attr("aria-hidden", "false");
        });

        $("#forget_location").click(function(e) {

            e.preventDefault();
            Geolocation.set_is_using_location(false);
            window.dispatchEvent(Geolocation.location_updating);

            $("#shared_position").hide();
            $("#shared_position").attr("aria-hidden", "true");

            $("#default_position").show();
            $("#default_position").attr("aria-hidden", "false");

            $("#forget_location").hide();
            $("#forget_location").attr("aria-hidden", "true");

            $("#use_location").show();
            $("#use_location").attr("aria-hidden", "false");

        });
    }


};
