from .models import Cart, CartItem

def cart_items_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_items_count': count}