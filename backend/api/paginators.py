from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomNestedRecipePagination(PageNumberPagination):
    page_size_query_param = 'recipe_limit'
