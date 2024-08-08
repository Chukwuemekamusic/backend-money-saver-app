# from django.shortcuts import render
from django.http import Http404
from django.db.models import Max
from django.shortcuts import redirect
from django.conf import settings

from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
    GenericAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    AuthSerializer, CustomUserSerializer, SavingPlanSerializer, WeeklyAmountSerializer,
    LoginUserSerializer)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import mixins
# from rest_framework.authtoken.models import Token

# from django.contrib.auth import authenticate
# from rest_framework.authtoken.views import ObtainAuthToken
from .models import WeeklyAmount, CustomUser, SavingPlan

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.utils import timezone

from knox.views import (LoginView as KnoxLoginView,
                        LogoutView as KnoxLogoutView)
from knox.auth import TokenAuthentication
from knox.models import AuthToken

from rest_framework.exceptions import PermissionDenied
from .utils import get_id_token2, get_id_token_alt
from .services import get_user_data
from .utils import authentication_or_create_user


# TODO: Google OAuth2
class GoogleLoginView(APIView):
    def post(self, request):
        if 'code' in request.data:
            code = request.data['code']
            # id_token = get_id_token2(code)
            id_token = get_id_token_alt(code)
            user_email = id_token['email']
            first_name = id_token.get('given_name', '')
            last_name = id_token.get('family_name', '')
            user = authentication_or_create_user(user_email, first_name, last_name)
            user_data = CustomUserSerializer(user).data  # Serialize the user object
            _, token = AuthToken.objects.create(user)
            print('user_data', user_data)
            print('user', user)
            print('token', token)
            return Response({
                "user": user_data,
                "token": token
            })
        else:
            return Response({"message": "Google login failed"})


class GoogleLoginView2(APIView):

    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)
        
        user = CustomUser.objects.get(email=user_data['email'])
        login(request, user)
        print(user)

        return redirect(settings.BASE_APP_URL)

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


class GetUserView(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user


# class LogoutUserView(KnoxLogoutView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Perform logout actions
        request.auth.delete()  # Delete the user's token
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserSavingPlanListView(ListAPIView):
    serializer_class = SavingPlanSerializer
    permission_classes = [IsAuthenticated]
    
    # def validate(self, data):
    #     # Access the request object from the serializer's context
    #     request = self.context.get('request')
    #     data['user'] = request.user

    #     return data

    def get_queryset(self):
        queryset = SavingPlan.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        # serializer.validated_data['user'] = self.request.user
        serializer.save()
        # serializer.save(user=self.request.user)

    #  def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     for saving_plan in serializer.data:
    #         saved_amount = sum(amount['amount'] for amount in saving_plan['amount_list'] if amount['selected'])
    #         saving_plan['saved_amount'] = saved_amount
    #     return Response(serializer.data)


class SavingPlanCreateView(CreateAPIView):
    serializer_class = SavingPlanSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk']).first()

        # Check if the associated SavingPlan belongs to the current user
        if obj.saving_plan.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to perform this action.")

        return obj

    # TODO will this still work with queryset instead of WeeklyAmounts
    def perform_update(self, serializer):
        instance = serializer.instance
        data = self.get_queryset().filter(
            saving_plan=instance.saving_plan)
        max_week_index = data.aggregate(Max('week_index', default=0))
        latest_week_index = max_week_index['week_index__max']

        if latest_week_index != 0:
            instance.week_index = latest_week_index + 1
        else:
            instance.week_index = 1
        
        instance.date_selected = timezone.now()

        serializer.save()
        # print(data)
        # print()
        # print(type(max_week_index['week_index__max']))
        # print(instance.week_index)

        # return super().perform_update(serializer)

    # def get_object(self):
    #     saving_plan_id = self.kwargs['saving_plan_id']
    #     saving_plan_instance = SavingPlan.objects.get(id=saving_plan_id)
    #     self.queryset.filter(savings_plan=saving_plan_instance)
