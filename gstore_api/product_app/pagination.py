from rest_framework.pagination import PageNumberPagination, CursorPagination

class CustomPagination(PageNumberPagination):
    page_query_param = "p"
    page_size_query_param = "size"
    
class CustomCursorPagination(CursorPagination):
    ordering = "created_at"
    