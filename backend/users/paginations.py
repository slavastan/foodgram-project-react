from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class DefaultPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 999
    page_size_query_param = 'limit'


class UserPagination(LimitOffsetPagination):
    max_page_size = 100
