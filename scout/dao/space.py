from spotseeker_restclient.spotseeker import Spotseeker
from spotseeker_restclient.exceptions import DataFailureException
import datetime
import pytz


OPEN_PERIODS = {
        # 5am - 10:59am
        'morning': {
            'start': datetime.time(5, 0, 00, 0),
            'end':  datetime.time(11, 0, 0, 0)
        },
        # 11am - 2:59pm
        'afternoon': {
            'start': datetime.time(11, 0, 0, 0),
            'end':  datetime.time(15, 0, 0, 0)
        },
        # 3pm - 9:59pm
        'evening': {
            'start': datetime.time(15, 0, 0, 0),
            'end':  datetime.time(22, 0, 0, 0)
        },
        # 10pm - 4:59am (spans midnight)
        'late_night': {
            'start': datetime.time(22, 0, 0, 0),
            'end':  datetime.time(5, 0, 0, 0)
        },
    }


def get_spot_list(app_type=None, groups=[]):
    spot_client = Spotseeker()
    res = []
    filters = []
    filters.append(('limit', 0))

    try:
        if app_type:
            filters.append(('extended_info:app_type', app_type))
        else:
            # study spots have no app_type, and must filter on something
            filters.append(('open_now', 'true'))
        for group in groups:
            filters.append(('extended_info:group', group))
        spots = spot_client.search_spots(filters)
        for spot in spots:
            spot = process_extended_info(spot)
            if spot is not None:
                res.append(spot)
    except DataFailureException:
        # TODO: consider logging on failure
        pass

    return res


def get_spots_by_filter(filters=[]):
    spot_client = Spotseeker()
    res = []
    try:
        spots = spot_client.search_spots(filters)
        for spot in spots:
            spot = process_extended_info(spot)
            if spot is not None:
                res.append(spot)
    except DataFailureException:
        # TODO: consider logging on failure
        pass
    return res


def get_filtered_spots(request, app_type=None):
    filters = _get_spot_filters(request)
    # adding 'default' filter params
    filters.append(('limit', 0))
    if(app_type == "food"):
        filters.append(('extended_info:app_type', 'food'))
    elif(app_type == "tech"):
        filters.append(('extended_info:app_type', 'tech'))
    elif(app_type == "study"):
        filters.append(('open_now', 'true'))
    return get_spots_by_filter(filters)


def _get_spot_filters(request):
    params = []
    for param in request.GET:
        if "campus" in param:
            params.append(("extended_info:campus", request.GET[param]))
        if "type" in param:
            params.append(("type", request.GET[param]))
        if "food" in param:
            params.append(
                ("extended_info:or_group:food", request.GET[param])
            )
        if "cuisine" in param:
            params.append(
                ("extended_info:or_group:cuisine", request.GET[param])
            )
        if "payment" in param:
            params.append(
                ("extended_info:or_group:payment", request.GET[param])
            )
        if "period" in param:
            params += get_period_filter(request.GET[param])
        if "open_now" in param:
            params.append(("open_now", "true"))
        if "building" in param:
            params.append(("building_name", request.GET[param]))
        if "resources" in param:
            params.append(
                ("extended_info:or_group:resources", request.GET[param])
            )
        if "noise" in param:
            params.append(("extended_info:noise_level", request.GET[param]))
        if "lighting" in param:
            params.append(
                ("extended_info:or_group:lighting", request.GET[param])
            )
    return params


def get_period_filter(param):
    today = datetime.datetime.today().strftime("%A")
    tomorrow = (datetime.datetime.today() +
                datetime.timedelta(days=1)).strftime("%A")
    start_time = OPEN_PERIODS[param]["start"].strftime("%H:%M")
    start_string = "%s,%s" % (today, start_time)
    end_time = OPEN_PERIODS[param]["end"].strftime("%H:%M")
    if param == "late_night":
        end_string = "%s,%s" % (tomorrow, end_time)
    else:
        end_string = "%s,%s" % (today, end_time)

    return [("fuzzy_hours_start", start_string),
            ("fuzzy_hours_end", end_string)]


def get_spot_by_id(spot_id):
    spot_client = Spotseeker()
    try:
        res = spot_client.get_spot_by_id(spot_id)
    except DataFailureException:
        return None
    return process_extended_info(res)


def process_extended_info(spot):
    is_hidden = _get_extended_info_by_key("is_hidden", spot.extended_info)
    if is_hidden:
        return None
    spot = add_foodtype_names_to_spot(spot)
    spot = add_cuisine_names(spot)
    spot = add_payment_names(spot)
    spot = add_additional_info(spot)
    spot = add_study_info(spot)
    spot = organize_hours(spot)

    now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    spot.is_open = get_is_spot_open(spot, now)
    spot.open_periods = get_open_periods_by_day(spot, now)
    return spot


def organize_hours(spot):
    days_list = ('monday',
                 'tuesday',
                 'wednesday',
                 'thursday',
                 'friday',
                 'saturday',
                 'sunday')
    hours_object = {}
    raw_hours = list(spot.spot_availability)
    for idx, day in enumerate(days_list):
        today_hours = []
        start_of_day = datetime.time(0, 0)
        end_of_day = datetime.time(23, 59)
        day_hours = [h for h in raw_hours if h.day == day]
        # Try to find an hours object that spans to end of day, excluding
        # anything that spans the entire day
        overnight_today = [h for h in day_hours
                           if h.end_time == end_of_day and
                           h.start_time != start_of_day]
        # Try to find an hours object that starts at 0:00 tomorrow
        next_day = days_list[(idx + 1) % len(days_list)]
        overnight_next_day = [h for h in raw_hours if h.day == next_day and
                              h.start_time == start_of_day and
                              h.end_time != end_of_day]
        # If we have a period today that extends to 23:59 and a period
        # tomorrow that starts at 0:00, combine them and remove originals.
        if overnight_today and overnight_next_day:
            today_hours.append((overnight_today[0].start_time,
                                overnight_next_day[0].end_time))
            raw_hours.remove(overnight_next_day[0])
            day_hours.remove(overnight_today[0])
            # Preserving SCOUT-238 behavior for now. If we want to change
            # that behavior, delete the following two lines.
            if day == 'sunday':
                del hours_object['monday'][0]

        # Add all the non-special-case hours
        for hours in day_hours:
            today_hours.append((hours.start_time, hours.end_time))
        # Fixes SCOUT-237
        today_hours.sort()
        hours_object[day] = today_hours

    spot.hours = hours_object
    return spot


def get_open_periods_by_day(spot, now):
    # defining 'late night' as any time not covered by another period
    open_periods = {'morning': False,
                    'afternoon': False,
                    'evening': False,
                    'late_night': False}
    hours = spot.hours[now.strftime("%A").lower()]
    for opening in hours:
        start = opening[0]
        end = opening[1]
        # spot spans midnight
        if start > end:
            end = datetime.time(23, 59, 59)
            open_periods['late_night'] = True
        # open for morning
        morning = OPEN_PERIODS['morning']
        if morning['start'] < end and morning['end'] > start:
            open_periods['morning'] = True
        # open for afternoon
        afternoon = OPEN_PERIODS['afternoon']
        if afternoon['start'] < end and afternoon['end'] > start:
            open_periods['afternoon'] = True
        # open for evening
        evening = OPEN_PERIODS['evening']
        if evening['start'] < end and evening['end'] > start:
            open_periods['evening'] = True
        # open late night
        if start < morning['start'] or end > evening['end']:
            open_periods['late_night'] = True
    return open_periods


def get_is_spot_open(spot, now):
    hours_today = spot.hours[now.strftime("%A").lower()]
    yesterday = now - datetime.timedelta(days=1)
    hours_yesterday = spot.hours[yesterday.strftime("%A").lower()]
    for period in hours_yesterday:
        open_time = period[0]
        close_time = period[1]
        if open_time > close_time and now.time() < close_time:
            # has an opening past midnight yesterday and NOW is before close
            return True
    if len(hours_today) == 0:
        # has no openings today
        return False
    for period in hours_today:
        open_time = period[0]
        close_time = period[1]
        if open_time > close_time:
            if open_time < now.time():
                # Spot is open past midnight and open before now
                return True
        elif open_time <= now.time() < close_time:
            return True
    return False


def add_additional_info(spot):
    # global extended_info (study & food)
    spot.app_type = _get_extended_info_by_key("app_type", spot.extended_info)
    spot.location_description = \
        _get_extended_info_by_key("location_description",
                                  spot.extended_info)
    spot.campus = _get_extended_info_by_key("campus", spot.extended_info)
    spot.hours_notes = _get_extended_info_by_key("hours_notes",
                                                 spot.extended_info)
    spot.access_notes = _get_extended_info_by_key("access_notes",
                                                  spot.extended_info)
    spot.has_alert = _get_extended_info_by_key("has_alert",
                                               spot.extended_info)
    spot.alert_notes = _get_extended_info_by_key("alert_notes",
                                                 spot.extended_info)
    # new extended_info (food only)
    spot.has_reservation = _get_extended_info_by_key("s_has_reservation",
                                                     spot.extended_info)
    spot.reservation_notes = _get_extended_info_by_key("s_reservation_notes",
                                                       spot.extended_info)
    spot.menu_url = _get_extended_info_by_key("s_menu_url",
                                              spot.extended_info)
    spot.has_coupon = _get_extended_info_by_key("s_has_coupon",
                                                spot.extended_info)
    spot.coupon_expiration = _get_extended_info_by_key("s_coupon_expiration",
                                                       spot.extended_info)
    spot.coupon_url = _get_extended_info_by_key("s_coupon_url",
                                                spot.extended_info)
    spot.phone = _get_extended_info_by_key("s_phone",
                                           spot.extended_info)
    spot.email = _get_extended_info_by_key("s_email",
                                           spot.extended_info)
    spot.website_url = _get_extended_info_by_key("s_website_url",
                                                 spot.extended_info)

    if spot.app_type is None:
        spot.app_type = "study"

    return spot


def add_study_info(spot):
    RESOURCE_MAPPING = {
        "has_whiteboards": "Whiteboards",
        "has_outlets": "Outlets",
        "has_printing": "Printing",
        "has_scanning": "Scanning",
        "has_displays": "Displays",
        "has_projector": "Projector"
    }
    spot.spot_resources = _get_names_for_extended_info("",
                                                       RESOURCE_MAPPING,
                                                       spot.extended_info)

    if (_get_extended_info_by_key("has_computers", spot.extended_info) ==
            "true"):
        spot.computers = True
        spot.num_computers = _get_extended_info_by_key("num_computers",
                                                       spot.extended_info)

    if (_get_extended_info_by_key("has_natural_light", spot.extended_info) ==
            "true"):
        spot.natural_light = True

    spot.spot_noise = _get_extended_info_by_key("noise_level",
                                                spot.extended_info)

    spot.food_nearby = _get_extended_info_by_key("food_nearby",
                                                 spot.extended_info)

    if _get_extended_info_by_key("reservable", spot.extended_info) == "true":
        spot.reservable = "true"

    spot.reservation_notes = _get_extended_info_by_key("reservation_notes",
                                                       spot.extended_info)

    if _get_extended_info_by_key("has_labstats", spot.extended_info) == "true":
        spot.labstats = True
        spot.labstats_id = _get_extended_info_by_key("labstats_id",
                                                     spot.extended_info)
        spot.auto_labstats_total = _get_extended_info_by_key(
                                                     "auto_labstats_total",
                                                     spot.extended_info)
        spot.auto_labstats_available = _get_extended_info_by_key(
                                                     "auto_labstats_available",
                                                     spot.extended_info)
        if spot.auto_labstats_available is None\
           or spot.auto_labstats_total is None:
            spot.auto_labstats_total = 0
            spot.auto_labstats_available = 0

    return spot


def _get_extended_info_by_key(key, extended_info):
    for info in extended_info:
        if info.key == key:
            return info.value


def _get_names_for_extended_info(prefix, mapping, info):
    names = []
    for obj in info:
        if prefix in obj.key and obj.value:
            try:
                names.append(mapping[obj.key])
            except KeyError:
                pass
    return names


def add_payment_names(spot):
    PAYMENT_PREFIX = "s_pay"
    PAYMENT_MAPPING = {
        "s_pay_cash": "Cash",
        "s_pay_visa": "Visa",
        "s_pay_mastercard": "Mastercard",
        "s_pay_husky": "Husky Card",
        "s_pay_dining": "Dining Account",
    }
    spot.payment_names = _get_names_for_extended_info(PAYMENT_PREFIX,
                                                      PAYMENT_MAPPING,
                                                      spot.extended_info)
    return spot


def add_cuisine_names(spot):
    CUISINE_TYPE_PREFIX = "s_cuisine"
    CUISINE_TYPE_MAPPING = {
        "s_cuisine_american": "American",
        "s_cuisine_bbq": "BBQ",
        "s_cuisine_chinese": "Chinese",
        "s_cuisine_hawaiian": "Hawaiian",
        "s_cuisine_indian": "Indian",
        "s_cuisine_italian": "Italian",
        "s_cuisine_korean": "Korean",
        "s_cuisine_mexican": "Mexican",
        "s_cuisine_vietnamese": "Vietnamese",
    }
    spot.cuisinetype_names = _get_names_for_extended_info(CUISINE_TYPE_PREFIX,
                                                          CUISINE_TYPE_MAPPING,
                                                          spot.extended_info)
    return spot


def add_foodtype_names_to_spot(spot):
    FOOD_TYPE_PREFIX = "s_food_"
    FOOD_TYPE_MAPPING = {
        "s_food_burgers": "Burgers",
        "s_food_breakfast": "Breakfast",
        "s_food_curry": "Curry",
        "s_food_desserts": "Desserts",
        "s_food_entrees": "Entrees",
        "s_food_espresso": "Espresso",
        "s_food_frozen_yogurt": "Frozen Yogurt",
        "s_food_groceries": "Groceries",
        "s_food_pasta": "Pasta",
        "s_food_pastries": "Pastries",
        "s_food_pho": "Pho",
        "s_food_pizza": "Pizza",
        "s_food_salads": "Salads",
        "s_food_sandwiches": "Sandwiches",
        "s_food_smoothies": "Smoothies",
        "s_food_sushi_packaged": "Sushi (packaged)",
        "s_food_tacos": "Tacos",
    }
    spot.foodtype_names = _get_names_for_extended_info(FOOD_TYPE_PREFIX,
                                                       FOOD_TYPE_MAPPING,
                                                       spot.extended_info)
    return spot


def group_spots_by_building(spots):
    grouped_spots = {}
    for spot in spots:
        if spot.building_name in grouped_spots:
            grouped_spots[spot.building_name].append(spot)
        else:
            grouped_spots[spot.building_name] = [spot]
    list_structure = []
    for name in grouped_spots:
        building_dict = {"name": name,
                         "spots": grouped_spots[name]}
        list_structure.append(building_dict)
    return add_latlng_to_building(list_structure)


def add_latlng_to_building(building_list):
    for building in building_list:
        building['latitude'], building['longitude'] = \
            get_avg_latlng_for_spots(building['spots'])
    return building_list


def get_avg_latlng_for_spots(spots):
    avg_lat = 0
    avg_lng = 0
    count = len(spots)
    for spot in spots:
        avg_lat += spot.latitude
        avg_lng += spot.longitude

    return avg_lat/count, avg_lng/count
