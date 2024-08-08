from rest_framework import serializers
from .models import CustomUser, SavingPlan, WeeklyAmount
from rest_framework.serializers import (ModelSerializer)
from django.contrib.auth import authenticate


class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = f"{validated_data['first_name']}_{validated_data['last_name']}"
        validated_data['username'] = username
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    # def validate(self, data):
    #     user = authenticate(**data)
    #     if user and user.is_active:
    #         return user
    #     raise serializers.ValidationError("Invalid Details.")

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Please provide both email and password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        return user


class SaveWeeklyAmountSerializer(ModelSerializer):
    class Meta:
        model = WeeklyAmount
        fields = ['id', 'amount', 'selected', 'week_index',
                  'date_selected']

# TODO fix that only users can save to their list


class WeeklyAmountSerializer(ModelSerializer):
    # saving_plan = serializers.PrimaryKeyRelatedField(queryset=SavingPlan.objects.all(), write_only=True)
    saving_plan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WeeklyAmount
        fields = ['id', 'amount', 'selected', 'week_index',
                  'date_selected', 'saving_plan']

def get_amount_list(saving_plan):
    """
    Helper function to fetch the amount_list associated with the SavingPlan.
    """
    amount_list = WeeklyAmount.objects.filter(saving_plan=saving_plan)
    serializer = WeeklyAmountSerializer(amount_list, many=True)
    return serializer.data

class SavingPlanSerializer(ModelSerializer):
    amount_list = WeeklyAmountSerializer(many=True)
    # selected_weekly_amount = serializers.SerializerMethodField()

    class Meta:
        model = SavingPlan
        fields = ['id', 'user', 'savings_name',
                  'amount', 'date_created', 'amount_list', 'number_of_weeks', 'total_saved_amount']

    def create(self, validated_data):
        amount_list_data = validated_data.pop('amount_list')
        # validated_data['user'] = self.request.user
        saving_plan = SavingPlan.objects.create(**validated_data)

        for amount_data in amount_list_data:
            WeeklyAmount.objects.create(saving_plan=saving_plan, **amount_data)
        return saving_plan
    
    # def get_selected_weekly_amounts(self, obj):
    #     return obj.selected_weekly_amounts()
        
# update weeklyAmount
