from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from scout.dao.space import get_spot_list, get_spot_by_id, get_filtered_spots,\
    get_period_filter, get_spots_by_filter, group_spots_by_building,\
    get_building_list, validate_detail_info
from scout.dao.image import get_spot_image, get_item_image
from scout.dao.item import get_item_by_id, get_filtered_items, \
    get_item_count, add_item_info

from django.views.generic.base import TemplateView

# using red square as the default center
DEFAULT_LAT = 47.6558539
DEFAULT_LON = -122.3094925


CAMPUS_LOCATIONS = {
    "seattle": {"latitude": 47.653811, "longitude": -122.307815},
    "south_lake_union": {"latitude": 47.62456939, "longitude": -122.34105337},
    "bothell": {"latitude": 47.75907121, "longitude": -122.19103843},
    "tacoma": {"latitude": 47.24458187, "longitude": -122.43763134},
}


def validate_campus_selection(function):
    def wrap(request, *args, **kwargs):
        if settings.CAMPUS_URL_LIST and isinstance(settings.CAMPUS_URL_LIST,
                                                   list):
            campuses = settings.CAMPUS_URL_LIST
        else:
            raise ImproperlyConfigured("Must define a CAMPUS_URL_LIST"
                                       "of type list in the settings")
        if kwargs['campus'] in campuses:
            return function(request, *args, **kwargs)
        else:
            return custom_404_response(request)
    return wrap


# discover
class DiscoverView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        # import pdb; pdb.set_trace()
        context = {"campus": kwargs['campus'],
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class DiscoverCardView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        # Will figure this out later
        lat = self.request.GET.get('latitude', None)
        lon = self.request.GET.get('longitude', None)

        # Hardcoded for food at the moment. Change it per need basis.
        discover_categories = {
            "open": {
                "title": "Open Now",
                "spot_type": "food",
                "filter_url": "open_now=true",
                "filter": [
                    ('limit', 5),
                    ('open_now', True),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('extended_info:app_type', 'food')
                    ]
            },
            "morning": {
                "title": "Open Mornings (5am - 11am)",
                "spot_type": "food",
                "filter_url": "period0=morning",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('extended_info:app_type', 'food')
                    ] + get_period_filter('morning')

            },
            "late": {
                "title": "Open Late Night (10pm - 5am)",
                "spot_type": "food",
                "filter_url": "period0=late_night",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('extended_info:app_type', 'food')
                    ] + get_period_filter('late_night')
            },
            "studyoutdoors": {
                "title": "Outdoor Study Areas",
                "spot_type": "study",
                "filter_url": "type0=outdoor",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'outdoor')
                    ]
            },
            "studycomputerlab": {
                "title": "Computer Labs",
                "spot_type": "study",
                "filter_url": "type0=computer_lab",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'computer_lab')
                ]

            },
        }

        try:
            discover_data = discover_categories[kwargs['discover_category']]
        except KeyError:
            return custom_404_response(self.request)

        discover_data["filter"].append(('extended_info:campus',
                                        kwargs['campus']))

        spots = get_spots_by_filter(discover_data["filter"])
        if len(spots) == 0:
            return custom_404_response(self.request)
        context = {
            "spots": spots,
            "campus": kwargs['campus'],
            "card_title": discover_data["title"],
            "spot_type": discover_data["spot_type"],
            "card_filter_url": discover_data["filter_url"]
        }
        return context


# food
class FoodListView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        spots = get_filtered_spots(self.request, kwargs['campus'], "food")
        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "count": len(spots),
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class FoodDetailView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        spot = get_spot_by_id(kwargs['spot_id'])
        spot = validate_detail_info(spot, kwargs['campus'], "food")
        if not spot:
            return custom_404_response(self.request, kwargs['campus'])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class FoodFilterView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        context = {"campus": kwargs['campus'],
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


# study
class StudyListView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        spots = get_filtered_spots(self.request, kwargs['campus'], "study")
        grouped_spots = group_spots_by_building(spots)
        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "grouped_spots": grouped_spots,
                   "count": len(spots),
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class StudyDetailView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        spot = get_spot_by_id(kwargs['spot_id'])
        spot = validate_detail_info(spot, kwargs['campus'], "study")
        if not spot:
            return custom_404_response(self.request, kwargs['campus'])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class StudyFilterView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        context = {"campus": kwargs['campus'],
                   "buildings": get_building_list(kwargs['campus']),
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


# tech
class TechListView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        # spots = get_spots_by_filter([('has_items', 'true')])
        spots = get_filtered_spots(self.request, kwargs['campus'], "tech")
        spots = get_filtered_items(spots, self.request)
        count = get_item_count(spots)
        if count <= 0:
            spots = []

        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "count": count,
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class TechDetailView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        spot = get_item_by_id(int(kwargs['item_id']))
        spot = validate_detail_info(spot, kwargs['campus'], "tech")
        if not spot:
            return custom_404_response(self.request, kwargs['campus'])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class TechFilterView(TemplateView):
    @validate_campus_selection
    def get_context_data(self, **kwargs):
        context = {"campus": kwargs['campus'],
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


def hybrid_comps_view(request):
    return render_to_response('hybridize/components.html',
                              context_instance=RequestContext(request))


# image views
def spot_image_view(request, image_id, spot_id):
    width = request.GET.get('width', None)
    try:
        resp, content = get_spot_image(spot_id, image_id, width)
        etag = resp.get('etag', None)
        response = HttpResponse(content, content_type=resp['content-type'])
        response['etag'] = etag
        return response
    except Exception:
        return custom_404_response(request)


def item_image_view(request, image_id, item_id):
    width = request.GET.get('width', None)
    try:
        resp, content = get_item_image(item_id, image_id, width)
        etag = resp.get('etag', None)
        response = HttpResponse(content, content_type=resp['content-type'])
        response['etag'] = etag
        return response
    except Exception:
        return custom_404_response(request)


# Custom 404 page
def custom_404_response(request, campus="seattle"):
    context = {"campus": campus}
    response = render_to_response('404.html', context,
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
