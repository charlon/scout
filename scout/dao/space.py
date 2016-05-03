from spotseeker_restclient.spotseeker import Spotseeker
from spotseeker_restclient.exceptions import DataFailureException
import datetime
import pytz


OPEN_PERIODS = {
        # 5am - 10:59am
        'breakfast': {
            'start': datetime.time(5, 0, 00, 0),
            'end':  datetime.time(11, 0, 0, 0)
        },
        # 11am - 2:59pm
        'lunch': {
            'start': datetime.time(11, 0, 0, 0),
            'end':  datetime.time(15, 0, 0, 0)
        },
        # 3pm - 9:59pm
        'dinner': {
            'start': datetime.time(15, 0, 0, 0),
            'end':  datetime.time(22, 0, 0, 0)
        },
        # 10pm - 4:59am (spans midnight)
        'late_night': {
            'start': datetime.time(22, 0, 0, 0),
            'end':  datetime.time(5, 0, 0, 0)
        },
    }


def get_spot_list():
    spot_client = Spotseeker()
    try:
        res = spot_client.search_spots([('limit', 0),
                                        ('extended_info:app_type', 'food')])
        for spot in res:
            spot = process_extended_info(spot)
    except DataFailureException:
        # TODO: consider logging on failure
        res = []

    return res


def get_spots_by_filter(filters=[]):
    filters.append(('extended_info:app_type', 'food'))
    spot_client = Spotseeker()
    try:
        res = spot_client.search_spots(filters)
        for spot in res:
            spot = process_extended_info(spot)
    except DataFailureException:
        # TODO: consider logging on failure
        res = []
    return res


def get_filtered_spots(request):
    filters = _get_spot_filters(request)
    # adding 'default' filter params
    filters.append(('limit', 0))
    return get_spots_by_filter(filters)


def _get_spot_filters(request):
    params = []
    for param in request.GET:
        if "campus" in param:
            params.append(("extended_info:campus", request.GET[param]))
        if "type" in param:
            params.append(("type", request.GET[param]))
        if "food" in param:
            params.append(("extended_info:or:" + request.GET[param], "true"))
        if "cuisine" in param:
            params.append(("extended_info:or:" + request.GET[param], "true"))
        if "payment" in param:
            params.append(("extended_info:or:" + request.GET[param], "true"))
        if "period" in param:
            params += get_period_filter(request.GET[param])
        if "open_now" in param:
            params.append(("open_now", "true"))
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
    spot = add_foodtype_names_to_spot(spot)
    spot = add_cuisine_names(spot)
    spot = add_payment_names(spot)
    spot = add_additional_info(spot)
    spot = organize_hours(spot)

    now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    spot.is_open = get_is_spot_open(spot, now)
    spot.open_periods = get_open_periods_by_day(spot, now)
    return spot


def organize_hours(spot):
    hours_object = {
        'monday': [],
        'tuesday': [],
        'wednesday': [],
        'thursday': [],
        'friday': [],
        'saturday': [],
        'sunday': [],
    }

    days_list = ['monday',
                 'tuesday',
                 'wednesday',
                 'thursday',
                 'friday',
                 'saturday',
                 'sunday']

    for day in days_list:
        overnight = False
        day_hours = \
            [hours for hours in spot.spot_availability if hours.day == day]
        next_day = (days_list.index(day) + 1) % len(days_list)
        next_day_hours = \
            [hours for hours in spot.spot_availability
             if hours.day == days_list[next_day]]
        close_used = True
        for hours in next_day_hours:
            if hours.start_time == datetime.time(0, 0):
                overnight = True
                close = hours.end_time  # get early morning end time
                close_used = False
        for hours in day_hours:
            if hours.end_time == datetime.time(23, 59) and overnight:
                hours_object[hours.day].append((hours.start_time, close))
                close_used = True
            elif (hours.end_time == datetime.time(23, 59) and
                    not hours.start_time == datetime.time(0, 0)):
                hours_object[hours.day].append((hours.start_time,
                                                datetime.time(0, 0)))
            elif (not hours.start_time == datetime.time(0, 0) and
                    not hours.end_time == datetime.time(23, 59)):
                hours_object[hours.day].append((hours.start_time,
                                                hours.end_time))
        if not close_used:
            hours_object[hours.day].append((datetime.time(0, 0),
                                            close))
        overnight = False
    spot.hours = hours_object
    return spot


def get_open_periods_by_day(spot, now):
    # defining 'late night' as any time not covered by another period
    open_periods = {'breakfast': False,
                    'lunch': False,
                    'dinner': False,
                    'late_night': False}
    hours = spot.hours[now.strftime("%A").lower()]
    for opening in hours:
        start = opening[0]
        end = opening[1]
        # spot spans midnight
        if start > end:
            end = datetime.time(23, 59, 59)
            open_periods['late_night'] = True
        # open for breakfast
        breakfast = OPEN_PERIODS['breakfast']
        if breakfast['start'] < end and breakfast['end'] > start:
            open_periods['breakfast'] = True
        # open for lunch
        lunch = OPEN_PERIODS['lunch']
        if lunch['start'] < end and lunch['end'] > start:
            open_periods['lunch'] = True
        # open for dinner
        dinner = OPEN_PERIODS['dinner']
        if dinner['start'] < end and dinner['end'] > start:
            open_periods['dinner'] = True
        # open late night
        if start < breakfast['start'] or end > dinner['end']:
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
    spot.has_alert = _get_extended_info_by_key("s_has_alert",
                                               spot.extended_info)
    spot.alert_notes = _get_extended_info_by_key("s_alert_notes",
                                                 spot.extended_info)
    spot.has_reservation = _get_extended_info_by_key("s_has_reservation",
                                                     spot.extended_info)
    spot.reservation_notes = _get_extended_info_by_key("s_reservation_notes",
                                                       spot.extended_info)
    spot.menu_url = _get_extended_info_by_key("s_menu_url",
                                              spot.extended_info)
    spot.hours_notes = _get_extended_info_by_key("hours_notes",
                                                 spot.extended_info)
    spot.access_notes = _get_extended_info_by_key("s_access_notes",
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
    spot.location_description = \
        _get_extended_info_by_key("location_description",
                                  spot.extended_info)
    spot.campus = _get_extended_info_by_key("campus", spot.extended_info)

    spot.app_type = _get_extended_info_by_key("app_type", spot.extended_info)
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
