from django import template

register = template.Library()

@register.simple_tag
def multiply(qty, price, *args, **kwargs):
    # you would need to do any localization of the result here
    n = 2
    total = qty * price
    # return '{:,}'.format(qty * price)
    return '{0:,.2f}'.format(total)


# {% load your_custom_template_tags %}
#
# {% for cart_item in cart.cartitem_set.all %}
#     {% multiply cart_item.quantity cart_item.unit_price %}
# {% endfor %}
