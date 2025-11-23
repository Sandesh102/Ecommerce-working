from django.contrib import admin
from .models import Category, Product, CartItem, Order, DeliveryAddress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'stock')
        }),
        ('Product Images', {
            'fields': ('image', 'image2', 'image3'),
            'description': 'You can upload up to 3 images. The first image is the main product image.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'province', 'district', 'location', 'phone_number', 'is_default', 'created_at']
    list_filter = ['province', 'district', 'is_default', 'created_at']
    search_fields = ['full_name', 'user__username', 'phone_number', 'location']
    list_editable = ['is_default']

admin.site.register(Order, OrderAdmin)
admin.site.register(CartItem)