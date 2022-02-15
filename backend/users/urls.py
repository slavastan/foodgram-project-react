from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet, FollowingAPI, FollowsListViewSet

app_name = "users"

router = DefaultRouter()
router.register(
    r"users/subscriptions", FollowsListViewSet, basename="api_follow"
)
router.register("users", CustomUserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/<int:id>/subscribe/", FollowingAPI.as_view()),
]
