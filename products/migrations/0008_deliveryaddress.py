# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0007_remove_wishlist_product_remove_wishlist_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=15)),
                ('province', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('street_address', models.TextField()),
                ('landmark', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Delivery Addresses',
            },
        ),
    ]
