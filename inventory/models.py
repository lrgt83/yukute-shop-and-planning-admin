from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from computed_property import ComputedBooleanField


class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categoria"


class Provider(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


class InventoryType(models.TextChoices):
    SALABLE = "SB", "Para venta"
    EVENTS = "EV", "Para eventos"


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    inventory_type = models.CharField(
        max_length=2,
        choices=InventoryType.choices,
        default=InventoryType.SALABLE,
    )
    min_threshold = models.PositiveIntegerField(null=True, blank=True)
    supplied = ComputedBooleanField(compute_from="is_supplied")
    barcode = models.CharField(max_length=100, blank=True, null=True)

    @property
    def is_supplied(self):
        if self.min_threshold is not None and self.stock is not None:
            return self.stock > self.min_threshold
        return True

    def __str__(self):
        return self.name

    def increment_stock(self, amount):
        self.stock = self.stock + amount
        self.save()

    def decrement_stock(self, amount):
        self.stock = self.stock - amount
        self.save()

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    voided = models.BooleanField(default=False)

    def __str__(self):
        return f"Compra {self.pk} realizada por {self.user.username}"

    def void_purchase(self):
        for purchaseItem in self.purchase_items.all():
            purchaseItem.product.decrement_stock(purchaseItem.quantity)
        self.voided = True
        self.save()

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"


class PurchaseItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="purchase_items"
    )
    expiration_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} comprado en {self.purchase}"

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"


class SaleType(models.TextChoices):
    REGULAR_SALE = "RS", "Venta normal"
    EVENT = "EV", "Evento"


class SaleInvoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    sale_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    voided = models.BooleanField(default=False)
    sale_type = models.CharField(
        max_length=2,
        choices=SaleType.choices,
        default=SaleType.REGULAR_SALE,
    )

    def __str__(self):
        return f"{self.id} | {self.customer} | {self.sale_type}"

    def void_sale(self):
        for saleItem in self.sale_invoice_items.all():
            saleItem.product.increment_stock(saleItem.quantity)
        self.voided = True
        self.save()

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class SaleInvoiceItem(models.Model):
    sale_invoice = models.ForeignKey(
        SaleInvoice, on_delete=models.CASCADE, related_name="sale_invoice_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # def __str__(self):
    #     return f"{self.quantity} x {self.product.name} comprado en {self.sale_invoice}"

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"


class CashFlowType(models.TextChoices):
    INCOME = "IN", "Ingreso de efectivo"
    CASH_OUT = "OUT", "Retiro de efectivo"


class CashFlow(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    operation_type = models.CharField(
        max_length=3,
        choices=CashFlowType.choices,
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Flujo de efectivo"
        verbose_name_plural = "Flujos de efectivo"
