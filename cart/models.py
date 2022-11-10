from django.conf import settings
from django.db import models

from store.models import Product


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='order_user')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    billing_status = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
        managed = True
        
    @property
    def items(self):
        return self.items_set.all()
    
    def __str__(self):
        return str(self.created)


class Items(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,
        decimal_places=2,)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
