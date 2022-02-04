from django.urls import include, path
from api.views import ListSubscribesView, get_or_delete_sub

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', ListSubscribesView.as_view()),
    path('users/<int:pk>/subscribe/', get_or_delete_sub),
]
