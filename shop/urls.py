from django.urls import path,include
from rest_framework.routers import DefaultRouter
from shop.api import ShopUserViewSet,ShopViewSet,ConsumerViewSet,PaymentViewSet,MenuItemViewSet,OrderViewSet

router = DefaultRouter()
router.register('api/shopuser', ShopUserViewSet, basename='shopuser')
router.register('api/shop',ShopViewSet,basename='shop')
router.register('api/consumer',ConsumerViewSet,basename='consumer')
router.register('api/payment',PaymentViewSet,basename='payment')
router.register('api/menuitem',MenuItemViewSet,basename='menuitem')
router.register('api/order',OrderViewSet,basename='order')



urlpatterns=router.urls


