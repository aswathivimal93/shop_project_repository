from rest_framework import serializers
from .models import Shop, ShopUser,Consumer,Payment,MenuItem,Order,OrderItem
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
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=MenuItem
        fields=['name','price']


'''class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_type', 'total_amount']

    def create(self, validated_data):
        order_list_data = validated_data.pop('order_list', [])  # Handle the case where 'order_list' is not present

        # Create the order instance
        order = Order.objects.create(**validated_data)

        # Now save the related order items
        order_items = []
        for item_data in order_list_data:
            order_item = OrderItem(order=order, **item_data)
            order_item.save()
            order_items.append(order_item)

        # Calculate the total amount
        total_amount = sum(order_item.subtotal() for order_item in order_items)
        
        # Update and save the order with the total amount
        order.total_amount = total_amount
        order.save()

        return order'''
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    #order_items = OrderItemSerializer(many=True)

    '''class Meta:
        model = Order
        fields = ['payment_type','consumer']'''
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), required=False)

    def create(self, validated_data):
        order_items_data = self.context.get('order_items_data', [])  # Access order_items_data from context

        #print("Order items data from serializer:", order_items_data)  # Add this line to print order_items_data

        with transaction.atomic():
            order = Order.objects.create(**validated_data)  # Create the order first

            # Create OrderItem instances associated with the order
            for order_item_data in order_items_data:
                menu_item_id = order_item_data.get('menu_item')
                quantity = order_item_data.get('quantity')
                # Fetch the MenuItem instance corresponding to the provided ID
                menu_item = MenuItem.objects.get(pk=menu_item_id)
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)

            # Calculate total amount by iterating over order items
            total_amount = sum(order_item.subtotal() for order_item in order.order_items.all())
            order.total_amount = total_amount
            order.save()

        return order
    class Meta:
        model = Order
        fields = ['shop', 'consumer', 'order_date', 'payment_type', 'payment', 'total_amount']

        '''def create(self, validated_data):
        #order_items_data = validated_data.pop('order_items', [])  # Extract order_items data
        order_items_data = self.context.get('order_items_data', [])  # Access order_items_data from context

        print("Order items data from serializer:", order_items_data)  # Add this line to print order_items_data

        order = Order.objects.create(**validated_data)  # Create the order first

        # Calculate total amount by iterating over order items
        total_amount = sum(order_item['menu_item'].price * order_item['quantity'] for order_item in order_items_data)
        order.total_amount = total_amount
        order.save()

        return order'''

    
      