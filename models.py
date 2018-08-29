from __future__ import unicode_literals
from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid

class size(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)

class color(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.name)

class product_type(models.Model):
    name          = models.CharField(max_length=1000)
    description   = models.TextField(max_length=10000)
    is_clothing   = models.BooleanField(default=False)
    display_name  = models.CharField(max_length=1000, default="")
    sub_type_only = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

# These are the distinct images Enspirus Arts creates.
# An image may be on many different products.
class image(models.Model):
    name          = models.CharField(max_length=2000, unique=True)
    display_name  = models.CharField(max_length=2000, default="")
    description   = models.TextField(max_length=10000)
    # Depricated. Delete commented line below once fully confident not needed.
    #product_types = models.ManyToManyField(product_type)

    def __str__(self):
        return self.name

# These are the products that we're selling.
class product(models.Model):
    name           = models.CharField(max_length=1000, unique=True)
    description    = models.TextField(max_length=10000)
    product_type   = models.ForeignKey(product_type, default=1, related_name='product_type')
    sub_types      = models.ManyToManyField('product_type', null=True, blank=True, related_name='sub_types')
    available      = models.IntegerField(default=0)
    # Sometimes we may have a sale on particular items. This modifier allows us to do this.
    # Sometimes we may have a popular item that should cost more. This modifier allows us to do this.
    # price_modifier = -10 would mean that the item is 10% off.
    # rpice_modifier =  10 would mean that the item costs 10% more (than what is defined in the price table).
    price_modifier = models.FloatField(default=0)
    image_file     = models.ImageField(upload_to="static/ludega_art/product_images/", null=True, blank=True)
    image          = models.ForeignKey(image, default=1)
    colors         = models.ManyToManyField(color)
    sizes          = models.ManyToManyField(size)
    display        = models.BooleanField(default=False)
    order          = models.DecimalField(default=0.0, decimal_places=10,max_digits=20)

    def in_stock(self):
        return self.available > 0

    in_stock.boolean = True
    in_stock.short_description = 'In Stock?'


    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('name',)

# These are the products that show up at the top of the page
class top_product(models.Model):
    name = models.ForeignKey(product, on_delete=models.CASCADE)

    def description(self):
        return self.name.description

    def product_type(self):
        return self.name.product_type

    def available(self):
        return self.name.available

    def price_modifier(self):
        return self.name.price_modifier

    def in_stock(self):
        return self.name.available > 0

    in_stock.boolean = True
    in_stock.short_description = 'In Stock?'

    def __str__(self):
        return str(self.name)

# These are the prices for products of different types and sizes
class price(models.Model):
    product_type    = models.ForeignKey(product_type)
    size    = models.ForeignKey(size)
    price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.product_type) + "_" + str(self.size) + "_" + str(self.price)

# This table keeps track of how many of each product we have
class stock(models.Model):
    product = models.ForeignKey(product)
    size    = models.ForeignKey(size)
    stock   = models.IntegerField()

    def __str__(self):
        return str(self.stock) + "_" + self.size + "_" + self.product

class shopfiy_variant_id(models.Model):
    product    = models.ForeignKey(product)
    type       = models.ForeignKey(product_type)
    size       = models.ForeignKey(size)
    variant_id = models.CharField(max_length=2000)

    def __str__(self):
        return str(self.product.name) + "_" + str(self.size) + "_" + str(self.type)

class Board(models.Model):
    pieces = ArrayField(ArrayField(models.IntegerField()))

class customer_order(models.Model):
    email = models.CharField(max_length=2000)
    firstName = models.CharField(max_length=2000)
    lastName = models.CharField(max_length=2000)
    address1 = models.CharField(max_length=2000)
    address2 = models.CharField(max_length=2000)
    city = models.CharField(max_length=2000)
    state = models.CharField(max_length=2000)
    zip = models.IntegerField()
    country = models.CharField(max_length=2000)
    shipping_cost = models.DecimalField(decimal_places=2, max_digits=1000)
    shipping_method = models.CharField(max_length=2000)
    total_price = models.DecimalField(decimal_places=2, max_digits=1000)
    order_time = models.DateTimeField()
    order_fulfilled = models.BooleanField()
    sales_tax = models.DecimalField(decimal_places=2, max_digits=1000)
    order_price = models.DecimalField(decimal_places=2, max_digits=1000)
    order_id_hash = models.CharField(max_length=2000)
    customer_note = models.CharField(max_length=2000)


    def __str__(self):
        return str(self.id)

class order_detail(models.Model):

    product = models.ForeignKey(product)
    product_type = models.ForeignKey(product_type)
    product_size = models.ForeignKey(size)
    item_price = models.ForeignKey(price)
    product_quantity = models.IntegerField()
    customer_order = models.ForeignKey(customer_order)


    def __str__(self):
        return str(self.id)





