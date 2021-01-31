from rest_framework.pagination import PageNumberPagination


class GeneralPaginationClass(PageNumberPagination):
    page_size = 4