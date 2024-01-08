from http import HTTPStatus

from django.shortcuts import render

ERROR_404_PAGE = 'core/404.html'
ERROR_403_PAGE = 'core/403.html'
ERROR_500_PAGE = 'core/500.html'


def page_not_found(request, exception):
    return render(
        request,
        ERROR_404_PAGE,
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def permission_denied(request, exception):
    return render(request, ERROR_403_PAGE, status=HTTPStatus.FORBIDDEN)


def server_error(request):
    return render(
        request, ERROR_500_PAGE, status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
