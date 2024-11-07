# Generated by Django 5.1.3 on 2024-11-07 07:26

import django.core.validators
import django.db.models.deletion
import django_extensions.db.fields
import versatileimagefield.fields
import warehouse.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('iso_3166', models.CharField(max_length=10)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('invoice_number', models.CharField(max_length=50, unique=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_contact', models.CharField(max_length=15)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('invoice_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Delivered', 'Delivered')], default='Pending', max_length=9)),
                ('date_paid', models.DateTimeField(blank=True, null=True)),
                ('date_supplied', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=9)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('product_unit', models.CharField(max_length=50)),
                ('threshold_value', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('stock_value', models.FloatField(verbose_name=django.core.validators.MinValueValidator(0))),
                ('qr_code', models.CharField(max_length=100)),
                ('image', versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to=warehouse.models.path_and_filename, verbose_name='product_image')),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=9)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email address')),
                ('dial_in_code', models.CharField(default='+234', max_length=8, verbose_name='Dial_in code')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Phone number')),
                ('first_name', models.CharField(blank=True, max_length=25, verbose_name='First name')),
                ('middle_name', models.CharField(blank=True, default='', max_length=25, verbose_name='Middle name')),
                ('last_name', models.CharField(blank=True, max_length=25, verbose_name='Last name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Is staff')),
                ('is_superuser', models.BooleanField(default=False)),
                ('avatar', versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to=warehouse.models.path_and_filename, verbose_name='avatar')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', warehouse.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reset_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('quantity', models.FloatField()),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_products', to='warehouse.invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_products', to='warehouse.product')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='products',
            field=models.ManyToManyField(through='warehouse.InvoiceProduct', to='warehouse.product'),
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.DateTimeField()),
                ('quantity', models.FloatField(verbose_name=django.core.validators.MinValueValidator(0))),
                ('movement_type', models.CharField(choices=[('Increase', 'Increase'), ('Decrease', 'Decrease')], max_length=9)),
                ('stock_before', models.FloatField()),
                ('stock_after', models.FloatField()),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_movements', to='warehouse.invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_movements', to='warehouse.product')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='warehouse.supplier'),
        ),
    ]
