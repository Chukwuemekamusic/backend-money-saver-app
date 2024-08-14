# from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
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

from .models import WeeklyAmount, CustomUser, SavingPlan

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.utils import timezone

from knox.views import (LoginView as KnoxLoginView,
                        LogoutView as KnoxLogoutView)
from knox.auth import TokenAuthentication
from knox.models import AuthToken

from rest_framework.exceptions import PermissionDenied
from .utils import get_id_token, get_id_token_alt
from .services import get_user_data
from .utils import authentication_or_create_user

# signup
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
import logging
from .utils import Util

# from django.contrib.sites.shortcuts import get_current_site
# 
logger = logging.getLogger(__name__)

def email_confirm_redirect(request, key):
    return HttpResponseRedirect(settings.EMAIL_CONFIRM_REDIRECT_BASE_URL + key + '/')

def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL + uidb64 + '/' + token + '/')

# TODO: Google OAuth2
class GoogleLoginView(APIView):
    def post(self, request):
        if 'code' in request.data:
            code = request.data['code']
            # id_token = get_id_token2(code)
            id_token = get_id_token_alt(code)
            print('id_token', id_token)
            if id_token is None:
                return Response({"error": "Failed to retrieve ID token"}, status=status.HTTP_400_BAD_REQUEST)
            
            user_email = id_token['email']
            if user_email is None:
                return Response({"error": "Email not found in ID token"}, status=status.HTTP_400_BAD_REQUEST)
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


# class GoogleLoginView2(APIView):

#     def get(self, request, *args, **kwargs):
#         auth_serializer = AuthSerializer(data=request.GET)
#         auth_serializer.is_valid(raise_exception=True)
        
#         validated_data = auth_serializer.validated_data
#         user_data = get_user_data(validated_data)
        
#         user = CustomUser.objects.get(email=user_data['email'])
#         login(request, user)
#         print(user)

#         return redirect(settings.BASE_APP_URL)

class UserCreateView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


# a new view that handles registers but ensures that email validation is done
class UserRegisterView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        user.is_email_verified = False
        user.is_active = False
        user.save()
        self.send_email_confirmation(user)
    
    def send_email_confirmation(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # current_site = get_current_site(request)
        # verification_link = f"{current_site.domain}/verify-email/{uid}/{token}/"
        verification_link = f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{uid}/{token}/"

        subject = "Verify your email address"
        data = {
            'email_subject': subject,
            'email_body': verification_link,
            'to_email': user.email
        }
        
        try:
            Util.send_email(data)
        except Exception as e:
            # Log the error or handle it as needed
            logger.error(f"Error sending email: {e}")
            # Optionally, you could raise an exception or return a response indicating failure
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Registration successful. Please check your email to verify your account."}, status=response.status_code)

class ActivateUserApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True  # Activate the user account
            user.save()
            login(request, user)  # log in the user
            
            # create or retrieve the token
            _, token = AuthToken.objects.create(user)
            return Response({
                "message": "Email verified successfully.",
                "user": CustomUserSerializer(user).data,
                "token": token
            })
        else:
            return Response({"error": "Activation link is invalid!"}, status=status.HTTP_400_BAD_REQUEST)


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
        if not user.is_email_verified:
            return Response({"error": "Email not verified."}, status=status.HTTP_403_FORBIDDEN)
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
