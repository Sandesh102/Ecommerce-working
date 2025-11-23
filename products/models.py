from django.db import models
from django.conf import settings  # Import settings to reference the user model
from django.utils.text import slugify


# ------------------------- Category Model -------------------------
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ------------------------- Product Model -------------------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to="products/images/", blank=True, null=True, default="products/images/default.png",
        help_text="Main product image (required)"
    )
    image2 = models.ImageField(
        upload_to="products/images/", blank=True, null=True,
        help_text="Second product image (optional)"
    )
    image3 = models.ImageField(
        upload_to="products/images/", blank=True, null=True,
        help_text="Third product image (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_additional_images(self):
        """Get additional images (image2 and image3) if they exist"""
        images = []
        if self.image2:
            images.append(self.image2)
        if self.image3:
            images.append(self.image3)
        return images


# ------------------------- CartItem Model -------------------------
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} in cart"


# ------------------------- DeliveryAddress Model -------------------------
class DeliveryAddress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="delivery_address")
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # City/Municipality
    street_address = models.TextField()  # Detailed street address
    landmark = models.CharField(max_length=200, blank=True, null=True)  # Optional landmark
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Delivery Addresses"

    def save(self, *args, **kwargs):
        # Single address per user; just save
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.location}, {self.district}"


# ------------------------- Order Model -------------------------
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Fake Screenshot', 'Fake Screenshot'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending Payment Verification'),  # QR payment screenshot uploaded, awaiting admin verification
        ('Order Confirmed', 'Order Confirmed'),    # Payment verified (auto for Khalti, manual for QR)
        ('Processing', 'Processing'),                  # Order is being prepared/packed
        ('Shipped', 'Shipped'),                        # Order dispatched for delivery
        ('Out for Delivery', 'Out for Delivery'),      # Order is with delivery person
        ('Delivered', 'Delivered'),                    # Order successfully delivered
        ('Cancelled', 'Cancelled'),                    # Order cancelled by user/admin
        ('Failed', 'Failed'),                          # Payment failed or order rejected
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_proof = models.FileField(upload_to='products/payment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

