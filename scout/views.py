# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import Http404, HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from scout.dao.space import (
    get_spot_by_id,
    get_filtered_spots,
    get_spot_list,
    get_period_filter,
    get_spots_by_filter,
    group_spots_by_building,
    get_building_list,
    validate_detail_info,
    get_random_limit_from_spots,
)
from scout.dao.image import get_spot_image, get_item_image
from scout.dao.item import get_item_by_id, get_filtered_items, get_item_count

from django.views.generic.base import TemplateView, TemplateResponse

# using red square as the default center
DEFAULT_LAT = 47.653811
DEFAULT_LON = -122.3094925

CAMPUS_LOCATIONS = {
    "seattle": {"latitude": 47.653811, "longitude": -122.307815},
    "south_lake_union": {"latitude": 47.62456939, "longitude": -122.34105337},
    "bothell": {"latitude": 47.75907121, "longitude": -122.19103843},
    "tacoma": {"latitude": 47.24458187, "longitude": -122.43763134},
}

TECH_CATEGORIES = {
    "cameras": "Cameras",
    "camera_accessories": "Camera Accessories",
    "computers": "Computers",
    "computer_accessories": "Computer Accessories",
    "audio_systems": "Audio Systems",
    "audio_accessories": "Audio Accessories",
}


def validate_campus_selection(function):
    def wrap(request, *args, **kwargs):
        if settings.CAMPUS_URL_LIST and isinstance(
            settings.CAMPUS_URL_LIST, list
        ):
            campuses = settings.CAMPUS_URL_LIST
        else:
            raise ImproperlyConfigured(
                "Must define a CAMPUS_URL_LIST" "of type list in the settings"
            )
        if kwargs["campus"] in campuses:
            return function(request, *args, **kwargs)
        else:
            raise Http404

    return wrap


# news splash
class NewsSplashView(TemplateView):
    template_name = "newssplash.html"


# discover
class DiscoverView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        context = {
            "campus": kwargs["campus"],
            "campus_locations": CAMPUS_LOCATIONS,
            "random_cards": ["studyrandom", "foodrandom"],
        }
        return context


class DiscoverCardView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]

        # if h_lat and h_lng is provided, use it
        # otherwise, user latitude and longitude

        # handle hybridize user lat/lng requests
        hlat = self.request.GET.get("h_lat", None)
        hlon = self.request.GET.get("h_lng", None)

        # handle standard lat/lng requests for web
        lat = self.request.GET.get("latitude", None)
        lon = self.request.GET.get("longitude", None)

        # Hardcoded for food at the moment. Change it per need basis.
        discover_categories = {
            "safestudy": {
                "title": "Study Spots Open Now",
                "spot_type": "study",
                "filter_url": "open_now=true",
                "filter": [
                    ("limit", 5),
                    ("open_now", True),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                ],
            },
            "safefood": {
                "title": "Food Spots Open Now",
                "spot_type": "food",
                "filter_url": "open_now=true",
                "filter": [
                    ("limit", 5),
                    ("open_now", True),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                    ("extended_info:app_type", "food"),
                ],
            },
            "morning": {
                "title": "Open Mornings (5am - 11am)",
                "spot_type": "food",
                "filter_url": "period0=morning",
                "filter": [
                    ("limit", 5),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                    ("extended_info:app_type", "food"),
                ]
                + get_period_filter("morning"),
            },
            "late": {
                "title": "Open Late Night (10pm - 5am)",
                "spot_type": "food",
                "filter_url": "period0=late_night",
                "filter": [
                    ("limit", 5),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                    ("extended_info:app_type", "food"),
                ]
                + get_period_filter("late_night"),
            },
            "studyoutdoors": {
                "title": "Outdoor Study Areas",
                "spot_type": "study",
                "filter_url": "type0=outdoor",
                "filter": [
                    ("limit", 5),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                    ("type", "outdoor"),
                ],
            },
            "studycomputerlab": {
                "title": "Computer Labs",
                "spot_type": "study",
                "filter_url": "type0=computer_lab",
                "filter": [
                    ("limit", 5),
                    (
                        "center_latitude",
                        hlat if hlat else lat if lat else DEFAULT_LAT,
                    ),
                    (
                        "center_longitude",
                        hlon if hlon else lon if lon else DEFAULT_LON,
                    ),
                    ("distance", 100000),
                    ("type", "computer_lab"),
                ],
            },
            "studyrandom": {
                "title": "Places to study",
                "spot_type": "study",
                "filter_url": "",
                "filter": [("limit", 0)],
            },
            "foodrandom": {
                "title": "Places to eat",
                "spot_type": "food",
                "filter_url": "",
                "filter": [("extended_info:app_type", "food"), ("limit", 0)],
            },
        }

        try:
            discover_data = discover_categories[kwargs["discover_category"]]
        except KeyError:
            raise Http404

        discover_data["filter"].append(
            ("extended_info:campus", kwargs["campus"])
        )

        spots = get_spots_by_filter(discover_data["filter"])
        if len(spots) == 0:
            raise Http404
        if kwargs["discover_category"] in ["foodrandom", "studyrandom"]:
            spots = get_random_limit_from_spots(spots, 5)

        context = {
            "spots": spots,
            "campus": kwargs["campus"],
            "card_title": discover_data["title"],
            "spot_type": discover_data["spot_type"],
            "card_filter_url": discover_data["filter_url"],
        }
        return context


# food
class PlaceHolderView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        context = {
            "campus": kwargs["campus"],
            "app_type": kwargs["app_type"],
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class FoodListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        spots = get_filtered_spots(self.request, kwargs["campus"], "food")
        context = {
            "spots": spots,
            "campus": kwargs["campus"],
            "count": len(spots),
            "app_type": "food",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class FoodDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        spot = get_spot_by_id(kwargs["spot_id"])
        spot = validate_detail_info(spot, kwargs["campus"], "food")
        if not spot:
            raise Http404

        context = {
            "spot": spot,
            "campus": kwargs["campus"],
            "app_type": "food",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class FoodFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]

        # load parameters into context
        filter_types = ["payment", "period", "type"]

        context = _load_filter_params_checked(self.request, filter_types)

        context.update(
            {
                "campus": kwargs["campus"],
                "app_type": "food",
                "campus_locations": CAMPUS_LOCATIONS,
            }
        )

        return context


# study
class StudyListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        spots = get_filtered_spots(self.request, kwargs["campus"], "study")
        grouped_spots = group_spots_by_building(spots)
        context = {
            "spots": spots,
            "campus": kwargs["campus"],
            "grouped_spots": grouped_spots,
            "count": len(spots),
            "app_type": "study",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class StudyDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        spot = get_spot_by_id(kwargs["spot_id"])
        spot = validate_detail_info(spot, kwargs["campus"], "study")
        if not spot:
            raise Http404

        context = {
            "spot": spot,
            "campus": kwargs["campus"],
            "app_type": "study",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class StudyFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]

        # load parameters into context
        filter_types = [
            "type",
            "resources",
            "noise",
            "food",
            "lighting",
            "reservation",
            "building",
            "capacity",
        ]

        context = _load_filter_params_checked(self.request, filter_types)

        context.update(
            {
                "campus": kwargs["campus"],
                "buildings": get_building_list(kwargs["campus"]),
                "app_type": "study",
                "campus_locations": CAMPUS_LOCATIONS,
            }
        )

        return context


# tech
class TechListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        # spots = get_spots_by_filter([('has_items', 'true')])
        self.request.GET = self.request.GET.copy()
        self.request.GET["item_is_active"] = "true"
        spots = get_filtered_spots(self.request, kwargs["campus"], "tech")
        spots = get_filtered_items(spots, self.request)
        count = get_item_count(spots)
        if count <= 0:
            spots = []

        context = {
            "spots": spots,
            "campus": kwargs["campus"],
            "count": count,
            "app_type": "tech",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class TechDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]
        spot = get_item_by_id(int(kwargs["item_id"]))
        spot = validate_detail_info(spot, kwargs["campus"], "tech")
        if not spot:
            raise Http404

        context = {
            "spot": spot,
            "campus": kwargs["campus"],
            "app_type": "tech",
            "campus_locations": CAMPUS_LOCATIONS,
        }
        return context


class TechFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs["template_name"]

        # load parameters into context
        filter_types = ["brand", "subcategory"]
        tech_spots = get_spot_list("tech")
        info = extract_spots_item_info(tech_spots)

        pre = _load_filter_params_checked(self.request, filter_types)
        context = {}

        for obj in pre:
            new_key = obj.replace(" ", "_").replace("-", "_").replace("/", "_")
            context[new_key] = pre[obj]

        context.update(
            {
                "campus": kwargs["campus"],
                "app_type": "tech",
                "filters": info,
                "campus_locations": CAMPUS_LOCATIONS,
            }
        )

        return context


def extract_spots_item_info(spots):
    category_list = {}
    brand_list = []
    for spot in spots:
        for item in spot.items:
            cat = item.category
            sub = item.subcategory

            if cat not in category_list:
                category_list[cat] = {"sub": {}, "name": ""}

            if sub not in category_list[cat]["sub"]:
                category_list[cat]["sub"][sub] = {"name": ""}

            for info in item.extended_info:
                if info.key == "i_brand" and info.value not in brand_list:
                    brand_list.append(info.value)
                if info.key == "i_subcat_print_name":
                    category_list[cat]["sub"][sub]["name"] = info.value

    for cat_name in TECH_CATEGORIES:
        if cat_name in category_list:
            category_list[cat_name]["name"] = TECH_CATEGORIES[cat_name]

    result = {"categories": category_list, "brands": brand_list}
    return result


# image views
def spot_image_view(request, image_id, spot_id):
    width = request.GET.get("width", None)
    try:
        resp, content = get_spot_image(spot_id, image_id, width)
        etag = resp.headers.get("etag", None)
        response = HttpResponse(
            content, content_type=resp.headers["content-type"]
        )
        response["etag"] = etag
        return response
    except Exception:
        raise Http404


def item_image_view(request, image_id, item_id):
    width = request.GET.get("width", None)
    try:
        resp, content = get_item_image(item_id, image_id, width)
        etag = resp.headers.get("etag", None)
        response = HttpResponse(
            content, content_type=resp.headers["content-type"]
        )
        response["etag"] = etag
        return response
    except Exception:
        raise Http404


def _load_filter_params_checked(request, filter_types):
    context = {}

    if "open_now" in request.GET:
        context["open_now"] = True

    for param_class in filter_types:
        has_type = True
        i = 0
        while has_type:
            if param_class + str(i) in request.GET:
                param = request.GET[param_class + str(i)]
                context[param] = True
            else:
                has_type = False
            i = i + 1

    return context
