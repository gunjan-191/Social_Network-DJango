from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import *
from rest_framework.generics import ListAPIView , UpdateAPIView , CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser , FriendRequest
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta


class UserSearchPagination(PageNumberPagination):
    page_size = 10

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserSearchView(ListAPIView):
    serializer_class = CustomUserSerializer
    pagination_class = UserSearchPagination

    def get_queryset(self):
        search_serializer = UserSearchSerializer(data=self.request.query_params)
        search_serializer.is_valid(raise_exception=True)
        search_keyword = search_serializer.validated_data['search_keyword']
        
        if not search_keyword:
            raise NotFound("Search keyword not provided.")
        
        # Search by email
        # users_by_email = CustomUser.objects.filter(email__icontains=search_keyword)
        # if users_by_email.exists():
        #     return users_by_email
        
        # # Search by name (contains)
        # users_by_name = CustomUser.objects.filter(name__icontains=search_keyword)
        
        # if users_by_name.exists():
        #     return users_by_name
        
        # raise NotFound("No users found with the given search keyword.")
        
        users_by_email = CustomUser.objects.filter(email__icontains=search_keyword).order_by('email')
        if users_by_email.exists():
            return users_by_email
        
        users_by_name = CustomUser.objects.filter(name__icontains=search_keyword).order_by('name')
        if users_by_name.exists():
            return users_by_name
        
        raise Response({'detail': 'No users found with the given search keyword.'}, status=status.HTTP_404_NOT_FOUND)

class SendFriendRequestView(APIView):
    def post(self, request, *args, **kwargs):
        sender_id = request.data.get('sender')
        receiver_id = request.data.get('receiver')

        # Get current time and calculate one minute ago
        now = timezone.now()
        one_minute_ago = now - timedelta(minutes=1)

        # Check if the sender has already sent 3 or more friend requests in the past minute
        recent_requests_count = FriendRequest.objects.filter(
            sender_id=sender_id,
            created_at__gte=one_minute_ago
        ).count()

        if recent_requests_count >= 3:
            return Response({
                'error': 'You can only send up to 3 friend requests per minute.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if a friend request already exists between the sender and receiver
        existing_request = FriendRequest.objects.filter(sender_id=sender_id, receiver_id=receiver_id).first()

        if existing_request:
            if existing_request.status == 'rejected':
                # Allow creating a new request if previous was rejected
                existing_request.status = 'pending'
                existing_request.save()
                return Response({
                    'status': 'New friend request sent after rejection.',
                    'friend_request_id': existing_request.id
                }, status=status.HTTP_201_CREATED)
            else:
                # If the request is pending or accepted, return an error
                return Response({
                    'error': 'Friend request already exists.',
                    'friend_request_id': existing_request.id
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new friend request
        friend_request = FriendRequest.objects.create(sender_id=sender_id, receiver_id=receiver_id, status='pending')
        return Response({
            'status': 'Friend request sent.',
            'friend_request_id': friend_request.id
        }, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(UpdateAPIView):
    serializer_class = FriendRequestSerializer

    def patch(self, request, *args, **kwargs):
        request_id = kwargs.get('pk')
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        if friend_request.status != 'pending':
            return Response({'error': 'Friend request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'accepted'
        friend_request.save()
        return Response({'status': 'Friend request accepted.'}, status=status.HTTP_200_OK)

class RejectFriendRequestView(UpdateAPIView):
    serializer_class = FriendRequestSerializer

    def patch(self, request, *args, **kwargs):
        request_id = kwargs.get('pk')
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        if friend_request.status != 'pending':
            return Response({'error': 'Friend request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'status': 'Friend request rejected.'}, status=status.HTTP_200_OK)

class ListFriendsView(ListAPIView):
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        # Get all friend requests where the user is either the sender or the receiver and the status is 'accepted'
        sent_requests = FriendRequest.objects.filter(sender_id=user_id, status='accepted')
        received_requests = FriendRequest.objects.filter(receiver_id=user_id, status='accepted')

        # Combine all the friends (remove duplicates if necessary)
        friends = set()
        for req in sent_requests:
            friends.add(req.receiver)
        for req in received_requests:
            friends.add(req.sender)

        # Serialize the friend list
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)

class ListPendingFriendRequestsView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        # Get all pending friend requests where the user is the receiver
        pending_requests = FriendRequest.objects.filter(receiver_id=user_id, status='pending')

        if pending_requests.exists():
            serializer = FriendRequestSerializer(pending_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No pending friend requests found."}, status=status.HTTP_404_NOT_FOUND)
