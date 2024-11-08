from django.db.models.signals import post_save
from django.dispatch import receiver

from warehouse.models import Product, User
from warehouse.utils import send_threshold_alert


@receiver(post_save, sender=Product)
def send_threshold_notification(sender, instance, **kwargs):
    if instance.stock_value <= instance.threshold_value:
        managers = User.objects.filter(groups__name='Warehouse Manager')
        send_threshold_alert(instance, managers)
