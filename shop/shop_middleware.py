from django.utils.deprecation import MiddlewareMixin
from shop.models import ShopUser

'''
class ShopMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                # Assuming ShopUser is related to User and contains the related_shop field
                request.shop_id = request.user.shopuser.related_shop.id
                print("shopid:")
                print( request.shop_id)
            except ShopUser.DoesNotExist:
                # Handle the case where the ShopUser instance doesn't exist
                request.shop_id = None
'''
class ShopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_shop():
            if not hasattr(request, "_shop"):
                if request.user.is_authenticated:
                    shopuser_profile = getattr(request.user, 'shopuser', None)
                    request._shop = shopuser_profile.related_shop if shopuser_profile else None
                else:
                    request._shop = None
            return request._shop

        request.get_shop = lambda : get_shop()
        return self.get_response(request)