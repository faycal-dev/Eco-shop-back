from django.conf import settings
from django.db import models
from django.urls import reverse
# gettext_lazy is used before any text we want to translate based on the system language.
from django.utils.translation import gettext_lazy as _
# mptt is used for hiarcical data in a tree form
from mptt.models import MPTTModel, TreeForeignKey


def product_directory_path(instance, filename):
    return f'Products/{instance.product.slug}/{filename}'


class Category(MPTTModel):
    """
    Category Table implimented with MPTT.
    """

    name = models.CharField(
        verbose_name=_("Category name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    # slug is an dentifier "URL" to the category
    slug = models.SlugField(verbose_name=_(
        "Category URL"), max_length=255, unique=True)
    # here each category can have a parent category refered as foreign key in a tree format
    parent = TreeForeignKey("self", on_delete=models.CASCADE,
                            null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        # mptt config
        order_insertion_by = ["name"]

    class Meta:
        # model config
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def get_absolute_url(self):
        return reverse("store:category_list", args=[self.slug])

    def __str__(self):
        return self.name
    
    class Meta:
        managed = True


class ProductType(models.Model):
    """
    ProductType Table will provide a list of the different types
    of products that are for sale.
    """

    name = models.CharField(
        verbose_name=_("Product name"),
        help_text=_("Required"),
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        # model config
        verbose_name = _("Product type")
        verbose_name_plural = _("Product types")
    

    def __str__(self):
        return self.name
    
    class Meta:
        managed = True


class ProductSpecification(models.Model):
    """
    The Product Specification Table contains product
    specifiction or features for the product types.
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(verbose_name=_(
        "Name"), help_text=_("Required"), max_length=255)

    class Meta:
        verbose_name = _("Product Specification")
        verbose_name_plural = _("Product Specifications")

    def __str__(self):
        return self.name
    
    class Meta:
        managed = True


class Product(models.Model):
    """
    The Product table contining all product items.
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Required"),
        max_length=255,
    )
    description = models.TextField(verbose_name=_(
        "description"), help_text=_("Not Required"), blank=True)
    slug = models.SlugField(max_length=255)
    regular_price = models.DecimalField(
        verbose_name=_("Regular price"),
        help_text=_("Maximum 99999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 99999.99."),
            },
        },
        max_digits=10,
        decimal_places=2,
    )
    discount_price = models.DecimalField(
        verbose_name=_("Discount price"),
        help_text=_("Maximum 99999.99"),
        error_messages={
            "name": {
                "max_length": _("The price must be between 0 and 99999.99."),
            },
        },
        max_digits=7,
        decimal_places=2,
    )
    brand = models.CharField(
        verbose_name=_("brand"),
        help_text=_("Required"),
        max_length=255,
        default=""
    )
    rating_number = models.IntegerField(
        verbose_name=_("Total number of ratings"),
        default=0

    )
    rating = models.DecimalField(
        verbose_name=_("rating"),
        help_text=_("Maximum 5"),
        error_messages={
            "name": {
                "max_length": _("The rating must be between 0 and 5."),
            },
        },
        max_digits=2,
        decimal_places=1,
        default=0
    )
    is_active = models.BooleanField(
        verbose_name=_("Product visibility"),
        help_text=_("Change product visibility"),
        default=True,
    )
    created_at = models.DateTimeField(
        _("Created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    users_wishlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="user_wishlist", blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
    
    @property
    def productSpecificationValue(self):
        return self.productspecificationvalue_set.all()

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    def __str__(self):
        return self.title

    class Meta:
        managed = True


class ProductSpecificationValue(models.Model):
    """
    The Product Specification Value table holds each of the
    products individual specification or features.
    """

    # once product deleted we don't need it
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # but if restriction deleted we need to keep it anyway
    specification = models.ForeignKey(
        ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name=_("value"),
        help_text=_("Product specification value (maximum of 255 words"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Product Specification Value")
        verbose_name_plural = _("Product Specification Values")
        managed = True

    def __str__(self):
        return self.value



class ProductImage(models.Model):
    """
    The Product Image table.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_image")
    # a link to the image
    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_("Upload a product image"),
        upload_to=product_directory_path,
        default="images/default.png",
    )
    alt_text = models.CharField(
        verbose_name=_("Alturnative text"),
        help_text=_("Please add alturnative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    is_feature = models.BooleanField(
        default=False)  # the main image of a product
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        managed = True
