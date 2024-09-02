from django.urls import path
from .views import SignupView, LoginView, UserSearchView , SendFriendRequestView , AcceptFriendRequestView , RejectFriendRequestView, ListFriendsView , ListPendingFriendRequestsView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search_users'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/accept/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friend-request/reject/<int:pk>/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('<int:user_id>/friends/', ListFriendsView.as_view(), name='list-friends'),
    path('<int:user_id>/pending-requests/', ListPendingFriendRequestsView.as_view(), name='list-pending-requests'),
]
