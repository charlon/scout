# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings


def google_maps(request):
    """See if there is a Google Analytics web property id"""
    gmaps_api_key = getattr(settings, "GOOGLE_MAPS_API", False)
    return {"GOOGLE_MAPS_API": gmaps_api_key, "google_maps": gmaps_api_key}


def google_analytics(request):
    ga_key = getattr(settings, "GOOGLE_ANALYTICS_KEY", False)
    return {"GOOGLE_ANALYTICS_KEY": ga_key, "google_analytics": ga_key}


def is_desktop(request):
    dk = not request.user_agent.is_mobile and not request.user_agent.is_tablet

    return {"is_desktop": dk}


def is_hybrid(request):
    hybridapp = request.GET.get("hybrid")

    return {"is_hybrid": hybridapp}


def scout_show_alt_tech(request):
    return {"scout_show_alt_tech": settings.SCOUT_SHOW_ALT_TECH}


def compress_enabled(request):
    return {"compress_enabled": settings.COMPRESS_ENABLED}


def campus_detect_url(request):
    url = request.get_full_path()
    for campus in settings.CAMPUS_URL_LIST:
        if campus in url:
            return {"campus": campus}
    return {"campus": "seattle"}
