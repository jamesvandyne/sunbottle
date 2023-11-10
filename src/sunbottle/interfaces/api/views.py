from typing import Iterable

import arrow
from django import http

from sunbottle.domain.electricity import queries

from . import serializers


def get_generation_line_graph(request: http.HttpRequest) -> http.JsonResponse:
    today = arrow.now().floor("day")
    yesterday = today.shift(days=-1)
    today_last_year = today.shift(years=-1)

    generation = queries.get_generation_series_for_date(yesterday.datetime)
    generation_today = queries.get_generation_series_for_date(today.datetime, exclude_future=True)
    generation_today_last_year = queries.get_generation_series_for_date(today_last_year.datetime)
    data = serializers.LineGraphData(
        data={
            "labels": list(_get_15_minute_interval_labels()),
            "yesterday": {
                "label": "Yesterday",
                "data": list(generation),
            },
            "today": {"label": "Today", "data": list(generation_today)},
            "last_year_today": {"label": "One Year Ago Today", "data": list(generation_today_last_year)},
        }
    )
    if data.is_valid():
        return http.JsonResponse(data=data.validated_data)
    return http.JsonResponse(data={"error": data.errors})


def get_generation_summary(request: http.HttpRequest) -> http.JsonResponse:
    today = arrow.now().floor("day").datetime
    data = serializers.GenerationSummary(
        data={
            "total_generation": queries.get_total_generation(),
            "today_generation": queries.get_generation_for_date(today),
        }
    )
    if data.is_valid():
        return http.JsonResponse(data=data.validated_data)
    return http.JsonResponse(data={"error": data.errors})


def _get_15_minute_interval_labels() -> Iterable[str]:
    for hour in range(0, 24):
        for interval in [0, 15, 30, 45]:
            if interval == 0:
                yield str(hour)
            else:
                yield ""
