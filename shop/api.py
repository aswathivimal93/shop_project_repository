from shop.models import ShopUser,Shop,Consumer,Payment,MenuItem,OrderItem,Order
from rest_framework import viewsets,permissions
from .serializers import ShopUserSerializer,ShopSerializer,ConsumerSerializer,PaymentSerializer,UserSerializer,MenuItemSerializer,OrderSerializer
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from decimal import Decimal




class ShopUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopUserSerializer

    def get_queryset(self):
        return ShopUser.objects.filter(user=self.request.user)

    def perform_create(self, serializer):    
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create Shopuser.")
        
        # Extract user data from request data
        user_data = self.request.data.pop('user', {})
        
        # Hash the password before saving the user
        if 'password' in user_data:
            hashed_password = make_password(user_data['password'])
            print("Hashed password:", hashed_password)
            user_data['password'] = hashed_password
        
        # Save shop user and user
        serializer.is_valid(raise_exception=True)
        shop_user_instance = serializer.save()
        
        # Add the id of the created instance to the serializer data
        serializer_data = serializer.data
        serializer_data['id'] = shop_user_instance.id
        
        # No need to save user_serializer separately, it's automatically saved
        
        return Response(serializer_data, status=status.HTTP_201_CREATED)



class ShopViewSet(viewsets.ModelViewSet):
    permission_classes=[
        permissions.IsAuthenticated
    ]
    serializer_class=ShopSerializer
    def get_queryset(self):
        return Shop.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create Shop.")
        serializer.save(created_by=self.request.user,updated_by=self.request.user)
    
   

class ConsumerViewSet(viewsets.ModelViewSet):
    permission_classes=[
       permissions.IsAuthenticated
    ]
    serializer_class=ConsumerSerializer
    def get_queryset(self):
        return Consumer.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        if  self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create consumer.")
        serializer.save(created_by=self.request.user,updated_by=self.request.user)



class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def make_payment(self, request):
        consumer_code = request.data.get('consumer_code')
        amount = request.data.get('amount')
        payment_type = request.data.get('type')
       
         # Fetch the shop  from the middleware
        shop = self.request.get_shop()
        if shop is None:
            return Response({"message": "Shop  not found in request."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            consumer = Consumer.objects.get(code=consumer_code)
        except Consumer.DoesNotExist:
            return Response({"message": "Consumer not found. Please create the consumer first."}, status=status.HTTP_404_NOT_FOUND)
         
         # Check if the shop associated with the payment matches the shop associated with the consumer's creator
        if consumer.created_by.shopuser.related_shop.id != shop.id:
            return Response({"message": "Payment shop does not match consumer creator's shop."}, status=status.HTTP_400_BAD_REQUEST)

        if payment_type == 'debit':
            consumer.total_debit += amount
        elif payment_type == 'credit':
            consumer.total_credit+=amount
            consumer.total_debit -= amount
        consumer.save()

         # Check if there's an existing payment for the consumer
        payment = Payment.objects.filter(consumer=consumer,shop=shop).first()
        if payment:
            payment.amount = amount
            payment.type = payment_type
            payment.updated_by = request.user
        else:    
            payment_data = {
                'amount': amount,
                'consumer': consumer.id,
                'type': payment_type,
                'shop': shop.id,
                'created_by': request.user.id,  
                'updated_by': request.user.id
            }
            serializer = PaymentSerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        payment.save()
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MenuItemViewSet(viewsets.ModelViewSet):
    permission_classes=[
       permissions.IsAuthenticated
    ]
    serializer_class=MenuItemSerializer
    

    def get_queryset(self):
        shop = self.request.get_shop()
        return MenuItem.objects.filter(shop=shop)
    def perform_create(self, serializer):
        shop = self.request.get_shop()
        if shop is None:
            return Response({"message": "Shop  not found in request."}, status=status.HTTP_400_BAD_REQUEST)
        if  self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create consumer.")
        serializer.save(shop=shop)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        shop = self.request.get_shop()
        if shop is None:
            return Response({"message": "Shop  not found in request."}, status=status.HTTP_400_BAD_REQUEST)
        
        order_items_data = request.data.get('order_items', [])  # Get order_items_data from request data
        #print("order_items_data",order_items_data)
        serializer = OrderSerializer(data=request.data, context={'order_items_data': order_items_data})
        

        if serializer.is_valid():
            payment_type = serializer.validated_data.get('payment_type')    
            order = serializer.save(shop=shop)

            if payment_type == 'credit':
                consumer_id = request.data.get('consumer')
                try:
                    consumer = Consumer.objects.get(id=consumer_id)
                except Consumer.DoesNotExist:
                    return Response({"message": "Consumer not found. Please create the consumer first."}, status=status.HTTP_404_NOT_FOUND)
                # Check if the shop associated with the payment matches the shop associated with the consumer's creator
                if consumer.created_by.shopuser.related_shop.id != shop.id:
                    return Response({"message": "Payment shop does not match consumer creator's shop."}, status=status.HTTP_400_BAD_REQUEST)
                consumer.save()
                 # Check if there's an existing payment for the consumer
                
                    # Create a new payment entry
                payment_data = {
                    'amount': 0.0 ,
                    'consumer': consumer.id,
                    'type': payment_type,
                    'shop': shop.id,
                    'created_by': request.user.id,
                    'updated_by': request.user.id
                        }
                payment_serializer = PaymentSerializer(data=payment_data)

                if payment_serializer.is_valid():

                    payment=payment_serializer.save()
                    # Assign the created payment instance to the payment field of the order
                    order.payment = payment
                    order.save()
                    payment.amount=order.total_amount
                    payment.save()
                    consumer.total_credit+=order.total_amount
                    consumer.total_debit -= order.total_amount
                    consumer.save()
                else:
                 return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    

            elif payment_type == 'paid':
                # If payment is paid, total_amount should be already calculated
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)