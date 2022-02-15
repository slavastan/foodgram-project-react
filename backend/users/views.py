from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import CustomUserSerializer
from .models import Follow
from .paginations import DefaultPagination, UserPagination

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = UserPagination
    permission_classes = [AllowAny]


class FollowingAPI(APIView):
    def get(self, request, id):
        if request.user == get_object_or_404(User, id=id):
            return Response(
                {"errors": "Unable to subscribe to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follower = User.objects.get(id=id)
        serializer = CustomUserSerializer(
            follower, context={"request": self.request}
        )
        if not Follow.objects.filter(
            user=request.user, follower=follower
        ).exists():
            Follow.objects.create(user=request.user, follower=follower)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"errors": "You are already subscribed to the user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, id):
        follower = User.objects.get(id=id)
        if Follow.objects.filter(
            user=request.user, follower=follower
        ).exists():
            Follow.objects.get(user=request.user, follower=follower).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"errors": "You are not subscribed on this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FollowsListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        follow_objects = get_list_or_404(Follow, user=self.request.user)
        subscriptions = [object_.follower for object_ in follow_objects]
        return subscriptions
    
