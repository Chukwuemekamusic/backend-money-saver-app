# from django.shortcuts import render
from django.http import Http404
from rest_framework.generics import (
    CreateAPIView, ListCreateAPIView, UpdateAPIView,
    GenericAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    CustomUserSerializer, SavingPlanSerializer, WeeklyAmountSerializer,
    LoginUserSerializer)

# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.authtoken.models import Token

# from django.contrib.auth import authenticate
# from rest_framework.authtoken.views import ObtainAuthToken
from .models import WeeklyAmount, CustomUser, SavingPlan

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from knox.views import (LoginView as KnoxLoginView,
                        LogoutView as KnoxLogoutView)
from knox.auth import TokenAuthentication
from knox.models import AuthToken


class UserCreateView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

# not used


class UserLoginView(KnoxLoginView):
    permission_classes = (AllowAny,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = LoginUserSerializer
    # serializer_class = CustomUserSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(UserLoginView, self).post(request, format=None)


class LoginAPI(GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": CustomUserSerializer(
                user, context=self.get_serializer_context()
            ).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserSavingPlanListCreateView(ListCreateAPIView):
    serializer_class = SavingPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SavingPlan.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class SavingPlanCreateView(CreateAPIView):
#     serializer_class = SavingPlanSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


class UserSavingPlanDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SavingPlanSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'  # Specify the lookup field to be 'pk'y

    def get_queryset(self):
        # Retrieve the list of saving plans for the authenticated user
        return SavingPlan.objects.filter(user=self.request.user)


class WeeklyAmountUpdateView(UpdateAPIView):
    queryset = WeeklyAmount.objects.all()
    serializer_class = WeeklyAmountSerializer
    permission_classes = [IsAuthenticated]
