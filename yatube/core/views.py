from django.shortcuts import render

from http import HTTPStatus


def page_not_found(request, exception):
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)


def server_error(request):
    return render(
        request, 'core/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
