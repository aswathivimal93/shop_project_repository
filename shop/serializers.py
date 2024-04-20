from rest_framework import serializers
from .models import Shop, ShopUser,Consumer,Payment
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction,IntegrityError
from django.db.models import Max





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

 #serializers to handle the input data for creating shop users.
class ShopUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = ShopUser
        fields = ['id', 'user', 'username', 'first_name', 'last_name', 'phone', 'email', 'total_collection', 'related_shop']

    def create(self, validated_data):

        user_data = validated_data.pop('user', None)
        print("User  data creation:", user_data)

        if user_data:
            # Hash the password before creating the user
            user_data['password'] = make_password(user_data.get('password'))
            print("User  data after hashing:", user_data)
            user_instance = User.objects.create(**user_data)
        else:
            user_instance = None 

        shop_user = ShopUser.objects.create(user=user_instance, **validated_data)

        shop_user.save()
        print("ShopUser id after creation:", shop_user.id)
        return shop_user
 


    
class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model=Shop
        fields='__all__'
class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'   

    @transaction.atomic
    def create(self, validated_data):
        # Get the maximum existing consumer code
        max_code = Consumer.objects.aggregate(Max('code'))['code__max']

        # If no existing code, start with CN00001
        if max_code is None:
            new_code = 'CN00001'
        else:
            # Extract the number part, increment by 1, and pad with zeros
            new_code = 'CN{:05d}'.format(int(max_code[2:]) + 1)

        # Add the new code to the validated data
        validated_data['code'] = new_code

        # Create the consumer instance
        return super().create(validated_data)
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'''

