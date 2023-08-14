from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegisterView.as_view()),
    path('users/', UserList.as_view()),
    path('friend-requests/', FriendRequestApi.as_view()),
    path('send-request/', SendFriendRequestApi.as_view()),
    path('accept-request/', AcceptFriendRequestApi.as_view()),
    path('reject-request/', RejectFriendRequestApi.as_view()),
    path('friends/', FriendsList.as_view()),
]