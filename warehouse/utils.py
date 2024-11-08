
import os
import threading
from django.core.mail import EmailMessage
from django_filters import rest_framework as filters
from . import models
# from .models import User


# @shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()


def send_threshold_alert(product, managers):
    for user in managers:
        email_body = f"<html>" \
                     f"<head>" \
                     f"</head>" \
                     f"<body>" \
                     f"<p>Hi {user.first_name},</p>" \
                     f"<p>This is to notify you that the product <b>{product.name}</b> is running low. The current stock is {product.stock_value} {product.product_unit}</p>" \
                     f"<p>Consider restocking as soon as possible</p>" \
                     f"</body>" \
                     f"</html>"

        payload = {
            'subject': 'Product level notification',
            'html_content': email_body,
            'to_email': user.email
        }
        threshold_alert_thread = threading.Thread(
            target=send_email, args=(payload,)
        )
        threshold_alert_thread.start()
    return


def send_pw_reset_email(token, user):
    frontend_url = os.getenv('FRONTEND_URL')
    email_body = f"<html>" \
                 f"<head>" \
                 f"</head>" \
                 f"<body>" \
                 f"<p>Hi {user.first_name},</p>" \
                 f"<p>You requested for a password reset on <b>WareHouse</b></p>" \
                 f"<p>Kindly click on the link below to reset your password</p>" \
                 f"<a href=\"{frontend_url}?email={user.email}&token={token}\">Reset password</a>" \
                 f"</body>" \
                 f"</html>"

    payload = {
        'subject': 'Password Reset',
        'html_content': email_body,
        'to_email': user.email
    }
    pw_reset_thread = threading.Thread(
        target=send_email, args=(payload,)
    )
    pw_reset_thread.start()
    return


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    supplier = filters.NumberFilter(field_name='supplier', lookup_expr='exact')
    # stock_value = filters.LookupChoiceFilter(
    #     field_name='stock_value',
    #     lookup_choices=[('exact', 'Equal'), ('gte', 'Greater than'), ('lte', 'Less than')]
    # )
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")


class StockMovementFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name='user', lookup_expr='exact')
    product = filters.NumberFilter(field_name='product', lookup_expr='exact')
    invoice = filters.NumberFilter(field_name='invoice', lookup_expr='exact')
    # exact_date = filters.DateFilter(field_name='date__date', lookup_expr='exact')
    # before_date = filters.DateFilter(field_name='date__date', lookup_expr='lte')
    # after_date = filters.DateFilter(field_name='date__date', lookup_expr='gte')
    movement_type = filters.CharFilter(field_name='movement_type', lookup_expr='iexact')


def generate_invoice_number():
    last_invoice = models.Invoice.objects.filter(invoice_number__isnull=False).order_by('invoice_number').last()
    if last_invoice:
        invoice_number = int(last_invoice.invoice_number.split('-')[-1]) + 1
        return f'INV-{invoice_number:06}'
    return 'INV-000001'
