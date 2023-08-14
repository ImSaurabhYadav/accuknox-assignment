from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import *
from social_app.serializers import *
from rest_framework import filters
from rest_framework import pagination
from django.contrib.auth import authenticate,  login, logout
from social_app.models import *
from datetime import datetime, timedelta
from pytz import timezone
from django.db.models import Q
from django.db.models.signals import post_save
from django.shortcuts import redirect


def make_friend(sender, instance, **kwargs):
    if instance.accepted == True:
        friend = Friends()
        friend.primary_id = instance.sender_id
        friend.friend_id = instance.receiver_id
        friend.save()

post_save.connect(make_friend, sender=FriendRequest)

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serialized_data = LoginSerializer(data=request.data)
        if serialized_data.is_valid():
            credentials = serialized_data.data
            credentials['email'] = credentials['email'].lower()
            user = authenticate(**credentials)
            if user is not None:
                login(request, user)
                return Response("Logged in successfully")
            return Response("Invalid Credentials Provided", 401)
        return Response({"result": "Login failed", "errors": serialized_data._errors}, 401)

class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response("Logged Out Successfully")

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        if not request.user.is_authenticated:
            serialized = RegisterSerializer(data=request.data)
            if serialized.is_valid():
                email = serialized.data['email'].lower()
                full_name = serialized.data['full_name']
                try:
                    user = User.objects.get(email=email)
                    return Response({"Error": "User with the email exists."}, 401)
                except:
                    user = User()
                    user.email = email
                    user.full_name = full_name
                    user.set_password(serialized.data['password'])
                    user.save()
                    login(request, user)
                    return Response("User created successfully.")
            return Response({"Error": serialized._errors})
        return Response({"You're not authroised to register other users."}, 401)
    
class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'email']

class FriendRequestApi(APIView):
    def get(self, request):
        sent_requests = RequestSerializer(FriendRequest.objects.filter(sender_id=request.user.id, accepted=False, rejected=False).values(), many=True).data
        received_requests = RequestSerializer(FriendRequest.objects.filter(receiver_id=request.user.id, accepted=False, rejected=False).values(), many=True).data
        return Response({'sent': sent_requests, 'received': received_requests})

class SendFriendRequestApi(APIView):
    def post(self, request):
        serialized_data = SentRequestSerializer(data=request.data)
        if serialized_data.is_valid():
            requests_no = FriendRequest.objects.filter(sender_id=request.user.id, send_date__gt=datetime.now(tz=timezone('Asia/Kolkata'))-timedelta(minutes=1)).count()
            sender_id, receiver_id = request.data["sender_id"], request.data["receiver_id"]
            if request.user.id != sender_id:
                return Response("Invalid sender id", 401)
            if sender_id == receiver_id:
                return Response("Invalid receiver id", 401)
            if User.objects.filter(id=receiver_id).count() < 1:
                return Response("Invalid receiver id, User doesn't exist.", 401)
            if Friends.objects.filter(Q(primary_id=sender_id, friend_id=receiver_id) | Q(primary_id=receiver_id, friend_id=sender_id)).count():
                return Response("Can't send request to a friend", 401)
            if FriendRequest.objects.filter(Q(sender_id=sender_id, receiver_id=receiver_id) | Q(sender_id=receiver_id, receiver_id=sender_id)).count():
                return Response("Request is already sent", 401)
            if requests_no >= 3:
                return Response("Can't send more than 3 requests in a minute", 401)
            FriendRequest.objects.create(**serialized_data.data)
            return Response("Successful")
        return Response({"Error": serialized_data._errors}, 401)
        
class AcceptFriendRequestApi(APIView):
    def post(self, request):
        if "request_id" in request.data:
            id = request.data["request_id"]
            friend_request = FriendRequest.objects.get_or_none(id=id, receiver_id=request.user.id)
            if friend_request is not None:
                if friend_request.accepted:
                    return Response("Friend request is already accepted", 401)
                elif friend_request.rejected:
                    return Response("Friend request is already rejected", 401)
                friend_request.accepted = True
                friend_request.save()
                return Response("Successful")
            return Response({"Error": "Invalid request id"}, 401)
        return Response({"Error": {"request_id": "This is a required field"}}, 401)

class RejectFriendRequestApi(APIView):
    def post(self, request):
        if "request_id" in request.data:
            id = request.data["request_id"]
            friend_request = FriendRequest.objects.get_or_none(id=id, receiver_id=request.user.id)
            if friend_request is not None:
                if friend_request.accepted:
                    return Response("Friend request is already accepted", 401)
                elif friend_request.rejected:
                    return Response("Friend request is already rejected", 401)
                friend_request.rejected = True
                friend_request.save()
                return Response("Successful")
            return Response({"Error": "Invalid request id"}, 401)
        return Response({"Error": {"request_id": "This is a required field"}}, 401)

class FriendsList(APIView):
    def get(self, request):
        friendslist = FriendSerializer(Friends.objects.filter(Q(primary_id=request.user.id)|Q(friend_id=request.user.id)), many=True).data
        return Response({"friends": friendslist})