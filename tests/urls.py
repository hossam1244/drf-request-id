from django.http import JsonResponse
from django.urls import path


def echo_request_id(request):
    from drf_request_id.middleware import get_request_id

    return JsonResponse({"request_id": get_request_id()})


def boom(request):
    raise ValueError("inside a request")


urlpatterns = [
    path("echo", echo_request_id, name="echo"),
    path("boom", boom, name="boom"),
]
